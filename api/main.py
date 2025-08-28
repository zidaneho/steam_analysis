# main.py

import os
import string
import asyncio
import aiohttp
import pandas as pd
import numpy as np
import io
import google.generativeai as genai
from fastapi import FastAPI
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import urllib.parse

load_dotenv(override=True)  # Load environment variables from .env file

# --------------------------------------------------------------------------
#  1. FastAPI App Initialization & CORS Configuration
# --------------------------------------------------------------------------

app = FastAPI()

origins = [
    "http://0.0.0.0",  # Your Next.js frontend
    "http://127.0.0.1:3000", # Also good to include this
    "http://localhost:3000",
    # Add your Vercel deployment URL here when you deploy
    "https://steam-analysis.vercel.app/" ,
    "https://steam-analysis-frontend.onrender.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Use the specific list of origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------------------------------------------------------
#  2. Global Variables & Startup Data Loading
# --------------------------------------------------------------------------

steam_data = None
game_embeddings = None
model = None
vectorizer = TfidfVectorizer()
unique_tags_list = []
tag_embeddings_tfidf = None

# IMPORTANT: Replace these with the actual public URLs where you host your data files.
# You can use services like AWS S3, Google Cloud Storage, or others.
GAMES_DATA_URL = "https://github.com/zidaneho/steam_analysis/releases/download/v1.0.0/games_data.pkl"
GAME_EMBEDDINGS_URL = "https://github.com/zidaneho/steam_analysis/releases/download/v1.0.0/game_embeddings.npy"

@app.on_event("startup")
async def load_preprocessed_data():
    global steam_data, game_embeddings, model, unique_tags_list, tag_embeddings_tfidf, vectorizer
    print("API starting up: Loading models and pre-processed data...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    try:
        async with aiohttp.ClientSession() as session:
            # Fetch and load games_data.pkl
            print(f"Fetching games data from {GAMES_DATA_URL}...")
            async with session.get(GAMES_DATA_URL) as response:
                response.raise_for_status()
                steam_data = pd.read_pickle(io.BytesIO(await response.read()))
            print("✅ Successfully loaded games_data.pkl.")

            # Fetch and load game_embeddings.npy
            print(f"Fetching game embeddings from {GAME_EMBEDDINGS_URL}...")
            async with session.get(GAME_EMBEDDINGS_URL) as response:
                response.raise_for_status()
                # Save to a temporary in-memory buffer to be loaded by numpy
                game_embeddings = np.load(io.BytesIO(await response.read()))
            print("✅ Successfully loaded game_embeddings.npy.")

        all_tags = set(steam_data['tags'].str.cat(sep=' ').split())
        unique_tags_list = list(all_tags)
        tag_embeddings_tfidf = vectorizer.fit_transform(unique_tags_list)
        print("✅ Successfully initialized models and data.")
        
    except Exception as e:
        print(f"❌ FATAL ERROR: Could not load pre-processed data. Error: {e}")
        steam_data = None

# --------------------------------------------------------------------------
#  3. Pydantic Data Models
# --------------------------------------------------------------------------

class Prompt(BaseModel):
    description: str

class Game(BaseModel):
    id: int
    name: str
    score: float
    header_image_url: str
    store_page_url: str

class Tag(BaseModel):
    name: str
    score: float

class Review(BaseModel):
    id : str
    name: str
    review_text: str
    recommended: bool
    

class ReviewSummary(BaseModel):
    challenges: str
    likes: str

class AnalysisResult(BaseModel):
    unique_score: float
    similar_games: list[Game]
    predicted_tags: list[Tag]
    reviews: list[Review]
    review_summary: ReviewSummary

# --------------------------------------------------------------------------
#  4. Helper Functions & Review Fetching
# --------------------------------------------------------------------------

def clean_text(s: str) -> str:
    new_str = s.lower().translate(str.maketrans('', '', string.punctuation + string.digits))
    return new_str.strip()

async def fetch_reviews_for_app(session, app_id: int, name: str, max_reviews: int = 100) -> list:
    """
    Fetches unique reviews for a given app_id, handling pagination correctly.
    """
    reviews_list = []
    seen_ids = set() # ✅ FIX 1: Add a set to track seen review IDs.
    cursor = "*"
    
    while len(reviews_list) < max_reviews:
        encoded_cursor = urllib.parse.quote(cursor)
        
        # ✅ FIX 2: Change filter from "all" to "recent" for stable pagination.
        url = (f"https://store.steampowered.com/appreviews/{app_id}?json=1"
               f"&filter=recent" 
               f"&language=english"
               f"&num_per_page=100"
               f"&cursor={encoded_cursor}")

        try:
            async with session.get(url) as response:
                response.raise_for_status()
                data = await response.json()

                if data.get("success") != 1 or not data.get("reviews"):
                    break 

                new_reviews_found = False
                for review_data in data["reviews"]:
                    review_id = review_data.get("recommendationid")

                    # ✅ FIX 1 (continued): Only add the review if we haven't seen its ID before.
                    if review_id and review_id not in seen_ids:
                        seen_ids.add(review_id)
                        reviews_list.append({
                            "id": review_id,
                            "name": name,
                            "review_text": review_data.get("review", ""),
                            "recommended": review_data.get("voted_up", False)
                        })
                        new_reviews_found = True
                        
                        # Optional: You can remove this print or keep it for debugging
                        # print(f"Fetched unique review for {name} (ID: {app_id}): {review_id}")

                # If the entire page was duplicates or empty, stop to prevent infinite loops.
                if not new_reviews_found:
                    break

                cursor = data.get("cursor")
                if not cursor:
                    break

        except Exception as e:
            print(f"Warning: Could not fetch reviews for {name} (ID: {app_id}). Error: {e}")
            break
            
    return reviews_list[:max_reviews]

async def fetch_all_reviews(apps_to_fetch: list) -> list:
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_reviews_for_app(session, app_id, name) for app_id, name in apps_to_fetch]
        results_list_of_lists = await asyncio.gather(*tasks)
        all_reviews = [review for sublist in results_list_of_lists for review in sublist]
        
        return all_reviews

# --------------------------------------------------------------------------
#  5. Gemini Review Summarization Function (CORRECTED)
# --------------------------------------------------------------------------

async def summarize_reviews_with_gemini(reviews: list) -> dict:
    # Use GOOGLE_API_KEY as the standard, but check for GEMINI_API_KEY for backward compatibility
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Warning: GOOGLE_API_KEY or GEMINI_API_KEY not found. Skipping review summarization.")
        return {"challenges": "API key not configured.", "likes": "API key not configured."}
    genai.configure(api_key=api_key)

    review_texts = ""
    for review in reviews:
        sentiment = "Positive" if review["recommended"] else "Negative"
        review_texts += f"- ({sentiment} review for game '{review['name']}'): {review['review_text']}\n"
    
    if not review_texts:
         return {"challenges": "No reviews were found to summarize.", "likes": "No reviews were found to summarize."}

    prompt = f"""
    You are a video game market analyst. Analyze the following player reviews for a set of similar games.
    Based *only* on the text provided, identify the common themes.

    Reviews:
    {review_texts}

    ---

    Provide your analysis in two distinct categories:
    1.  **Common Challenges & Criticisms:** What are the recurring problems, frustrations, or negative feedback points players mention? (e.g., bugs, repetitive gameplay, poor controls). Do not be specific on one game.
    2.  **Common Likes & Praises:** What are the recurring positive aspects that players enjoy? (e.g., great story, fun mechanics, beautiful art style). Do not be specific on one game.

    Present your summary as two bulleted lists. Do not add any extra commentary or introduction.
    """

    try:
        # 1. Initialize the correct model
        # Using gemini-1.5-flash as it's a valid and fast model for this task.
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # 2. Use the correct async method: generate_content_async
        response = await model.generate_content_async(prompt)
        
        # 3. Parse the response text
        parts = response.text.split("Common Likes & Praises:")
        challenges_part = parts[0].replace("Common Challenges & Criticisms:", "").strip()
        likes_part = parts[1].strip() if len(parts) > 1 else "Could not parse summary."

        return {"challenges": challenges_part, "likes": likes_part}
        
    except Exception as e:
        print(f"Error during Gemini API call: {e}")
        return {"challenges": "An error occurred while summarizing.", "likes": "An error occurred while summarizing."}

# --------------------------------------------------------------------------
#  6. Main API Endpoint
# --------------------------------------------------------------------------

@app.post("/analyze", response_model=AnalysisResult)
async def analyze_description(prompt: Prompt):
    if steam_data is None:
        return {"error": "Server is not ready."}
        
    new_desc = clean_text(prompt.description)
    new_vector = model.encode([new_desc])

    similarity_scores = cosine_similarity(new_vector, game_embeddings)
    top_5_indices = np.argsort(similarity_scores[0])[-5:][::-1]
    similar_games = []
    for i in top_5_indices:
        game_name = steam_data.iloc[i]['name']
        header_image_url = steam_data.iloc[i]['header_image_url']
        store_page_url = steam_data.iloc[i]['store_page_url']
        app_id = steam_data.iloc[i]['appid']
        
    
        similar_games.append({
            "id": app_id,
            "name": game_name,
            "score": float(similarity_scores[0][i]),
            "header_image_url": header_image_url,
            "store_page_url":store_page_url
        })
       
    uniqueness_score = 1 - float(np.max(similarity_scores[0]))
    description_embedding_tfidf = vectorizer.transform([new_desc])
    tag_sim_scores = cosine_similarity(description_embedding_tfidf, tag_embeddings_tfidf)
    top_3_tag_indices = np.argsort(tag_sim_scores[0])[-3:][::-1]
    predicted_tags = [{"name": unique_tags_list[i], "score": float(tag_sim_scores[0][i])} for i in top_3_tag_indices]

    games_to_fetch = [(steam_data.iloc[i]['appid'], steam_data.iloc[i]['name']) for i in top_5_indices]
    reviews_data = await fetch_all_reviews(games_to_fetch)
    
    review_summary = await summarize_reviews_with_gemini(reviews_data)
    
    return {
        "unique_score": uniqueness_score,
        "similar_games": similar_games,
        "predicted_tags": predicted_tags,
        "reviews": reviews_data,
        "review_summary": review_summary
    }