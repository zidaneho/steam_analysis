import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from scipy.stats import chi2_contingency
import re

boxleiter_num = 50 #sales per review
revenue_threshold = 50000
top_genres_count = 40

steam_data_path = 'data/games_march2025_cleaned.csv'
release_date = 'release_date'
review_count = 'num_reviews_total'
price = 'price'
tags = 'tags'
title = 'name'
review_score = 'user_score'
appid = 'appid'

def main():
    df = pd.read_csv(steam_data_path)
    
    df = clean_data(df)
    
    
    plot_release_dates(df)

    # revenue_df = get_estimated_revenue(df)
    # df = pd.merge(revenue_df,df,on=title)

    
   
   
    

def clean_data(df):
    #clean up launch price to real numbers
    df = df[df[review_count] >= 10]
    df = df[df[tags].str.contains('Indie')].copy()

    positive = df['positive'].astype(int)
    negative = df['negative'].astype(int)
    total = (positive + negative).astype(float)
    df[review_score] = positive / total
   
    df[tags] = df[tags].apply(get_tags)
    df = df.explode(tags)
    df = df[~df[tags].str.contains('Indie')]
    top_genres = df[tags].value_counts().sort_values(ascending=False)[:top_genres_count]

    df = df[df[tags].isin(top_genres.index)]

    
    
    return df

def get_tags(x):
    matches = re.findall(r"'(.*?)'", x)
    return matches


def get_estimated_revenue(df):
    #f2p games revenue cannot be calculated
    df = df[df[price] > 0]
    new_df = df[[title]].copy()
    new_df.loc[:,'estimated_revenue'] = df.loc[:,review_count] * boxleiter_num * pd.to_numeric(df.loc[:,price])
    return new_df


# Calculate IQR (Interquartile Range)
def remove_outliers(df,col):
    Q1 = df.groupby(tags)[col].transform(lambda x: x.quantile(0.25))
    Q3 = df.groupby(tags)[col].transform(lambda x: x.quantile(0.75))
    IQR = Q3-Q1

    lower_bound = Q1 - 1.5*IQR
    upper_bound = Q3 + 1.5*IQR

    return df[(df[col] >= lower_bound) & (df[col] <= upper_bound)]


def plot_profitable_genres(df):
    top_200 = df.groupby(tags).head(200)
    top_200 = top_200.groupby(tags).apply(remove_outliers).reset_index(drop=True)
    top_200 = top_200.sort_values(by='estimated_revenue',ascending=False)

    # Compute median revenue per genre
    median_revenue_per_genre = top_200.groupby(tags)['estimated_revenue'].median()
    # Sort `top_200` based on median revenue per genre
    top_200 = top_200.set_index(tags).loc[median_revenue_per_genre.sort_values(ascending=False).index].reset_index()
  

    median_rev = median_rev.sort_values(by='estimated_revenue',ascending=False)
    fig = px.box(top_200, x=tags, y='estimated_revenue', title="Revenue Distribution by Genre", 
                labels={tags: "Genre", 'estimated_revenue': "Revenue ($)"},
                color=tags)

    fig.show()    

    

def plot_release_dates(df):
    # Convert to datetime

    df[release_date] = pd.to_datetime(df[release_date],errors='coerce')

    df['release_year'] = pd.to_datetime(df['release_date'], errors='coerce').dt.year

    # Drop NaNs and count number of games per year
    yearly_counts = df['release_year'].dropna().astype(int).value_counts().sort_index()
    year_df = yearly_counts.reset_index()
    year_df.columns = ['Release Year', 'Number of Games']

    # Plot bar chart
    fig = px.bar(
        year_df,
        x='Release Year',
        y='Number of Games',
        title='Yearly Distribution of Game Releases',
        labels={'Release Year': 'Year', 'Number of Games': 'Games Released'},
    )

    fig.update_layout(
        xaxis_tickangle=-45,
        template='plotly_white',
        width=1000,
        height=500
    )

    fig.show()

    years = df['release_year'].dropna().astype(int)

    # Calculate statistics
    mean_year = years.mean()
    median_year = years.median()
    mode_year = years.mode().iloc[0] if not years.mode().empty else None

    print(f"Mean Release Year: {mean_year:.2f}")
    print(f"Median Release Year: {median_year}")
    print(f"Mode Release Year: {mode_year}")

   



def plot_success_rate(df):
    df_no_outliers = remove_outliers(df,'estimated_revenue')
    

    success_rate_per_genre = df_no_outliers.groupby(tags)['estimated_revenue'].apply(lambda x: (x >= revenue_threshold).mean() * 100).reset_index()

    # Rename the column for clarity
    success_rate_per_genre.columns = [tags, "Success Rate"]

    # Sort by success rate (highest first)
    success_rate_per_genre = success_rate_per_genre.sort_values(by="Success Rate", ascending=False)
    df['Success'] = df['estimated_revenue'] >= revenue_threshold

    contingency = pd.crosstab(df[tags],df['Success'])
    chi2, p, dof, expected = chi2_contingency(contingency)
    print("Chi-Square Test Results")
    print("Chi2 Stat:", chi2)
    print("p-value:", p)
    print("Degrees of Freedom:", dof)

    alpha = 0.05
    if p < alpha:
        print("Reject the null hypothesis: Success rate differs by genre.")
    else:
        print("Fail to reject the null hypothesis: No significant difference in success rates.") 
    success_rates = df.groupby(tags)['Success'].mean().sort_values(ascending=False) * 100
    fig = px.bar(success_rates.reset_index(), x=tags, y='Success',
       title='Success Rate per Genre',
       labels={tags: 'Genre', 'Success': 'Success Rate (%)'})
    fig.show()
    
    # Create a horizontal bar chart
    fig = px.bar(
        success_rate_per_genre,
        x="Success Rate",
        y=tags,
        orientation="h",  # Horizontal bars
        text="Success Rate",  # Display values on bars
        labels={"Success Rate": "Success Rate (%)", tags: "Genres"},
        title="Success Rate per Genre",
        color="Success Rate",  # Color by success rate
        color_continuous_scale="Viridis"  # Color theme
    )
    
    # Improve readability
    fig.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
    fig.update_layout(yaxis_categoryorder="total ascending")  # Sort by success rate
    #fig.show()

if __name__ == '__main__':
    main()
