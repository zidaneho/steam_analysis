import pandas as pd
from clean_data import *
from datetime import datetime, timedelta
import requests
import pickle
from pathlib import Path
from tqdm import tqdm
import re

def main():
    df = pd.read_csv(steam_data_path)
    df = clean_data(df)
    df = df[[review_count,review_score,appid,title]]
    df = df[df[review_score] < 70.00]
    df = df[df[review_count] >= 500]
    
    df_sample = df.sample(frac = 0.50).reset_index(drop=True)
    print('Starting to review the sample. size:',df_sample.shape)
    
    
    all_reviews = []
    for _, row in tqdm(df_sample.iterrows(), total=len(df_sample), desc="Scraping Reviews"):
        id = row[appid]  # make sure column is named correctly
        game_reviews = get_reviews(id)
        if len(game_reviews) <= 0:
            continue

        for review in game_reviews:
            review['game_title'] = row[title]
            review['appid'] = id
            all_reviews.append(review)
    reviews_df = pd.DataFrame(all_reviews)
    reviews_df.to_csv('exported_data/controversial_reviews.csv', index=False)

def looks_like_bad_text(text):
    words = len(text.split())
    if words > 300:
        return True
    lines = text.split('\n')
    ascii_art_lines = 0

    for line in lines:
        # Long lines with high character repetition
        if len(line) > 80:
            return True

        # Lines with too many symbols
        if re.search(r"[#=\*\-_/\\|<>]{5,}", line):
            ascii_art_lines += 1

        # Box characters
        if re.search(r"[┌┐└┘─│═║╔╗╚╝▄▀█▓░⠟⣛⠀⣿⠄]+", line):
            return True

    # If 2 or more lines are suspicious, count as ASCII art
    return ascii_art_lines >= 2

def get_user_reviews(review_appid, params):

    user_review_url = f'https://store.steampowered.com/appreviews/{review_appid}'
    req_user_review = requests.get(
        user_review_url,
        params=params
    )

    if req_user_review.status_code != 200:
        print(f'Fail to get response. Status code: {req_user_review.status_code}')
        return {"success": 2}
    try:
        user_reviews = req_user_review.json()
    except:
        return {"success": 2}

    return user_reviews

def get_reviews(review_appid):
    # the params of the API
    params = {
            'json':1,
            'language': 'english',
            'cursor': '*',                                  # set the cursor to retrieve reviews from a specific "page"
            'num_per_page': 100,
            'filter': 'all'
        }
                
    # end_time = datetime.fromtimestamp(1716718910)               # the timestamp in the return result are unix timestamp (GMT+0)
    end_time = datetime.now()
    # start_time = end_time - time_interval
    start_time = datetime(2024, 1, 1, 0, 0, 0)

    passed_start_time = False
    passed_end_time = False

    page_count = 2

    selected_reviews = []

    counter = 0
    while (not passed_start_time or not passed_end_time):

        reviews_response = get_user_reviews(review_appid, params)

        # not success?
        if reviews_response["success"] != 1:
            print("Not a success")
            print(reviews_response)
            break

        if reviews_response["query_summary"]['num_reviews'] == 0:
            #print("No reviews.")
            #print(reviews_response)
            break

        for review in reviews_response["reviews"]:
            recommendation_id = review['recommendationid']
            
            timestamp_created = review['timestamp_created']
            timestamp_updated = review['timestamp_updated']

            # skip the comments that beyond end_time
            if not passed_end_time:
                if timestamp_created > end_time.timestamp():
                    continue
                else:
                    passed_end_time = True
                    
            # exit the loop once detected a comment that before start_time
            if not passed_start_time:
                if timestamp_created < start_time.timestamp():
                    passed_start_time = True
                    break
            
            if looks_like_bad_text(review['review']):
                continue

            # extract the useful (to me) data
            author_steamid = review['author']['steamid']        # will automatically redirect to the profileURL if any
            playtime_forever = review['author']['playtime_forever']
            playtime_last_two_weeks = review['author']['playtime_last_two_weeks']
            playtime_at_review_minutes = review['author']['playtime_at_review']
            last_played = review['author']['last_played']

            review_text = review['review']
            voted_up = review['voted_up']
            votes_up = review['votes_up']
            votes_funny = review['votes_funny']
            weighted_vote_score = review['weighted_vote_score']
            steam_purchase = review['steam_purchase']
            received_for_free = review['received_for_free']
            written_during_early_access = review['written_during_early_access']


            my_review_dict = {
                'recommendationid': recommendation_id,
                'author_steamid': author_steamid,
                'playtime_at_review_minutes': playtime_at_review_minutes,
                'playtime_forever_minutes': playtime_forever,
                'playtime_last_two_weeks_minutes': playtime_last_two_weeks,
                'last_played': last_played,

                'review_text': review_text,
                'timestamp_created': timestamp_created,
                'timestamp_updated': timestamp_updated,

                'voted_up': voted_up,
                'votes_up': votes_up,
                'votes_funny': votes_funny,
                'weighted_vote_score': weighted_vote_score,
                'steam_purchase': steam_purchase,
                'received_for_free': received_for_free,
                'written_during_early_access': written_during_early_access,
            }

            selected_reviews.append(my_review_dict)

        # go to next page
        try:
            cursor = reviews_response['cursor']         # cursor field does not exist in the last page
        except Exception as e:
            cursor = ''

        # no next page
        # exit the loop
        if not cursor:
            print("Reached the end of all comments.")
            break
        
        # set the cursor object to move to next page to continue
        params['cursor'] = cursor
        #print('To next page. Next page cursor:', cursor)
        counter += 1
        if counter >= page_count:
            #print('Exceeded Page Count. Moving on to next game.')
            break
    return selected_reviews

main()
