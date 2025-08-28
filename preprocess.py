import pandas as pd
import numpy as np
import string
from sentence_transformers import SentenceTransformer
import os
import re

print("Starting preprocessing...")

# --- 1. Define Cleaning Functions ---
# A more suitable cleaning function
def better_clean_text(s):
    """
    Cleans text by converting to lowercase and removing special characters,
    but preserves spaces, numbers, and basic structure.
    """
    if not isinstance(s, str):
        return ""
    s = s.lower()  # Convert to lowercase
    s = re.sub(r'<[^>]+>', '', s) # Remove HTML tags often found in descriptions
    s = re.sub(r'[^a-z0-9\s,.-]', '', s) # Keep letters, numbers, and basic punctuation
    s = re.sub(r'\s+', ' ', s).strip() # Normalize whitespace
    return s

def clean_tags(tags_str):
    """Cleans and joins tags with spaces."""
    if not isinstance(tags_str, str):
        return ""
    # Assuming tags are comma-separated or in another delimiter
    # This turns "Action,RPG,Indie" into "action rpg indie"
    return " ".join(tag.strip() for tag in tags_str.split(',')).lower()

# --- 2. Load the Raw Data ---
try:
    # Use an absolute path to be safe
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(script_dir, 'data', 'updated_steam_games.csv')
    steam = pd.read_csv(csv_path)
    print("Successfully loaded raw CSV data.")
except FileNotFoundError:
    print(f"Error: Could not find the CSV file at {csv_path}")
    exit() # Exit the script if the data isn't there

# --- 3. Clean and Prepare the Text ---
print("Cleaning and preparing text data...")
steam = steam[steam['supported_languages'].str.contains("English")]
steam = steam[steam['num_reviews_total'] > 500]



steam['combined_text'] =  steam['detailed_description'].apply(better_clean_text) + ' ' + steam['tags'].apply(clean_tags)

# We only need to keep the essential columns for the API
api_data = steam[['appid', 'name', 'combined_text', 'header_image_url','store_page_url', 'tags']].copy()

# --- 4. Load Model and Generate Embeddings ---
print("Loading SentenceTransformer model (this may take a moment)...")
model = SentenceTransformer('all-MiniLM-L6-v2')

print("Generating embeddings for all games (this is the slow part)...")
# The .tolist() is important for performance
game_embeddings = model.encode(api_data['combined_text'].tolist(), show_progress_bar=True)

# --- 5. Save the Processed Data and Embeddings ---
# Define where to save the output files, inside the `api` folder
output_dir = os.path.join(script_dir, 'api', 'preprocessed_data')
os.makedirs(output_dir, exist_ok=True) # Create the directory if it doesn't exist

# Save the cleaned game data using a more efficient format like pickle
api_data.to_pickle(os.path.join(output_dir, 'games_data.pkl'))
print(f"Saved cleaned game data to {os.path.join(output_dir, 'games_data.pkl')}")

# Save the embeddings array as a NumPy file
np.save(os.path.join(output_dir, 'game_embeddings.npy'), game_embeddings)
print(f"Saved game embeddings to {os.path.join(output_dir, 'game_embeddings.npy')}")

print("\nPreprocessing complete! Your API is now ready to use the pre-calculated files.")