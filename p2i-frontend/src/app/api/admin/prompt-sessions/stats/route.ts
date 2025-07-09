import { NextResponse } from "next/server";
import { auth } from "~/server/auth";
import { getPromptSessionStats } from "~/lib/debugLogger";

export async function GET() {
  try {
    const session = await auth();

    if (!session?.user?.id) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    if (session.user.role !== "admin") {
      return NextResponse.json({ error: "Forbidden" }, { status: 403 });
    }

    const stats = await getPromptSessionStats();

    return NextResponse.json({ stats });
  } catch (error) {
    console.error("Error fetching prompt session stats:", error);
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    );
  }
}
