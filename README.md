# Steam Game Release Date Optimizer 🚀

This project uses a machine learning model to analyze historical Steam data and predict the optimal time of year to release a new video game to maximize its success.

---

## 💡 Project Overview

The goal is to move beyond simple gut feelings and use data to answer the question: **"When is the best time to launch my game?"**

The model learns the complex relationships between a game's genre, price, and its release date, and how those factors historically correlate with success metrics like player count or owner estimates. It can then forecast the best potential launch windows for a hypothetical new game.

---

## 🛠️ Tech Stack

- **Language:** Python 3.x
- **Core Libraries:**
  - **Pandas:** For loading, cleaning, and manipulating the game data.
  - **Scikit-learn:** For building and evaluating the machine learning models.
  - **Matplotlib / Seaborn:** For visualizing the results.
- **Environment:** Jupyter Notebook (recommended for analysis and visualization).

---

## 🔬 How It Works: The Machine Learning Pipeline

This project follows a standard machine learning workflow from data preparation to prediction.

### **Phase 1: Data Preparation**

1.  **Data Acquisition:** The model is trained on a publicly available Steam dataset (e.g., from Kaggle), containing information on thousands of games.
2.  **Define Success Metric:** A **target variable** is established to quantify "success." This could be `total_owners`, `peak_concurrent_players`, or another relevant metric.
3.  **Feature Engineering:** The raw data is converted into numerical features the model can understand. This includes extracting the `month` and `week_of_year` from the release date and converting categorical data like `genre` into a numerical format (One-Hot Encoding).

### **Phase 2: Model Training**

1.  **Data Splitting:** The dataset is split into a **training set** (80%) and a **testing set** (20%). The model learns from the training set and is evaluated on the unseen testing set to ensure its predictions are valid.
2.  **Model Selection:** A **Random Forest Regressor** model is used. This type of model is effective at capturing complex, non-linear relationships in the data.
3.  **Training:** The model is trained by calling the `.fit()` method on the training data, allowing it to learn the patterns connecting game features and release timing to the defined success metric.

### **Phase 3: Prediction and Recommendation**

1.  **Evaluation:** The trained model's performance is measured on the testing set using a metric like **Mean Absolute Error (MAE)** to determine its average prediction error.
2.  **Application:** To get a recommendation, a profile for a hypothetical new game is created. The model then runs 52 predictions for this game, one for each week of the year. The week that results in the highest predicted success score is the **optimal launch window**.

---

## USAGE

1.  **Clone the repository:**

    ```bash
    git clone [https://github.com/your-username/release-date-optimizer.git](https://github.com/your-username/release-date-optimizer.git)
    cd release-date-optimizer
    ```

2.  **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

3.  **Download the dataset:**

    - Acquire a Steam dataset from a source like Kaggle.
    - Place the `.csv` file in the `data/` directory.

4.  **Run the analysis:**
    - Open and run the `optimizer.ipynb` Jupyter Notebook.
    - You can change the parameters for your hypothetical game in the "Prediction" section to get a custom recommendation.
