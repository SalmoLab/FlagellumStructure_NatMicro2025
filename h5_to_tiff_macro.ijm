// Define the input and output directories
inputDir = "P:/PROTOCOLS/0_LabWiki/Protocols already in LabWiki/Swimming-evaluation pipeline/3_ilastik_output/";
outputDir = "P:/PROTOCOLS/0_LabWiki/Protocols already in LabWiki/Swimming-evaluation pipeline/4_h5_to_tifs/";

// Get a list of all HDF5 files in the input directory
list = getFileList(inputDir);
for (i = 0; i < list.length; i++) {
    if (endsWith(list[i], ".h5") || endsWith(list[i], ".hdf5")) {
        // Construct the full path to the HDF5 file
        filePath = inputDir + list[i];
        
        // Open the HDF5 file using the Ilastik plugin
        run("Import HDF5", "select=[" + filePath + "] datasetname=/exported_data axisorder=tyxc");
        // Set the properties that where used for imaging
        run("Properties...", "channels=1 slices=1 frames=998 pixel_width=0.325 pixel_height=0.325 voxel_depth=1 unit=micron frame=[0.01 sec]");
        // Save the currently opened image as TIFF
        saveAs("Tif", outputDir + list[i] + ".tif");
        
        // Close the currently opened image
        close();
    }
}
