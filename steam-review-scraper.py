#!/usr/bin/env python
# coding: utf-8

# # Steam Review Scraper
# 
# A scraper that scrape reviews within a fixed time interval
# 
# Using API: https://partner.steamgames.com/doc/store/getreviews

# ## Scrape Reviews

# In[1]:


from datetime import datetime, timedelta
import requests
import pickle
from pathlib import Path


# In[2]:


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


# In[3]:


review_appname = "ELDEN RING"                              # the game name
review_appid = 1245620                                      # the game appid on Steam

# the params of the API
params = {
        'json':1,
        'language': 'english',
        'cursor': '*',                                  # set the cursor to retrieve reviews from a specific "page"
        'num_per_page': 100,
        'filter': 'recent'
    }

time_interval = timedelta(hours=24)                         # the time interval to get the reviews
# end_time = datetime.fromtimestamp(1716718910)               # the timestamp in the return result are unix timestamp (GMT+0)
end_time = datetime.now()
# start_time = end_time - time_interval
start_time = datetime(2024, 1, 1, 0, 0, 0)

print(f"Start time: {start_time}")     # printing local timezone for logging
print(f"End time: {end_time}")
print(start_time.timestamp(), end_time.timestamp())

passed_start_time = False
passed_end_time = False

page_count = 10

selected_reviews = []

counter = 0
while ((not passed_start_time or not passed_end_time) and counter < page_count):

    reviews_response = get_user_reviews(review_appid, params)

    # not success?
    if reviews_response["success"] != 1:
        print("Not a success")
        print(reviews_response)
        break

    if reviews_response["query_summary"]['num_reviews'] == 0:
        print("No reviews.")
        print(reviews_response)
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
    print('To next page. Next page cursor:', cursor)
    counter += 1


# In[4]:


selected_reviews[:10]


# In[5]:


len(selected_reviews)


# In[6]:


# save the selected reviews to a file

foldername = f"{review_appid}_{review_appname}"
filename = f"{review_appid}_{review_appname}_reviews_{start_time.strftime('%Y%m%d-%H%M%S')}_{end_time.strftime('%Y%m%d-%H%M%S')}.pkl"
output_path = Path(
    foldername, filename
)
if not output_path.parent.exists():
    output_path.parent.mkdir(parents=True)

pickle.dump(selected_reviews, open(output_path, 'wb'))


# ## Read a review pickle object

# In[7]:


review_appname = "ELDEN RING"                              # the game name
review_appid = 1245620                                      # the game appid on Steam


foldername = f"{review_appid}_{review_appname}"
filename = f"{review_appid}_{review_appname}_reviews_{start_time.strftime('%Y%m%d-%H%M%S')}_{end_time.strftime('%Y%m%d-%H%M%S')}.pkl"
output_path = Path(
    foldername, filename
)

if not output_path.exists():
    print("File not found.")
    exit()


selected_reviews = pickle.load(open(output_path, 'rb'))


# In[8]:


len(selected_reviews)


# In[9]:


selected_reviews[0]


# In[ ]:




