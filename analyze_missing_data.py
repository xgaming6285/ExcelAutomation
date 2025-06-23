import pandas as pd

# Read the CSV file
df = pd.read_csv('18062025 - Парфюми  - Sheet1 (1).csv')

print(f'Total records: {len(df)}')
print('\nMissing data analysis:')

# Define the content columns we need to check
content_cols = [
    'Image 1', 'Image 2', 'Image 3', 'Image 4', 'Image 5', 'Video',
    '1. Captivating Headline or Tagline',
    '2. Sensory Introduction (1–2 sentences)',
    '3. Key Features or Ingredients (Bullet Points or Icons)',
    '4. How to Use (Optional but useful)',
    '5. Emotional or Lifestyle Hook',
    '6. Tech Specs or Product Facts'
]

missing_data = {}

for col in content_cols:
    if col in df.columns:
        # Count missing (NaN) and empty string values
        missing = df[col].isna().sum() + (df[col] == '').sum()
        missing_data[col] = missing
        percentage = (missing / len(df)) * 100
        print(f'{col}: {missing} missing out of {len(df)} ({percentage:.1f}%)')
    else:
        print(f'{col}: Column not found')

print(f'\nTotal missing content fields: {sum(missing_data.values())}')

# Find records that have missing content
records_with_missing = 0
for index, row in df.iterrows():
    has_missing = False
    for col in content_cols:
        if col in df.columns:
            if pd.isna(row[col]) or row[col] == '':
                has_missing = True
                break
    if has_missing:
        records_with_missing += 1

print(f'Records with at least one missing content field: {records_with_missing} out of {len(df)} ({(records_with_missing/len(df)*100):.1f}%)') 