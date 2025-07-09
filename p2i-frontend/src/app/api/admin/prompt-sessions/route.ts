import { NextRequest, NextResponse } from "next/server";
import { auth } from "~/server/auth";
import { getAllPromptSessions } from "~/lib/debugLogger";

export async function GET(request: NextRequest) {
  try {
    const session = await auth();

    if (!session?.user?.id) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    if (session.user.role !== "admin") {
      return NextResponse.json({ error: "Forbidden" }, { status: 403 });
    }

    const { searchParams } = new URL(request.url);
    const limit = parseInt(searchParams.get("limit") || "50", 10);

    const sessions = await getAllPromptSessions(limit);

    return NextResponse.json({ sessions });
  } catch (error) {
    console.error("Error fetching prompt sessions:", error);
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    );
  }
}
