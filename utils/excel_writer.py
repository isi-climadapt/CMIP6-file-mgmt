"""
Excel export utilities for coordinate-based climate data.
"""

import pandas as pd
from pathlib import Path
from typing import Dict
import config


def write_to_excel(
    data_dict: Dict,
    output_path: Path,
    sheet_name: str = None,
    max_rows_per_sheet: int = None
) -> None:
    """
    Write coordinate-based data to Excel file.
    
    Args:
        data_dict: Dictionary with keys as column names and values as arrays
                  Must include 'lat' and 'lon' keys
        output_path: Path where Excel file should be saved
        sheet_name: Name of the Excel sheet (default from config)
        max_rows_per_sheet: Maximum rows per sheet (default from config)
    
    Raises:
        ValueError: If data_dict doesn't contain 'lat' and 'lon' keys
    """
    if 'lat' not in data_dict or 'lon' not in data_dict:
        raise ValueError("data_dict must contain 'lat' and 'lon' keys")
    
    if sheet_name is None:
        sheet_name = config.EXCEL_SHEET_NAME
    
    if max_rows_per_sheet is None:
        max_rows_per_sheet = config.EXCEL_MAX_ROWS_PER_SHEET
    
    print(f"Creating DataFrame from {len(data_dict['lat'])} coordinate pairs...")
    
    # Create DataFrame
    df = pd.DataFrame(data_dict)
    
    # Ensure lat and lon are first columns
    cols = ['lat', 'lon'] + [c for c in df.columns if c not in ['lat', 'lon']]
    df = df[cols]
    
    print(f"DataFrame shape: {df.shape}")
    print(f"Columns: {df.columns.tolist()}")
    
    # Check if we need to split into multiple sheets
    if len(df) > max_rows_per_sheet:
        print(f"Warning: DataFrame has {len(df)} rows, which exceeds "
              f"Excel's recommended limit. Splitting into multiple sheets...")
        
        # Split into multiple sheets
        # Use ceiling division to correctly calculate number of sheets needed
        num_sheets = (len(df) + max_rows_per_sheet - 1) // max_rows_per_sheet
        
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            for i in range(num_sheets):
                start_idx = i * max_rows_per_sheet
                end_idx = min((i + 1) * max_rows_per_sheet, len(df))
                
                sheet_df = df.iloc[start_idx:end_idx]
                current_sheet_name = f"{sheet_name}_{i+1}" if num_sheets > 1 else sheet_name
                
                sheet_df.to_excel(
                    writer,
                    sheet_name=current_sheet_name,
                    index=False
                )
                
                print(f"  Written sheet '{current_sheet_name}' with {len(sheet_df)} rows")
    else:
        # Single sheet
        print(f"Writing to Excel file: {output_path}")
        df.to_excel(output_path, sheet_name=sheet_name, index=False)
        print(f"  Written {len(df)} rows to sheet '{sheet_name}'")
    
    print(f"Excel file saved successfully: {output_path}")


def validate_excel_file(file_path: Path) -> bool:
    """
    Validate that an Excel file was created successfully.
    
    Args:
        file_path: Path to the Excel file
    
    Returns:
        True if file exists and can be read
    """
    if not file_path.exists():
        return False
    
    try:
        # Try to read the file
        df = pd.read_excel(file_path, nrows=1)
        return True
    except Exception as e:
        print(f"Warning: Could not validate Excel file: {e}")
        return False

