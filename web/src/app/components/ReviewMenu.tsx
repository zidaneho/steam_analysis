import { useState } from "react";

// NOTE: Assumes your data types have IDs to link them.
// A 'gameId' on the Review links it to a Game's 'id'.
export interface Game {
  id: number;
  name: string;
}

export interface Review {
  id : string;
  name: string;
  recommended: boolean;
  review_text: string;
  gameId: number; // Foreign key to link to a Game
}

export interface ReviewMenuProps {
  games: Game[];
  reviews: Review[];
}

function ReviewMenu(props: ReviewMenuProps) {
  // 1. State to track the currently selected game. Initialize with the first game.
  const [selectedGame, setSelectedGame] = useState<Game | null>(
    props.games[0] || null
  );

  // 2. Filter reviews based on the selected game's ID.
  const filteredReviews = selectedGame
    ? props.reviews.filter((review) => review.gameId === selectedGame.id)
    : [];

  return (
    <div className="flex flex-col">
      <div className="flex flex-row justify-center p-2 border-b border-gray-700 mb-4">
        {props.games.map((game, index) => (
          <div key={index} className="p-2">
            {/* 3. Add onClick to update state and conditional styling for feedback */}
            <button
              onClick={() => setSelectedGame(game)}
              className={`text-lg font-semibold mt-2 transition-colors duration-200 ${
                selectedGame?.id === game.id
                  ? "text-blue-400 underline" // Style for the active button
                  : "text-gray-300 hover:text-white"
              }`}
            >
              {game.name}
            </button>
          </div>
        ))}
      </div>
      <div className="space-y-4 max-h-96 overflow-y-auto pr-2 rounded-lg bg-gray-800/50 p-4">
        {/* 4. Render the filtered reviews and a message if none exist */}
        {filteredReviews.length > 0 ? (
          filteredReviews.map((review) => (
            <div
              key={review.id} // A more robust key
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
            No reviews for {selectedGame?.name || "this game"} yet.
          </p>
        )}
      </div>
    </div>
  );
}

export default ReviewMenu;