#!/usr/bin/env python3
"""
Script to import content fields from parf.csv to target CSV file.
Matches records by ID and imports specified fields without overriding existing data.
"""

import pandas as pd
import sys
from pathlib import Path

def import_content_from_parf():
    """Import content fields from parf.csv to target CSV file."""
    
    # File paths
    source_file = "parf.csv"
    target_file = "18062025 - Парфюми  - Sheet1 (1).csv"
    backup_file = "18062025 - Парфюми  - Sheet1 (1)_backup.csv"
    
    # Check if files exist
    if not Path(source_file).exists():
        print(f"Error: Source file '{source_file}' not found!")
        return False
    
    if not Path(target_file).exists():
        print(f"Error: Target file '{target_file}' not found!")
        return False
    
    try:
        # Read CSV files
        print("Reading CSV files...")
        source_df = pd.read_csv(source_file)
        target_df = pd.read_csv(target_file)
        
        # Create backup
        print("Creating backup...")
        target_df.to_csv(backup_file, index=False)
        print(f"Backup created: {backup_file}")
        
        # Define the fields to import
        fields_to_import = [
            'Image 1', 'Image 2', 'Image 3', 'Image 4', 'Image 5', 'Video',
            '1. Captivating Headline or Tagline',
            '2. Sensory Introduction (1–2 sentences)',
            '3. Key Features or Ingredients (Bullet Points or Icons)',
            '4. How to Use (Optional but useful)',
            '5. Emotional or Lifestyle Hook',
            '6. Tech Specs or Product Facts'
        ]
        
        # Statistics
        total_matches = 0
        total_updates = 0
        total_fields_updated = 0
        
        print("\nStarting import process...")
        print(f"Source records: {len(source_df)}")
        print(f"Target records: {len(target_df)}")
        
        # Create a mapping of source data by ID
        source_by_id = {}
        for idx, row in source_df.iterrows():
            if pd.notna(row['ID']):
                source_by_id[row['ID']] = row
        
        print(f"Source records with valid ID: {len(source_by_id)}")
        
        # Process each row in target file
        for idx, target_row in target_df.iterrows():
            if pd.notna(target_row['ID']) and target_row['ID'] in source_by_id:
                total_matches += 1
                source_row = source_by_id[target_row['ID']]
                
                # Track if this record was updated
                record_updated = False
                
                # Import each field if it's empty in target and has content in source
                for field in fields_to_import:
                    if field in target_df.columns and field in source_df.columns:
                        # Check if target field is empty or contains only whitespace
                        target_value = target_row[field]
                        source_value = source_row[field]
                        
                        # Consider field empty if it's NaN, empty string, or only whitespace
                        target_is_empty = (pd.isna(target_value) or 
                                         (isinstance(target_value, str) and target_value.strip() == ''))
                        
                        # Consider source has content if it's not NaN and not empty after stripping
                        source_has_content = (pd.notna(source_value) and 
                                            isinstance(source_value, str) and 
                                            source_value.strip() != '')
                        
                        # Import if target is empty and source has content
                        if target_is_empty and source_has_content:
                            target_df.at[idx, field] = source_value.strip()
                            total_fields_updated += 1
                            record_updated = True
                
                if record_updated:
                    total_updates += 1
                    print(f"Updated record ID {target_row['ID']}: {target_row.get('Brand', 'Unknown')} - {target_row.get('Line', 'Unknown')}")
        
        # Save the updated target file
        print(f"\nSaving updated file...")
        target_df.to_csv(target_file, index=False)
        
        # Print summary
        print(f"\n=== IMPORT SUMMARY ===")
        print(f"Total records matched by ID: {total_matches}")
        print(f"Total records updated: {total_updates}")
        print(f"Total fields updated: {total_fields_updated}")
        print(f"Backup file: {backup_file}")
        print(f"Updated file: {target_file}")
        
        # Show some examples of updated records
        if total_updates > 0:
            print(f"\n=== SAMPLE UPDATED RECORDS ===")
            updated_records = target_df[target_df['ID'].isin(source_by_id.keys())]
            for idx, row in updated_records.head(5).iterrows():
                if pd.notna(row.get('1. Captivating Headline or Tagline')):
                    print(f"ID {row['ID']}: {row.get('Brand', 'Unknown')} - {row.get('Line', 'Unknown')}")
                    print(f"  Headline: {row.get('1. Captivating Headline or Tagline', 'N/A')[:100]}...")
                    print()
        
        return True
        
    except Exception as e:
        print(f"Error during import: {str(e)}")
        return False

if __name__ == "__main__":
    success = import_content_from_parf()
    if success:
        print("\n✅ Import completed successfully!")
    else:
        print("\n❌ Import failed!")
        sys.exit(1) 