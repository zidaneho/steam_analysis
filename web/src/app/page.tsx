"use client";

import Image from "next/image";
import { useState } from "react";
import ReviewMenu from "./components/ReviewMenu";

// --- Define interfaces for the data we expect from the API ---
export interface Game {
  id: number;
  name: string;
  score: number;
  header_image_url: string;
  store_page_url: string;
}

interface Tag {
  name: string;
  score: number;
}

export interface Review {
  id: string;
  name: string;
  review_text: string;
  recommended: boolean;
  gameId: number;
}

interface ReviewSummary {
  challenges: string;
  likes: string;
}

interface AnalysisResult {
  unique_score: number;
  similar_games: Game[];
  predicted_tags: Tag[];
  reviews: Review[];
  review_summary: ReviewSummary;
}

// --- SVG Icon Components for UI ---

const SendIcon = () => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    viewBox="0 0 24 24"
    fill="currentColor"
    className="w-6 h-6"
  >
    <path d="M3.478 2.404a.75.75 0 0 0-.926.941l2.432 7.905H13.5a.75.75 0 0 1 0 1.5H4.984l-2.432 7.905a.75.75 0 0 0 .926.94 60.519 60.519 0 0 0 18.445-8.986.75.75 0 0 0 0-1.218A60.517 60.517 0 0 0 3.478 2.404Z" />
  </svg>
);

export default function Home() {
  const [prompt, setPrompt] = useState("");
  const [submittedPrompt, setSubmittedPrompt] = useState("");
  const [results, setResults] = useState<AnalysisResult | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!prompt.trim() || isLoading) return;

    setIsLoading(true);
    setResults(null);
    setError(null);
    setSubmittedPrompt(prompt);

    try {
      const response = await fetch("/api/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ description: prompt }),
      });

      if (!response.ok) {
        throw new Error(
          "Network response was not ok. Please check the server."
        );
      }

      const data: AnalysisResult = await response.json();

      // --- Augment data with IDs for the ReviewMenu component ---
      const augmentedData = {
        ...data,
        similar_games: data.similar_games.map((game, index) => ({
          ...game,
          id: index, // Simple index-based ID
        })),
        reviews: data.reviews.map((review, index) => ({
          ...review,
          // This is a placeholder. Ideally, your API should provide the gameId
          // to link a review to a specific game from similar_games.
          gameId: index % data.similar_games.length, // Simple modulo for demonstration
        })),
      };
      console.log("Augmented data:", augmentedData);
      setResults(augmentedData);
    } catch (error) {
      console.error("Failed to fetch analysis:", error);
      setError("Failed to get a response from the server. Is it running?");
    } finally {
      setIsLoading(false);
    }
  };

  const formatSummary = (text: string) => {
    return text
      .split("* ")
      .filter((item) => item.trim() !== "")
      .map((item, index) => (
        <li key={index} className="mb-2">
          {item.trim()}
        </li>
      ));
  };
  const ProgressBar = ({ isLoading }: { isLoading: boolean }) => {
    // We use CSS transitions for a smooth fade-in/fade-out effect
    return (
      <div
        className={`fixed top-0 left-0 w-full h-1 z-50 transition-opacity duration-300 ${
          isLoading ? "opacity-100" : "opacity-0"
        }`}
      >
        <div className="h-full w-full bg-blue-500 animate-pulse"></div>
      </div>
    );
  };

  const hasSubmitted = isLoading || results || error;

  return (
    <main className="min-h-screen text-gray-200 p-4 font-sans flex flex-col justify-center items-center">
      <ProgressBar isLoading={isLoading} />
      {/* --- Main Content Area (Scrollable) --- */}
      <div
        className={`w-full max-w-3xl mx-auto flex-1 overflow-y-auto pb-24 transition-opacity duration-500 ${
          hasSubmitted ? "opacity-100" : "opacity-0 pointer-events-none"
        }`}
      >
        {hasSubmitted && (
          <div className="space-y-10 py-8">
            {/* --- User's Prompt --- */}
            <div className="flex gap-4">
              <p className="font-medium pt-1 whitespace-pre-wrap">
                {submittedPrompt}
              </p>
            </div>

            {/* --- AI's Response --- */}
            <div className="flex gap-4">
              <div className="w-full">
                {error && <div className="text-red-400">{error}</div>}
                {results && (
                  <div className="space-y-8">
                    {/* Uniqueness Score */}
                    <div>
                      <h2 className="text-2xl font-semibold mb-3">
                        Uniqueness Score
                      </h2>
                      <p className="text-6xl font-bold text-center text-green-400 bg-gray-800/50 py-6 rounded-lg">
                        {(results.unique_score * 100).toFixed(1)}%
                      </p>
                    </div>

                    {/* AI Review Summary */}
                    <div>
                      <h2 className="text-2xl font-semibold mb-3">
                        🤖 AI Review Summary
                      </h2>
                      <div className="p-6 rounded-lg bg-gray-800/50 grid md:grid-cols-2 gap-x-8 gap-y-6">
                        <div>
                          <h3 className="text-lg font-bold text-red-400 mb-2">
                            Common Challenges & Criticisms
                          </h3>
                          <ul className="list-disc pl-5 text-gray-300 space-y-1">
                            {formatSummary(results.review_summary.challenges)}
                          </ul>
                        </div>
                        <div>
                          <h3 className="text-lg font-bold text-green-400 mb-2">
                            Common Likes & Praises
                          </h3>
                          <ul className="list-disc pl-5 text-gray-300 space-y-1">
                            {formatSummary(results.review_summary.likes)}
                          </ul>
                        </div>
                      </div>
                    </div>

                    {/* Similar Games */}
                    <div>
                      <h2 className="text-2xl font-semibold mb-3">
                        Most Similar Games
                      </h2>
                      <ul className="space-y-2">
                        {results.similar_games.map((game, index) => (
                          <li
                            key={index}
                            className="flex items-center justify-between p-2 bg-gray-800/50 rounded-lg hover:bg-gray-700/50 transition-colors"
                          >
                            <a
                              href={game.store_page_url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="flex items-center space-x-4"
                            >
                              <Image
                                src={game.header_image_url}
                                alt={game.name}
                                width={460}
                                height={215}
                              />

                              <span className="font-medium">{game.name}</span>
                            </a>
                            <span className="font-mono text-sm text-green-400">
                              {(game.score * 100).toFixed(1)}% match
                            </span>
                          </li>
                        ))}
                      </ul>
                    </div>

                    <div>
                      <h2 className="text-2xl font-semibold mb-3">
                        Raw Reviews
                      </h2>
                      <ReviewMenu
                        games={results.similar_games}
                        reviews={results.reviews}
                      />
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* --- Sticky Input Form (Animated) --- */}
      <div className="w-full max-w-md">
        <form onSubmit={handleSubmit} className="relative">
          <textarea
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="Describe your game idea here..."
            className="w-full h-40 p-4 pr-20 bg-gray-800 border border-gray-700 rounded-2xl focus:ring-2 focus:ring-blue-500 focus:outline-none resize-none text-base"
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                handleSubmit(e);
              }
            }}
          />
          <button
            type="submit"
            className="absolute px-4 py-2 bottom-3 right-3 rounded-full bg-blue-600 text-white hover:bg-blue-500 disabled:bg-gray-600 disabled:cursor-not-allowed transition-colors"
            disabled={isLoading || !prompt.trim()}
          >
            <SendIcon />
          </button>
        </form>
      </div>
    </main>
  );
}
