import numpy as np
import numpy.ma as ma
from netCDF4 import Dataset
import matplotlib
import matplotlib.cm
import matplotlib.pyplot as plt
import scipy.interpolate as interp
import scipy.stats as stats
from matplotlib.widgets import Button
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
startYear = 2006
latitudeRes = 90
longitudeRes = 180

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
	np.savez_compressed(cacheDir + '/processedData.npz',
		perc26=percRCP26, perc26_mask=percRCP26.mask,
		perc85=percRCP85, perc85_mask=percRCP85.mask,
		diff26=diffRCP26, diff26_mask=diffRCP26.mask,
		diff85=diffRCP85, diff85_mask=diffRCP85.mask,
		diffRCP=diffRCPs, diffRCP_mask=diffRCPs.mask)

# Load processed data from cache
allData = np.load(cacheDir + '/processedData.npz')
percRCP26 = ma.masked_array(allData['perc26'], allData['perc26_mask'])
percRCP85 = ma.masked_array(allData['perc85'], allData['perc85_mask'])
diffPerc = percRCP85 - percRCP26
diffRCP26 = ma.masked_array(allData['diff26'], allData['diff26_mask'])
diffRCP85 = ma.masked_array(allData['diff85'], allData['diff85_mask'])
diffRCPs = ma.masked_array(allData['diffRCP'], allData['diffRCP_mask'])

## PART 3: Draw graph

# Create space for slider
fig, ax = plt.subplots()
fig.subplots_adjust(bottom=0.15)

# Create time index
time_index = 0

# Construct data sets
titleDiff = {'plt_1_2_units': 'Soil Moisture Anomaly Since Jan 2006', 'diff_title': 'Difference in Soil Moisture With Higher Global Warming'}
unitsDiff = '% Change'
rangesDiff = {'plt_1_2': [-1,1], 'plt_3': [-1,1]}
ampDiff = {'plt_1_2': 2, 'plt_3': 2}
dataDiff = {'rcp26': diffRCP26, 'rcp85': diffRCP85, 'diff': diffRCPs}
titlePerc = {'plt_1_2_units': 'Percentile Soil Moisture', 'diff_title': 'Difference in Soil Moisture Percentile With Higher Global Warming'}
unitsPerc = '%ile Moisture'
rangesPerc = {'plt_1_2': [0,1], 'plt_3': [-1,1]}
ampPerc = {'plt_1_2': 1, 'plt_3': 2}
dataPerc = {'rcp26': percRCP26, 'rcp85': percRCP85, 'diff': diffPerc}

# Change colormap settings to make masked values black
cmap = matplotlib.cm.jet_r
cmap.set_bad('black',1)
# Create title
plt.suptitle("Projected Effect of Global Warming on Soil Moisture Over Time")
# Plot RCP 2.6, 8.5, and difference
def changeDataset(titles, units, ranges, amplification, data):
	subplt1 = plt.subplot(2,2,1)
	im_h26 = subplt1.imshow(amplification['plt_1_2']*data['rcp26'][time_index, :], cmap='jet_r', vmin=ranges['plt_1_2'][0], vmax=ranges['plt_1_2'][1], interpolation='nearest', origin='lower')
	subplt1.set_title("%s With Low Global Warming (RCP26)" % titles['plt_1_2_units'])
	cbar26 = plt.colorbar(im_h26, ticks=ranges['plt_1_2'], orientation='vertical')
	cbar26.ax.set_yticklabels([str(100.0/amplification['plt_1_2']*ranges['plt_1_2'][0]) + units, str(100.0/amplification['plt_1_2']*ranges['plt_1_2'][1]) + units])

	subplt2 = plt.subplot(2,2,2)
	im_h85 = subplt2.imshow(amplification['plt_1_2']*data['rcp85'][time_index, :], cmap='jet_r', vmin=ranges['plt_1_2'][0], vmax=ranges['plt_1_2'][1], interpolation='nearest', origin='lower')
	subplt2.set_title("%s With High Global Warming (RCP85)" % titles['plt_1_2_units'])
	cbar85 = plt.colorbar(im_h85, ticks=ranges['plt_1_2'], orientation='vertical')
	cbar85.ax.set_yticklabels([str(100.0/amplification['plt_1_2']*ranges['plt_1_2'][0]) + units, str(100.0/amplification['plt_1_2']*ranges['plt_1_2'][1]) + units])

	subplt3 = plt.subplot(2,2,3)
	im_hdiff = subplt3.imshow(amplification['plt_3']*data['diff'][time_index, :], cmap='jet_r', vmin=ranges['plt_3'][0], vmax=ranges['plt_3'][1], interpolation='nearest', origin='lower')
	subplt3.set_title(titles['diff_title'])
	cbarDiff = plt.colorbar(im_hdiff, ticks=ranges['plt_3'], orientation='vertical')
	cbarDiff.ax.set_yticklabels([str(100.0/amplification['plt_3']*ranges['plt_3'][0]) + units, str(100.0/amplification['plt_3']*ranges['plt_3'][1]) + units])

	return ({'rcp26': im_h26, 'rcp85': im_h85, 'diff': im_hdiff}, {'rcp26': subplt1, 'rcp85': subplt2, 'diff': subplt3}, {'rcp26': cbar26, 'rcp85': cbar85, 'diff': cbarDiff})

data = dataDiff
amplification = ampDiff
(heatmaps, subplots, colorbars) = changeDataset(titleDiff, unitsDiff, rangesDiff, ampDiff, dataDiff)

# Function to clear colorbars
def clearColorbars(subplots, colorbars):
	for key in colorbars:
		colorbars[key].remove()
	for key in subplots:
		subplots[key].remove()

# Create dataset changer buttons
ax_button1 = plt.axes([0, 0.9, 0.5, 0.025])
ax_button2 = plt.axes([0.5, 0.9, 0.5, 0.025])
diff_button = Button(ax_button1, 'Difference')
perc_button = Button(ax_button2, 'Percentile')
diff_button.color = 'grey'
perc_button.color = 'silver'
def changeToDiff(val):
	global data, amplification
	global heatmaps, subplots, colorbars
	clearColorbars(subplots, colorbars)
	data = dataDiff
	amplification = ampDiff
	(heatmaps, subplots, colorbars) = changeDataset(titleDiff, unitsDiff, rangesDiff, ampDiff, dataDiff)
	diff_button.color = 'grey'
	perc_button.color = 'silver'
def changeToPerc(val):
	global data, amplification
	global heatmaps, subplots, colorbars
	clearColorbars(subplots, colorbars)
	data = dataPerc
	amplification = ampPerc
	(heatmaps, subplots, colorbars) = changeDataset(titlePerc, unitsPerc, rangesPerc, ampPerc, dataPerc)
	diff_button.color = 'silver'
	perc_button.color = 'grey'
diff_button.on_clicked(changeToDiff)
perc_button.on_clicked(changeToPerc)

# Create slider
ax_depth = plt.axes([0.23, 0.02, 0.56, 0.04])
slider_depth = Slider(ax_depth, 'Year', startYear, ((numMonths-1)/12)+startYear, valinit=startYear, valfmt='%0.2f')
def update_depth(val):
	global time_index
	time_index = int(round((slider_depth.val-startYear)*12))
	heatmaps['rcp26'].set_data(amplification['plt_1_2']*data['rcp26'][time_index, :])
	heatmaps['rcp85'].set_data(amplification['plt_1_2']*data['rcp85'][time_index, :])
	heatmaps['diff'].set_data(amplification['plt_3']*data['diff'][time_index, :])
slider_depth.on_changed(update_depth)

# Show plot
plt.show()