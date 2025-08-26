import Image from 'next/image';

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

interface GameCardProps {
  game: Game;
}

function daysLeft(targetDateString: string): number {
  const today: Date = new Date();
  const targetDate: Date = new Date(targetDateString);

  // Calculate difference in milliseconds
  const diffMs: number = targetDate.getTime() - today.getTime();

  // Convert milliseconds to days
  const diffDays: number = Math.ceil(diffMs / (1000 * 60 * 60 * 24));

  return diffDays;
}

function formatHebrewDate(dateString: string): string {
  const date = new Date(dateString);

  // Options for day name, day, and month in Hebrew
  const dateOptions: Intl.DateTimeFormatOptions = {
    weekday: "long",
    day: "numeric",
    month: "long",
    timeZone: "UTC" // Keep original UTC time
  };

  const formattedDate = date.toLocaleDateString("he-IL", dateOptions);

  // Keep the exact hours and minutes from the original string
  const hours = date.getUTCHours().toString().padStart(2, "0");
  const minutes = date.getUTCMinutes().toString().padStart(2, "0");
  const formattedTime = `${hours}:${minutes}`;

  return `${formattedDate} | ${formattedTime} | טוטו טרנר`;
}

export default function GameCard({ game }: GameCardProps) {
  return (
    <div className="bg-gray-800 rounded-xl border border-gray-700 overflow-hidden">
      {/* Featured Match Header */}
      <div className="bg-gray-700 px-4 py-2">
        <span className="text-gray-300 text-sm font-medium">Featured Match</span>
      </div>

      {/* League and Countdown */}
      <div className="text-center py-4 border-b border-gray-700">
        <div className="flex items-center justify-center space-x-2 mb-2">
          <span className="text-lg font-semibold">ליגת העל</span>
          <div className="w-6 h-6 bg-blue-500 rounded-full flex items-center justify-center">
            <span className="text-white text-xs">⚽</span>
          </div>
        </div>
        <div className="text-3xl font-bold text-blue-400" dir="rtl">
          {daysLeft(game.start_time)} ימים
        </div>
      </div>

      {/* Match Details */}
      <div className="p-6">
        <div className="flex items-center justify-between">
          {/* Team 1 (Away) */}
          <div className="flex-1 bg-gray-700 rounded-lg p-4 text-center">
            <div className="w-20 h-20 bg-blue-600 rounded-full mx-auto mb-3 flex items-center justify-center overflow-hidden relative">
              <Image
                src={`https://imagecache.365scores.com/image/upload/f_png,w_82,h_82,c_limit,q_auto:eco,dpr_2,d_Competitors:default1.png/v3/Competitors/${game.awayId}`}
                alt={game.away_team}
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
            <div className="text-white font-semibold text-lg mb-2">{game.away_team}</div>
            <div className="bg-black rounded-lg px-3 py-2">
              <span className="text-white font-bold">-</span>
              <span className="text-gray-400 text-sm ml-1">- 2</span>
            </div>
          </div>

          {/* VS */}
          <div className="mx-8">
            <div className="text-4xl font-bold text-white">VS</div>
            <div className="bg-black rounded-lg px-4 py-2 mt-2 text-center">
              <span className="text-white font-bold">-</span>
              <span className="text-gray-400 text-sm ml-1">- X</span>
            </div>
          </div>

          {/* Team 2 (Home) */}
          <div className="flex-1 bg-red-600 rounded-lg p-4 text-center">
            <div className="w-20 h-20 bg-white rounded-full mx-auto mb-3 flex items-center justify-center overflow-hidden relative">
              <Image
                src={`https://imagecache.365scores.com/image/upload/f_png,w_82,h_82,c_limit,q_auto:eco,dpr_2,d_Competitors:default1.png/v3/Competitors/${game.homeId}`}
                alt={game.home_team}
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
            <div className="text-white font-semibold text-lg mb-2">{game.home_team}</div>
            <div className="bg-black rounded-lg px-3 py-2">
              <span className="text-white font-bold">-</span>
              <span className="text-gray-400 text-sm ml-1">- 1</span>
            </div>
          </div>
        </div>

        {/* Match Schedule */}
        <div className="text-center mt-6 text-gray-300">
          <div className="text-lg">
            {formatHebrewDate(game.start_time)}
          </div>
        </div>

        {/* Assigned Group */}
        <div className="mt-6 p-4 bg-gray-700 rounded-lg">
          <h3 className="text-center font-semibold text-blue-400 mb-2">Assigned Group</h3>
          <div className="text-center text-white text-lg">{game.assigned_group}</div>
        </div>
      </div>

      {/* Bottom Navigation */}
      <div className="bg-gray-700 px-4 py-3">
        <div className="flex justify-around">
          <div className="text-center">
            <div className="w-8 h-8 bg-blue-500 rounded-full mx-auto mb-1 flex items-center justify-center">
              <span className="text-white text-xs font-bold">H2H</span>
            </div>
            <span className="text-orange-400 text-sm">ראש בראש</span>
          </div>
          <div className="text-center">
            <div className="w-8 h-8 bg-gray-600 rounded-full mx-auto mb-1 flex items-center justify-center">
              <span className="text-white text-xs">📊</span>
            </div>
            <span className="text-orange-400 text-sm">טבלאות</span>
          </div>
          <div className="text-center">
            <div className="w-8 h-8 bg-gray-600 rounded-full mx-auto mb-1 flex items-center justify-center">
              <span className="text-white text-xs">📈</span>
            </div>
            <span className="text-orange-400 text-sm">סטטיסטיקות</span>
          </div>
          <div className="text-center">
            <div className="w-8 h-8 bg-gray-600 rounded-full mx-auto mb-1 flex items-center justify-center">
              <span className="text-white text-xs">📋</span>
            </div>
            <span className="text-orange-400 text-sm">עמוד משחק</span>
          </div>
        </div>
      </div>
    </div>
  );
}
