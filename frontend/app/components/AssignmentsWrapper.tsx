"use client";

import { useState, useEffect } from "react";
import GameCard from "./GameCard";
import RefreshButton from "./RefreshButton";
import { Root } from "../types/game";

interface AssignmentsWrapperProps {
  initialAssignments: Root[];
}

export default function AssignmentsWrapper({ initialAssignments }: AssignmentsWrapperProps) {
  const [assignments, setAssignments] = useState<Root[]>(initialAssignments);
  const [error, setError] = useState<{ error: string } | null>(null);
  const [isRefreshing, setIsRefreshing] = useState(false);

  async function loadAssignments() {
    setError(null);
    setIsRefreshing(true);
    try {
      const res = await fetch("/api/assignments", {
        cache: 'no-store', // Always fetch fresh data on refresh
      });
      const data = await res.json();
      if (res.ok) {
        setAssignments(data);
      } else {
        setError(data);
      }
    } catch (err) {
      setError({ error: err instanceof Error ? err.message : String(err) });
    } finally {
      setIsRefreshing(false);
    }
  }

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
        <RefreshButton onRefresh={loadAssignments} isLoading={isRefreshing} />
      </div>
    </>
  );
}
