"use client";

import { useState, useEffect } from "react";
import HamburgerMenu from "../components/HamburgerMenu";
import { User } from "../types/game";

export default function UsersPage() {
  const [users, setUsers] = useState<User[] | null>(null);
  const [error, setError] = useState<{ error: string } | null>(null);
  const [loading, setLoading] = useState(true);

  async function loadUsers() {
    setError(null);
    setLoading(true);
    try {
      const res = await fetch("/api/users");
      const data = await res.json();
      if (res.ok) {
        setUsers(data);
      } else {
        setError(data);
      }
    } catch (err) {
      setError({ error: err instanceof Error ? err.message : String(err) });
    } finally {
      setLoading(false);
    }
  }

  // Load users on component mount
  useEffect(() => {
    loadUsers();
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

  return (
    <div className="min-h-screen bg-gray-900">
      <HamburgerMenu />
      
      {/* Header */}
      <div className="pt-20 pb-6 px-4">
        <h1 className="text-3xl font-bold text-white mb-2">Users</h1>
        <p className="text-gray-400">Manage and view user details</p>
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
          <p className="text-gray-400 mt-2">Loading users...</p>
        </div>
      )}

      {/* Users List */}
      {users && !loading && (
        <div className="px-4 space-y-4">
          {users.map((user) => (
            <div key={user.id} className="bg-gray-800 rounded-xl border border-gray-700 p-6">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center space-x-4">
                  <div className="w-12 h-12 bg-blue-500 rounded-full flex items-center justify-center">
                    <span className="text-white text-lg font-bold">
                      {user.name.charAt(0).toUpperCase()}
                    </span>
                  </div>
                  <div>
                    <h3 className="text-xl font-semibold text-white">{user.name}</h3>
                    <p className="text-gray-400">{user.email}</p>
                  </div>
                </div>
                <div className={`px-3 py-1 rounded-full text-sm font-medium ${
                  user.is_active 
                    ? 'bg-green-900 text-green-100' 
                    : 'bg-red-900 text-red-100'
                }`}>
                  {user.is_active ? 'Active' : 'Inactive'}
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-gray-700 rounded-lg p-4">
                  <div className="text-sm text-gray-400 mb-1">Games Assigned</div>
                  <div className="text-2xl font-bold text-blue-400">{user.total_games_assigned}</div>
                </div>
                <div className="bg-gray-700 rounded-lg p-4">
                  <div className="text-sm text-gray-400 mb-1">Games Completed</div>
                  <div className="text-2xl font-bold text-green-400">{user.total_games_completed}</div>
                </div>
                <div className="bg-gray-700 rounded-lg p-4">
                  <div className="text-sm text-gray-400 mb-1">Last Assigned</div>
                  <div className="text-sm text-white">{formatDate(user.last_assigned_at)}</div>
                </div>
              </div>

              {/* Completion Rate */}
              <div className="mt-4">
                <div className="flex justify-between text-sm text-gray-400 mb-2">
                  <span>Completion Rate</span>
                  <span>
                    {user.total_games_assigned > 0 
                      ? Math.round((user.total_games_completed / user.total_games_assigned) * 100)
                      : 0}%
                  </span>
                </div>
                <div className="w-full bg-gray-700 rounded-full h-2">
                  <div 
                    className="bg-blue-500 h-2 rounded-full transition-all duration-300"
                    style={{
                      width: `${user.total_games_assigned > 0 
                        ? (user.total_games_completed / user.total_games_assigned) * 100
                        : 0}%`
                    }}
                  ></div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Refresh Button */}
      <div className="flex justify-center mt-8 mb-4">
        <button
          onClick={loadUsers}
          disabled={loading}
          className="px-6 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white rounded-lg font-medium transition-colors"
        >
          {loading ? 'Loading...' : 'Refresh'}
        </button>
      </div>
    </div>
  );
}
