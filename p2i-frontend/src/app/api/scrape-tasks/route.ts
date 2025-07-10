import { NextRequest, NextResponse } from "next/server";
import { auth } from "~/server/auth";
import { logScrapeTask, updateScrapeTask, type ScrapeTaskData } from "~/lib/debugLogger";

export async function POST(request: NextRequest) {
  try {
    const session = await auth();

    if (!session?.user?.id) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    const data: ScrapeTaskData = await request.json();

    // Validate required fields
    if (!data.productName || !data.site || !data.taskType || !data.sessionId) {
      return NextResponse.json(
        { error: "Missing required fields" },
        { status: 400 }
      );
    }

    const scrapeTask = await logScrapeTask(data);

    return NextResponse.json({
      success: true,
      task: scrapeTask,
    });
  } catch (error) {
    console.error("Failed to log scrape task:", error);
    return NextResponse.json(
      { error: "Failed to log scrape task" },
      { status: 500 }
    );
  }
}

export async function PATCH(request: NextRequest) {
  try {
    const session = await auth();

    if (!session?.user?.id) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    const { taskId, ...updates } = await request.json();

    if (!taskId) {
      return NextResponse.json(
        { error: "Task ID is required" },
        { status: 400 }
      );
    }

    const scrapeTask = await updateScrapeTask(taskId, updates);

    return NextResponse.json({
      success: true,
      task: scrapeTask,
    });
  } catch (error) {
    console.error("Failed to update scrape task:", error);
    return NextResponse.json(
      { error: "Failed to update scrape task" },
      { status: 500 }
    );
  }
}
