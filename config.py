### Configuration for process.py
# mrso config

dataDir = "data"
cacheDir = "cache/mrso"
landSeaFile = "landsea.nc"
dataFilesRCP26 = ["mrso_Lmon_HadGEM2-AO_rcp26_r1i1p1_200601-210012.nc", "mrso_Lmon_MPI-ESM-LR_rcp26_r1i1p1_200601-210012.nc", "mrso_Lmon_MRI-CGCM3_rcp26_r1i1p1_200601-210012.nc"]
dataFilesRCP85 = ["mrso_Lmon_HadGEM2-AO_rcp85_r1i1p1_200601-210012.nc", "mrso_Lmon_MPI-ESM-LR_rcp85_r1i1p1_200601-210012.nc", "mrso_Lmon_MRI-CGCM3_rcp85_r1i1p1_200601-210012.nc"]
varOfInterest = "mrso"
numMonths = 1140
startYear = 2006
latitudeRes = 90
longitudeRes = 180
realm = 'land' # This must be land, sea, or atmos (landsea). If it is atmos, this script will save "landSea" in the data to overlay in plot.py.

# pr config
'''
dataDir = "data"
cacheDir = "cache/pr"
landSeaFile = "landsea.nc"
dataFilesRCP26 = ["pr_Amon_CanESM2_rcp26_r1i1p1_200601-210012.nc", "pr_Amon_MRI-CGCM3_rcp26_r1i1p1_200601-210012.nc", "pr_Amon_GISS-E2-H_rcp26_r1i1p1_200601-210012.nc"]
dataFilesRCP85 = ["pr_Amon_CanESM2_rcp85_r1i1p1_200601-210012.nc", "pr_Amon_MRI-CGCM3_rcp85_r1i1p1_200601-210012.nc", "pr_Amon_GISS-E2-H_rcp85_r1i1p1_200601-210012.nc"]
varOfInterest = "pr"
numMonths = 1140
startYear = 2006
latitudeRes = 90
longitudeRes = 180
realm = 'atmos' # This must be land, sea, or atmos (landsea). If it is atmos, this script will save "landSea" in the data to overlay in plot.py.
'''

### Configuration for plot.py
# mrso config

# Variables for loading and interpreting processed data
processedDataFile = "mrso.npz"
numMonths = 1140
startYear = 2006
latitudeRes = 90
longitudeRes = 180
play_interval = 100
overlayLandSea = False

# Data Set Settings
suptitle = "Projected Effect of Global Warming on Soil Moisture Over Time"
titleDiff = {'plt_1_2_units': 'Soil Moisture Anomaly Since Jan 2006', 'diff_title': 'Difference in Soil Moisture With Higher Global Warming'}
unitsDiff = '% Change'
rangesDiff = {'plt_1_2': [-1,1], 'plt_3': [-1,1]}
ampDiff = {'plt_1_2': 2, 'plt_3': 2}
titlePerc = {'plt_1_2_units': 'Percentile Soil Moisture', 'diff_title': 'Difference in Soil Moisture Percentile With Higher Global Warming'}
unitsPerc = '%ile Moisture'
rangesPerc = {'plt_1_2': [0,1], 'plt_3': [-1,1]}
ampPerc = {'plt_1_2': 1, 'plt_3': 2}

# pr config
'''
# Variables for loading and interpreting processed data
processedDataFile = "pr.npz"
numMonths = 1140
startYear = 2006
latitudeRes = 90
longitudeRes = 180
play_interval = 100
overlayLandSea = True

# Data Set Settings
suptitle = "Projected Effect of Global Warming on Precipitation Over Time"
titleDiff = {'plt_1_2_units': 'Precipitation Anomaly Since Jan 2006', 'diff_title': 'Difference in Precipitation With Higher Global Warming'}
unitsDiff = '% Change'
rangesDiff = {'plt_1_2': [-1,1], 'plt_3': [-1,1]}
ampDiff = {'plt_1_2': 2, 'plt_3': 2}
titlePerc = {'plt_1_2_units': 'Percentile Precipitation', 'diff_title': 'Difference in Precipitation Percentile With Higher Global Warming'}
unitsPerc = '%ile Precipitation'
rangesPerc = {'plt_1_2': [0,1], 'plt_3': [-1,1]}
ampPerc = {'plt_1_2': 1, 'plt_3': 2}
'''