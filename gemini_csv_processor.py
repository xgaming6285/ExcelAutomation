import pandas as pd
import google.generativeai as genai
import time
import os
import requests
import json
import re
from typing import List, Dict, Optional
from googleapiclient.discovery import build

class GoogleImageSearcher:
    def __init__(self, api_key: str, search_engine_id: str):
        """Initialize Google Custom Search API client"""
        self.api_key = api_key
        self.search_engine_id = search_engine_id
        self.service = build("customsearch", "v1", developerKey=api_key)
        
    def search_images(self, query: str, num_images: int = 5) -> List[str]:
        """Search for images using Google Custom Search API"""
        try:
            # Perform the search
            result = self.service.cse().list(
                q=query,
                cx=self.search_engine_id,
                searchType='image',
                num=num_images,
                imgSize='LARGE',
                imgType='photo',
                safe='active'
            ).execute()
            
            # Extract image URLs
            image_urls = []
            if 'items' in result:
                for item in result['items']:
                    if 'link' in item:
                        image_urls.append(item['link'])
            
            return image_urls
        except Exception as e:
            print(f"Error searching images for '{query}': {str(e)}")
            return []
    
    def validate_image_url(self, url: str, timeout: int = 10) -> bool:
        """Validate if an image URL is accessible and returns an image"""
        try:
            response = requests.head(url, timeout=timeout, allow_redirects=True)
            content_type = response.headers.get('content-type', '').lower()
            
            # Check if the response is successful and content type is an image
            return (response.status_code == 200 and 
                    any(img_type in content_type for img_type in ['image/', 'jpeg', 'jpg', 'png', 'gif', 'webp']))
        except:
            return False
    
    def get_working_image_urls(self, query: str, num_images: int = 5) -> List[str]:
        """Get working image URLs for a search query"""
        # Search for more images than needed to account for invalid ones
        search_results = self.search_images(query, num_images * 2)
        
        working_urls = []
        for url in search_results:
            if len(working_urls) >= num_images:
                break
                
            if self.validate_image_url(url):
                working_urls.append(url)
                print(f"✓ Valid image URL found: {url[:80]}...")
            else:
                print(f"✗ Invalid image URL: {url[:80]}...")
        
        return working_urls

class YouTubeSearcher:
    def __init__(self, api_key: str):
        """Initialize YouTube Data API client"""
        self.api_key = api_key
        self.service = build("youtube", "v3", developerKey=api_key)
    
    def search_video(self, query: str) -> Optional[str]:
        """Search for a YouTube video"""
        try:
            # Perform the search
            result = self.service.search().list(
                q=query,
                part='snippet',
                type='video',
                maxResults=1,
                order='relevance',
                safeSearch='moderate'
            ).execute()
            
            # Extract video URL
            if 'items' in result and len(result['items']) > 0:
                video_id = result['items'][0]['id']['videoId']
                return f"https://www.youtube.com/watch?v={video_id}"
            
            return None
        except Exception as e:
            print(f"Error searching YouTube for '{query}': {str(e)}")
            return None

class GeminiCSVProcessor:
    def __init__(self, gemini_api_key: str, google_api_key: str, search_engine_id: str):
        """Initialize the Gemini API client and Google Search"""
        genai.configure(api_key=gemini_api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        # Initialize search services
        self.image_searcher = GoogleImageSearcher(google_api_key, search_engine_id)
        self.youtube_searcher = YouTubeSearcher(google_api_key)
        
    def create_prompt(self, product_name: str) -> str:
        """Create the prompt for each product"""
        base_prompt = f"""Write a detailed product description for this beauty/perfume product in Bulgarian language following this structure:

Best Description Structure for Beauty & Perfume Products

1. Captivating Headline or Tagline
Start with a brief, poetic or powerful phrase that evokes the essence of the product in Bulgarian.

2. Sensory Introduction (1–2 sentences)
Describe the experience of using the product, focusing on the feel, scent, effect, or vibe in Bulgarian.

3. Key Features or Ingredients (Bullet Points)
Present the top 4–6 features, focusing on performance, quality, and what sets it apart in Bulgarian.

4. How to Use
Simple step-by-step instructions in Bulgarian.

5. Emotional or Lifestyle Hook
Show the identity or vibe the user taps into by using it in Bulgarian.

6. Tech Specs or Product Facts
Include size/volume, longevity, origin, certifications in Bulgarian.

Product: {product_name}

Please write ONLY the product description in Bulgarian. Do NOT include any image URLs or video links in your response as I will handle those separately."""
        
        return base_prompt
    
    def search_product_media(self, product_name: str) -> Dict:
        """Search for images and video for a product"""
        print(f"Searching for media for: {product_name}")
        
        # Search for product images
        image_query = f"{product_name} product high quality"
        image_urls = self.image_searcher.get_working_image_urls(image_query, 5)
        
        # Search for YouTube video
        video_query = f"{product_name} review tutorial"
        video_url = self.youtube_searcher.search_video(video_query)
        
        return {
            'images': image_urls,
            'video': video_url
        }
    
    def process_product(self, product_name: str) -> Dict:
        """Process a single product through Gemini API and search for media"""
        try:
            # Get product description from Gemini
            prompt = self.create_prompt(product_name)
            response = self.model.generate_content(prompt)
            
            # Search for actual working media links
            media_data = self.search_product_media(product_name)
            
            return {
                'product': product_name,
                'description': response.text,
                'images': media_data['images'],
                'video': media_data['video'],
                'status': 'success'
            }
        except Exception as e:
            return {
                'product': product_name,
                'description': f"Error: {str(e)}",
                'images': [],
                'video': None,
                'status': 'error'
            }
    
    def get_last_processed_product(self, output_file: str) -> int:
        """Get the number of the last processed product from the output file"""
        if not os.path.exists(output_file):
            return 0
        
        try:
            with open(output_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Find all product numbers using regex
            product_matches = re.findall(r'PRODUCT (\d+):', content)
            
            if product_matches:
                last_product_num = max(int(num) for num in product_matches)
                print(f"Found existing output file. Last processed product: {last_product_num}")
                return last_product_num
            else:
                return 0
        except Exception as e:
            print(f"Error reading existing output file: {str(e)}")
            return 0

    def process_csv(self, csv_file_path: str, output_file: str = 'gemini_results_with_links.txt', delay: float = 2.0, resume: bool = True, start_from: int = None) -> List[Dict]:
        """Process the entire CSV file"""
        try:
            # Read CSV file
            df = pd.read_csv(csv_file_path)
            
            # Extract column F (Line) - assuming it's the 6th column (index 5)
            products = df.iloc[:, 5].dropna().tolist()  # Column F, remove NaN values
            
            print(f"Found {len(products)} products to process")
            
            # Check if we should resume from a previous run or start from a specific product
            start_index = 0
            file_mode = 'w'
            
            if start_from is not None:
                # Force start from a specific product number
                start_index = start_from - 1  # Convert to 0-based index
                file_mode = 'a'  # Append to existing file
                print(f"Force starting from product {start_from}")
            elif resume:
                last_processed = self.get_last_processed_product(output_file)
                if last_processed > 0:
                    start_index = last_processed  # Start from the next product
                    file_mode = 'a'  # Append to existing file
                    print(f"Resuming from product {start_index + 1}")
                else:
                    print("Starting fresh processing")
            else:
                print("Starting fresh processing")
            
            results = []
            
            # Open output file for writing/appending
            with open(output_file, file_mode, encoding='utf-8') as f:
                # Write header only if starting fresh
                if file_mode == 'w':
                    f.write("GEMINI API RESULTS WITH WORKING LINKS FOR BEAUTY PRODUCTS\n")
                    f.write("=" * 60 + "\n\n")
                
                # Process products starting from the resume point
                products_to_process = products[start_index:]
                
                for i, product in enumerate(products_to_process):
                    current_product_num = start_index + i + 1
                    print(f"\nProcessing {current_product_num}/{len(products)}: {product}")
                    
                    # Process the product
                    result = self.process_product(product)
                    results.append(result)
                    
                    # Write to file
                    f.write(f"PRODUCT {current_product_num}: {product}\n")
                    f.write("-" * 50 + "\n")
                    f.write(f"Status: {result['status']}\n\n")
                    
                    if result['status'] == 'success':
                        f.write("DESCRIPTION:\n")
                        f.write(result['description'])
                        f.write("\n\n")
                        
                        f.write("WORKING IMAGE LINKS:\n")
                        for j, img_url in enumerate(result['images'], 1):
                            f.write(f"Image {j}: {img_url}\n")
                        if not result['images']:
                            f.write("No working image links found\n")
                        f.write("\n")
                        
                        f.write("VIDEO LINK:\n")
                        if result['video']:
                            f.write(f"Video: {result['video']}\n")
                        else:
                            f.write("No video found\n")
                    else:
                        f.write("ERROR:\n")
                        f.write(result['description'])
                    
                    f.write("\n\n" + "=" * 60 + "\n\n")
                    
                    # Flush to ensure data is written immediately
                    f.flush()
                    
                    # Add delay to avoid rate limiting (Google APIs have limits)
                    if current_product_num < len(products):  # Don't delay after the last item
                        time.sleep(delay)
            
            print(f"\nProcessing complete! Results saved to {output_file}")
            return results
            
        except Exception as e:
            print(f"Error processing CSV file: {str(e)}")
            return []

def main():
    # Configuration
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
    SEARCH_ENGINE_ID = os.getenv('GOOGLE_SEARCH_ENGINE_ID')
    
    # Check for required API keys
    if not GEMINI_API_KEY:
        print("Please set your GEMINI_API_KEY environment variable")
        print("You can get an API key from: https://makersuite.google.com/app/apikey")
        GEMINI_API_KEY = input("Enter your Gemini API key: ").strip()
    
    if not GOOGLE_API_KEY:
        print("\nPlease set your GOOGLE_API_KEY environment variable")
        print("You can get an API key from: https://console.developers.google.com/")
        GOOGLE_API_KEY = input("Enter your Google API key: ").strip()
    
    if not SEARCH_ENGINE_ID:
        print("\nPlease set your GOOGLE_SEARCH_ENGINE_ID environment variable")
        print("You can create a custom search engine at: https://cse.google.com/")
        SEARCH_ENGINE_ID = input("Enter your Google Search Engine ID: ").strip()
    
    CSV_FILE = "18062025 - Парфюми  - Sheet1.csv"
    OUTPUT_FILE = "gemini_beauty_products_results_with_working_links.txt"
    DELAY_BETWEEN_REQUESTS = 2.0  # seconds (increased for API limits)
    
    # Initialize processor
    processor = GeminiCSVProcessor(GEMINI_API_KEY, GOOGLE_API_KEY, SEARCH_ENGINE_ID)
    
    # Process the CSV file (with resume capability)
    # Set START_FROM_PRODUCT to force start from a specific product number (set to None for auto-resume)
    START_FROM_PRODUCT = 748  # Change this number to start from a different product
    
    results = processor.process_csv(CSV_FILE, OUTPUT_FILE, DELAY_BETWEEN_REQUESTS, resume=True, start_from=START_FROM_PRODUCT)
    
    # Print summary
    successful = sum(1 for r in results if r['status'] == 'success')
    failed = len(results) - successful
    total_images = sum(len(r['images']) for r in results if r['status'] == 'success')
    total_videos = sum(1 for r in results if r['status'] == 'success' and r['video'])
    
    print(f"\nSUMMARY (Current Run):")
    print(f"Products processed in this run: {len(results)}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"Total working image links found: {total_images}")
    print(f"Total video links found: {total_videos}")
    
    # Show overall progress
    if os.path.exists(OUTPUT_FILE):
        last_processed = processor.get_last_processed_product(OUTPUT_FILE)
        df = pd.read_csv(CSV_FILE)
        total_products = len(df.iloc[:, 5].dropna())
        print(f"\nOVERALL PROGRESS:")
        print(f"Total products processed so far: {last_processed}/{total_products}")
        print(f"Progress: {(last_processed/total_products)*100:.1f}%")
        if last_processed < total_products:
            print(f"Remaining products: {total_products - last_processed}")
        else:
            print("🎉 All products have been processed!")

if __name__ == "__main__":
    main() 