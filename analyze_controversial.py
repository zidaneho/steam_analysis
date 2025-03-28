import pandas as pd
import re
from nltk.corpus import stopwords
from collections import Counter
from scipy import stats
from scipy.stats import skew
from clean_data import *
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from sklearn.preprocessing import MultiLabelBinarizer
import seaborn as sns

criticism_types = {
        "performance": [
            "lag", "low fps", "frame drops", "frame rate", "stutter", "sluggish", 
            "slow", "performance issues", "poor performance", "optimization", 
            "not optimized", "bad fps", "inconsistent fps"
        ],
        "stability": [
            "crash", "crashes", "bug", "bugs", "glitch", "glitches", 
            "freeze", "freezes", "freezing", "crashing", "broken", "corrupted", 
            "softlock", "hardlock", "unplayable"
        ],
        "content": [
            "boring", "repetitive", "nothing to do", "empty", "lack of content", 
            "too short", "too little content", "shallow", "unfinished", 
            "needs more content", "barebones", "no replay value"
        ],
        "design": [
            "unbalanced", "imbalanced", "pay to win", "pay2win", "grindy", "grinding", 
            "tedious", "unfair", "clunky", "awkward", "poorly designed", 
            "frustrating", "janky", "bad design", "bad mechanics", "bad ai", 
            "bad level design", "bad difficulty curve"
        ],
        "monetization": [
            "dlc", "microtransaction", "microtransactions", "overpriced", "greedy", 
            "cash grab", "paywall", "monetization", "nickel and diming", 
            "money hungry", "milking", "battle pass", "paid cosmetics", 
            "locked behind paywall", "expensive for what it is"
        ],
        "communication": [
            "abandoned", "roadmap", "developers don't care", "devs silent", 
            "no updates", "ignored", "lack of communication", "radio silence", 
            "no patch notes", "devs stopped", "devs gone", "no response", 
            "false promises", "broken promises"
        ],
        "ui_ux": [
            "bad controls", "unintuitive", "ui is terrible", "bad ui", 
            "confusing menus", "camera issues", "hud is bad", "poor interface", 
            "bad interface", "weird controls", "clunky controls", "bad keybinds", 
            "menu navigation sucks", "bad layout", "no controller support"
        ],
        "multiplayer": [
            "multiplayer", "online", "co-op", "coop", "server", "servers", 
            "disconnect", "disconnects", "matchmaking", "no matchmaking", 
            "desync", "netcode", "connection", "latency", "laggy online", 
            "lobby", "host", "peer", "rubberbanding", "can't connect", 
            "can't join", "matchmaking broken", "network error"
        ],
        "politics": [
            "woke", "sjw", "agenda", "identity politics", "forced diversity",
            "political", "virtue signaling", "gender politics", "race agenda",
            "checklist casting", "token character", "lgbt agenda", "too political",
            "social commentary", "representation forced"
        ]
    }

def main():
    # Load and merge
    reviews_df = pd.read_csv('exported_data/controversial_reviews.csv')
    reviews_df = merge_genre(reviews_df)
    reviews_df = merge_criticism(reviews_df)


    # Ensure criticism_tags is a list
    reviews_df['criticism_tags'] = reviews_df['criticism_tags'].apply(lambda x: x if isinstance(x, list) else [])

    

    # Multi-hot encode criticism tags   
    mlb = MultiLabelBinarizer()
    multi_hot_df = pd.DataFrame(
        mlb.fit_transform(reviews_df['criticism_tags']),
        columns=mlb.classes_,
        index=reviews_df.index
    )
    reviews_df = pd.concat([reviews_df, multi_hot_df],  axis=1)

    stability_ratios_by_game = reviews_df.groupby('game_title').apply(compute_stability_ratio).reset_index()
    # Sort to see which games have the highest ratio
    top_stability_games = stability_ratios_by_game.sort_values(by='stability_ratio', ascending=False)
    print(top_stability_games.head(10))

    # Count total occurrences of each criticism type
    # total_crit_counts = reviews_df[mlb.classes_].sum().sort_values(ascending=False).reset_index()
    # total_crit_counts.columns = ['Criticism Type', 'Count']

    # values = total_crit_counts['Count'].values

    # mean = np.mean(values)
    # median = np.median(values)
    # mode = stats.mode(values, keepdims=False).mode
    # shape_skew = skew(values)

    # print('mean:',mean)
    # print('median:',median)
    # print('mode:',mode)
    # print('skew:',shape_skew)

    # # Plot the distribution
    # plt.figure(figsize=(10, 6))
    # sns.barplot(data=total_crit_counts, x='Criticism Type', y='Count', palette='Reds')
    # plt.title("Overall Distribution of Criticism Types")
    # plt.xlabel("Criticism Type")
    # plt.ylabel("Number of Reviews Tagged")
    # plt.xticks(rotation=45)
    # plt.tight_layout()
    # plt.show()


    

    # Group by genre and sum criticism counts
    # crit_columns = mlb.classes_.tolist()
    # genre_crit_summary = reviews_df.groupby(tags)[crit_columns].sum()

    # # Normalize to get proportion heatmap
    # genre_crit_normalized = genre_crit_summary.div(genre_crit_summary.sum(axis=1), axis=0)

    # plt.figure(figsize=(12, 6))
    # sns.heatmap(genre_crit_normalized, annot=True, cmap="Reds", linewidths=0.5)
    # plt.title("Criticism Distribution by Genre")
    # plt.xlabel("Criticism Type")
    # plt.ylabel("Genre")
    # plt.xticks(rotation=45)
    # plt.tight_layout()
    # plt.show()

    # # Find dominant criticism per genre
    # dominant_crit = genre_crit_summary.idxmax(axis=1).value_counts().reset_index()
    # dominant_crit.columns = ['Criticism Type', 'Genre Count']

    # plt.figure(figsize=(10, 6))
    # sns.barplot(data=dominant_crit, x='Criticism Type', y='Genre Count', hue='Criticism Type', palette='Reds', legend=False)
    # plt.title("Most Dominant Criticism Type per Genre")
    # plt.xlabel("Criticism Type")
    # plt.ylabel("Number of Genres Dominated")
    # plt.xticks(rotation=45)
    # plt.tight_layout()
    # plt.show()
    
    
def clean_and_tokenize(text):
    text = text.lower()
    text = re.sub(r'[^a-z\s]', '', text)  # keep letters and spaces
    tokens = text.split()
    stop_words = set(stopwords.words('english'))
    return [word for word in tokens if word not in stop_words and len(word) > 2]

def find_most_common(df):
    all_text = " ".join(df['review_text'].dropna().astype(str))
    tokens = clean_and_tokenize(all_text)
    word_counts = Counter(tokens)
    print(word_counts.most_common(50))
    # wordcloud = WordCloud(width=800, height=400).generate_from_frequencies(word_counts)
    # plt.figure(figsize=(12, 6))
    # plt.imshow(wordcloud, interpolation='bilinear')
    # plt.axis("off")
    # plt.show()
def merge_genre(reviews_df):
    df = pd.read_csv('data/games_march2025_cleaned.csv')
    df = clean_data(df)

    reviews_df = pd.merge(reviews_df,df,on='appid')
    reviews_df = reviews_df[['appid','game_title','review_text',tags]]
    return reviews_df
def merge_criticism(df):
    df['criticism_tags'] = df['review_text'].dropna().astype(str).apply(
        lambda x: tag_criticism_types(x, criticism_types)
    )
    df['criticism_tags'] = df['criticism_tags'].apply(
        lambda x: x if isinstance(x, list) else []
    )
    return df
def tag_criticism_types(text, categories):
    text = text.lower()
    tags = []
    for label, keywords in categories.items():
        for keyword in keywords:
            if keyword in text:
                tags.append(label)
                break  # avoid double-counting
    return tags
def compute_stability_ratio(group):
    stability_count = group['stability'].sum()
    other_or_none_count = len(group) - stability_count  # reviews that do not have stability
    ratio = stability_count / other_or_none_count if other_or_none_count > 0 else 0
    return pd.Series({
        'stability_reviews': stability_count,
        'other_or_none_reviews': other_or_none_count,
        'stability_ratio': ratio
    })

main()

