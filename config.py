"""
Configuration file for CMIP6 NetCDF to Excel merger.

This module contains all configurable parameters for the project.
"""

import os
from pathlib import Path

# Base paths
BASE_INPUT_PATH = r"C:\Users\ibian\Desktop\ClimAdapt\CMIP6"
BASE_OUTPUT_PATH = r"C:\Users\ibian\Desktop\ClimAdapt\CMIP6\ACCESS CM2 xlsx"

# Default parameters
DEFAULT_MODEL = "ACCESS CM2"
DEFAULT_SCENARIO = "SSP585"
DEFAULT_VARIABLE = "tasmax"

# Available models, scenarios, and variables
AVAILABLE_MODELS = ["ACCESS CM2"]
AVAILABLE_SCENARIOS = ["SSP585", "SSP245"]
AVAILABLE_VARIABLES = ["tasmax", "tasmin", "pr", "hurs"]

# File naming patterns
# Pattern to extract year from filename: *_{year}_*.nc
YEAR_PATTERN = r"_(\d{4})_"

# Directory structure pattern
# {Model} {Scenario}/CMIP6 Files_{variable}/
DIRECTORY_PATTERN = "{model} {scenario}/CMIP6 Files_{variable}/"

# Coordinate precision for matching (decimal places)
COORDINATE_PRECISION = 2

# Excel export settings
EXCEL_AGGREGATION = "mean"  # Options: "mean", "max", "min", "all"
EXCEL_SHEET_NAME = "Data"
EXCEL_MAX_ROWS_PER_SHEET = 1000000  # Excel limit is 1,048,576

# NetCDF processing settings
CHUNK_SIZE = {
    'time': 365,
    'lat': 100,
    'lon': 100
}

# Output file naming
OUTPUT_FILENAME_PATTERN = "{model}_{scenario}_{variable}.xlsx"
OUTPUT_FILENAME_SEPARATOR = "_"  # Replace spaces with this in filenames


def get_input_directory(model: str, scenario: str, variable: str) -> Path:
    """
    Get the input directory path for a given model, scenario, and variable.
    
    Args:
        model: Model name (e.g., "ACCESS CM2")
        scenario: Scenario name (e.g., "SSP585")
        variable: Variable name (e.g., "tasmax")
    
    Returns:
        Path object for the input directory
    """
    directory_name = DIRECTORY_PATTERN.format(
        model=model,
        scenario=scenario,
        variable=variable
    )
    return Path(BASE_INPUT_PATH) / directory_name


def get_output_path(model: str, scenario: str, variable: str) -> Path:
    """
    Get the output file path for a given model, scenario, and variable.
    
    Args:
        model: Model name (e.g., "ACCESS CM2")
        scenario: Scenario name (e.g., "SSP585")
        variable: Variable name (e.g., "tasmax")
    
    Returns:
        Path object for the output file
    """
    # Clean model name for filename (replace spaces with separator)
    model_clean = model.replace(" ", OUTPUT_FILENAME_SEPARATOR)
    scenario_clean = scenario.replace(" ", OUTPUT_FILENAME_SEPARATOR)
    
    filename = OUTPUT_FILENAME_PATTERN.format(
        model=model_clean,
        scenario=scenario_clean,
        variable=variable
    )
    
    # Ensure output directory exists
    output_dir = Path(BASE_OUTPUT_PATH)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    return output_dir / filename


def validate_paths():
    """
    Validate that base paths exist.
    
    Returns:
        tuple: (input_exists, output_exists)
    """
    input_exists = os.path.exists(BASE_INPUT_PATH)
    output_exists = os.path.exists(BASE_OUTPUT_PATH) or os.path.exists(os.path.dirname(BASE_OUTPUT_PATH))
    return input_exists, output_exists

