"use client";

import { useState, useEffect } from "react";
import GameCard from "./GameCard";
import RefreshButton from "./RefreshButton";

interface Game {
  id: number;
  game_id: string;
  start_time: string;
  home_team: string;
  away_team: string;
  homeId: string;
  awayId: string;
  assigned_group: string;
  created_at: string;
}

export default function AssignmentsWrapper() {
  const [assignments, setAssignments] = useState<Game[] | null>(null);
  const [error, setError] = useState<{ error: string } | null>(null);

  async function loadAssignments() {
    setError(null);
    try {
      const res = await fetch("/api/assignments");
      const data = await res.json();
      if (res.ok) {
        setAssignments(data);
      } else {
        setError(data);
      }
    } catch (err) {
      setError({ error: err instanceof Error ? err.message : String(err) });
    }
  }

  // Load assignments on component mount
  useEffect(() => {
    loadAssignments();
  }, []);

  return (
    <>
      {/* Error Display */}
      {error && (
        <div className="mx-4 mt-4 p-4 bg-red-900 border border-red-600 text-red-100 rounded-lg">
          <h3 className="font-bold">Error:</h3>
          <pre className="text-sm">{JSON.stringify(error, null, 2)}</pre>
        </div>
      )}

      {/* Games Grid */}
      <div className="p-4 space-y-6">
        {assignments && assignments.map((game) => (
          <GameCard key={game.id} game={game} />
        ))}
      </div>

      {/* Debug Data (hidden by default) */}
      {process.env.NODE_ENV === 'development' && assignments && (
        <details className="mx-4 mt-4 p-4 bg-gray-800 border border-gray-600 rounded-lg">
          <summary className="cursor-pointer text-gray-400">Debug: Raw Data</summary>
          <pre className="text-sm text-gray-300 mt-2 overflow-auto">
            {JSON.stringify(assignments, null, 2)}
          </pre>
        </details>
      )}

      {/* Refresh Button */}
      <div className="flex justify-center mt-6 mb-4">
        <RefreshButton onRefresh={loadAssignments} />
      </div>
    </>
  );
}
