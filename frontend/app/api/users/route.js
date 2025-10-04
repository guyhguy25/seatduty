export async function GET() {
    try {
      console.log("Attempting to fetch users from API...");
      
      const response = await fetch("http://backend:5000/users", {
        cache: "no-store", // prevent caching
        signal: AbortSignal.timeout(10000), // 10 second timeout
      });
  
      console.log("Users response status:", response.status);
      console.log("Users response headers:", Object.fromEntries(response.headers.entries()));
  
      if (!response.ok) {
        const errorText = await response.text();
        console.error("Users API response error:", errorText);
        return new Response(JSON.stringify({ 
          error: "Failed to fetch users", 
          status: response.status,
          statusText: response.statusText,
          details: errorText
        }), { status: 500 });
      }
  
      const data = await response.json();
      console.log("Successfully fetched users:", data);
      
      // Return the users array from the response
      const users = data.users || [];
      
      return new Response(JSON.stringify(users), { status: 200 });
    } catch (err) {
      console.error("Users fetch error details:", err);
      return new Response(JSON.stringify({ 
        error: err.message, 
        name: err.name,
        stack: err.stack 
      }), { status: 500 });
    }
}
