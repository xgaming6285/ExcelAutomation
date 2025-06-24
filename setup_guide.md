# Setup Guide for Working Image Links

This guide will help you set up the necessary API keys to get working image and video links for your beauty products.

## Required APIs

You need to set up 3 API keys:

1. **Gemini API Key** (for product descriptions)
2. **Google API Key** (for image search and YouTube search)
3. **Google Custom Search Engine ID** (for image search)

## Step 1: Get Gemini API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the API key and save it

## Step 2: Get Google API Key

1. Go to [Google Cloud Console](https://console.developers.google.com/)
2. Sign in with your Google account
3. Create a new project or select an existing one
4. Enable the following APIs:
   - **Custom Search API**
   - **YouTube Data API v3**

### To enable APIs:
1. In the Google Cloud Console, go to "APIs & Services" > "Library"
2. Search for "Custom Search API" and click "Enable"
3. Search for "YouTube Data API v3" and click "Enable"

### To create API key:
1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "API Key"
3. Copy the API key and save it

## Step 3: Create Google Custom Search Engine

1. Go to [Google Custom Search Engine](https://cse.google.com/)
2. Click "Add" or "Create a custom search engine"
3. In "Sites to search", enter: `*` (asterisk to search the entire web)
4. Give your search engine a name (e.g., "Beauty Products Image Search")
5. Click "Create"
6. After creation, click on your search engine
7. Go to "Setup" > "Basics"
8. Turn ON "Image search"
9. Turn ON "SafeSearch"
10. Copy the "Search engine ID" and save it

## Step 4: Set Environment Variables

### On Windows (PowerShell):
```powershell
$env:GEMINI_API_KEY="AIzaSyBU9EkPhk4mOv80HpGJ78AyrZAPLuP4CdI"
$env:GOOGLE_API_KEY="AIzaSyBy-o2B6GUV_lZ7CerEpjy40E1CtGl0RUs"
$env:GOOGLE_SEARCH_ENGINE_ID="525190855bed547cc"
```

### On Windows (Command Prompt):
```cmd
set GEMINI_API_KEY=your_gemini_api_key_here
set GOOGLE_API_KEY=your_google_api_key_here
set GOOGLE_SEARCH_ENGINE_ID=your_search_engine_id_here
```

### On Linux/Mac:
```bash
export GEMINI_API_KEY="your_gemini_api_key_here"
export GOOGLE_API_KEY="your_google_api_key_here"
export GOOGLE_SEARCH_ENGINE_ID="your_search_engine_id_here"
```

## Step 5: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 6: Run the Scripts

1. **Generate descriptions and find working links:**
   ```bash
   python gemini_csv_processor.py
   ```

2. **Update your CSV with the working links:**
   ```bash
   python update_csv_with_links.py
   ```

## API Usage Limits

Be aware of the following daily limits:

- **Google Custom Search API**: 100 queries per day (free tier)
- **YouTube Data API**: 10,000 units per day (free tier)
- **Gemini API**: Varies by plan

If you need more searches, you may need to upgrade to a paid plan.

## Troubleshooting

### "API key not valid" error:
- Make sure you've enabled the correct APIs in Google Cloud Console
- Check that your API key is correct
- Ensure there are no extra spaces in your environment variables

### "Search engine ID not found" error:
- Verify your Custom Search Engine ID is correct
- Make sure image search is enabled in your CSE settings

### "No images found" errors:
- This is normal for some products - not all products will have available images
- The script will find working links where possible

### Rate limiting errors:
- The script includes delays between requests to avoid rate limits
- If you hit limits, wait 24 hours for the quota to reset

## Expected Results

After running both scripts, your CSV file will be updated with:
- Working image URLs in columns O, P, Q, R (up to 4 images per product)
- Working YouTube video URLs in column T
- All links are validated to ensure they actually work

The script will also create a backup of your original CSV file before making changes. 