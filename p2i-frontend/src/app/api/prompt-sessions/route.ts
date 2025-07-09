import { NextRequest, NextResponse } from "next/server";
import { auth } from "~/server/auth";
import { logPromptSession, updatePromptSession, type PromptSessionData } from "~/lib/debugLogger";

// Create a new prompt session
export async function POST(request: NextRequest) {
  try {
    const session = await auth();

    if (!session?.user?.id) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    const body: PromptSessionData = await request.json();

    // Ensure the userId matches the authenticated user
    if (body.userId !== session.user.id) {
      return NextResponse.json({ error: "Forbidden" }, { status: 403 });
    }

    const promptSession = await logPromptSession(body);

    return NextResponse.json({ success: true, session: promptSession });
  } catch (error) {
    console.error("Error creating prompt session:", error);
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    );
  }
}

// Update an existing prompt session
export async function PATCH(request: NextRequest) {
  try {
    const session = await auth();

    if (!session?.user?.id) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    const body = await request.json();
    const { sessionId, ...updates } = body;

    if (!sessionId) {
      return NextResponse.json({ error: "Session ID is required" }, { status: 400 });
    }

    const promptSession = await updatePromptSession(sessionId, updates);

    return NextResponse.json({ success: true, session: promptSession });
  } catch (error) {
    console.error("Error updating prompt session:", error);
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    );
  }
}
