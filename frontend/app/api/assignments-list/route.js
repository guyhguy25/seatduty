export async function GET() {
    try {
      console.log("Attempting to fetch assignments from API...");
      
      const response = await fetch("http://localhost:5000/assignments", {
        cache: "no-store", // prevent caching
        signal: AbortSignal.timeout(10000), // 10 second timeout
      });
  
      console.log("Assignments response status:", response.status);
      console.log("Assignments response headers:", Object.fromEntries(response.headers.entries()));
  
      if (!response.ok) {
        const errorText = await response.text();
        console.error("Assignments API response error:", errorText);
        return new Response(JSON.stringify({ 
          error: "Failed to fetch assignments", 
          status: response.status,
          statusText: response.statusText,
          details: errorText
        }), { status: 500 });
      }
  
      const data = await response.json();
      console.log("Successfully fetched assignments:", data);
      
      // Return the assignments array from the response
      const assignments = data.assignments || [];
      
      return new Response(JSON.stringify(assignments), { status: 200 });
    } catch (err) {
      console.error("Assignments fetch error details:", err);
      return new Response(JSON.stringify({ 
        error: err.message, 
        name: err.name,
        stack: err.stack 
      }), { status: 500 });
    }
}
