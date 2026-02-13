import { NextResponse } from "next/server";

export async function POST(req: Request) {
    try {
        const body = await req.json();

        // Proxy to local FastAPI backend
        const localResponse = await fetch("http://localhost:8080/api/chat/dual-loop", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(body)
        });

        if (!localResponse.ok) {
            const errorText = await localResponse.text();
            return NextResponse.json(
                { error: `Backend error: ${localResponse.status}`, details: errorText },
                { status: localResponse.status }
            );
        }

        return new Response(localResponse.body, {
            headers: {
                "Content-Type": "text/plain; charset=utf-8",
            },
        });
    } catch (error: any) {
        console.error("Dual-Loop Proxy Error:", error);
        return NextResponse.json(
            { error: "Failed to connect to dual-loop backend", details: error.message },
            { status: 500 }
        );
    }
}
