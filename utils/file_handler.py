"""
File handling utilities for discovering and organizing NetCDF files.
"""

import re
from pathlib import Path
from typing import List, Tuple, Dict
import config


def extract_year_from_filename(filename: str) -> int:
    """
    Extract year from NetCDF filename.
    
    Filename pattern: *_{year}_*.nc
    Example: QDC-CMIP6__tasmax_day_ACCESS-CM2_ssp585_r4i1p1f1_AUS-05_2035_*.nc
    
    Args:
        filename: Name of the NetCDF file
    
    Returns:
        Year as integer
    
    Raises:
        ValueError: If year cannot be extracted from filename
    """
    match = re.search(config.YEAR_PATTERN, filename)
    if not match:
        raise ValueError(f"Could not extract year from filename: {filename}")
    return int(match.group(1))


def discover_nc_files(model: str, scenario: str, variable: str) -> List[Tuple[Path, int]]:
    """
    Discover all NetCDF files for a given model, scenario, and variable.
    
    Args:
        model: Model name (e.g., "ACCESS CM2")
        scenario: Scenario name (e.g., "SSP585")
        variable: Variable name (e.g., "tasmax")
    
    Returns:
        List of tuples (file_path, year) sorted by year
    
    Raises:
        FileNotFoundError: If the input directory does not exist
        ValueError: If no files are found or year extraction fails
    """
    input_dir = config.get_input_directory(model, scenario, variable)
    
    if not input_dir.exists():
        raise FileNotFoundError(
            f"Input directory does not exist: {input_dir}"
        )
    
    # Find all .nc files
    nc_files = list(input_dir.glob("*.nc"))
    
    if not nc_files:
        raise ValueError(
            f"No NetCDF files found in directory: {input_dir}"
        )
    
    # Extract years and create tuples
    files_with_years = []
    for file_path in nc_files:
        try:
            year = extract_year_from_filename(file_path.name)
            files_with_years.append((file_path, year))
        except ValueError as e:
            print(f"Warning: {e}. Skipping file: {file_path.name}")
            continue
    
    if not files_with_years:
        raise ValueError(
            f"Could not extract years from any files in: {input_dir}"
        )
    
    # Sort by year
    files_with_years.sort(key=lambda x: x[1])
    
    return files_with_years


def validate_coordinate_consistency(file_paths: List[Path]) -> bool:
    """
    Validate that all NetCDF files have consistent coordinate grids.
    
    This is a basic check - full validation happens during reading.
    
    Args:
        file_paths: List of NetCDF file paths to validate
    
    Returns:
        True if validation passes (or if validation cannot be performed)
    
    Note:
        This is a lightweight check. Full coordinate validation
        should be done during the actual file reading process.
    """
    if len(file_paths) < 2:
        return True  # Single file or no files - nothing to validate
    
    try:
        import netCDF4
        
        # Read first file's coordinates
        with netCDF4.Dataset(file_paths[0], 'r') as nc:
            first_lat = nc.variables['lat'][:]
            first_lon = nc.variables['lon'][:]
        
        # Check a few other files
        for file_path in file_paths[1:min(5, len(file_paths))]:
            with netCDF4.Dataset(file_path, 'r') as nc:
                lat = nc.variables['lat'][:]
                lon = nc.variables['lon'][:]
                
                if not (len(lat) == len(first_lat) and len(lon) == len(first_lon)):
                    print(f"Warning: Coordinate dimensions differ between files")
                    return False
                
                # Check if coordinates match (with tolerance)
                if not (abs(lat - first_lat).max() < 0.01 and 
                        abs(lon - first_lon).max() < 0.01):
                    print(f"Warning: Coordinate values differ between files")
                    return False
        
        return True
    
    except Exception as e:
        print(f"Warning: Could not validate coordinate consistency: {e}")
        return True  # Don't fail on validation errors, let the reader handle it


def get_file_info(model: str, scenario: str, variable: str) -> Dict:
    """
    Get information about files for a given category.
    
    Args:
        model: Model name
        scenario: Scenario name
        variable: Variable name
    
    Returns:
        Dictionary with file information:
        - input_directory: Path to input directory
        - file_count: Number of files found
        - years: List of years found
        - year_range: Tuple of (min_year, max_year)
    """
    input_dir = config.get_input_directory(model, scenario, variable)
    files_with_years = discover_nc_files(model, scenario, variable)
    
    years = [year for _, year in files_with_years]
    
    return {
        'input_directory': str(input_dir),
        'file_count': len(files_with_years),
        'years': years,
        'year_range': (min(years), max(years)) if years else None
    }

