"use client";

import { useState, useEffect } from "react";
import HamburgerMenu from "../components/HamburgerMenu";
import { Assignment } from "../types/game";

export default function AssignmentsPage() {
  const [assignments, setAssignments] = useState<Assignment[] | null>(null);
  const [error, setError] = useState<{ error: string } | null>(null);
  const [loading, setLoading] = useState(true);

  async function loadAssignments() {
    setError(null);
    setLoading(true);
    try {
      const res = await fetch("/api/assignments-list");
      const data = await res.json();
      if (res.ok) {
        setAssignments(data);
      } else {
        setError(data);
      }
    } catch (err) {
      setError({ error: err instanceof Error ? err.message : String(err) });
    } finally {
      setLoading(false);
    }
  }

  // Load assignments on component mount
  useEffect(() => {
    loadAssignments();
  }, []);

  const formatDate = (dateString: string) => {
    try {
      return new Date(dateString).toLocaleDateString("he-IL", {
        year: "numeric",
        month: "short",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
        timeZone: "Asia/Jerusalem"
      });
    } catch {
      return dateString;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'assigned':
        return 'bg-yellow-900 text-yellow-100';
      case 'completed':
        return 'bg-green-900 text-green-100';
      case 'cancelled':
        return 'bg-red-900 text-red-100';
      default:
        return 'bg-gray-700 text-gray-300';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status.toLowerCase()) {
      case 'assigned':
        return '📋';
      case 'completed':
        return '✅';
      case 'cancelled':
        return '❌';
      default:
        return '❓';
    }
  };

  return (
    <div className="min-h-screen bg-gray-900">
      <HamburgerMenu />
      
      {/* Header */}
      <div className="pt-20 pb-6 px-4">
        <h1 className="text-3xl font-bold text-white mb-2">Assignments</h1>
        <p className="text-gray-400">View all game assignments and their status</p>
      </div>

      {/* Error Display */}
      {error && (
        <div className="mx-4 mt-4 p-4 bg-red-900 border border-red-600 text-red-100 rounded-lg">
          <h3 className="font-bold">Error:</h3>
          <pre className="text-sm">{JSON.stringify(error, null, 2)}</pre>
        </div>
      )}

      {/* Loading State */}
      {loading && (
        <div className="mx-4 mt-4 p-8 text-center">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
          <p className="text-gray-400 mt-2">Loading assignments...</p>
        </div>
      )}

      {/* Assignments List */}
      {assignments && !loading && (
        <div className="px-4 space-y-4">
          {assignments.map((assignment) => (
            <div key={assignment.id} className="bg-gray-800 rounded-xl border border-gray-700 p-6">
              {/* Assignment Header */}
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center space-x-3">
                  <div className="text-2xl">{getStatusIcon(assignment.status)}</div>
                  <div>
                    <h3 className="text-lg font-semibold text-white">
                      {assignment.home_competitor_name} vs {assignment.away_competitor_name}
                    </h3>
                    <p className="text-sm text-gray-400">Game ID: {assignment.game_id}</p>
                  </div>
                </div>
                <div className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(assignment.status)}`}>
                  {assignment.status}
                </div>
              </div>

              {/* Assignment Details */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                <div className="bg-gray-700 rounded-lg p-4">
                  <div className="text-sm text-gray-400 mb-1">Assigned User</div>
                  <div className="flex items-center space-x-2">
                    <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center">
                      <span className="text-white text-sm font-bold">
                        {assignment.user_name.charAt(0).toUpperCase()}
                      </span>
                    </div>
                    <span className="text-white font-medium">{assignment.user_name}</span>
                  </div>
                </div>
                <div className="bg-gray-700 rounded-lg p-4">
                  <div className="text-sm text-gray-400 mb-1">User ID</div>
                  <div className="text-white font-medium">{assignment.user_id}</div>
                </div>
              </div>

              {/* Time Information */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="bg-gray-700 rounded-lg p-4">
                  <div className="text-sm text-gray-400 mb-1">Game Start Time</div>
                  <div className="text-white">{formatDate(assignment.start_time)}</div>
                </div>
                <div className="bg-gray-700 rounded-lg p-4">
                  <div className="text-sm text-gray-400 mb-1">Assigned At</div>
                  <div className="text-white">{formatDate(assignment.assigned_at)}</div>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="mt-4 flex space-x-3">
                <a
                  href={`https://www.365scores.com/he/football/match/${assignment.game_id}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex-1 bg-blue-600 hover:bg-blue-700 text-white text-center py-2 px-4 rounded-lg font-medium transition-colors"
                >
                  View Game
                </a>
                <button className="flex-1 bg-gray-600 hover:bg-gray-700 text-white text-center py-2 px-4 rounded-lg font-medium transition-colors">
                  Update Status
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Empty State */}
      {assignments && assignments.length === 0 && !loading && (
        <div className="mx-4 mt-8 p-8 text-center">
          <div className="text-6xl mb-4">📋</div>
          <h3 className="text-xl font-semibold text-white mb-2">No Assignments Found</h3>
          <p className="text-gray-400">There are no assignments to display at the moment.</p>
        </div>
      )}

      {/* Refresh Button */}
      <div className="flex justify-center mt-8 mb-4">
        <button
          onClick={loadAssignments}
          disabled={loading}
          className="px-6 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white rounded-lg font-medium transition-colors"
        >
          {loading ? 'Loading...' : 'Refresh'}
        </button>
      </div>
    </div>
  );
}
