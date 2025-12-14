# CMIP6 NetCDF to Excel Merger - Project Plan

## Overview

This project processes heavy NetCDF climate data files from CMIP6, merging them by geographic coordinates (latitude/longitude) into Excel format. The workflow is designed to be configurable for different models, scenarios, and variables.

## File Structure Analysis

Based on exploration of the tasmax files:
- **Dimensions**: time (365 days), lat (691 points), lon (886 points)
- **Coordinate ranges**: Lat: -44.5° to -10.0°, Lon: 112.0° to 156.25° (Australia)
- **Data structure**: Each file contains one year of daily data
- **Total coordinate pairs**: 691 × 886 = 612,326 unique (lat, lon) combinations

## Project Structure

```
CMIP6-file-mgmt/
├── config.py                 # Configuration parameters (paths, models, scenarios, variables)
├── merge_nc_to_excel.py      # Main processing script
├── utils/
│   ├── __init__.py
│   ├── file_handler.py       # File discovery and organization
│   ├── nc_reader.py          # NetCDF reading utilities
│   └── excel_writer.py       # Excel export functionality
├── requirements.txt          # Python dependencies
├── PROJECT_PLAN.md           # This file
└── README.md                 # Usage documentation
```

## Implementation Approach

### 1. Configuration System (`config.py`)

- Define base paths:
  - Input: `C:\Users\ibian\Desktop\ClimAdapt\CMIP6`
  - Output: `C:\Users\ibian\Desktop\ClimAdapt\CMIP6\ACCESS CM2 xlsx`
- Configurable parameters:
  - Model names (e.g., "ACCESS CM2")
  - Scenarios (e.g., "SSP585", "SSP245")
  - Variables (e.g., "tasmax", "tasmin", "pr", "hurs")
  - File naming patterns
  - Coordinate precision for merging

### 2. File Discovery (`utils/file_handler.py`)

- Scan directory structure: `{Model} {Scenario}/CMIP6 Files_{variable}/`
- Extract year from filenames (pattern: `*_{year}_*.nc`)
- Sort files chronologically
- Validate coordinate consistency across files

### 3. NetCDF Processing (`utils/nc_reader.py`)

- Use `xarray` for efficient NetCDF handling (supports chunking for large files)
- Read and concatenate multiple files along time dimension
- Extract coordinate arrays (lat, lon)
- Handle memory efficiently for large datasets (use chunking/streaming)

### 4. Data Merging Strategy

**Option A: Year-based columns** (Recommended for Excel compatibility)

- Rows: Unique (lat, lon) coordinate pairs
- Columns: `lat`, `lon`, `year_2035`, `year_2036`, ..., `year_2064`
- Values: Aggregated daily data per year (mean, max, min, or all days as separate columns)

**Option B: Time-series format**

- Rows: (lat, lon, date) combinations
- Columns: `lat`, `lon`, `date`, `tasmax`
- More rows but simpler structure

**Decision**: Start with Option A using yearly aggregates (mean daily value per year) to keep Excel files manageable. Can be configured to use daily data if needed.

### 5. Excel Export (`utils/excel_writer.py`)

- Use `openpyxl` or `xlsxwriter` for Excel creation
- Structure: Single sheet with coordinate-based rows
- Format: 
  - Columns: `lat`, `lon`, `{variable}_2035`, `{variable}_2036`, ..., `{variable}_2064`
  - Rows: One per unique (lat, lon) pair
- Handle large datasets efficiently (may need to split into multiple sheets if >1M rows)

### 6. Main Processing Script (`merge_nc_to_excel.py`)

- Command-line interface with parameters:
  - Model (default: "ACCESS CM2")
  - Scenario (default: "SSP585")
  - Variable (default: "tasmax")
- Workflow:
  1. Load configuration
  2. Discover files for specified category
  3. Read and merge NetCDF files
  4. Transform to coordinate-based DataFrame
  5. Export to Excel
  6. Save to output directory with naming: `{Model}_{Scenario}_{Variable}.xlsx`

## Technical Considerations

### Memory Management

- Files are large (~223M data points per file × 30 years = ~6.7B points)
- Use `xarray` with chunking (`chunks={'time': 365, 'lat': 100, 'lon': 100}`)
- Process in batches if needed
- Consider using Dask for parallel processing

### Coordinate Matching

- Ensure all files use the same lat/lon grid (validate on first file)
- Use coordinate matching (not index-based) for robustness
- Handle floating-point precision issues in coordinate comparison

### Excel Limitations

- Excel max rows: 1,048,576 (we have 612,326 coordinate pairs - OK)
- Excel max columns: 16,384 (we have ~30 years - OK)
- Consider splitting by lat/lon regions if needed for very large datasets

## Dependencies

- `xarray` - NetCDF reading and array operations
- `netCDF4` - Low-level NetCDF access
- `pandas` - Data manipulation
- `openpyxl` or `xlsxwriter` - Excel file creation
- `numpy` - Numerical operations

## Example Usage

```bash
# Process tasmax for ACCESS CM2 SSP585
python merge_nc_to_excel.py --model "ACCESS CM2" --scenario "SSP585" --variable "tasmax"

# Process tasmin for ACCESS CM2 SSP245
python merge_nc_to_excel.py --model "ACCESS CM2" --scenario "SSP245" --variable "tasmin"
```

## Output Structure

Files saved to: `C:\Users\ibian\Desktop\ClimAdapt\CMIP6\ACCESS CM2 xlsx\`

- `ACCESS_CM2_SSP585_tasmax.xlsx`
- `ACCESS_CM2_SSP585_tasmin.xlsx`
- `ACCESS_CM2_SSP245_tasmax.xlsx`
- etc.

## Implementation Tasks

1. **Setup Project Structure**
   - Create project directory structure
   - Initialize utils package with `__init__.py`

2. **Create Configuration System**
   - Implement `config.py` with all configurable parameters
   - Define paths and default values

3. **Implement File Handler**
   - Create `utils/file_handler.py` for file discovery
   - Implement year extraction from filenames
   - Add coordinate validation

4. **Implement NetCDF Reader**
   - Create `utils/nc_reader.py` using xarray
   - Implement efficient file reading with chunking
   - Add coordinate extraction and merging logic

5. **Implement Excel Writer**
   - Create `utils/excel_writer.py`
   - Implement coordinate-based DataFrame to Excel conversion
   - Handle large file sizes efficiently

6. **Create Main Script**
   - Implement `merge_nc_to_excel.py` with CLI
   - Integrate all components
   - Add error handling and logging

7. **Create Requirements File**
   - List all Python dependencies in `requirements.txt`

8. **Test with Example**
   - Test workflow with tasmax files from ACCESS CM2 SSP585
   - Verify output Excel file structure and data integrity

## Notes

- All files should merge by coordinates (lat, lon) - this is a critical requirement
- The system must be easily configurable for different models, scenarios, and variables
- Processing should handle large files efficiently without running out of memory
- Output files should be clearly named and organized in the specified output directory

