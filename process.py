import numpy as np
import numpy.ma as ma
from netCDF4 import Dataset
import os
import os.path
import scipy.interpolate as interp
import scipy.stats as stats
from config import *

## PART 1: Import data and combine

# Import model files for RCP 2.6 and 8.5, replacing masked data with nans
def importData(dataFiles):
	data = []
	for dataFileName in dataFiles:
		dataFile = dataDir + "/" + dataFileName
		# Because latitudes and logitudes are of different sizes, we must interpolate.
		dataRaw = Dataset(dataFile, "r").variables[varOfInterest][:]
		# Loop through time, interpolating latitude and longitude
		dataInterp = np.zeros((numMonths, latitudeRes, longitudeRes))
		for i in range(numMonths):
			dataInterpGen = interp.interp2d(np.arange(dataRaw.shape[2]), np.arange(dataRaw.shape[1]), dataRaw[i])
			dataInterp[i] = dataInterpGen(np.linspace(0, dataRaw.shape[2], longitudeRes), np.linspace(0, dataRaw.shape[1], latitudeRes))
		data += [dataInterp]
	# Stack, average, and return
	return np.stack(data,axis=0).mean(axis=0)

# Create cache, try to import from cache, and if it isn't possible, import from data instead
if not os.path.exists(cacheDir):
	os.mkdir(cacheDir)
if not os.path.exists(cacheDir + '/rcpData.npz'):
	np.savez_compressed(cacheDir + '/rcpData.npz', rcp26=importData(dataFilesRCP26), rcp85=importData(dataFilesRCP85))
allData = np.load(cacheDir + '/rcpData.npz')
dataRCP26 = allData['rcp26']
dataRCP85 = allData['rcp85']

## PART 2: Process data

# Process data if it wasn't cached
if not os.path.exists(cacheDir + '/processedData.npz'):
	# Remove irrelavent realms using ocean data
	landSea = Dataset(dataDir + "/" + landSeaFile,'r')
	landSeaData = landSea.variables['LSMASK'][:]
	landSeaInterpGen = interp.interp2d(np.arange(landSeaData.shape[1]), np.arange(landSeaData.shape[0]), landSeaData)
	landSeaDataInterp = landSeaInterpGen(np.linspace(0, landSeaData.shape[1], longitudeRes), np.linspace(0, landSeaData.shape[0], latitudeRes))
	# Set mask according to realm specified in config
	if realm == 'land':
		landSeaMask = np.tile(landSeaDataInterp == 0, (numMonths, 1, 1))
	elif realm == 'sea':
		landSeaMask = np.tile(landSeaDataInterp != 0, (numMonths, 1, 1))
	elif realm == 'atmos':
		landSeaMask = False

	# Apply mask
	dataRCP26 = ma.masked_array(dataRCP26, mask=landSeaMask)
	dataRCP85 = ma.masked_array(dataRCP85, mask=landSeaMask)

	# Get difference between the two RCPs and between each RCP and its initial value and divide it to a difference (-1 for -100% and +1 for +100%) for our difference graph.
	def getPercentDifference(data1, data2):
		dataDiff = data1 - data2
		return dataDiff/data2
	# Difference from initial
	diffRCP26 = getPercentDifference(dataRCP26, dataRCP26[0,:])
	diffRCP85 = getPercentDifference(dataRCP85, dataRCP85[0,:])
	diffRCPs = getPercentDifference(dataRCP85, dataRCP26)

	# Change data to rankings, replacing oceans with -inf, then mask oceans (again; stats.rankdata doesn't like masks.) They'll come as the lowest value.
	percRCP26 = stats.rankdata(ma.filled(dataRCP26, -np.inf), method='dense').reshape(dataRCP26.shape)
	percRCP85 = stats.rankdata(ma.filled(dataRCP85, -np.inf), method='dense').reshape(dataRCP85.shape)
	percRCP26 = ma.masked_array(percRCP26, mask=(percRCP26 == 1))
	percRCP85 = ma.masked_array(percRCP85, mask=(percRCP85 == 1))

	# Normalize data to between 0 and 1 and reverse it to make them into precentiles
	minVal = min(percRCP26.min(), percRCP85.min())
	maxVal = max(percRCP26.max(), percRCP85.max())
	rangeVal = maxVal-minVal
	percRCP26 = (percRCP26 - minVal)/rangeVal
	percRCP85 = (percRCP85 - minVal)/rangeVal

	# Cache our processed data
	if realm == 'atmos':
		np.savez_compressed(cacheDir + '/processedData.npz',
			perc26=percRCP26, perc26_mask=percRCP26.mask,
			perc85=percRCP85, perc85_mask=percRCP85.mask,
			diff26=diffRCP26, diff26_mask=diffRCP26.mask,
			diff85=diffRCP85, diff85_mask=diffRCP85.mask,
			diffRCP=diffRCPs, diffRCP_mask=diffRCPs.mask,
			landSea=landSeaDataInterp)
	else: # Realm is land or sea
		np.savez_compressed(cacheDir + '/processedData.npz',
			perc26=percRCP26, perc26_mask=percRCP26.mask,
			perc85=percRCP85, perc85_mask=percRCP85.mask,
			diff26=diffRCP26, diff26_mask=diffRCP26.mask,
			diff85=diffRCP85, diff85_mask=diffRCP85.mask,
			diffRCP=diffRCPs, diffRCP_mask=diffRCPs.mask)

print("Done. Run plot.py to show.")