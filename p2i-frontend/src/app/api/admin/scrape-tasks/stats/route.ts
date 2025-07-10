import { NextResponse } from "next/server";
import { auth } from "~/server/auth";
import { getScrapeTaskStats } from "~/lib/debugLogger";

export async function GET() {
  try {
    const session = await auth();

    if (!session?.user?.id) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    if (session.user.role !== "admin") {
      return NextResponse.json({ error: "Forbidden" }, { status: 403 });
    }

    const stats = await getScrapeTaskStats();

    return NextResponse.json(stats);
  } catch (error) {
    console.error("Failed to fetch scrape task stats:", error);
    return NextResponse.json(
      { error: "Failed to fetch scrape task stats" },
      { status: 500 }
    );
  }
}
