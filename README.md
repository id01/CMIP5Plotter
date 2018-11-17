## CMIP5Plotter

This is a simple interactive script to analyze CMIP5 climate model predictions.

The code files in this repository are:
* `config.py`: Configuration file to process and plot different variables
* `process.py`: Processes netcdf data into npz files for display
* `plot.py`: Displays npz files created with process.py interactively

The configuration variables are:
* `process.py` configuration
	* `dataDir`: directory where data is being stored
	* `cacheDir`: directory to store npz cache and output data
	* `landSeaFile`: file containing mask determining whether an latitude/longitude is land or sea
	* `dataFilesRCP26`: NetCDF files containing RCP2.6 experiment data (to be averaged)
	* `dataFilesRCP85`: NetCDF files containing RCP8.5 experiment data (to be averaged)
	* `varOfInterest`: Variable to analyze
* Universal configuration
	* `numMonths`: Total number of months of climate model data to analyze
	* `startYear`: The starting year
	* `latitudeRes`: The latitude resolution
	* `longitudeRes`: The longitude resolution
	* `realm`: Which locations of Earth to plot
* `plot.py` configuration
	* `processedDataFile`: The file contining processed data
	* `play_interval`: The number of milliseconds between each frame when playing
	* (I'll write the others later if I feel like it. I'm tired.)

I have some samples of output [here](https://photos.app.goo.gl/Vox58HGd9NK9jXRv7)
