#!/usr/bin/env python3
"""
Product List Regeneration Script
This script processes a specific list of beauty/perfume products through the Gemini API
to generate descriptions, search for images and videos, and create output files.
"""

import pandas as pd
import google.generativeai as genai
import time
import os
import requests
import json
import re
from typing import List, Dict, Optional
from googleapiclient.discovery import build
from datetime import datetime

# Import the existing classes
from gemini_csv_processor import GeminiCSVProcessor

class ProductListRegenerator:
    def __init__(self, gemini_api_key: str, google_api_key: str, search_engine_id: str):
        """Initialize the product list regenerator"""
        self.processor = GeminiCSVProcessor(gemini_api_key, google_api_key, search_engine_id)
        
    def get_product_list(self) -> List[str]:
        """Return the specific product list to regenerate"""
        return [
            "Lalique Satine (L) EDP 100ml",
            "Montblanc Signature (L) EDP 30ml",
            "Trussardi (L) EDP 30ml",
            "Trussardi Ruby Red (L) EDP 30ml",
            "Davidoff Cool Water (M) EDT 125ml",
            "Dsquared2 Wood For Him (M) EDT 100ml Tester",
            "Montblanc Legend Blue (M) EDP 30ml",
            "Shiseido Clarifyng Cleansing Foam 125ml",
            "Clinique Happy (L) EDP 100ml",
            "Boucheron Boucheron (L) EDP 100ml Tester",
            "Coach Blue Men (M) EDT 100ml Tester",
            "Coach Man (M) EDT 100ml Tester",
            "Coach Wild Rose (L) EDP 90ml Tester",
            "Rochas Eau De Rochas (L) EDT 100ml Tester",
            "Clinique Superbalanced Makeup CN90 Sand 30ml",
            "Dr. Hauschka Soothing Mask 30ml",
            "Nars Radiant Creamy Concealer - Biscuit MD1 6ml",
            "Nars Radiant Creamy Concealer - Caramel MD2 6ml",
            "Nars Radiant Creamy Concealer - Ginger M2 6ml",
            "Jimmy Choo Rose Passion EDP 100ml Tester",
            "Boucheron Quatre (M) EDT 100ml Tester",
            "Boucheron Singulier (M) EDP 50ml",
            "Cacharel Anais Anais L Original (L) EDT 50ml",
            "Diesel Fuel For Life (M) EDT 125ml Tester",
            "Lanvin Eclat D Arpege (L) EDP 100ml Tester",
            "Clinique Clarifying Lotion 2 - Dry To Combination 400ml",
            "Clinique Dramatically Different Moisturizing Gel 125ml",
            "Armaf Club De Nuit Intense Man (M) EDT 105ml",
            "Boucheron Quatre (L) EDP 50ml",
            "Azzaro Chrome Legend (M) EDT 100ml",
            "Dsquared2 Green Wood (M) EDT 50ml",
            "Azzaro Pour Homme (M) EDT 100ml Tester",
            "Boucheron Jaipur (M) EDP 100ml Tester",
            "Coach Coach (L) EDT 90ml Tester",
            "Dsquared2 2 Wood (U) EDT 100ml Tester",
            "Issey Miyake L Eau D Issey Vetiver (M) EDT 50ml",
            "Jimmy Choo I Want Choo Forever (L) EDP 40ml",
            "Montblanc Legend (M) EDT 100ml Tester",
            "Moschino Pink Fresh Couture (L) EDT 100ml Tester",
            "Rochas Byzance (L) EDP 60ml",
            "Zadig & Voltaire This Is Him (M) EDT 30ml",
            "Clinique Superbalanced Makeup CN62 Porcelain Beige 30ml",
            "Armaf Club De Nuit Milestone (U) EDP 105ml",
            "Jimmy Choo I Want Choo (L) EDP 40ml",
            "Moschino Fresh Couture (L) EDT 100ml Tester",
            "Biotherm Aquasource Cream NC 50ml",
            "Armaf Club De Nuit Sillage (M) EDP 105ml",
            "Burberry Weekend (L) EDP 100ml Tester",
            "Cacharel Noa (L) EDT 100ml Tester",
            "Dsquared2 Wood For Him (M) EDT 100ml NC",
            "Estee Lauder Sensuous (L) EDP 50ml",
            "Moschino Gold Fresh Couture (L) EDP 100ml Tester",
            "Coach Dreams (L) EDP 90ml Tester",
            "Coach Floral (L) EDP 90ml Tester",
            "Dsquared2 Red Wood (L) EDT 100ml Tester",
            "Elie Saab Girl Of Now Forever (L) EDP 30ml",
            "Jimmy Choo (L) EDP 100ml Tester",
            "Michael Kors Wonderlust (L) EDP 50ml",
            "Dsquared2 Original Wood (M) EDP 100ml Tester NC",
            "Elie Saab Girl Of Now Lovely (L) EDP 30ml",
            "Karl Lagerfeld Ikonik (L) EDP 60ml",
            "Karl Lagerfeld Ikonik (M) EDP 60ml",
            "Montblanc Legend (M) EDP 50ml",
            "Versace Woman (L) EDP 100ml",
            "Clinique For Men Maximum Hydrator Activated Water-Gel Concentrate 48ml",
            "Boucheron Singulier (M) EDP 100ml Tester",
            "Elie Saab Girl Of Now Shine (L) EDP 30ml",
            "Cacharel Anais Anais L Original (L) EDT 100ml",
            "Elie Saab Le Parfum Lumiere (L) EDP 30ml",
            "Moschino Pink Fresh Couture (L) EDT 50ml",
            "Moschino Toy 2 (L) EDP 100ml Tester",
            "Lacoste Pour Femme (L) EDP 50ml",
            "Philipp Plein Fatale (L) EDP 50ml",
            "Philipp Plein No Limits Super Fresh (M) EDT 90ml",
            "CK Euphoria (M) EDT 100ml",
            "Elie Saab Le Parfum (L) EDP 30ml",
            "Michael Kors Gorgeous! (L) EDP 100ml Tester",
            "Michael Kors Wonderlust (L) EDP 100ml Tester",
            "DKNY Be Delicious Fresh Blossom (L) EDP 100ml",
            "Escada Especially (L) EDP 50ml",
            "Escada Magnetism (L) EDP 50ml",
            "Issey Miyake L Eau D issey (M) EDT 125ml T",
            "Jimmy Choo Man (M) EDT 100ml Tester",
            "Montblanc Legend Red (M) EDP 100ml",
            "Montblanc Signature Absolue (L) EDP 50ml",
            "Philipp Plein No Limits Gold (M) EDP 50ml",
            "Philipp Plein No Limits Platinum (M) EDP 50ml",
            "Ralph Lauren Polo Black (M) EDT 125ml Tester",
            "Rochas Eau De Rochas Homme (M) EDT 100ml",
            "Boucheron Quatre (M) EDT 100ml",
            "CK One (U) EDT 200ml",
            "Elie Saab Le Parfum In White (L) EDP 30ml",
            "Lanvin Eclat D Arpege (L) EDP 100ml",
            "Cacharel Noa (L) EDT 100ml",
            "Montblanc Explorer Platinum (M) EDP 60ml",
            "Montblanc Legend (M) EDP 100ml Tester",
            "Cacharel Amor Amor (L) EDT 100ml",
            "D&G Light Blue (M) EDT 40ml",
            "Montblanc Signature Absolue (L) EDP 90ml Tester",
            "Carolina Herrera Good Girl (L) Body Cream 200ml",
            "Dr. Hauschka Regenerating Body Cream 150ml",
            "Estee Lauder Double Wear Stay-In-Place Makeup SPF10 1N1 Ivory Nude 30ml",
            "Shiseido Men Total Revitalizer Eye Cream 15ml",
            "Lancome Teint Idole Ultra Wear 24H Foundation SPF35 400W 30ml",
            "Kenzo L Eau (L) EDT 50ml",
            "Cacharel Amor Amor (L) EDP 100ml Tester",
            "Coach Love (L) EDP 90ml Tester",
            "D&G Light Blue Eau Intense (L) EDP 25ml",
            "Estee Lauder Modern Muse (L) EDP 50ml",
            "Jimmy Choo (L) EDP 60ml",
            "Lacoste Eau De Lacoste L.12.12 Blanc (M) EDT 100ml Tester",
            "Versace Dylan Turquoise Pour Femme (L) EDT 100ml Tester",
            "Boss Hugo Man (M) EDT 125ml Tester",
            "Diesel D Red By Diesel (U) EDP 100ml Tester",
            "DKNY Be Delicious 100% Delicious (L) EDP 100ml",
            "Escada Especially (L) EDP 75ml",
            "Jimmy Choo Man Intense (M) EDT 100ml Tester",
            "Lancome Miracle (L) EDP 30ml",
            "Montblanc Explorer (M) EDP 60ml",
            "Montblanc Legend (M) EDT 100ml",
            "Paco Rabanne Pure XS (M) EDT 50ml",
            "Michael Kors Gorgeous! (L) EDP 50ml",
            "Versace Man Eau Fraiche (M) EDT 100ml Tester",
            "Dsquared2 Red Wood (L) EDT 100ml",
            "Jimmy Choo I Want Choo Le Parfum (L) Parfum 40ml",
            "Michael Kors Sexy Amber (L) EDP 100ml Tester",
            "Montblanc Legend Blue (M) EDP 50ml",
            "Paco Rabanne Ultrared (L) EDP 30ml",
            "Shiseido Body Firming Cream 200ml",
            "Michael Kors Gorgeous! (L) EDP 100ml",
            "Estee Lauder Double Wear Stay-In-Place Makeup SPF10 4C2 Auburn 30ml",
            "DKNY Be Delicious Be Tempted (L) EDP 100ml",
            "DKNY Be Delicious Be Tempted Blush (L) EDP 100ml",
            "Trussardi Ruby Red (L) EDP 60ml",
            "Versace Bright Crystal (L) EDT 90ml Tester",
            "Narciso Rodriguez For Her (L) BL 200ml",
            "Moschino Toy Boy (M) EDP 100ml Tester",
            "Estee Lauder Beautiful (L) EDP 75ml",
            "Boucheron Quatre Iconic (L) EDP 100ml",
            "Jo Malone Amber & Lavender Cologne 100ml",
            "Jo Malone Blackberry & Bay Cologne 100ml",
            "Xerjoff Accento EDP 100ml",
            "Xerjoff K Blue Holysm (U) Parfum 50ml Tester",
            "Maison Crivelli Neroli Nasimba (U) EDP 100ml",
            "Maison Crivelli Rose Saltifolia (U) EDP 100ml",
            "Creed Green Irish Tweed (M) EDP 100ml Tester",
            "Xerjoff Erba Gold EDP 100ml Tester",
            "Xerjoff Don EDP 100ml",
            "Versace Atelier Jasmin Au Soleil (U) EDP 100ml",
            "Xerjoff Soprano (U) EDP 100ml",
            "Creed Love In Black (L) EDP 75ml Tester",
            "Xerjoff 1861 Naxos (L) EDP 100ml",
            "Bond No. 9 Nolita (L) EDP 100ml",
            "Byredo Mojave Ghost (U) EDP 100ml Tester",
            "Xerjoff Ouverture (U) EDP 100ml",
            "Xerjoff Wardasina (U) EDP 100ml",
            "Bond No. 9 New York Flowers (U) EDP 100ml",
            "Creed Original Santal (U) EDP 100ml Tester",
            "Creed Royal Water (U) EDP 100ml Tester",
            "Xerjoff Erba Pura EDP 100ml",
            "Xerjoff K Blue Empiryan (U) Parfum 100ml Tester",
            "Xerjoff Opera EDP 100ml",
            "Xerjoff Oud Stars Luxor Parfum 50ml",
            "Xerjoff Oud Stars Zafar (U) Parfum 50ml",
            "Sisley All Day All Year Essential Anti-Aging Protection 50ml",
            "Xerjoff Ouverture (U) EDP 100ml",
            "Dior Miss Dior (L) EDP 150ml",
            "Kilian Old Fashioned (U) EDP 50ml Reffillable",
            "Xerjoff Laylati (U) EDP 100ml",
            "Dior Sauvage (M) EDP 200ml",
            "Creed Aventus For Her (L) EDP 75ml Tester",
            "Creed Millesime Imperial (U) EDP 100ml Tester",
            "Dior Sauvage (M) Parfum 200ml",
            "Frederic Malle Promise (U) EDP 50ml",
            "Xerjoff K Blue Ether (U) Parfum 50ml Tester",
            "Xerjoff Oud Stars Alexandria Orientale (U) EDP 50ml",
            "Xerjoff More Than Words (L) EDP 100ml",
            "Xerjoff Join The Club 40 Knots EDP 100ml",
            "Frederic Malle French Lover (M) EDP 100ml Tester",
            "Frederic Malle Monsieur (M) EDP 100ml Tester",
            "Xerjoff K Blue Empiryan (U) Parfum 100ml",
            "Kilian Voulez Vous Coucher Avec Moi (U) EDP 50ml Refillable",
            "Dior Sauvage Elixir (M) EDP 100ml",
            "Kilian Playing With The Devil (L) EDP 50ml Refillable",
            "Dior J Adore L Or Essence De Parfum (L) EDP 80ml",
            "Xerjoff K Blue Ether (U) Parfum 50ml",
            "Xerjoff Oud Stars Alexandria II (U) Parfum 50ml",
            "Xerjoff Tony Iommi Monkey Special (U) EDP 100ml Tester",
            "Initio Blessed Baraka (U) EDP 90ml",
            "Initio Blessed Baraka (U) EDP 90ml",
            "Parfums de Marly Kalan (U) EDP 125ml",
            "Parfums de Marly Perseus (M) EDP 125ml",
            "Xerjoff Oud Java Blossom (U) Parfume Attar Oil 15ml",
            "Xerjoff Elle Anniversary Parfum 50ml Tester",
            "Initio High Frequency (U) EDP 90ml",
            "Initio High Frequency (U) EDP 90ml",
            "Initio Mystic Experience (U) EDP 90ml",
            "Initio Psychedelic Love (U) EDP 90ml",
            "Parfums de Marly Palatine (L) EDP 75ml",
            "Initio Rehab (U) Extrait De Parfum 90ml",
            "Jo Malone Gardenia & Oud Cologne 100ml",
            "Jo Malone Rose & White Musk Cologne 100ml",
            "Jo Malone Violet & Amber Cologne 100ml",
            "Frederic Malle Carnal Flower (U) EDP 100ml",
            "Xerjoff Shooting Stars Red Hoba (U) Parfum 100ml Tester",
            "Xerjoff XXY (U) Parfum 50ml",
            "Frederic Malle Vetiver Extraordinaire (M) EDP 100ml",
            "Frederic Malle Musc Revageur (U) EDP 100ml",
            "Xerjoff Damarose (L) Parfum 50ml",
            "Xerjoff Homme (M) Parfum 50ml",
            "Xerjoff Oud Stars Alexandria II (U) Parfum 100ml Tester",
            "Xerjoff Symphonium (U) Parfum 50ml",
            "Initio Black Gold Oud For Greatness (U) EDP 90ml",
            "Creed Green Irish Tweed (M) EDP 100ml",
            "Creed Sier Mountain Water (U) EDT 100ml",
            "Xerjoff Elle (L) Parfum 50ml",
            "Frederic Malle Iris Poudre (U) EDP 100ml",
            "Xerjoff Shooting Stars Blue Hope (U) Parfum 100ml",
            "Xerjoff Tony Iommi Monkey Special (U) EDP 100ml",
            "Kilian A Kiss From A Rose (L) EDP 50ml",
            "Kilian Good Girl Gone Bad (L) Set EDP 50ml Refillable + Clutch",
            "Xerjoff Shooting Stars Red Hoba (U) Parfum 100ml",
            "Xerjoff Elle (L) Parfum 100ml Tester",
            "Frederic Malle Portrait Of A Lady (L) EDP 100ml",
            "Xerjoff Damarose (L) Parfum 100ml Tester",
            "Clive Christian Original Collection - No 1 Masculine EDP 50ml Tester",
            "Xerjoff Oud Stars Ceylon Parfum 50ml",
            "Xerjoff Oud Stars Alexandria II (U) Parfum 100ml",
            "Bond No. 9 Chelsea Nights Limited Edition (U) EDP 100ml",
            "Xerjoff Irisss (L) Parfum 100ml Tester",
            "Kilian Good Girl Gone Bad (L) EDP 100ml",
            "Creed Centaurus (L) EDP 100ml Tester",
            "Xerjoff Symphonium (U) Parfum 100ml Tester",
            "Xerjoff XXY (U) Parfum 100ml Tester",
            "Xerjoff Homme (M) Parfum 100ml",
            "Xerjoff Irisss (L) Parfum 100ml",
            "Xerjoff Elle (L) Parfum 100ml",
            "Xerjoff Oud Stars Alexandria II Anniversary (U) Parfum 100ml"
        ]
    
    def process_product_list(self, output_file: str = None, delay: float = 2.0) -> List[Dict]:
        """Process the specific product list"""
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f'regenerated_products_results_{timestamp}.txt'
        
        products = self.get_product_list()
        results = []
        
        print(f"Starting to process {len(products)} products...")
        print(f"Output file: {output_file}")
        print("=" * 60)
        
        # Clear the output file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"PRODUCT LIST REGENERATION RESULTS\n")
            f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total products: {len(products)}\n")
            f.write("=" * 60 + "\n\n")
        
        for i, product in enumerate(products, 1):
            print(f"\nProcessing {i}/{len(products)}: {product}")
            
            try:
                # Process the product
                result = self.processor.process_product(product)
                results.append(result)
                
                # Write result to file immediately
                self.write_result_to_file(output_file, i, result)
                
                # Status update
                if result['status'] == 'success':
                    image_count = len(result['images'])
                    video_status = "✓" if result['video'] else "✗"
                    print(f"✓ Success - {image_count} images, video: {video_status}")
                else:
                    print(f"✗ Error: {result['description']}")
                
                # Add delay between requests
                if i < len(products):  # Don't delay after the last product
                    print(f"Waiting {delay} seconds...")
                    time.sleep(delay)
                    
            except Exception as e:
                error_result = {
                    'product': product,
                    'description': f"Processing error: {str(e)}",
                    'images': [],
                    'video': None,
                    'status': 'error'
                }
                results.append(error_result)
                self.write_result_to_file(output_file, i, error_result)
                print(f"✗ Processing error: {str(e)}")
        
        # Write summary
        self.write_summary_to_file(output_file, results)
        
        print("\n" + "=" * 60)
        print(f"Processing complete! Results saved to: {output_file}")
        self.print_summary(results)
        
        return results
    
    def write_result_to_file(self, output_file: str, product_number: int, result: Dict):
        """Write a single result to the output file"""
        with open(output_file, 'a', encoding='utf-8') as f:
            f.write(f"PRODUCT {product_number}: {result['product']}\n")
            f.write(f"Status: {result['status']}\n")
            f.write(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            if result['status'] == 'success':
                # Write description
                f.write("DESCRIPTION:\n")
                f.write(result['description'])
                f.write("\n\n")
                
                # Write image links
                f.write("WORKING IMAGE LINKS:\n")
                if result['images']:
                    for i, img_url in enumerate(result['images'], 1):
                        f.write(f"Image {i}: {img_url}\n")
                else:
                    f.write("No working image links found.\n")
                f.write("\n")
                
                # Write video link
                f.write("VIDEO LINK:\n")
                if result['video']:
                    f.write(f"Video: {result['video']}\n")
                else:
                    f.write("No video link found.\n")
                f.write("\n")
            else:
                f.write(f"ERROR: {result['description']}\n\n")
            
            f.write("=" * 60 + "\n\n")
    
    def write_summary_to_file(self, output_file: str, results: List[Dict]):
        """Write processing summary to the output file"""
        successful = len([r for r in results if r['status'] == 'success'])
        failed = len([r for r in results if r['status'] == 'error'])
        total_images = sum(len(r['images']) for r in results if r['status'] == 'success')
        total_videos = len([r for r in results if r['status'] == 'success' and r['video']])
        
        with open(output_file, 'a', encoding='utf-8') as f:
            f.write("\n" + "=" * 60 + "\n")
            f.write("PROCESSING SUMMARY\n")
            f.write("=" * 60 + "\n")
            f.write(f"Total products processed: {len(results)}\n")
            f.write(f"Successful: {successful}\n")
            f.write(f"Failed: {failed}\n")
            f.write(f"Total images found: {total_images}\n")
            f.write(f"Total videos found: {total_videos}\n")
            f.write(f"Processing completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    def print_summary(self, results: List[Dict]):
        """Print processing summary to console"""
        successful = len([r for r in results if r['status'] == 'success'])
        failed = len([r for r in results if r['status'] == 'error'])
        total_images = sum(len(r['images']) for r in results if r['status'] == 'success')
        total_videos = len([r for r in results if r['status'] == 'success' and r['video']])
        
        print(f"Total products processed: {len(results)}")
        print(f"Successful: {successful}")
        print(f"Failed: {failed}")
        print(f"Total images found: {total_images}")
        print(f"Total videos found: {total_videos}")

def main():
    """Main function to run the product list regeneration"""
    # Configuration - you'll need to set these environment variables or modify the values
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
    SEARCH_ENGINE_ID = os.getenv('SEARCH_ENGINE_ID')
    
    if not all([GEMINI_API_KEY, GOOGLE_API_KEY, SEARCH_ENGINE_ID]):
        print("ERROR: Missing required API keys!")
        print("Please set the following environment variables:")
        print("- GEMINI_API_KEY")
        print("- GOOGLE_API_KEY")
        print("- SEARCH_ENGINE_ID")
        print("\nOr modify the script to include your API keys directly.")
        return
    
    # Create regenerator instance
    regenerator = ProductListRegenerator(GEMINI_API_KEY, GOOGLE_API_KEY, SEARCH_ENGINE_ID)
    
    # Process the product list
    try:
        results = regenerator.process_product_list(delay=2.0)
        
        print(f"\nRegeneration complete!")
        print(f"Check the output file for detailed results.")
        
    except KeyboardInterrupt:
        print("\nProcessing interrupted by user.")
    except Exception as e:
        print(f"Error during processing: {e}")

if __name__ == "__main__":
    main()