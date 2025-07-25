#!/usr/bin/env python3
"""
Missing Content Regeneration Script
This script reads the CSV file, identifies records with missing content fields,
and regenerates only those missing fields using the Gemini API.
"""

import pandas as pd
import google.generativeai as genai
import time
import os
import requests
import json
import re
from typing import List, Dict, Optional, Tuple
from googleapiclient.discovery import build
from datetime import datetime

# Import the existing classes
from gemini_csv_processor import GoogleImageSearcher, YouTubeSearcher

class MissingContentRegenerator:
    def __init__(self, gemini_api_key: str, google_api_key: str, search_engine_id: str):
        """Initialize the missing content regenerator"""
        genai.configure(api_key=gemini_api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        # Initialize search services
        self.image_searcher = GoogleImageSearcher(google_api_key, search_engine_id)
        self.youtube_searcher = YouTubeSearcher(google_api_key)
        
        # Define the content columns we work with
        self.content_columns = [
            'Image 1', 'Image 2', 'Image 3', 'Image 4', 'Image 5', 'Video',
            '1. Captivating Headline or Tagline',
            '2. Sensory Introduction (1–2 sentences)',
            '3. Key Features or Ingredients (Bullet Points or Icons)',
            '4. How to Use (Optional but useful)',
            '5. Emotional or Lifestyle Hook',
            '6. Tech Specs or Product Facts'
        ]
        
    def analyze_missing_data(self, csv_file: str) -> Tuple[pd.DataFrame, List[Dict]]:
        """Analyze the CSV file and identify missing data"""
        print(f"Reading CSV file: {csv_file}")
        df = pd.read_csv(csv_file)
        
        print(f"Total records: {len(df)}")
        
        # Analyze missing data
        missing_analysis = {}
        for col in self.content_columns:
            if col in df.columns:
                missing = df[col].isna().sum() + (df[col] == '').sum()
                missing_analysis[col] = missing
                percentage = (missing / len(df)) * 100
                print(f"{col}: {missing} missing ({percentage:.1f}%)")
            else:
                print(f"Column '{col}' not found in CSV")
        
        # Find records that need regeneration
        records_needing_regeneration = []
        records_complete = 0
        
        for index, row in df.iterrows():
            missing_fields = []
            for col in self.content_columns:
                if col in df.columns:
                    # Check if field is missing (NaN, empty string, or just whitespace)
                    cell_value = row[col]
                    if pd.isna(cell_value) or str(cell_value).strip() == '':
                        missing_fields.append(col)
            
            if missing_fields:
                records_needing_regeneration.append({
                    'index': index,
                    'id': row.get('ID', 'Unknown'),
                    'product_name': row.get('Line', 'Unknown Product'),
                    'brand': row.get('Brand', 'Unknown Brand'),
                    'missing_fields': missing_fields
                })
                if len(records_needing_regeneration) <= 10:  # Only show first 10 to avoid spam
                    print(f"Record {index + 1} ({row.get('Brand', 'Unknown')} {row.get('Line', 'Unknown')}): Missing {len(missing_fields)} fields - {', '.join(missing_fields[:3])}{'...' if len(missing_fields) > 3 else ''}")
                elif len(records_needing_regeneration) == 11:
                    print("... (showing only first 10 records with missing data)")
            else:
                records_complete += 1
                if records_complete <= 5:  # Only show first 5 complete records to avoid spam
                    print(f"Record {index + 1} ({row.get('Brand', 'Unknown')} {row.get('Line', 'Unknown')}): ✓ Complete - SKIPPING")
                elif records_complete == 6:
                    print("... (additional complete records will be skipped silently)")
        
        print(f"\n" + "="*60)
        print(f"ANALYSIS SUMMARY:")
        print(f"Total records: {len(df)}")
        print(f"Records with complete data (will be SKIPPED): {records_complete}")
        print(f"Records needing regeneration: {len(records_needing_regeneration)}")
        
        if records_needing_regeneration:
            print(f"\nMost frequently missing fields:")
            missing_summary = self.get_missing_fields_summary(records_needing_regeneration)
            for field, count in sorted(missing_summary.items(), key=lambda x: x[1], reverse=True):
                percentage = (count / len(records_needing_regeneration)) * 100
                print(f"  {field}: {count} records ({percentage:.1f}%)")
        
        print(f"="*60)
        
        return df, records_needing_regeneration
    
    def has_complete_data(self, row: pd.Series) -> bool:
        """Check if a record has all required content fields filled"""
        for col in self.content_columns:
            if col in row.index:
                cell_value = row[col]
                if pd.isna(cell_value) or str(cell_value).strip() == '':
                    return False
        return True
    
    def get_missing_fields_summary(self, records_needing_regeneration: List[Dict]) -> Dict[str, int]:
        """Get a summary of which fields are missing most frequently"""
        field_missing_count = {}
        for record in records_needing_regeneration:
            for field in record['missing_fields']:
                field_missing_count[field] = field_missing_count.get(field, 0) + 1
        return field_missing_count
    
    def create_content_prompt(self, product_name: str, brand: str, missing_fields: List[str]) -> str:
        """Create a prompt to generate only the missing content fields"""
        full_product_name = f"{brand} {product_name}"
        
        field_descriptions = {
            '1. Captivating Headline or Tagline': 'Write a brief, poetic or powerful phrase that evokes the essence of the product in Bulgarian.',
            '2. Sensory Introduction (1–2 sentences)': 'Describe the experience of using the product, focusing on the feel, scent, effect, or vibe in Bulgarian (1-2 sentences).',
            '3. Key Features or Ingredients (Bullet Points or Icons)': 'Present the top 4–6 features as bullet points, focusing on performance, quality, and what sets it apart in Bulgarian.',
            '4. How to Use (Optional but useful)': 'Provide simple step-by-step instructions in Bulgarian.',
            '5. Emotional or Lifestyle Hook': 'Show the identity or vibe the user taps into by using this product in Bulgarian.',
            '6. Tech Specs or Product Facts': 'Include size/volume, longevity, origin, certifications in Bulgarian.'
        }
        
        prompt = f"""Generate content for this beauty/perfume product in Bulgarian language: {full_product_name}

Please provide ONLY the following sections that are missing:

"""
        
        for field in missing_fields:
            if field in field_descriptions:
                prompt += f"**{field}:**\n{field_descriptions[field]}\n\n"
        
        prompt += """
Please write each section clearly separated and labeled. Write ONLY in Bulgarian language.
Do NOT include any image URLs or video links as I will handle those separately.
"""
        
        return prompt
    
    def search_missing_media(self, product_name: str, brand: str, missing_fields: List[str]) -> Dict:
        """Search for missing images and video"""
        full_product_name = f"{brand} {product_name}"
        media_data = {'images': [], 'video': None}
        
        # Check if we need images
        image_fields = [f for f in missing_fields if f.startswith('Image')]
        if image_fields:
            print(f"Searching for images for: {full_product_name}")
            image_query = f"{full_product_name} product high quality"
            image_urls = self.image_searcher.get_working_image_urls(image_query, 5)
            media_data['images'] = image_urls
        
        # Check if we need video
        if 'Video' in missing_fields:
            print(f"Searching for video for: {full_product_name}")
            video_query = f"{full_product_name} review tutorial"
            video_url = self.youtube_searcher.search_video(video_query)
            media_data['video'] = video_url
        
        return media_data
    
    def parse_generated_content(self, content: str, missing_fields: List[str]) -> Dict:
        """Parse the generated content into individual fields"""
        parsed_content = {}
        
        # Define patterns to match each field
        field_patterns = {
            '1. Captivating Headline or Tagline': r'\*\*1\.\s*Captivating Headline or Tagline:\*\*\s*\n(.*?)(?=\n\*\*|\n\n|\Z)',
            '2. Sensory Introduction (1–2 sentences)': r'\*\*2\.\s*Sensory Introduction.*?\*\*\s*\n(.*?)(?=\n\*\*|\n\n|\Z)',
            '3. Key Features or Ingredients (Bullet Points or Icons)': r'\*\*3\.\s*Key Features.*?\*\*\s*\n(.*?)(?=\n\*\*|\n\n|\Z)',
            '4. How to Use (Optional but useful)': r'\*\*4\.\s*How to Use.*?\*\*\s*\n(.*?)(?=\n\*\*|\n\n|\Z)',
            '5. Emotional or Lifestyle Hook': r'\*\*5\.\s*Emotional or Lifestyle Hook.*?\*\*\s*\n(.*?)(?=\n\*\*|\n\n|\Z)',
            '6. Tech Specs or Product Facts': r'\*\*6\.\s*Tech Specs.*?\*\*\s*\n(.*?)(?=\n\*\*|\n\n|\Z)'
        }
        
        for field in missing_fields:
            if field in field_patterns:
                pattern = field_patterns[field]
                match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
                if match:
                    parsed_content[field] = match.group(1).strip()
                else:
                    # Fallback: try to extract content after the field name
                    simple_pattern = rf'{re.escape(field)}:?\s*\n(.*?)(?=\n[0-9]+\.|\n\*\*|\Z)'
                    match = re.search(simple_pattern, content, re.DOTALL | re.IGNORECASE)
                    if match:
                        parsed_content[field] = match.group(1).strip()
        
        return parsed_content
    
    def regenerate_missing_content(self, csv_file: str, output_csv: str = None, delay: float = 2.0, start_from_id: str = None) -> None:
        """Main method to regenerate missing content"""
        if output_csv is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_csv = f'updated_products_{timestamp}.csv'
        
        # Analyze missing data
        df, records_needing_regeneration = self.analyze_missing_data(csv_file)
        
        if not records_needing_regeneration:
            print("No missing content found. All records are complete!")
            return

        # Define the specific records to process based on user request
        # - Rows 196 (ID 14127) and 197 (ID 39745) -> indices 195, 196
        # - Rows 221 to 226 -> indices 220 to 225
        # - Rows 228 to 245 -> indices 227 to 244
        indices_to_process = set()
        indices_to_process.add(195)  # Row 196
        indices_to_process.add(196)  # Row 197
        indices_to_process.update(range(220, 226))  # Rows 221 to 226
        indices_to_process.update(range(227, 245))  # Rows 228 to 245

        records_to_process = [
            r for r in records_needing_regeneration if r['index'] in indices_to_process
        ]
        
        if not records_to_process:
            print("No records found for regeneration in the specified ranges.")
            return

        print(f"\nStarting regeneration of {len(records_to_process)} specific records...")
        print(f"Output file: {output_csv}")
        print("=" * 60)
        
        # Create a backup
        backup_file = csv_file.replace('.csv', '_backup_regen.csv')
        df.to_csv(backup_file, index=False)
        print(f"Backup created: {backup_file}")
        
        # Create initial output file
        df.to_csv(output_csv, index=False)
        print(f"Initial output file created: {output_csv}")
        
        # Process each record
        updated_count = 0
        total_fields_updated = 0
        skipped_count = 0
        
        print(f"\nStarting to process {len(records_needing_regeneration)} records with missing data...")
        print(f"Note: Records with complete data have already been identified and will be skipped.")
        print(f"Auto-save: Progress will be saved after each record to prevent data loss.\n")
        
        for i, record in enumerate(records_to_process, 1):
            index = record['index']
            product_name = record['product_name']
            brand = record['brand']
            missing_fields = record['missing_fields']
            
            print(f"\nProcessing {i}/{len(records_to_process)}: {brand} {product_name} (Row: {index + 1})")
            print(f"Missing fields: {', '.join(missing_fields)}")
            
            try:
                # Generate content for text fields
                text_fields = [f for f in missing_fields if not f.startswith('Image') and f != 'Video']
                generated_content = {}
                
                if text_fields:
                    prompt = self.create_content_prompt(product_name, brand, text_fields)
                    response = self.model.generate_content(prompt)
                    generated_content = self.parse_generated_content(response.text, text_fields)
                
                # Search for missing media
                media_data = self.search_missing_media(product_name, brand, missing_fields)
                
                # Update the dataframe
                fields_updated = 0
                
                # Update text fields
                for field, content in generated_content.items():
                    if field in df.columns and content:
                        df.at[index, field] = content
                        fields_updated += 1
                
                # Update image fields
                for img_idx, image_url in enumerate(media_data['images']):
                    image_field = f'Image {img_idx+1}'
                    if image_field in missing_fields and image_field in df.columns:
                        df.at[index, image_field] = image_url
                        fields_updated += 1
                
                # Update video field
                if 'Video' in missing_fields and media_data['video'] and 'Video' in df.columns:
                    df.at[index, 'Video'] = media_data['video']
                    fields_updated += 1
                
                if fields_updated > 0:
                    updated_count += 1
                    total_fields_updated += fields_updated
                    print(f"✓ Updated {fields_updated} fields")
                    
                    # Save progress after each successful update
                    df.to_csv(output_csv, index=False)
                    print(f"✓ Progress saved to {output_csv}")
                else:
                    print("✗ No content generated")
                
                # Add delay between requests
                if i < len(records_to_process):
                    print(f"Waiting {delay} seconds...")
                    time.sleep(delay)
                
            except Exception as e:
                print(f"✗ Error processing record: {str(e)}")
        
        print("\n" + "=" * 60)
        print(f"Regeneration complete!")
        print(f"Records processed: {len(records_to_process)}")
        print(f"Records updated: {updated_count}")
        print(f"Total fields updated: {total_fields_updated}")
        print(f"Final output saved to: {output_csv}")
        print(f"Backup created: {backup_file}")
        print(f"Note: Progress was automatically saved after each record.")
        print(f"=" * 60)

def main():
    """Main function to run the missing content regeneration"""
    
    print("=" * 60)
    print("MISSING CONTENT REGENERATION SCRIPT")
    print("=" * 60)
    print()
    
    # Check for API keys
    print("Checking for API keys...")
    
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
    SEARCH_ENGINE_ID = os.getenv('SEARCH_ENGINE_ID')
    
    # If environment variables are not set, try to get them from user input
    if not GEMINI_API_KEY:
        print("GEMINI_API_KEY not found in environment variables.")
        GEMINI_API_KEY = input("Please enter your Gemini API key: ").strip()
        if not GEMINI_API_KEY:
            print("ERROR: Gemini API key is required!")
            return
    
    if not GOOGLE_API_KEY:
        print("GOOGLE_API_KEY not found in environment variables.")
        GOOGLE_API_KEY = input("Please enter your Google API key: ").strip()
        if not GOOGLE_API_KEY:
            print("ERROR: Google API key is required!")
            return
    
    if not SEARCH_ENGINE_ID:
        print("SEARCH_ENGINE_ID not found in environment variables.")
        SEARCH_ENGINE_ID = input("Please enter your Google Custom Search Engine ID: ").strip()
        if not SEARCH_ENGINE_ID:
            print("ERROR: Search Engine ID is required!")
            return
    
    print("✓ All API keys found!")
    print()
    
    # CSV file to process
    csv_file = 'updated_products_20250624_131259.csv'
    
    if not os.path.exists(csv_file):
        print(f"ERROR: CSV file '{csv_file}' not found!")
        return
    
    # Get processing options
    delay = input("Enter delay between requests in seconds (default: 2.0): ").strip()
    if not delay:
        delay = 2.0
    else:
        try:
            delay = float(delay)
        except ValueError:
            print("Invalid delay value. Using default 2.0 seconds.")
            delay = 2.0
    
    output_file = input("Enter output CSV filename (press Enter for auto-generated): ").strip()
    if not output_file:
        output_file = None
    
    print()
    print("=" * 60)
    print("STARTING MISSING CONTENT REGENERATION")
    print("=" * 60)
    print(f"Input CSV: {csv_file}")
    print(f"Delay between requests: {delay} seconds")
    print(f"Output file: {'Auto-generated' if output_file is None else output_file}")
    print()
    
    # Create regenerator instance
    regenerator = MissingContentRegenerator(GEMINI_API_KEY, GOOGLE_API_KEY, SEARCH_ENGINE_ID)
    
    try:
        # Process the CSV file
        regenerator.regenerate_missing_content(csv_file, output_csv=output_file, delay=delay)
        
        print()
        print("=" * 60)
        print("REGENERATION COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        
    except KeyboardInterrupt:
        print("\n" + "=" * 60)
        print("PROCESSING INTERRUPTED BY USER")
        print("=" * 60)
        print("Partial results may have been saved.")
        
    except Exception as e:
        print(f"\n" + "=" * 60)
        print("ERROR DURING PROCESSING")
        print("=" * 60)
        print(f"Error: {e}")
        print("Please check your API keys and internet connection.")

if __name__ == "__main__":
    main() 