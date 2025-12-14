"""
Main script for merging CMIP6 NetCDF files by coordinates into Excel format.

Usage:
    python merge_nc_to_excel.py --model "ACCESS CM2" --scenario "SSP585" --variable "tasmax"
    python merge_nc_to_excel.py --model "ACCESS CM2" --scenario "SSP245" --variable "tasmin"
"""

import argparse
import sys
from pathlib import Path
import config
from utils.file_handler import discover_nc_files, get_file_info, validate_coordinate_consistency
from utils.nc_reader import merge_nc_files, extract_coordinate_data, prepare_dataframe_data
from utils.excel_writer import write_to_excel, validate_excel_file


def process_files(
    model: str,
    scenario: str,
    variable: str,
    aggregation: str = None
) -> Path:
    """
    Main processing function to merge NetCDF files and export to Excel.
    
    Args:
        model: Model name (e.g., "ACCESS CM2")
        scenario: Scenario name (e.g., "SSP585")
        variable: Variable name (e.g., "tasmax")
        aggregation: Aggregation method (default from config)
    
    Returns:
        Path to the created Excel file
    
    Raises:
        FileNotFoundError: If input directory doesn't exist
        ValueError: If no files found or processing fails
    """
    if aggregation is None:
        aggregation = config.EXCEL_AGGREGATION
    
    print("=" * 70)
    print(f"CMIP6 NetCDF to Excel Merger")
    print("=" * 70)
    print(f"Model: {model}")
    print(f"Scenario: {scenario}")
    print(f"Variable: {variable}")
    print(f"Aggregation: {aggregation}")
    print("=" * 70)
    
    # Step 1: Discover files
    print("\n[Step 1] Discovering NetCDF files...")
    try:
        files_with_years = discover_nc_files(model, scenario, variable)
        file_paths = [fp for fp, _ in files_with_years]
        years = [yr for _, yr in files_with_years]
        
        print(f"Found {len(file_paths)} files")
        print(f"Year range: {min(years)} - {max(years)}")
        
        # Display file info
        file_info = get_file_info(model, scenario, variable)
        print(f"Input directory: {file_info['input_directory']}")
        
    except (FileNotFoundError, ValueError) as e:
        print(f"ERROR: {e}")
        sys.exit(1)
    
    # Step 2: Validate coordinate consistency (lightweight check)
    print("\n[Step 2] Validating coordinate consistency...")
    if not validate_coordinate_consistency(file_paths):
        print("WARNING: Coordinate inconsistency detected. Proceeding anyway...")
    else:
        print("Coordinate validation passed")
    
    # Step 3: Read and merge NetCDF files
    print("\n[Step 3] Reading and merging NetCDF files...")
    try:
        merged_data, time_years = merge_nc_files(file_paths, variable, years)
        print(f"Merged data shape: {merged_data.shape}")
        print(f"Dimensions: {merged_data.dims}")
        print(f"Total time points: {len(time_years)}")
        
    except Exception as e:
        print(f"ERROR: Failed to merge files: {e}")
        sys.exit(1)
    
    # Step 4: Extract coordinate-based data
    print("\n[Step 4] Extracting coordinate-based data...")
    try:
        lat, lon, data_dict = extract_coordinate_data(merged_data, time_years, aggregation)
        print(f"Latitude range: {lat.min():.2f} to {lat.max():.2f}")
        print(f"Longitude range: {lon.min():.2f} to {lon.max():.2f}")
        print(f"Years processed: {sorted(data_dict.keys())}")
        
    except Exception as e:
        print(f"ERROR: Failed to extract coordinate data: {e}")
        sys.exit(1)
    
    # Step 5: Prepare DataFrame data
    print("\n[Step 5] Preparing data for Excel export...")
    try:
        dataframe_data = prepare_dataframe_data(lat, lon, data_dict, variable)
        print(f"Data prepared: {len(dataframe_data['lat'])} coordinate pairs")
        
    except Exception as e:
        print(f"ERROR: Failed to prepare DataFrame data: {e}")
        sys.exit(1)
    
    # Step 6: Export to Excel
    print("\n[Step 6] Exporting to Excel...")
    try:
        output_path = config.get_output_path(model, scenario, variable)
        write_to_excel(dataframe_data, output_path)
        
        # Validate output
        if validate_excel_file(output_path):
            print(f"\nSUCCESS! Excel file created: {output_path}")
            return output_path
        else:
            print(f"\nWARNING: Excel file created but validation failed: {output_path}")
            return output_path
            
    except Exception as e:
        print(f"ERROR: Failed to export to Excel: {e}")
        sys.exit(1)


def main():
    """Main entry point for command-line interface."""
    parser = argparse.ArgumentParser(
        description="Merge CMIP6 NetCDF files by coordinates into Excel format",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python merge_nc_to_excel.py --model "ACCESS CM2" --scenario "SSP585" --variable "tasmax"
  python merge_nc_to_excel.py --model "ACCESS CM2" --scenario "SSP245" --variable "tasmin" --aggregation "mean"
        """
    )
    
    parser.add_argument(
        '--model',
        type=str,
        default=config.DEFAULT_MODEL,
        help=f'Model name (default: {config.DEFAULT_MODEL})'
    )
    
    parser.add_argument(
        '--scenario',
        type=str,
        default=config.DEFAULT_SCENARIO,
        help=f'Scenario name (default: {config.DEFAULT_SCENARIO})'
    )
    
    parser.add_argument(
        '--variable',
        type=str,
        default=config.DEFAULT_VARIABLE,
        help=f'Variable name (default: {config.DEFAULT_VARIABLE})'
    )
    
    parser.add_argument(
        '--aggregation',
        type=str,
        choices=['mean', 'max', 'min', 'all'],
        default=config.EXCEL_AGGREGATION,
        help=f'Aggregation method for time dimension (default: {config.EXCEL_AGGREGATION})'
    )
    
    parser.add_argument(
        '--validate-paths',
        action='store_true',
        help='Validate that input and output paths exist'
    )
    
    args = parser.parse_args()
    
    # Validate paths if requested
    if args.validate_paths:
        input_exists, output_exists = config.validate_paths()
        print(f"Input path exists: {input_exists}")
        print(f"Output path exists: {output_exists}")
        if not input_exists:
            print(f"ERROR: Input path does not exist: {config.BASE_INPUT_PATH}")
            sys.exit(1)
        if not output_exists:
            print(f"WARNING: Output path does not exist: {config.BASE_OUTPUT_PATH}")
            print("It will be created automatically.")
    
    # Process files
    try:
        output_path = process_files(
            args.model,
            args.scenario,
            args.variable,
            args.aggregation
        )
        print(f"\n{'=' * 70}")
        print("Processing completed successfully!")
        print(f"{'=' * 70}")
        return 0
        
    except KeyboardInterrupt:
        print("\n\nProcessing interrupted by user.")
        return 1
    except Exception as e:
        print(f"\n\nFATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

