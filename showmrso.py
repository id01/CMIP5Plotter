import numpy as np
import numpy.ma as ma
import matplotlib
import matplotlib.cm
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
from matplotlib.widgets import Slider

# Variables for loading and interpreting processed data
processedDataFile = "mrso.npz"
numMonths = 1140
startYear = 2006
latitudeRes = 90
longitudeRes = 180

# Load processed data from cache
allData = np.load(processedDataFile)
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