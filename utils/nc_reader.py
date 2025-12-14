"""
NetCDF reading and processing utilities using xarray.
"""

import numpy as np
import xarray as xr
from pathlib import Path
from typing import List, Tuple, Dict
import config


def read_nc_file(file_path: Path, variable_name: str = None) -> xr.Dataset:
    """
    Read a single NetCDF file using xarray.
    
    Args:
        file_path: Path to the NetCDF file
        variable_name: Name of the variable to extract (if None, returns full dataset)
    
    Returns:
        xarray Dataset or DataArray
    """
    ds = xr.open_dataset(file_path, chunks=config.CHUNK_SIZE)
    
    if variable_name:
        if variable_name not in ds.data_vars:
            raise ValueError(
                f"Variable '{variable_name}' not found in file: {file_path}"
            )
        return ds[variable_name]
    
    return ds


def merge_nc_files(
    file_paths: List[Path],
    variable_name: str,
    years: List[int] = None
) -> Tuple[xr.DataArray, List[int]]:
    """
    Merge multiple NetCDF files along the time dimension.
    
    Args:
        file_paths: List of NetCDF file paths to merge
        variable_name: Name of the variable to extract and merge
        years: Optional list of years corresponding to each file
    
    Returns:
        Tuple of (merged DataArray, list of years for each time point)
    
    Raises:
        ValueError: If coordinates are inconsistent across files
    """
    if not file_paths:
        raise ValueError("No file paths provided")
    
    print(f"Reading {len(file_paths)} NetCDF files...")
    
    # Read all files
    datasets = []
    for i, file_path in enumerate(file_paths):
        print(f"  Reading file {i+1}/{len(file_paths)}: {file_path.name}")
        try:
            da = read_nc_file(file_path, variable_name)
            datasets.append(da)
        except Exception as e:
            raise RuntimeError(
                f"Error reading file {file_path}: {e}"
            )
    
    # Validate coordinate consistency
    if len(datasets) > 1:
        first_coords = {
            'lat': datasets[0].coords['lat'].values,
            'lon': datasets[0].coords['lon'].values
        }
        
        for i, da in enumerate(datasets[1:], 1):
            lat_match = np.allclose(
                da.coords['lat'].values,
                first_coords['lat'],
                atol=0.01
            )
            lon_match = np.allclose(
                da.coords['lon'].values,
                first_coords['lon'],
                atol=0.01
            )
            
            if not (lat_match and lon_match):
                raise ValueError(
                    f"Coordinate mismatch detected in file {i+1}. "
                    "All files must have the same lat/lon grid."
                )
    
    # Concatenate along time dimension
    print("Merging files along time dimension...")
    merged = xr.concat(datasets, dim='time')
    
    # Create year array for each time point
    # Each file has 365 days, so we assign the corresponding year to each day
    time_years = []
    if years:
        for i, year in enumerate(years):
            # Assume 365 days per file (or get actual length)
            days_in_file = len(datasets[i])
            time_years.extend([year] * days_in_file)
    else:
        # Try to extract from time coordinates
        try:
            import pandas as pd
            time_index = pd.to_datetime(merged.coords['time'].values)
            time_years = time_index.year.tolist()
        except:
            # Fallback: assume sequential years starting from first file
            print("Warning: Could not determine years. Using sequential years.")
            for i in range(len(datasets)):
                days_in_file = len(datasets[i])
                # This is a fallback - not ideal
                time_years.extend([2000 + i] * days_in_file)
    
    return merged, time_years


def extract_coordinate_data(
    data_array: xr.DataArray,
    time_years: List[int],
    aggregation: str = "mean"
) -> Tuple[np.ndarray, np.ndarray, Dict[int, np.ndarray]]:
    """
    Extract coordinate-based data from xarray DataArray.
    
    Args:
        data_array: xarray DataArray with dimensions (time, lat, lon)
        time_years: List of years corresponding to each time point
        aggregation: How to aggregate time dimension per year
                     Options: "mean", "max", "min", "all"
    
    Returns:
        Tuple of (lat_array, lon_array, data_dict)
        where data_dict is {year: aggregated_values_array}
    """
    lat = data_array.coords['lat'].values
    lon = data_array.coords['lon'].values
    
    # Convert time_years to numpy array
    years = np.array(time_years)
    
    # Group by year and aggregate
    unique_years = np.unique(years)
    data_dict = {}
    
    print(f"Aggregating data for {len(unique_years)} years...")
    
    for year in unique_years:
        year_mask = years == year
        # Convert boolean mask to integer indices for isel()
        year_indices = np.where(year_mask)[0]
        year_data = data_array.isel(time=year_indices)
        
        if aggregation == "mean":
            aggregated = year_data.mean(dim='time').values
        elif aggregation == "max":
            aggregated = year_data.max(dim='time').values
        elif aggregation == "min":
            aggregated = year_data.min(dim='time').values
        elif aggregation == "all":
            # Keep all time steps - this creates a larger array
            aggregated = year_data.values  # Shape: (days, lat, lon)
        else:
            raise ValueError(f"Unknown aggregation method: {aggregation}")
        
        data_dict[int(year)] = aggregated
        print(f"  Processed year {year}")
    
    return lat, lon, data_dict


def prepare_dataframe_data(
    lat: np.ndarray,
    lon: np.ndarray,
    data_dict: Dict[int, np.ndarray],
    variable_name: str
) -> Dict:
    """
    Prepare data in a format suitable for pandas DataFrame.
    
    Creates a structure where each row represents a unique (lat, lon) pair,
    and columns represent years.
    
    Args:
        lat: Latitude array
        lon: Longitude array
        data_dict: Dictionary mapping years to data arrays
        variable_name: Name of the variable (for column naming)
    
    Returns:
        Dictionary with keys: 'lat', 'lon', and year columns
    """
    n_lat, n_lon = len(lat), len(lon)
    
    # Create meshgrid for coordinates
    lon_grid, lat_grid = np.meshgrid(lon, lat)
    
    # Flatten coordinates
    lat_flat = lat_grid.flatten()
    lon_flat = lon_grid.flatten()
    
    # Prepare data dictionary
    result = {
        'lat': lat_flat,
        'lon': lon_flat
    }
    
    # Add data for each year
    for year, data_array in sorted(data_dict.items()):
        # Handle different data shapes
        if data_array.ndim == 2:  # (lat, lon) - aggregated data
            data_flat = data_array.flatten()
        elif data_array.ndim == 3:  # (time, lat, lon) - all days
            # For "all" aggregation, we might want to keep daily data
            # For now, flatten the first dimension
            data_flat = data_array.reshape(-1, n_lat * n_lon).mean(axis=0)
        else:
            raise ValueError(f"Unexpected data array shape: {data_array.shape}")
        
        column_name = f"{variable_name}_{year}"
        result[column_name] = data_flat
    
    return result

