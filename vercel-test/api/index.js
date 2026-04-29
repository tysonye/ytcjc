export const config = {
  runtime: 'edge',
}

export default async function handler(request) {
  const html = `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Vercel Edge Function Status</title>
  <style>
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
      max-width: 800px;
      margin: 50px auto;
      padding: 20px;
      background-color: #f5f5f5;
    }
    .container {
      background: white;
      padding: 30px;
      border-radius: 8px;
      box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    h1 {
      color: #333;
      margin-top: 0;
    }
    .status {
      color: #28a745;
      font-weight: bold;
    }
    .info {
      margin: 10px 0;
      color: #666;
    }
  </style>
</head>
<body>
  <div class="container">
    <h1>Vercel Edge Function</h1>
    <p class="status">✓ Status: OK</p>
    <p class="info">Message: Vercel Edge Function is running</p>
    <p class="info">Timestamp: ${new Date().toISOString()}</p>
  </div>
  <script>
    window.va = window.va || function () { 
      (window.vaq = window.vaq || []).push(arguments); 
    };
  </script>
  <script defer src="/_vercel/insights/script.js"></script>
</body>
</html>`

  return new Response(html, {
    status: 200,
    headers: {
      'Content-Type': 'text/html',
      'Access-Control-Allow-Origin': '*',
    },
  })
}
