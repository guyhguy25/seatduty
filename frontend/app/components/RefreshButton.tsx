"use client";

interface RefreshButtonProps {
  onRefresh: () => Promise<void>;
  isLoading?: boolean;
}

export default function RefreshButton({ onRefresh, isLoading = false }: RefreshButtonProps) {
  const handleClick = async () => {
    await onRefresh();
  };

  return (
    <button
      onClick={handleClick}
      disabled={isLoading}
      className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg disabled:opacity-50 transition-colors"
    >
      {isLoading ? "Loading..." : "Load Assignments"}
    </button>
  );
}
