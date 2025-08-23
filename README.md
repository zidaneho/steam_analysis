# Steam Competitor Analysis Tool 🎮

This project is a full-stack research tool designed to help game developers analyze the competitive landscape on Steam. By inputting a game idea or description, developers can discover similar existing games, understand their market positioning, and gain insights into their strengths and weaknesses based on player reviews.

---

## 🚀 Features

-   **Competitor Identification**: Uses natural language processing to find the top 5 most similar games to your concept.
-   **Uniqueness Score**: Calculates a "uniqueness score" to gauge how crowded the market is for your game idea.
-   **AI-Powered Review Analysis**: Fetches recent reviews for competitor games and uses the Gemini API to summarize common praises and criticisms.
-   **Interactive Frontend**: A clean, modern web interface built with Next.js and React to easily input your ideas and visualize the results.
-   **RESTful API**: A robust backend built with FastAPI that serves the analysis results to the frontend.

---

## 🛠️ How It Works

The tool is comprised of a data pipeline, a backend API, and a web frontend.

1.  **Data Pipeline**:
    *   A Kaggle dataset of Steam games is downloaded and processed.
    *   Game descriptions and tags are cleaned and combined.
    *   The `sentence-transformers` library is used to generate vector embeddings for each game's text, creating a numerical representation of its content.
    *   The processed data and embeddings are saved for the API to use.

2.  **Backend API**:
    *   The user submits their game description to the `/analyze` endpoint.
    *   The backend generates an embedding for the user's description.
    *   **Cosine similarity** is used to compare the user's embedding to all game embeddings in the database, identifying the most similar games.
    *   A uniqueness score is calculated based on the similarity of the top match.
    *   The API asynchronously fetches the latest reviews for the top 5 competitor games from Steam.
    *   The fetched reviews are passed to the Gemini API with a specialized prompt to extract common challenges and praises.
    *   The results are sent back to the frontend as a JSON object.

3.  **Frontend**:
    *   The user enters their game idea into a textarea.
    *   The frontend calls the backend API and displays the results in a user-friendly format, including the uniqueness score, a list of similar games with links to their Steam pages, and the AI-generated review summary.

---

## 🏆 Technical Showcase (for Resumes)

This project demonstrates a range of modern software engineering and data science skills:

-   **Backend Development**:
    -   Built a high-performance, asynchronous REST API using **FastAPI**.
    -   Utilized **Pydantic** for robust data validation.
    -   Implemented asynchronous network requests with `aiohttp` to efficiently fetch external data from the Steam API.
-   **Natural Language Processing (NLP)**:
    -   Applied **sentence embeddings** (`all-MiniLM-L6-v2` model) to represent and compare the semantic content of game descriptions.
    -   Used **cosine similarity** to perform a semantic search for competitor games.
    -   Leveraged **TF-IDF** to predict relevant tags for a given game description.
-   **Generative AI**:
    -   Integrated the **Google Gemini API** for advanced text summarization, crafting a specific prompt to extract actionable insights from unstructured review data.
-   **Frontend Development**:
    -   Developed a responsive and interactive user interface with **Next.js**, **React**, and **TypeScript**.
    -   Styled the application with **TailwindCSS** for a modern and clean aesthetic.
-   **Full-Stack Architecture**:
    -   Designed and built a complete full-stack application, from data preprocessing to a user-facing web interface.
    -   Managed a data pipeline that includes fetching, cleaning, and processing data for use in a machine learning application.

---

## USAGE

To run this project, you need to run the backend API and the frontend application separately.

### Backend Setup

1.  **Navigate to the API directory**:
    ```bash
    cd api
    ```
2.  **Install Python dependencies**:
    ```bash
    pip install -r ../requirements.txt
    ```
3.  **Set up your environment variables**:
    -   Create a file named `.env` in the `api/` directory.
    -   Add your Google API key to the `.env` file:
        ```
        GOOGLE_API_KEY="YOUR_API_KEY_HERE"
        ```
4.  **Run the preprocessing script**:
    -   Before running the API for the first time, you need to process the data. Make sure you have downloaded the dataset into the `data/` directory using the `update_data.sh` script.
    ```bash
    python ../preprocess.py
    ```
5.  **Start the FastAPI server**:
    ```bash
    uvicorn main:app --reload
    ```
    The API will be available at `http://127.0.0.1:8000`.

### Frontend Setup

1.  **Navigate to the web directory**:
    ```bash
    cd web
    ```
2.  **Install Node.js dependencies**:
    ```bash
    npm install
    ```
3.  **Start the Next.js development server**:
    ```bash
    npm run dev
    ```
    The web application will be available at `http://localhost:3000`.

---

## ቴክ Tech Stack

-   **Backend**: Python, FastAPI, `sentence-transformers`, `scikit-learn`, `pandas`, `numpy`, Google Gemini API
-   **Frontend**: Next.js, React, TypeScript, TailwindCSS
-   **Data**: Kaggle, SQLite
-   **DevOps**: `update_data.sh` script for data pipeline management