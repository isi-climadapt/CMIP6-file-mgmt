# CMIP6 NetCDF to Excel Merger

A Python tool for merging CMIP6 climate data NetCDF files by geographic coordinates (latitude/longitude) into Excel format.

## Overview

This project processes heavy NetCDF climate data files from CMIP6, merging multiple years of data for a given model, scenario, and variable. The merged data is organized by coordinates, with each row representing a unique (lat, lon) pair and columns representing different years.

## Features

- **Coordinate-based merging**: All files are merged by matching latitude and longitude coordinates
- **Configurable**: Easily process different models, scenarios, and variables
- **Memory efficient**: Uses xarray with chunking to handle large files
- **Excel export**: Outputs structured Excel files with coordinate-based organization
- **Year aggregation**: Supports mean, max, min, or all daily values per year

## Installation

1. Install required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

Process tasmax files for ACCESS CM2 SSP585:

```bash
python merge_nc_to_excel.py --model "ACCESS CM2" --scenario "SSP585" --variable "tasmax"
```

### Command-line Options

- `--model`: Model name (default: "ACCESS CM2")
- `--scenario`: Scenario name (default: "SSP585")
- `--variable`: Variable name (default: "tasmax")
- `--aggregation`: Aggregation method - "mean", "max", "min", or "all" (default: "mean")
- `--validate-paths`: Validate that input and output paths exist

### Examples

Process different variables:

```bash
# Process tasmax
python merge_nc_to_excel.py --model "ACCESS CM2" --scenario "SSP585" --variable "tasmax"

# Process tasmin
python merge_nc_to_excel.py --model "ACCESS CM2" --scenario "SSP585" --variable "tasmin"

# Process precipitation
python merge_nc_to_excel.py --model "ACCESS CM2" --scenario "SSP585" --variable "pr"

# Process relative humidity
python merge_nc_to_excel.py --model "ACCESS CM2" --scenario "SSP585" --variable "hurs"
```

Process different scenarios:

```bash
# SSP585 scenario
python merge_nc_to_excel.py --model "ACCESS CM2" --scenario "SSP585" --variable "tasmax"

# SSP245 scenario
python merge_nc_to_excel.py --model "ACCESS CM2" --scenario "SSP245" --variable "tasmax"
```

Use different aggregation methods:

```bash
# Mean value per year (default)
python merge_nc_to_excel.py --variable "tasmax" --aggregation "mean"

# Maximum value per year
python merge_nc_to_excel.py --variable "tasmax" --aggregation "max"

# Minimum value per year
python merge_nc_to_excel.py --variable "tasmax" --aggregation "min"
```

## Configuration

Edit `config.py` to customize:

- **Base paths**: Input and output directory paths
- **Default parameters**: Default model, scenario, and variable
- **File patterns**: NetCDF file naming patterns
- **Excel settings**: Sheet names, aggregation methods, row limits
- **Processing settings**: Chunk sizes for memory management

## Project Structure

```
CMIP6-file-mgmt/
├── config.py                 # Configuration parameters
├── merge_nc_to_excel.py      # Main processing script
├── utils/
│   ├── __init__.py
│   ├── file_handler.py       # File discovery and organization
│   ├── nc_reader.py          # NetCDF reading utilities
│   └── excel_writer.py       # Excel export functionality
├── requirements.txt          # Python dependencies
├── PROJECT_PLAN.md           # Detailed project plan
└── README.md                 # This file
```

## Input File Structure

Expected directory structure:

```
C:\Users\ibian\Desktop\ClimAdapt\CMIP6\
├── ACCESS CM2 SSP585\
│   ├── CMIP6 Files_tasmax\
│   │   ├── QDC-CMIP6__tasmax_day_ACCESS-CM2_ssp585_..._2035_...nc
│   │   ├── QDC-CMIP6__tasmax_day_ACCESS-CM2_ssp585_..._2036_...nc
│   │   └── ...
│   ├── CMIP6 Files_tasmin\
│   └── ...
└── ACCESS CM2 SSP245\
    └── ...
```

## Output Format

Excel files are saved to: `C:\Users\ibian\Desktop\ClimAdapt\CMIP6\ACCESS CM2 xlsx\`

File naming: `{Model}_{Scenario}_{Variable}.xlsx`

Example: `ACCESS_CM2_SSP585_tasmax.xlsx`

### Excel Structure

- **Rows**: One row per unique (lat, lon) coordinate pair
- **Columns**: 
  - `lat`: Latitude
  - `lon`: Longitude
  - `{variable}_2035`: Data for year 2035
  - `{variable}_2036`: Data for year 2036
  - ... (one column per year)

## Technical Details

### Data Processing

1. **File Discovery**: Scans directory structure and extracts years from filenames
2. **Coordinate Validation**: Ensures all files use the same lat/lon grid
3. **File Merging**: Concatenates files along the time dimension using xarray
4. **Data Extraction**: Extracts coordinate-based data with year aggregation
5. **Excel Export**: Creates structured Excel file with coordinate-based organization

### Memory Management

- Uses xarray with chunking to handle large files efficiently
- Processes data in chunks to avoid memory overflow
- Supports datasets with millions of coordinate points

### Coordinate Matching

- Validates coordinate consistency across all files
- Uses coordinate matching (not index-based) for robustness
- Handles floating-point precision issues

## Requirements

- Python 3.8+
- xarray >= 2023.1.0
- netCDF4 >= 1.6.4
- pandas >= 2.0.0
- openpyxl >= 3.1.0
- numpy >= 1.24.0

## Troubleshooting

### File Not Found Errors

- Verify input directory path in `config.py`
- Check that directory structure matches expected pattern
- Ensure files follow naming convention with year in filename

### Coordinate Mismatch Errors

- All files must use the same lat/lon grid
- Check that files are from the same model and scenario
- Verify coordinate arrays are consistent

### Memory Issues

- Reduce chunk sizes in `config.py` if processing fails
- Process fewer files at once
- Consider using Dask for parallel processing

## License

This project is for processing CMIP6 climate data files.

