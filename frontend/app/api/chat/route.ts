// app/api/chat/route.ts

import { NextRequest, NextResponse } from 'next/server';

// **IMPORTANT**: Replace this with the actual URL of your Python ADK server!
const PYTHON_AGENT_API_URL = process.env.PYTHON_AGENT_API_URL || 'http://localhost:8000/chat'; 

export async function POST(req: NextRequest) {
  try {
    const { message, user_id } = await req.json();

    if (!message || !user_id) {
      return NextResponse.json({ error: 'Missing message or user ID' }, { status: 400 });
    }

    // 1. Forward the request to your Python backend (which runs the ADK agent)
    const pythonResponse = await fetch(PYTHON_AGENT_API_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id, message }),
    });

    if (!pythonResponse.ok) {
      // Handle non-200 responses from the Python server
      const errorText = await pythonResponse.text();
      throw new Error(`Python API Error: ${pythonResponse.status} - ${errorText}`);
    }

    // 2. Return the data back to the client component
    const data = await pythonResponse.json();
    return NextResponse.json(data);

  } catch (error) {
    console.error('Next.js API Error:', error);
    return NextResponse.json({ error: 'An internal server error occurred.' }, { status: 500 });
  }
}