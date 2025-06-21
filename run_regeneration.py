#!/usr/bin/env python3
"""
Simple runner script for product list regeneration.
This script makes it easy to run the regeneration process.
"""

import os
import sys
from regenerate_products import ProductListRegenerator

def main():
    """Main function to run the product list regeneration"""
    
    print("=" * 60)
    print("PRODUCT LIST REGENERATION SCRIPT")
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
            sys.exit(1)
    
    if not GOOGLE_API_KEY:
        print("GOOGLE_API_KEY not found in environment variables.")
        GOOGLE_API_KEY = input("Please enter your Google API key: ").strip()
        if not GOOGLE_API_KEY:
            print("ERROR: Google API key is required!")
            sys.exit(1)
    
    if not SEARCH_ENGINE_ID:
        print("SEARCH_ENGINE_ID not found in environment variables.")
        SEARCH_ENGINE_ID = input("Please enter your Google Custom Search Engine ID: ").strip()
        if not SEARCH_ENGINE_ID:
            print("ERROR: Search Engine ID is required!")
            sys.exit(1)
    
    print("✓ All API keys found!")
    print()
    
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
    
    output_file = input("Enter output filename (press Enter for auto-generated): ").strip()
    if not output_file:
        output_file = None
    
    print()
    print("=" * 60)
    print("STARTING REGENERATION PROCESS")
    print("=" * 60)
    print(f"Delay between requests: {delay} seconds")
    print(f"Output file: {'Auto-generated' if output_file is None else output_file}")
    print()
    
    # Confirm before starting
    confirm = input("Do you want to proceed? (y/N): ").strip().lower()
    if confirm not in ['y', 'yes']:
        print("Operation cancelled.")
        sys.exit(0)
    
    print()
    print("Starting regeneration process...")
    print("Press Ctrl+C to interrupt if needed.")
    print()
    
    try:
        # Create regenerator instance
        regenerator = ProductListRegenerator(GEMINI_API_KEY, GOOGLE_API_KEY, SEARCH_ENGINE_ID)
        
        # Process the product list
        results = regenerator.process_product_list(output_file=output_file, delay=delay)
        
        print()
        print("=" * 60)
        print("REGENERATION COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        
    except KeyboardInterrupt:
        print("\n" + "=" * 60)
        print("PROCESSING INTERRUPTED BY USER")
        print("=" * 60)
        print("Partial results may have been saved to the output file.")
        
    except Exception as e:
        print(f"\n" + "=" * 60)
        print("ERROR DURING PROCESSING")
        print("=" * 60)
        print(f"Error: {e}")
        print("Please check your API keys and internet connection.")
        sys.exit(1)

if __name__ == "__main__":
    main() 