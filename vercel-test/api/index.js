export const config = {
  runtime: 'edge',
}

export default async function handler(request) {
  return new Response(JSON.stringify({ 
    status: 'ok',
    message: 'Vercel Edge Function is running',
    timestamp: new Date().toISOString()
  }), {
    status: 200,
    headers: {
      'Content-Type': 'application/json',
      'Access-Control-Allow-Origin': '*',
    },
  })
}
