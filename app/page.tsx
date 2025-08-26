import AssignmentsWrapper from "./components/AssignmentsWrapper";

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gray-900 text-white">
      {/* Header */}
      <header className="bg-gray-800 border-b border-gray-700 p-4">
        <h1 className="text-2xl font-bold text-center">Saving Duty Assignments</h1>
      </header>

      {/* Main Content - Client-side wrapper for interactivity */}
      <AssignmentsWrapper />
    </div>
  );
}
