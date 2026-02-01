/**
 * API proxy route to forward requests to backend
 *
 * This avoids CORS issues by routing all API calls through Next.js
 */
import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function GET(request: NextRequest, { params }: { params: { path: string[] } }) {
  const path = params.path.join('/');
  const url = `${BACKEND_URL}/api/${path}${request.nextUrl.search}`;

  const response = await fetch(url, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      // Forward authorization header if present
      ...(request.headers.get('authorization') && {
        Authorization: request.headers.get('authorization')!,
      }),
    },
  });

  const data = await response.json();
  return NextResponse.json(data, { status: response.status });
}

export async function POST(request: NextRequest, { params }: { params: { path: string[] } }) {
  const path = params.path.join('/');
  const url = `${BACKEND_URL}/api/${path}`;

  const body = await request.text();

  const response = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...(request.headers.get('authorization') && {
        Authorization: request.headers.get('authorization')!,
      }),
    },
    body,
  });

  const data = await response.json();
  return NextResponse.json(data, { status: response.status });
}

export async function PATCH(request: NextRequest, { params }: { params: { path: string[] } }) {
  const path = params.path.join('/');
  const url = `${BACKEND_URL}/api/${path}`;

  const body = await request.text();

  const response = await fetch(url, {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
      ...(request.headers.get('authorization') && {
        Authorization: request.headers.get('authorization')!,
      }),
    },
    body,
  });

  const data = await response.json();
  return NextResponse.json(data, { status: response.status });
}

export async function DELETE(request: NextRequest, { params }: { params: { path: string[] } }) {
  const path = params.path.join('/');
  const url = `${BACKEND_URL}/api/${path}`;

  const response = await fetch(url, {
    method: 'DELETE',
    headers: {
      ...(request.headers.get('authorization') && {
        Authorization: request.headers.get('authorization')!,
      }),
    },
  });

  const data = await response.json();
  return NextResponse.json(data, { status: response.status });
}
