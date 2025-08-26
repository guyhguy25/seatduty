export async function GET() {
    try {
      console.log("Attempting to fetch from n8n webhook...");
      
      // Use localhost since n8n.localhost is only resolvable from the browser
      const response = await fetch("http://localhost:5678/webhook/game-assignments", {
        cache: "no-store", // prevent caching
        // Add timeout and other fetch options
        signal: AbortSignal.timeout(10000), // 10 second timeout
      });
  
      console.log("Response status:", response.status);
      console.log("Response headers:", Object.fromEntries(response.headers.entries()));
  
      if (!response.ok) {
        const errorText = await response.text();
        console.error("n8n response error:", errorText);
        return new Response(JSON.stringify({ 
          error: "Failed to fetch from n8n", 
          status: response.status,
          statusText: response.statusText,
          details: errorText
        }), { status: 500 });
      }
  
      const data = await response.json();
      console.log("Successfully fetched data:", data);
      return new Response(JSON.stringify(data), { status: 200 });
    } catch (err) {
      console.error("Fetch error details:", err);
      return new Response(JSON.stringify({ 
        error: err.message, 
        name: err.name,
        stack: err.stack 
      }), { status: 500 });
    }
}