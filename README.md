Single-Cell Bacterial Swimming Analysis

This repository contains all code used for automated tracking and quantification of bacterial swimming behaviour, as described in our manuscript:

„Structure of the complete extracellular bacterial flagellum reveals mechanism for flagellin incorporation“

For questions, please contact the corresponding authors of the manuscript.

---

Overview

This pipeline processes microscopy videos of swimming bacteria into single-cell trajectory data, computes swimming speed metrics, and prepares the data for downstream analysis. It includes:

1. Conversion of raw microscopy files (.nd2 / .czi) to TIFF with Jupyter notebook 
2. Pixel classification using Ilastik (headless mode) with Jupyter notebook 
3. Segmentation post-processing via Fiji macro
4. Automated tracking in Fiji using TrackMate (Jython script)
5. CSV merging and cleanup with Jupyter notebook

---

Repository Contents

File - Description

`h5_to_tiff_macro.ijm` - Fiji macro to convert Ilastik segmentations into TIFFs

`TrackMate_Tracking.py` - Jython script to batch-process TIFFs (Ilastik masks) using TrackMate

`single_cell_tracking.ipynb` - Jupyter Notebook for file conversion (.nd2 / .czi to .tiff) and merging and cleaning exported `.csv` files from TrackMate

---

Dependencies

- Fiji (with TrackMate plugin)
- Ilastik v1.4.0+ (for cell segmentation)
- Python 3.9 (for running the Jupyter notebook and PyImageJ if used for format conversion)
