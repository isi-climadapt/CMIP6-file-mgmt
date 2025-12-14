# CMIP6 NetCDF Merger Notebooks - Process Description

## Overview

The CMIP6 NetCDF Merger notebooks provide an interactive Python environment for processing climate data from NetCDF files and converting them into Excel format. These notebooks demonstrate how to use the CMIP6 file management tool to merge multiple years of climate data by geographic coordinates (latitude/longitude).

## Purpose

The notebooks serve as:
- **Interactive tutorials** for using the merger tool
- **Documentation** of the processing workflow
- **Reproducible examples** for different climate variables
- **Analysis templates** for working with the generated Excel files

## Notebook Structure

Each notebook follows a consistent structure with the following sections:

### 1. Overview Section
- Introduction to the CMIP6 NetCDF to Excel merger tool
- Description of the coordinate-based merging approach
- Explanation of the data organization

### 2. Setup Section
- Instructions for installing required dependencies
- Python package requirements (xarray, netCDF4, pandas, openpyxl, numpy)

### 3. Import Required Modules
- Import statements for all necessary libraries
- Path configuration for accessing the project modules
- Import of custom modules:
  - `config` - Configuration parameters
  - `file_handler` - File discovery utilities
  - `merge_nc_to_excel` - Main processing function

### 4. Process Files Example
- Example code demonstrating how to process NetCDF files
- Configuration of model, scenario, and variable parameters
- Execution of the merging process

## Processing Workflow

### Step 1: File Discovery
The notebook uses the `get_file_info()` function to:
- Scan the specified directory structure
- Identify all NetCDF files for the given model, scenario, and variable
- Extract year information from filenames
- Validate that files exist and are accessible

**Example:**
```python
file_info = get_file_info(model="ACCESS CM2", scenario="SSP585", variable="tasmax")
```

### Step 2: File Processing
The `process_files()` function executes the complete workflow:

1. **File Discovery**: Finds all NetCDF files matching the criteria
2. **Coordinate Validation**: Ensures all files use the same lat/lon grid
3. **File Reading**: Uses xarray to read NetCDF files efficiently with chunking
4. **Time Dimension Merging**: Concatenates files along the time dimension
5. **Data Extraction**: Extracts coordinate-based data with year aggregation
6. **Excel Export**: Creates structured Excel file with coordinate-based organization

**Example:**
```python
output_path = process_files(
    model="ACCESS CM2",
    scenario="SSP585",
    variable="tasmax",
    aggregation="mean"  # Options: "mean", "max", "min", "all"
)
```

### Step 3: Output Generation
The process creates an Excel file with:
- **Rows**: One row per unique (lat, lon) coordinate pair
- **Columns**: 
  - `lat`: Latitude coordinate
  - `lon`: Longitude coordinate
  - `{variable}_2035`: Aggregated data for year 2035
  - `{variable}_2036`: Aggregated data for year 2036
  - ... (one column per year)

## Available Notebooks

### 1. CMIP6_NetCDF_Merger_Notebook.ipynb
- **Purpose**: General template for processing any variable
- **Default Variable**: tasmax (maximum temperature)
- **Location**: Project root directory

### 2. CMIP6_NetCDF_Merger_Notebook_tasmin.ipynb
- **Purpose**: Process minimum temperature (tasmin) data
- **Variable**: tasmin
- **Location**: Project root and output directory

### 3. CMIP6_NetCDF_Merger_Notebook_pr.ipynb (to be created)
- **Purpose**: Process precipitation (pr) data
- **Variable**: pr
- **Location**: Project root and output directory

## Configuration Parameters

### Model
- **Default**: "ACCESS CM2"
- **Description**: Climate model name
- **Available**: ACCESS CM2 (can be extended)

### Scenario
- **Default**: "SSP585"
- **Description**: Climate scenario (Shared Socioeconomic Pathway)
- **Available**: SSP585, SSP245

### Variable
- **Default**: "tasmax"
- **Description**: Climate variable to process
- **Available**: 
  - `tasmax`: Maximum temperature
  - `tasmin`: Minimum temperature
  - `pr`: Precipitation
  - `hurs`: Relative humidity

### Aggregation Method
- **Default**: "mean"
- **Options**:
  - `mean`: Average daily value per year
  - `max`: Maximum daily value per year
  - `min`: Minimum daily value per year
  - `all`: All daily values (creates larger files)

## Data Processing Details

### Input File Structure
NetCDF files are organized in the following directory structure:
```
C:\Users\ibian\Desktop\ClimAdapt\CMIP6\
├── ACCESS CM2 SSP585\
│   ├── CMIP6 Files_tasmax\
│   │   ├── QDC-CMIP6__tasmax_day_ACCESS-CM2_ssp585_..._2035_...nc
│   │   ├── QDC-CMIP6__tasmax_day_ACCESS-CM2_ssp585_..._2036_...nc
│   │   └── ...
│   ├── CMIP6 Files_tasmin\
│   ├── CMIP6 Files_pr\
│   └── CMIP6 Files_hurs\
```

### File Naming Convention
Files follow the pattern: `*_{year}_*.nc`
- Year is extracted using regex pattern: `_(\d{4})_`
- Example: `..._2035_...` extracts year 2035

### Coordinate System
- **Latitude**: 691 points, range: -44.5° to -10.0° (Australia)
- **Longitude**: 886 points, range: 112.0° to 156.25° (Australia)
- **Total coordinate pairs**: 612,226 unique (lat, lon) combinations
- **Time dimension**: 365 days per file (one year)

### Merging Process
1. **Coordinate Validation**: All files must use the same lat/lon grid
2. **Time Concatenation**: Files are merged along the time dimension
3. **Year Extraction**: Years are extracted from time coordinates or filenames
4. **Aggregation**: Daily values are aggregated per year based on the selected method
5. **Data Transformation**: 3D arrays (time, lat, lon) are converted to 2D tables (coordinate pairs × years)

## Output File Details

### File Location
All Excel files are saved to:
```
C:\Users\ibian\Desktop\ClimAdapt\CMIP6\ACCESS CM2 xlsx\
```

### File Naming
Files follow the pattern: `{Model}_{Scenario}_{Variable}.xlsx`
- Example: `ACCESS_CM2_SSP585_tasmax.xlsx`
- Spaces in model/scenario names are replaced with underscores

### File Structure
- **Format**: Excel (.xlsx)
- **Sheet Name**: "Data"
- **Maximum Rows**: 612,226 (within Excel's limit of 1,048,576)
- **Columns**: 32 (lat, lon, and 30 years of data)
- **File Size**: Approximately 190-200 MB per file

## Usage Instructions

### Running a Notebook

1. **Open Jupyter Notebook or JupyterLab**
   ```bash
   jupyter notebook
   # or
   jupyter lab
   ```

2. **Navigate to the notebook file**
   - Open the desired notebook (.ipynb file)

3. **Run cells sequentially**
   - Execute cells from top to bottom
   - Use Shift+Enter to run a cell
   - Use Cell → Run All to execute entire notebook

4. **Monitor progress**
   - Processing 30 files takes several minutes
   - Progress messages indicate current step
   - Warnings about chunking are normal and don't affect functionality

### Command-Line Alternative

The same processing can be done via command line:
```bash
python merge_nc_to_excel.py --model "ACCESS CM2" --scenario "SSP585" --variable "pr"
```

## Technical Considerations

### Memory Management
- Uses xarray with chunking to handle large files efficiently
- Chunk size: time=365, lat=100, lon=100
- Processes data in chunks to avoid memory overflow

### Performance
- Processing 30 files (30 years) takes approximately 5-10 minutes
- Depends on file size and system resources
- Chunking warnings are informational and don't affect correctness

### Error Handling
- Validates file existence before processing
- Checks coordinate consistency across files
- Provides clear error messages if issues occur

## Customization

### Modifying Aggregation
Change the aggregation method in the processing cell:
```python
output_path = process_files(
    model="ACCESS CM2",
    scenario="SSP585",
    variable="tasmax",
    aggregation="max"  # Change to "max", "min", or "all"
)
```

### Processing Different Variables
Simply change the variable parameter:
```python
# For precipitation
output_path = process_files(..., variable="pr")

# For relative humidity
output_path = process_files(..., variable="hurs")
```

### Processing Different Scenarios
Change the scenario parameter:
```python
# For SSP245 scenario
output_path = process_files(..., scenario="SSP245")
```

## Best Practices

1. **Run notebooks sequentially**: Process one variable at a time to avoid memory issues
2. **Check file existence**: Verify input files exist before running
3. **Monitor disk space**: Each Excel file is ~200 MB
4. **Keep notebooks organized**: Use descriptive names for variable-specific notebooks
5. **Document changes**: Add comments when customizing notebooks

## Troubleshooting

### Common Issues

1. **File Not Found**
   - Verify input directory path in config.py
   - Check that directory structure matches expected pattern

2. **Memory Errors**
   - Process fewer files at once
   - Reduce chunk sizes in config.py
   - Close other applications

3. **Coordinate Mismatch**
   - Ensure all files use the same model and scenario
   - Verify files are from the same source

4. **Slow Processing**
   - Normal for large datasets
   - Consider processing in batches if needed

## Future Enhancements

Potential improvements for the notebooks:
- Add data visualization cells
- Include statistical analysis examples
- Add quality control checks
- Create comparison plots between variables
- Add time series analysis

## Related Files

- `merge_nc_to_excel.py`: Main processing script
- `config.py`: Configuration parameters
- `utils/file_handler.py`: File discovery utilities
- `utils/nc_reader.py`: NetCDF reading utilities
- `utils/excel_writer.py`: Excel export functionality
- `PROJECT_PLAN.md`: Detailed project documentation
- `README.md`: Usage instructions


