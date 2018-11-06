import numpy as np
import numpy.ma as ma
from netCDF4 import Dataset
import matplotlib
import matplotlib.cm
import matplotlib.pyplot as plt
import scipy.interpolate as interp
import scipy.stats as stats
from matplotlib.widgets import Slider
import os
import os.path

# Variables for study area of interest
dataDir = "data"
cacheDir = "cache"
landSeaFile = "landsea.nc"
dataFilesRCP26 = ["mrso_Lmon_HadGEM2-AO_rcp26_r1i1p1_200601-210012.nc", "mrso_Lmon_MPI-ESM-LR_rcp26_r1i1p1_200601-210012.nc", "mrso_Lmon_MRI-CGCM3_rcp26_r1i1p1_200601-210012.nc"]
dataFilesRCP85 = ["mrso_Lmon_HadGEM2-AO_rcp85_r1i1p1_200601-210012.nc", "mrso_Lmon_MPI-ESM-LR_rcp85_r1i1p1_200601-210012.nc", "mrso_Lmon_MRI-CGCM3_rcp85_r1i1p1_200601-210012.nc"]
varOfInterest = "mrso"
numMonths = 1140
latitudeRes = 90
longitudeRes = 180
diffAmplification = 2

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
	# Remove oceans using ocean data
	landSea = Dataset(dataDir + "/" + landSeaFile,'r')
	landSeaData = landSea.variables['LSMASK'][:]
	landSeaInterpGen = interp.interp2d(np.arange(landSeaData.shape[1]), np.arange(landSeaData.shape[0]), landSeaData)
	landSeaDataInterp = landSeaInterpGen(np.linspace(0, landSeaData.shape[1], longitudeRes), np.linspace(0, landSeaData.shape[0], latitudeRes))
	landSeaMask = np.tile(landSeaDataInterp == 0, (numMonths, 1, 1))
	def removeOceans(data):
		return ma.masked_array(data, mask=landSeaMask)

	# Remove oceans
	dataRCP26 = removeOceans(dataRCP26)
	dataRCP85 = removeOceans(dataRCP85)

	# Get difference and divide it to between -1 and 1 for our difference graph.
	# This difference is in percent difference
	dataDiff = dataRCP85 - dataRCP26
	minDiff = dataDiff.min()
	maxDiff = dataDiff.max()
	dataDiff = dataDiff/dataRCP26

	# Change data to percentiles, replacing oceans with -inf, then mask oceans (again; stats.rankdata doesn't like masks.) They'll come as the lowest value.
	dataRCP26 = stats.rankdata(ma.filled(dataRCP26, -np.inf), method='dense').reshape(dataRCP26.shape)
	dataRCP85 = stats.rankdata(ma.filled(dataRCP85, -np.inf), method='dense').reshape(dataRCP85.shape)
	dataRCP26 = ma.masked_array(dataRCP26, mask=(dataRCP26 == 1))
	dataRCP85 = ma.masked_array(dataRCP85, mask=(dataRCP85 == 1))

	# Normalize data to between 0 and 1 and reverse it
	minVal = min(dataRCP26.min(), dataRCP85.min())
	maxVal = max(dataRCP26.max(), dataRCP85.max())
	rangeVal = maxVal-minVal
	dataRCP26 = (dataRCP26 - minVal)/rangeVal
	dataRCP85 = (dataRCP85 - minVal)/rangeVal

	# Cache our processed data
	np.savez_compressed(cacheDir + '/processedData.npz', rcp26=dataRCP26, rcp26_mask=dataRCP26.mask,
		rcp85=dataRCP85, rcp85_mask=dataRCP85.mask,
		diff=dataDiff, diff_mask=dataDiff.mask)

# Load processed data from cache
allData = np.load(cacheDir + '/processedData.npz')
dataRCP26 = ma.masked_array(allData['rcp26'], allData['rcp26_mask'])
dataRCP85 = ma.masked_array(allData['rcp85'], allData['rcp85_mask'])
dataDiff = ma.masked_array(allData['diff'], allData['diff_mask'])

## PART 3: Draw graph

# Create space for slider
fig, ax = plt.subplots()
fig.subplots_adjust(bottom=0.15)

# Change colormap settings to make masked values black
cmap = matplotlib.cm.jet_r
cmap.set_bad('black',1)
# Plot RCP 2.6, 8.5, and difference
subplt1 = plt.subplot(2,2,1)
im_h26 = subplt1.imshow(dataRCP26[0, :], cmap='jet_r', vmin=0.0, vmax=1.0, interpolation='nearest', origin='lower')
subplt1.set_title("Low Global Warming")
subplt2 = plt.subplot(2,2,2)
im_h85 = subplt2.imshow(dataRCP85[0, :], cmap='jet_r', vmin=0.0, vmax=1.0, interpolation='nearest', origin='lower')
subplt2.set_title("High Global Warming")
subplt3 = plt.subplot(2,2,3)
im_hdiff = subplt3.imshow(diffAmplification*dataDiff[0, :], cmap='jet_r', vmin=-1.0, vmax=1.0, interpolation='nearest', origin='lower')
subplt3.set_title("Difference in Soil Moisture With Higher Global Warming")
cbar = plt.colorbar(im_hdiff, ticks=[-1,0,1], orientation='vertical')
cbar.ax.set_yticklabels(['>' + str(100.0/diffAmplification) + '% Drier', 'No Effect', '>' + str(100.0/diffAmplification) + '% Wetter'])

# Create legend
percentileRangeArray = np.array([[0, 100]])
subplt4 = plt.subplot(2,2,4)
img = subplt4.imshow(percentileRangeArray, cmap='jet_r', aspect=0.01)
img.set_visible(False)
subplt4.axis('off')
plt.colorbar(img, orientation='horizontal')
subplt4.set_title("Soil Moisture (percentile)")

# Create title
plt.suptitle("Projected Effect of Global Warming on Soil Moisture Over Time")

# Create slider
ax_depth = plt.axes([0.23, 0.02, 0.56, 0.04])
slider_depth = Slider(ax_depth, 'Years Since Jan 2006', 0, (dataRCP26.shape[0]-1)/12, valinit=0, valfmt='%0.2f')
def update_depth(val):
	idx = int(round(slider_depth.val*12))
	im_h26.set_data(dataRCP26[idx, :])
	im_h85.set_data(dataRCP85[idx, :])
	im_hdiff.set_data(diffAmplification*dataDiff[idx, :])
slider_depth.on_changed(update_depth)

# Show plot
plt.show()