import AssignmentsWrapper from "./components/AssignmentsWrapper";
import HamburgerMenu from "./components/HamburgerMenu";
import { Root } from "./types/game";

async function getAssignments(): Promise<Root[]> {
  try {
    const baseUrl = process.env.VERCEL_URL 
      ? `https://${process.env.VERCEL_URL}` 
      : 'http://localhost:3000';
    
    const res = await fetch(`${baseUrl}/api/assignments`, {
      next: { 
        revalidate: 60, // Revalidate every 60 seconds
        tags: ['assignments'] 
      }
    });
    
    if (!res.ok) {
      throw new Error(`Failed to fetch assignments: ${res.status}`);
    }
    
    return res.json();
  } catch (error) {
    console.error('Error fetching assignments:', error);
    return [];
  }
}

export default async function HomePage() {
  const assignments = await getAssignments();

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      <HamburgerMenu />
      
      {/* Header */}
      <header className="pt-20 pb-6 px-4">
        <h1 className="text-3xl font-bold text-white mb-2">Games</h1>
        <p className="text-gray-400">View all available games and assignments</p>
      </header>

      {/* Main Content - Server-rendered with client-side interactivity */}
      <AssignmentsWrapper initialAssignments={assignments} />
    </div>
  );
}
