import { useState } from "react";

export interface Game {
  name: string;
}

export interface Review {
  id: string;
  name: string; // This is the game name associated with the review
  recommended: boolean;
  review_text: string;
}

export interface ReviewMenuProps {
  games: Game[];
  reviews: Review[];
}

function ReviewMenu(props: ReviewMenuProps) {
  const [selectedGame, setSelectedGame] = useState<Game | null>(
    props.games[0] || null
  );

  // --- FIX: Replaced the incorrect .reduce() with a simple .filter() ---
  // This correctly creates an array of all reviews matching the selected game's name.
  const filteredReviews = selectedGame
    ? props.reviews.filter((review) => review.name === selectedGame.name)
    : [];

  

  return (
    <div className="flex flex-col">
      <div className="flex flex-row justify-center p-2 border-b border-gray-700 mb-4">
        {props.games.map((game) => (
          <div key={game.name + "button"} className="p-2">
            <button
              onClick={() => setSelectedGame(game)}
              className={`text-lg font-semibold mt-2 transition-colors duration-200 ${
                selectedGame?.name === game.name
                  ? "text-blue-400 underline"
                  : "text-gray-300 hover:text-white"
              }`}
            >
              {game.name}
            </button>
          </div>
        ))}
      </div>
      <div className="space-y-4 max-h-96 overflow-y-auto pr-2 rounded-lg bg-gray-800/50 p-4">
        {filteredReviews.length > 0 ? (
          filteredReviews.map((review) => (
            <div
              key={review.id} // The review ID is unique enough
              className="border-b border-gray-700 pb-3 last:border-b-0"
            >
              <p className="font-bold text-gray-100">
                {review.recommended ? "👍 Recommended" : "👎 Not Recommended"}
              </p>
              <p className="text-gray-400 text-sm mt-1">{review.review_text}</p>
            </div>
          ))
        ) : (
          <p className="text-gray-400 text-center">
            No reviews for {selectedGame?.name || "this game"} found through Steam API. Please check the reviews directly.
          </p>
        )}
      </div>
    </div>
  );
}

export default ReviewMenu;
