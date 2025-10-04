"use client";

import Image from 'next/image';
import { useState, useEffect } from 'react';
import { Root } from '../types/game';

interface GameCardProps {
  game: Root;
}

function getTimeUntilMatch(targetDateString: string): string {
  const today: Date = new Date();
  const targetDate: Date = new Date(targetDateString);

  // Calculate difference in milliseconds
  const diffMs: number = targetDate.getTime() - today.getTime();

  if (diffMs < 0) {
    return "התחיל";
  }

  // Convert to hours and minutes
  const totalHours = Math.floor(diffMs / (1000 * 60 * 60));
  const totalMinutes = Math.floor(diffMs / (1000 * 60));
  const minutes = totalMinutes % 60;

  if (totalHours >= 24) {
    const days = Math.floor(totalHours / 24);
    const hours = totalHours % 24;
    return `${days} ימים ${hours} שעות`;
  } else if (totalHours > 0) {
    return `${totalHours} שעות ${minutes} דקות`;
  } else {
    return `${minutes} דקות`;
  }
}

function formatHebrewDate(dateString: string): string {
  const date = new Date(dateString);

  // Options for day name, day, and month in Hebrew
  const dateOptions: Intl.DateTimeFormatOptions = {
    weekday: "long",
    day: "numeric",
    month: "long",
    timeZone: "Asia/Jerusalem" // Use Jerusalem timezone
  };

  const formattedDate = date.toLocaleDateString("he-IL", dateOptions);

  // Format time in Jerusalem timezone
  const timeOptions: Intl.DateTimeFormatOptions = {
    hour: "2-digit",
    minute: "2-digit",
    timeZone: "Asia/Jerusalem"
  };
  const formattedTime = date.toLocaleTimeString("he-IL", timeOptions);

  return `${formattedDate} | ${formattedTime} | טוטו טרנר`;
}

export default function GameCard({ game }: GameCardProps) {
  const [timeUntilMatch, setTimeUntilMatch] = useState<string>("");
  const [isClient, setIsClient] = useState(false);

  useEffect(() => {
    setIsClient(true);
    const updateTime = () => {
      setTimeUntilMatch(getTimeUntilMatch(game.startTime));
    };
    
    updateTime();
    const interval = setInterval(updateTime, 60000); // Update every minute
    
    return () => clearInterval(interval);
  }, [game.startTime]);

  return (
    <div className="bg-gray-800 rounded-xl border border-gray-700 overflow-hidden">
      {/* Featured Match Header */}
      <div className="bg-gray-700 px-4 py-2">
        <span className="text-gray-300 text-sm font-medium">Featured Match</span>
      </div>

      {/* League and Countdown */}
      <div className="text-center py-4 border-b border-gray-700">
        <div className="flex items-center justify-center space-x-2 mb-2">
          <span className="text-lg font-semibold">{game.competitionDisplayName}</span>
          <div className="w-6 h-6 bg-blue-500 rounded-full flex items-center justify-center">
            <span className="text-white text-xs">⚽</span>
          </div>
        </div>
        <div className="text-3xl font-bold text-blue-400" dir="rtl">
          {isClient ? timeUntilMatch : "טוען..."}
        </div>
      </div>

      {/* Match Details */}
      <div className="p-6">
        <div className="flex items-center justify-between">
          {/* Team 1 (Away) */}
          <div className="flex-1 bg-gray-700 rounded-lg p-4 text-center">
            <div className="w-20 h-20 bg-blue-600 rounded-full mx-auto mb-3 flex items-center justify-center overflow-hidden relative">
              <Image
                src={`https://imagecache.365scores.com/image/upload/f_png,w_82,h_82,c_limit,q_auto:eco,dpr_2,d_Competitors:default1.png/v3/Competitors/${game.awayCompetitor.id}`}
                alt={game.awayCompetitor.name}
                width={80}
                height={80}
                className="rounded-full object-cover"
                onError={() => {
                  // Fallback handled by CSS
                }}
              />
              <div className="absolute inset-0 bg-blue-600 rounded-full flex items-center justify-center fallback-icon">
                <span className="text-white text-2xl">⚽</span>
              </div>
            </div>
            <div className="text-white font-semibold text-lg mb-2">{game.awayCompetitor.name}</div>
            <div className="bg-black rounded-lg px-3 py-2">
              <span className="text-white font-bold">
                {game.awayCompetitor.score >= 0 ? game.awayCompetitor.score : '-'}
              </span>
              <span className="text-gray-400 text-sm ml-1">- 2</span>
            </div>
          </div>

          {/* VS - Desktop with odds */}
          <div className="mx-8 hidden md:flex flex-col items-center justify-center">
            <div className="text-4xl font-bold text-white">VS</div>
            {game.odds && game.odds.options && game.odds.options.length > 0 && (
              <div className="bg-black rounded-lg px-4 py-2 mt-2 text-center">
                <div className="text-xs text-gray-400 mb-1">יחס</div>
                <div className="flex justify-center space-x-2 text-sm">
                  {game.odds.options.slice(0, 3).reverse().map((option, index) => (
                    <span key={index} className="text-white font-bold">
                      {option.rate.decimal.toFixed(2)}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* VS - Mobile without odds */}
          <div className="mx-4 md:hidden flex items-center justify-center">
            <div className="text-4xl font-bold text-white">VS</div>
          </div>

          {/* Team 2 (Home) */}
          <div className="flex-1 bg-red-600 rounded-lg p-4 text-center">
            <div className="w-20 h-20 bg-white rounded-full mx-auto mb-3 flex items-center justify-center overflow-hidden relative">
              <Image
                src={`https://imagecache.365scores.com/image/upload/f_png,w_82,h_82,c_limit,q_auto:eco,dpr_2,d_Competitors:default1.png/v3/Competitors/${game.homeCompetitor.id}`}
                alt={game.homeCompetitor.name}
                width={80}
                height={80}
                className="rounded-full object-cover"
                onError={() => {
                  // Fallback handled by CSS
                }}
              />
              <div className="absolute inset-0 bg-white rounded-full flex items-center justify-center fallback-icon">
                <span className="text-red-600 text-2xl">⚽</span>
              </div>
            </div>
            <div className="text-white font-semibold text-lg mb-2">{game.homeCompetitor.name}</div>
            <div className="bg-black rounded-lg px-3 py-2">
              <span className="text-white font-bold">
                {game.homeCompetitor.score >= 0 ? game.homeCompetitor.score : '-'}
              </span>
              <span className="text-gray-400 text-sm ml-1">- 1</span>
            </div>
          </div>
        </div>

        {/* Odds - Mobile only */}
        {game.odds && game.odds.options && game.odds.options.length > 0 && (
          <div className="md:hidden mt-4 text-center">
            <div className="bg-black rounded-lg px-4 py-2 inline-block">
              <div className="text-xs text-gray-400 mb-1">יחס</div>
              <div className="flex justify-center space-x-2 text-sm">
                {game.odds.options.slice(0, 3).reverse().map((option, index) => (
                  <span key={index} className="text-white font-bold">
                    {option.rate.decimal.toFixed(2)}
                  </span>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Match Schedule */}
        <div className="text-center mt-6 text-gray-300">
          <div className="text-lg">
            {formatHebrewDate(game.startTime)}
          </div>
          {game.statusText && (
            <div className="text-sm text-blue-400 mt-2">
              {game.statusText}
            </div>
          )}
        </div>

        {/* Assigned Group */}
        <div className="mt-6 p-4 bg-gray-700 rounded-lg">
          <h3 className="text-center font-semibold text-blue-400 mb-2">Assigned Users</h3>
          <div className="text-center text-white text-lg">
            {game.assigned_user_names.length > 0 ? game.assigned_user_names.join(', ') : 'No assignments'}
          </div>
        </div>
      </div>

      {/* Bottom Navigation */}
      <div className="bg-gray-700 px-4 py-3">
        <div className="flex justify-around">
          <a 
            href={`https://www.365scores.com/he/football/league/premier-league-${game.competitionId}/standings`}
            target="_blank"
            rel="noopener noreferrer"
            className="text-center hover:opacity-80 transition-opacity cursor-pointer"
          >
            <div className="w-8 h-8 bg-gray-600 rounded-full mx-auto mb-1 flex items-center justify-center">
              <span className="text-white text-xs">📊</span>
            </div>
            <span className="text-orange-400 text-sm">טבלאות</span>
          </a>
          <a 
            href={`https://www.365scores.com/he/football/match/premier-league-${game.competitionId}/${game.awayCompetitor.nameForURL}-${game.homeCompetitor.nameForURL}-${game.awayCompetitor.id}-${game.homeCompetitor.id}-${game.id}#id=${game.id}`}
            target="_blank"
            rel="noopener noreferrer"
            className="text-center hover:opacity-80 transition-opacity cursor-pointer"
          >
            <div className="w-8 h-8 bg-gray-600 rounded-full mx-auto mb-1 flex items-center justify-center">
              <span className="text-white text-xs">📋</span>
            </div>
            <span className="text-orange-400 text-sm">עמוד משחק</span>
          </a>
        </div>
      </div>
    </div>
  );
}
