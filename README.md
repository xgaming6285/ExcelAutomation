# Gemini CSV Beauty Products Processor with Working Image Links

This Python script processes a CSV file containing beauty product information and uses Google's Gemini AI to generate detailed product descriptions, plus **Google Custom Search API** to find actual working image and video links for each product.

## 🆕 New Features

- **Actual Working Image Links**: Uses Google Custom Search API to find real, accessible image URLs
- **YouTube Video Search**: Uses YouTube Data API to find relevant product videos
- **Link Validation**: Validates all URLs to ensure they actually work before adding to CSV
- **Direct CSV Update**: Automatically updates your CSV file with working links
- **Bulgarian Descriptions**: Generates product descriptions in Bulgarian language

## Features

- Reads CSV file and extracts product names from column F (Line)
- Sends each product to Google Gemini AI for detailed descriptions in Bulgarian
- **Searches for actual working image URLs** using Google Custom Search API
- **Finds relevant YouTube videos** using YouTube Data API
- **Validates all links** to ensure they're accessible
- **Updates CSV file directly** with working links in the appropriate columns
- Includes error handling and rate limiting for all APIs
- Creates backup of original CSV file

## Setup

⚠️ **Important**: This new version requires additional API keys for Google Search functionality.

See the detailed [Setup Guide](setup_guide.md) for complete instructions.

### Quick Setup Summary

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Get Required API Keys:**
   - Gemini API Key (for descriptions)
   - Google API Key (for search)
   - Google Custom Search Engine ID (for image search)

3. **Set Environment Variables:**
   ```bash
   # Windows PowerShell
   $env:GEMINI_API_KEY="your_gemini_key"
   $env:GOOGLE_API_KEY="your_google_key"
   $env:GOOGLE_SEARCH_ENGINE_ID="your_search_engine_id"
   ```

## Usage

### Step 1: Generate Descriptions and Find Working Links

```bash
python gemini_csv_processor.py
```

This will:
- Generate Bulgarian product descriptions using Gemini AI
- Search for working image URLs (up to 5 per product)
- Find relevant YouTube videos
- Validate all links to ensure they work
- Save results to `gemini_beauty_products_results_with_working_links.txt`

### Step 2: Update CSV with Working Links

```bash
python update_csv_with_links.py
```

This will:
- Parse the results file
- Update your CSV file with working links
- Add images to columns O, P, Q, R (up to 4 images)
- Add video links to column T
- Create a backup of your original CSV
- Validate all links in the updated CSV

## What's Different from the Old Version

| Old Version | New Version |
|-------------|-------------|
| Generated fake/placeholder links | **Finds actual working image URLs** |
| No link validation | **Validates every link before adding** |
| Manual CSV updating | **Automatically updates CSV file** |
| English descriptions | **Bulgarian descriptions** |
| Only Gemini API | **Uses 3 APIs: Gemini + Google Search + YouTube** |

## Output

### Text File Output
The script generates a comprehensive text file with:
- Bulgarian product descriptions
- **Actual working image URLs** (validated)
- **Working YouTube video links**
- Status information for each product

### CSV File Updates
Your original CSV file will be updated with:
- **Column O**: Image 1 URL
- **Column P**: Image 2 URL  
- **Column Q**: Image 3 URL
- **Column R**: Image 4 URL
- **Column T**: YouTube video URL

## API Usage and Limits

- **Google Custom Search API**: 100 searches/day (free tier)
- **YouTube Data API**: 10,000 units/day (free tier)
- **Gemini API**: Varies by plan

The script includes appropriate delays to respect rate limits.

## Example Results

After running both scripts, you'll have:

```
✅ Working image links like:
https://images.unsplash.com/photo-1234567890/perfume-bottle.jpg
https://cdn.shopify.com/s/files/1/product-image.jpg

✅ Working YouTube videos like:
https://www.youtube.com/watch?v=abc123def456

✅ Bulgarian product descriptions
✅ All links validated and working
✅ CSV file automatically updated
✅ Original CSV backed up safely
```

## Troubleshooting

### No Images Found
- This is normal for some products
- The script will find images where available
- Check your Custom Search Engine settings

### API Errors
- Ensure all APIs are enabled in Google Cloud Console
- Check your API keys are correct
- Verify your Search Engine ID is valid

### Rate Limits
- The script includes delays to avoid limits
- If you hit limits, wait 24 hours for quota reset
- Consider upgrading to paid tiers for higher limits

## Files

- `gemini_csv_processor.py` - Main script for generating descriptions and finding links
- `update_csv_with_links.py` - Updates CSV with working links
- `setup_guide.md` - Detailed setup instructions
- `requirements.txt` - Python dependencies

## Support

For detailed setup instructions, see [setup_guide.md](setup_guide.md).

The new version provides **actual working links** instead of placeholder URLs, making your product database much more valuable and usable. 