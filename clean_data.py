import pandas as pd
import numpy as np
import plotly.express as px

boxleiter_num = 50 #sales per review
revenue_threshold = 50000
top_genres_count = 40

def main():
    df = pd.read_csv('steam_data.csv')
    df = clean_data(df)
    plot_profitable_genres(df)
    plot_success_rate(df)

def clean_data(df):
    #clean up launch price to real numbers
    df = df[df['Reviews Total'] >= 10]
    df = df[df['Tags'].str.contains('Indie')].copy()
    df['Launch Price'] = df['Launch Price'].apply(clean_launch_price)
    df['Estimated Revenue'] = df['Reviews Total'] * boxleiter_num * pd.to_numeric(df['Launch Price'])

    df['Tags'] = df['Tags'].str.split(', ')
    df = df.explode('Tags')
    df = df[~df['Tags'].str.contains('Indie')]
    top_genres = df['Tags'].value_counts().sort_values(ascending=False)[:top_genres_count]

    df = df[df['Tags'].isin(top_genres.index)]
    return df

def clean_launch_price(x):
    x = x[:-3] +'.'+ x[-2:]
    x = x.replace('$','').replace(',','').replace(' ','').replace('\xa0','').strip() #\xa0 is the ASCII value for invisible space
    return x


# Calculate IQR (Interquartile Range)
def remove_outliers(group):
    Q1 = group["Estimated Revenue"].quantile(0.25)  # First quartile (25th percentile)
    Q3 = group["Estimated Revenue"].quantile(0.75)  # Third quartile (75th percentile)
    IQR = Q3 - Q1

    # Define lower and upper bounds
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR

    # Filter out outliers
    return group[(group["Estimated Revenue"] >= lower_bound) & (group["Estimated Revenue"] <= upper_bound)]

def plot_profitable_genres(df):
    top_200 = df.groupby('Tags').head(200)
    top_200 = top_200.groupby('Tags').apply(remove_outliers).reset_index(drop=True)
    top_200 = top_200.sort_values(by='Estimated Revenue',ascending=False)

    # Compute median revenue per genre
    median_revenue_per_genre = top_200.groupby('Tags')["Estimated Revenue"].median()
    # Sort `top_200` based on median revenue per genre
    top_200 = top_200.set_index('Tags').loc[median_revenue_per_genre.sort_values(ascending=False).index].reset_index()
    # Compute success rate per genre
    df_no_outliers = df.groupby('Tags').apply(remove_outliers).reset_index(drop=True)

    #median_rev = median_rev.sort_values(by='Estimated Revenue',ascending=False)
    fig = px.box(top_200, x="Tags", y="Estimated Revenue", title="Revenue Distribution by Genre", 
                labels={"Tags": "Genre", "Estimated Revenue": "Revenue ($)"},
                color="Tags")

    fig.show()    




def plot_success_rate(df):
    df_no_outliers = df.groupby('Tags').apply(remove_outliers).reset_index(drop=True)
    success_rate_per_genre = df_no_outliers.groupby("Tags")["Estimated Revenue"].apply(lambda x: (x >= revenue_threshold).mean() * 100).reset_index()

    # Rename the column for clarity
    success_rate_per_genre.columns = ["Tags", "Success Rate"]

    # Sort by success rate (highest first)
    success_rate_per_genre = success_rate_per_genre.sort_values(by="Success Rate", ascending=False)
    print(success_rate_per_genre.head())
    # Create a horizontal bar chart
    fig = px.bar(
        success_rate_per_genre,
        x="Success Rate",
        y="Tags",
        orientation="h",  # Horizontal bars
        text="Success Rate",  # Display values on bars
        labels={"Success Rate": "Success Rate (%)", "Tags": "Genres"},
        title="Success Rate per Genre",
        color="Success Rate",  # Color by success rate
        color_continuous_scale="Viridis"  # Color theme
    )
    
    # Improve readability
    fig.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
    fig.update_layout(yaxis_categoryorder="total ascending")  # Sort by success rate
    fig.show()

if __name__ == '__main__':
    main()
