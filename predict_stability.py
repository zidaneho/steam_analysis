from clean_data import *
from analyze_controversial import *
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, roc_auc_score
from imblearn.over_sampling import SMOTE
import pandas as pd

def main():
    reviews_df = pd.read_csv('exported_data/controversial_reviews.csv')
    reviews_df = merge_genre(reviews_df)
    reviews_df = merge_criticism(reviews_df)
    reviews_df['criticism_tags'] = reviews_df['criticism_tags'].apply(lambda x: x if isinstance(x, list) else [])
     # Multi-hot encode criticism tags   
    mlb = MultiLabelBinarizer()
    multi_hot_df = pd.DataFrame(
        mlb.fit_transform(reviews_df['criticism_tags']),
        columns=mlb.classes_,
        index=reviews_df.index
    )
    reviews_df = pd.concat([reviews_df, multi_hot_df],  axis=1)

    model, game_data, X, y = predict_buggy_games(reviews_df)

def predict_buggy_games(reviews_df, threshold=0.10, tags_col=tags):
    # Step 1: Aggregate to game level
    game_agg = reviews_df.groupby('game_title').agg({
        'stability': ['sum', 'count'],
        'performance': 'mean',
        'design': 'mean',
        'content': 'mean',
        'monetization': 'mean',
        tags_col: 'first'
    })

    # Flatten multi-index columns
    game_agg.columns = ['stability_sum', 'review_count', 'performance_ratio', 'design_ratio', 'content_ratio', 'monetization_ratio', tags_col]
    game_agg = game_agg.reset_index()

    # Step 2: Define 'buggy' label
    game_agg['stability_ratio'] = game_agg['stability_sum'] / game_agg['review_count']
    game_agg['buggy'] = (game_agg['stability_ratio'] >= threshold).astype(int)

    # Step 3: One-hot encode genre
    game_agg = pd.get_dummies(game_agg, columns=[tags_col], drop_first=True)

    # Step 4: Define features and target
    X = game_agg.drop(columns=['game_title', 'stability_sum', 'stability_ratio', 'buggy'])
    y = game_agg['buggy']

    # Step 5: Train/test split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    smote = SMOTE(random_state=42)
    X_resampled, y_resampled = smote.fit_resample(X, y)

    # Step 6: Train classifier
    model = RandomForestClassifier(random_state=42,class_weight='balanced')
    model.fit(X_resampled, y_resampled)

    # Step 7: Evaluate
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]

    print("Classification Report:\n", classification_report(y_test, y_pred))
    print("AUC Score:", roc_auc_score(y_test, y_prob))

    return model, game_agg, X, y

    

if __name__ == "__main__":
    main()