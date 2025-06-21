import pandas as pd
import re
import os
from typing import Dict, List, Optional, Tuple

class CSVLinkUpdater:
    def __init__(self, csv_file: str, results_file: str):
        """Initialize the CSV Link Updater"""
        self.csv_file = csv_file
        self.results_file = results_file
        self.df = None
        self.updated_count = 0
        self.skipped_count = 0
        
    def load_csv(self) -> bool:
        """Load the CSV file"""
        try:
            self.df = pd.read_csv(self.csv_file)
            print(f"Loaded CSV with {len(self.df)} rows")
            return True
        except Exception as e:
            print(f"Error loading CSV file: {e}")
            return False
    
    def extract_links_from_new_format(self, section: str) -> Tuple[List[str], Optional[str], Dict[str, str]]:
        """Extract image links, video link, and marketing content from the new results format"""
        image_urls = []
        video_url = None
        marketing_content = {}
        
        # Extract image URLs from WORKING IMAGE LINKS section
        image_section_match = re.search(r'WORKING IMAGE LINKS:\n(.*?)(?=\n\nVIDEO LINK:|$)', section, re.DOTALL)
        if image_section_match:
            image_content = image_section_match.group(1)
            # Find all image URLs in the format "Image X: URL"
            image_matches = re.findall(r'Image \d+: (https?://[^\s]+)', image_content)
            image_urls.extend(image_matches)
        
        # Extract video URL from VIDEO LINK section
        video_section_match = re.search(r'VIDEO LINK:\n(.*?)(?=\n\n|$)', section, re.DOTALL)
        if video_section_match:
            video_content = video_section_match.group(1)
            # Find video URL in the format "Video: URL"
            video_match = re.search(r'Video: (https?://[^\s]+)', video_content)
            if video_match:
                video_url = video_match.group(1)
        
        # Extract marketing content sections
        marketing_sections = {
            'headline': r'\*\*1\. Captivating Headline or Tagline[:\*]*\s*(.*?)(?=\n\*\*2\.|$)',
            'sensory': r'\*\*2\. Sensory Introduction[^:]*[:\*]*\s*(.*?)(?=\n\*\*3\.|$)',
            'features': r'\*\*3\. Key Features or Ingredients[^:]*[:\*]*\s*(.*?)(?=\n\*\*4\.|$)',
            'how_to_use': r'\*\*4\. How to Use[^:]*[:\*]*\s*(.*?)(?=\n\*\*5\.|$)',
            'emotional': r'\*\*5\. Emotional or Lifestyle Hook[^:]*[:\*]*\s*(.*?)(?=\n\*\*6\.|$)',
            'tech_specs': r'\*\*6\. Tech Specs or Product Facts[^:]*[:\*]*\s*(.*?)(?=\n\*\*|$)'
        }
        
        for key, pattern in marketing_sections.items():
            match = re.search(pattern, section, re.DOTALL | re.IGNORECASE)
            if match:
                content = match.group(1).strip()
                # Clean up the content by removing extra whitespace and newlines
                content = re.sub(r'\n\s*\n', '\n', content)  # Remove empty lines
                content = re.sub(r'\s+', ' ', content)  # Normalize whitespace
                marketing_content[key] = content
            else:
                marketing_content[key] = ''
        
        return image_urls, video_url, marketing_content
    
    def parse_results_file(self) -> Dict[str, Dict]:
        """Parse the Gemini results file and extract links for each product"""
        if not os.path.exists(self.results_file):
            print(f"Results file not found: {self.results_file}")
            return {}
        
        try:
            with open(self.results_file, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"Error reading results file: {e}")
            return {}
        
        # Split content by product sections (updated separator)
        product_sections = content.split('============================================================')
        
        products_data = {}
        
        for section in product_sections:
            if 'PRODUCT' not in section:
                continue
                
            # Extract product name
            product_match = re.search(r'PRODUCT \d+: (.+)', section)
            if not product_match:
                continue
                
            product_name = product_match.group(1).strip()
            
            # Check if the request was successful
            if 'Status: error' in section:
                print(f"Skipping {product_name} - API error")
                continue
            
            # Extract links from the new format
            image_urls, video_url, marketing_content = self.extract_links_from_new_format(section)
            
            # Include products that have links OR marketing content
            if image_urls or video_url or any(marketing_content.values()):
                products_data[product_name] = {
                    'images': image_urls,
                    'video': video_url,
                    'marketing_content': marketing_content
                }
                content_info = []
                if image_urls:
                    content_info.append(f"{len(image_urls)} images")
                if video_url:
                    content_info.append("1 video")
                if any(marketing_content.values()):
                    content_info.append("marketing content")
                print(f"Found {', '.join(content_info)} for: {product_name}")
            else:
                print(f"Skipping {product_name} - No content found")
        
        return products_data
    
    def update_csv_with_links(self, products_data: Dict[str, Dict]) -> bool:
        """Update the CSV file with extracted links and marketing content"""
        if self.df is None:
            print("CSV not loaded")
            return False
        
        # Column mappings (assuming 0-based indexing)
        # Column F is index 5 (Line/Product name)
        # Column O is index 14 (Image 1)
        # Column P is index 15 (Image 2)  
        # Column Q is index 16 (Image 3)
        # Column R is index 17 (Image 4)
        # Column T is index 19 (Video)
        # Column U is index 20 (1. Captivating Headline or Tagline)
        # Column V is index 21 (2. Sensory Introduction)
        # Column W is index 22 (3. Key Features or Ingredients)
        # Column X is index 23 (4. How to Use)
        # Column Y is index 24 (5. Emotional or Lifestyle Hook)
        # Column Z is index 25 (6. Tech Specs or Product Facts)
        
        product_col_index = 5  # Column F (Line)
        image_col_indices = [14, 15, 16, 17]  # Columns O, P, Q, R
        video_col_index = 19  # Column T
        marketing_col_indices = {
            'headline': 20,      # Column U
            'sensory': 21,       # Column V
            'features': 22,      # Column W
            'how_to_use': 23,    # Column X
            'emotional': 24,     # Column Y
            'tech_specs': 25     # Column Z
        }
        
        # Ensure we have enough columns
        required_cols = max(list(marketing_col_indices.values()) + image_col_indices + [video_col_index]) + 1
        while len(self.df.columns) < required_cols:
            self.df[f'Column_{len(self.df.columns)}'] = ''
        
        # Update each row
        for index, row in self.df.iterrows():
            product_name = str(row.iloc[product_col_index]).strip()
            
            if product_name in products_data:
                data = products_data[product_name]
                
                # Clear existing image data first
                for img_col_idx in image_col_indices:
                    self.df.iloc[index, img_col_idx] = ''
                
                # Update image columns with working URLs
                for i, img_url in enumerate(data['images']):
                    if i < len(image_col_indices):
                        self.df.iloc[index, image_col_indices[i]] = img_url
                
                # Update video column
                if data['video']:
                    self.df.iloc[index, video_col_index] = data['video']
                else:
                    self.df.iloc[index, video_col_index] = ''
                
                # Update marketing content columns
                if 'marketing_content' in data:
                    marketing_data = data['marketing_content']
                    for key, col_index in marketing_col_indices.items():
                        content = marketing_data.get(key, '')
                        self.df.iloc[index, col_index] = content
                
                self.updated_count += 1
                print(f"Updated row {index + 1}: {product_name} - {len(data['images'])} images, {'1' if data['video'] else '0'} video, marketing content added")
            else:
                self.skipped_count += 1
        
        return True
    
    def validate_links_in_csv(self) -> Dict[str, int]:
        """Validate the links that were added to the CSV"""
        if self.df is None:
            return {}
        
        import requests
        
        stats = {
            'total_image_links': 0,
            'working_image_links': 0,
            'broken_image_links': 0,
            'total_video_links': 0,
            'working_video_links': 0,
            'broken_video_links': 0
        }
        
        image_col_indices = [14, 15, 16, 17]  # Columns O, P, Q, R
        video_col_index = 19  # Column T
        
        print("Validating links in CSV...")
        
        for index, row in self.df.iterrows():
            # Check image links
            for img_col_idx in image_col_indices:
                url = str(row.iloc[img_col_idx]).strip()
                if url and url != 'nan' and url.startswith('http'):
                    stats['total_image_links'] += 1
                    try:
                        response = requests.head(url, timeout=10, allow_redirects=True)
                        if response.status_code == 200:
                            stats['working_image_links'] += 1
                        else:
                            stats['broken_image_links'] += 1
                    except:
                        stats['broken_image_links'] += 1
            
            # Check video link
            video_url = str(row.iloc[video_col_index]).strip()
            if video_url and video_url != 'nan' and video_url.startswith('http'):
                stats['total_video_links'] += 1
                try:
                    response = requests.head(video_url, timeout=10, allow_redirects=True)
                    if response.status_code == 200:
                        stats['working_video_links'] += 1
                    else:
                        stats['broken_video_links'] += 1
                except:
                    stats['broken_video_links'] += 1
        
        return stats
    
    def save_updated_csv(self, output_file: str = None) -> bool:
        """Save the updated CSV file"""
        if self.df is None:
            print("No data to save")
            return False
        
        if output_file is None:
            # Create backup and overwrite original
            backup_file = self.csv_file.replace('.csv', '_backup.csv')
            try:
                # Create backup only if it doesn't exist
                if not os.path.exists(backup_file):
                    original_df = pd.read_csv(self.csv_file)
                    original_df.to_csv(backup_file, index=False)
                    print(f"Created backup: {backup_file}")
                else:
                    print(f"Backup already exists: {backup_file}")
                
                # Save updated file
                output_file = self.csv_file
            except Exception as e:
                print(f"Error creating backup: {e}")
                output_file = self.csv_file.replace('.csv', '_updated.csv')
        
        try:
            self.df.to_csv(output_file, index=False)
            print(f"Updated CSV saved to: {output_file}")
            return True
        except Exception as e:
            print(f"Error saving CSV: {e}")
            return False
    
    def process(self, output_file: str = None, validate_links: bool = False) -> bool:
        """Main processing function"""
        print("Starting CSV update process...")
        
        # Load CSV
        if not self.load_csv():
            return False
        
        # Parse results file
        print("Parsing results file...")
        products_data = self.parse_results_file()
        
        if not products_data:
            print("No product data found in results file")
            return False
        
        print(f"Found data for {len(products_data)} products")
        
        # Update CSV with links
        print("Updating CSV with working links...")
        if not self.update_csv_with_links(products_data):
            return False
        
        # Save updated CSV
        if not self.save_updated_csv(output_file):
            return False
        
        # Validate links if requested
        if validate_links:
            print("Validating links...")
            stats = self.validate_links_in_csv()
            print("\nLink validation results:")
            print(f"Image links - Total: {stats['total_image_links']}, Working: {stats['working_image_links']}, Broken: {stats['broken_image_links']}")
            print(f"Video links - Total: {stats['total_video_links']}, Working: {stats['working_video_links']}, Broken: {stats['broken_video_links']}")
        
        print(f"\nUpdate complete!")
        print(f"Updated rows: {self.updated_count}")
        print(f"Skipped rows: {self.skipped_count}")
        
        return True

def main():
    # Configuration
    CSV_FILE = "18062025 - Парфюми  - Sheet1.csv"
    RESULTS_FILE = "gemini_beauty_products_results_with_working_links.txt"
    OUTPUT_FILE = None  # Will create backup and overwrite original
    VALIDATE_LINKS = True  # Set to True to validate all links after updating
    
    # Check if files exist
    if not os.path.exists(CSV_FILE):
        print(f"CSV file not found: {CSV_FILE}")
        return
    
    if not os.path.exists(RESULTS_FILE):
        print(f"Results file not found: {RESULTS_FILE}")
        print("Please run the gemini_csv_processor.py script first to generate the results file.")
        return
    
    # Initialize updater
    updater = CSVLinkUpdater(CSV_FILE, RESULTS_FILE)
    
    # Process the files
    success = updater.process(OUTPUT_FILE, VALIDATE_LINKS)
    
    if success:
        print("\n✅ CSV update completed successfully!")
        print("Your CSV file now contains working image and video links.")
    else:
        print("\n❌ CSV update failed. Please check the error messages above.")

if __name__ == "__main__":
    main() 