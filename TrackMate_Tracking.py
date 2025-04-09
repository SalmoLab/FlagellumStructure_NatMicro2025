import sys
import os
import csv
from ij import IJ
from ij.measure import Calibration
from fiji.plugin.trackmate import Model, Settings, TrackMate, SelectionModel, Logger
from fiji.plugin.trackmate.detection import ThresholdDetectorFactory
from fiji.plugin.trackmate.tracking.jaqaman import SparseLAPTrackerFactory
from fiji.plugin.trackmate.gui.displaysettings import DisplaySettingsIO
from fiji.plugin.trackmate.visualization.hyperstack import HyperStackDisplayer
import fiji.plugin.trackmate.visualization.hyperstack.HyperStackDisplayer as HyperStackDisplayer
import fiji.plugin.trackmate.features.FeatureFilter as FeatureFilter

# We have to do the following to avoid errors with UTF8 chars generated in TrackMate that will mess with our Fiji Jython.
reload(sys)
sys.setdefaultencoding('utf-8')

# Path to the folder containing the images
folder_path = '...'

# List all files in the folder and process each one
for filename in os.listdir(folder_path):
    if filename.endswith('.tif') or filename.endswith('.tiff'):
        image_path = os.path.join(folder_path, filename)
        imp = IJ.openImage(image_path)
        if imp is None:
            print("Failed to open image:", filename)
            continue  # Continue if the image fails to open

        # Get calibration data for pixel size and frame interval
        cal = imp.getCalibration()
        pixel_width = cal.pixelWidth  # Pixel width in micrometers
        frame_interval = cal.frameInterval  # Frame interval in seconds
        print("Pixel Width (µm):", pixel_width)
        print("Frame Interval (s):", frame_interval)

        # -------------------------
        # Instantiate model object
        # -------------------------
        model = Model()
        model.setLogger(Logger.IJ_LOGGER)

        # ------------------------
        # Prepare settings object
        # ------------------------
        settings = Settings(imp)
        settings.detectorFactory = ThresholdDetectorFactory()
        settings.detectorSettings = {
            'SIMPLIFY_CONTOURS': True,
            'INTENSITY_THRESHOLD': 1.0, #integer 1.0 it cant be 1 it needs the .0
            'TARGET_CHANNEL': 1,
        }
        #Add Spot filters
        filter1 = FeatureFilter('AREA', 1, True)
        filter2= FeatureFilter('AREA', 6, False)
        settings.addSpotFilter(filter1)
        settings.addSpotFilter(filter2)
        
        # Configure tracker
        settings.trackerFactory = SparseLAPTrackerFactory()
        settings.trackerSettings = settings.trackerFactory.getDefaultSettings()
        settings.trackerSettings['LINKING_MAX_DISTANCE'] = 2.0
        settings.trackerSettings['GAP_CLOSING_MAX_DISTANCE'] = 2.0
        settings.trackerSettings['MAX_FRAME_GAP'] = 2
		
	    # Add filters for tracks
        min_displacement = 0.0  # Minimum track displacement in micrometers
        min_duration = 1.0  # Minimum track duration in the time interval of your dataset
        min_track_speed = 0.0 #Minimum of speed
		
        displacement_filter = FeatureFilter('TRACK_DISPLACEMENT', min_displacement, True)
        duration_filter = FeatureFilter('TRACK_DURATION', min_duration, True)
        track_speed_filter = FeatureFilter('TRACK_MEAN_SPEED', min_track_speed, True)
        
        settings.addTrackFilter(displacement_filter)
        settings.addTrackFilter(duration_filter)
        settings.addTrackFilter(track_speed_filter)

        # Add the analyzers for some spot features.
        settings.addAllAnalyzers()
        settings.initialSpotFilterValue = 1.0

        print(str(settings))
	
        # Instantiate trackmate
        trackmate = TrackMate(model, settings)
		
		# Execute all
        if not trackmate.checkInput():
            print("Error in input:", trackmate.getErrorMessage())
            continue  # Continue if there's an error in input
        # Print the number of detected spots and tracks
        nSpots = model.getSpots().getNSpots(True)
        print("Total detected spots (PP):", nSpots)
        
        nTracks = model.getTrackModel().nTracks(True)
        print("Total tracks found (PP):", nTracks)
        
        if not trackmate.process():
            print("Error in processing:", trackmate.getErrorMessage())
            continue  # Continue if there's an error in processing

        # ----------------
        # Display results
        # ----------------
        model.getLogger().log('Found ' + str(model.getTrackModel().nTracks(True)) + ' tracks.')
        sm = SelectionModel(model)
        ds = DisplaySettingsIO.readUserDefault()
        displayer = HyperStackDisplayer(model, sm, imp, ds)
        displayer.render()

        csv_filename = os.path.join(folder_path, os.path.splitext(filename)[0] + '.csv')
        with open(csv_filename, 'wb') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(['filename',
            'Track ID', 
            'TRACK_MEAN_SPEED',
            'TRACK_MAX_SPEED', 
            'TRACK_MEDIAN_SPEED',
            'MEAN_STRAIGHT_LINE_SPEED',
            'TRACK_DISPLACEMENT',
            'TOTAL_DISTANCE_TRAVELED',
            'TRACK_DURATION'])

            # The feature model, that stores edge and track features.
            fm = model.getFeatureModel()

            # Iterate over all the tracks that are visible and write to CSV
            for id in model.getTrackModel().trackIDs(True):
                track = model.getTrackModel().trackSpots(id)
                track_mean_speed = fm.getTrackFeature(id, 'TRACK_MEAN_SPEED')
                track_max_speed = fm.getTrackFeature(id, 'TRACK_MAX_SPEED')
                track_median_speed = fm.getTrackFeature(id, 'TRACK_MEDIAN_SPEED')
                mean_line_speed = fm.getTrackFeature(id, 'MEAN_STRAIGHT_LINE_SPEED')
                track_displacement = fm.getTrackFeature(id, 'TRACK_DISPLACEMENT')
                total_distance_traveled = fm.getTrackFeature(id, 'TOTAL_DISTANCE_TRAVELED')
                duration = fm.getTrackFeature(id, 'TRACK_DURATION')
                
                csvwriter.writerow([filename, id, 
                track_mean_speed,
                track_max_speed,
                track_median_speed, 
                mean_line_speed,
                track_displacement,
                total_distance_traveled, 
                duration])

        print("Successfully processed and saved:", filename)

        # Optionally, close the image to save memory
        imp.close()
