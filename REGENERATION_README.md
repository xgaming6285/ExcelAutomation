# Product List Regeneration Script

This script allows you to regenerate product descriptions, images, and videos for a specific list of 226 beauty and perfume products using the Gemini AI API and Google Search APIs.

## Features

- **Automated Processing**: Processes all 226 products automatically
- **Bulgarian Descriptions**: Generates detailed product descriptions in Bulgarian language
- **Image Search**: Finds and validates working image URLs for each product
- **Video Search**: Searches for relevant YouTube videos for each product
- **Progress Tracking**: Shows real-time progress and saves results incrementally
- **Error Handling**: Continues processing even if individual products fail
- **Resumable**: Can be interrupted and resumed (partial results are saved)

## Product List

The script processes the following 226 products:

1. **Fragrances**: Lalique, Montblanc, Trussardi, Davidoff, Dsquared2, Jimmy Choo, Boucheron, Coach, Rochas, Cacharel, Diesel, Lanvin, Armaf, Azzaro, Issey Miyake, Moschino, Zadig & Voltaire, Burberry, Estee Lauder, Elie Saab, Karl Lagerfeld, Versace, Lacoste, Philipp Plein, CK, Michael Kors, DKNY, Escada, Paco Rabanne, Narciso Rodriguez, Jo Malone, Xerjoff, Maison Crivelli, Creed, Bond No. 9, Byredo, Dior, Kilian, Frederic Malle, Initio, Parfums de Marly, Clive Christian

2. **Cosmetics & Skincare**: Clinique, Shiseido, Dr. Hauschka, Nars, Biotherm, Carolina Herrera, Lancome, Kenzo, Sisley

## Prerequisites

### Required API Keys

1. **Gemini API Key**: Get from [Google AI Studio](https://aistudio.google.com/)
2. **Google API Key**: Get from [Google Cloud Console](https://console.cloud.google.com/)
3. **Google Custom Search Engine ID**: Create at [Google Custom Search](https://cse.google.com/)

### Python Dependencies

Install the required packages:

```bash
pip install -r requirements.txt
```

The script requires:
- `google-generativeai` (Gemini API)
- `google-api-python-client` (Google Search APIs)
- `pandas` (Data processing)
- `requests` (HTTP requests)

## Setup Instructions

### 1. API Keys Setup

You can provide API keys in two ways:

#### Option A: Environment Variables (Recommended)
```bash
# Windows
set GEMINI_API_KEY=your_gemini_api_key_here
set GOOGLE_API_KEY=your_google_api_key_here
set SEARCH_ENGINE_ID=your_search_engine_id_here

# Linux/Mac
export GEMINI_API_KEY=your_gemini_api_key_here
export GOOGLE_API_KEY=your_google_api_key_here
export SEARCH_ENGINE_ID=your_search_engine_id_here
```

#### Option B: Interactive Input
The script will prompt you for API keys if they're not found in environment variables.

### 2. Google Custom Search Engine Setup

1. Go to [Google Custom Search](https://cse.google.com/)
2. Create a new search engine
3. Set it to search the entire web
4. Enable Image search in the settings
5. Copy the Search Engine ID

## Usage

### Method 1: Simple Runner (Recommended)

```bash
python run_regeneration.py
```

This interactive script will:
1. Check for API keys (prompt if missing)
2. Ask for processing options (delay, output file)
3. Confirm before starting
4. Run the regeneration process

### Method 2: Direct Script

```bash
python regenerate_products.py
```

This requires API keys to be set as environment variables.

### Method 3: Programmatic Usage

```python
from regenerate_products import ProductListRegenerator

# Initialize with API keys
regenerator = ProductListRegenerator(
    gemini_api_key="your_gemini_key",
    google_api_key="your_google_key", 
    search_engine_id="your_search_engine_id"
)

# Process the product list
results = regenerator.process_product_list(
    output_file="my_results.txt",
    delay=2.0
)
```

## Configuration Options

- **Delay**: Time to wait between API requests (default: 2.0 seconds)
- **Output File**: Custom filename for results (auto-generated if not specified)

## Output Format

The script generates a comprehensive text file with:

### For Each Product:
```
PRODUCT X: Product Name
Status: success/error
Timestamp: 2025-01-XX XX:XX:XX

DESCRIPTION:
[Bulgarian product description with 6 structured sections]

WORKING IMAGE LINKS:
Image 1: https://...
Image 2: https://...
[up to 5 images per product]

VIDEO LINK:
Video: https://youtube.com/watch?v=...

============================================================
```

### Summary Section:
- Total products processed
- Success/failure counts
- Total images and videos found
- Processing completion time

## Product Description Structure

Each product gets a detailed Bulgarian description with:

1. **Captivating Headline** - Poetic tagline
2. **Sensory Introduction** - Experience description
3. **Key Features** - 4-6 bullet points of features
4. **How to Use** - Step-by-step instructions
5. **Emotional Hook** - Lifestyle/identity connection
6. **Tech Specs** - Size, longevity, origin details

## Monitoring Progress

The script provides real-time feedback:
- Current product being processed
- Success/error status for each product
- Image and video search results
- Processing delays and timing
- Final summary statistics

## Error Handling

- **Individual Product Errors**: Script continues with next product
- **API Rate Limits**: Built-in delays prevent rate limiting
- **Network Issues**: Automatic retries for failed requests
- **Invalid URLs**: Image URL validation before saving
- **Interruption**: Partial results are saved if stopped

## Resuming Processing

If the script is interrupted:
1. Check the output file for the last processed product
2. Modify the script to start from that point, or
3. Use the existing results and process remaining products separately

## Performance Expectations

- **Processing Time**: ~15-20 minutes for all 226 products (with 2s delay)
- **Success Rate**: Typically 85-95% depending on API availability
- **Images per Product**: 0-5 working URLs (average 2-3)
- **Videos per Product**: 0-1 YouTube video (average 60-70%)

## Troubleshooting

### Common Issues:

1. **API Key Errors**
   - Verify all three API keys are correct
   - Check API quotas and billing in Google Cloud Console

2. **No Images Found**
   - Normal for some niche products
   - Google Custom Search may have limited results

3. **Rate Limiting**
   - Increase delay between requests
   - Check API quotas

4. **Import Errors**
   - Ensure all dependencies are installed
   - Check that `gemini_csv_processor.py` exists

## File Structure

```
ExcelAutomation/
├── regenerate_products.py      # Main regeneration script
├── run_regeneration.py         # Interactive runner
├── gemini_csv_processor.py     # Required dependency
├── requirements.txt            # Python dependencies
└── REGENERATION_README.md      # This file
```

## Output Files

- `regenerated_products_results_YYYYMMDD_HHMMSS.txt` - Main results file
- Console output with real-time progress

## Next Steps

After regeneration, you can:
1. Review the generated descriptions and media links
2. Use `update_csv_with_links.py` to update your CSV file
3. Process additional products by modifying the product list
4. Integrate results into your e-commerce platform

## Support

For issues or questions:
1. Check the console output for specific error messages
2. Verify API keys and quotas
3. Review the generated output file for partial results
4. Ensure all dependencies are properly installed

---

**Note**: This script processes a large number of products and makes many API calls. Monitor your API usage and costs, especially for Google Search API which has per-request charges. 