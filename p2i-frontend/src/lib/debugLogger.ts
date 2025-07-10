import { db } from "~/server/db";

export type PromptSessionStatus = "pending" | "parsed" | "done" | "error";
export type ScrapeTaskStatus = "pending" | "scraped" | "error";

export interface PromptSessionData {
  sessionId: string;
  userId: string;
  originPrompt: string;
  status: PromptSessionStatus;
  resultData?: any;
  errorMessage?: string;
}

export interface ScrapeTaskData {
  taskId?: string;
  productName: string;
  site: string;
  taskType: string;
  status: ScrapeTaskStatus;
  sessionId: string;
  resultData?: any;
  errorMessage?: string;
}

/**
 * Log a new prompt session to the database
 * @param data The prompt session data to log
 * @returns The created prompt session record
 */
export async function logPromptSession(data: PromptSessionData) {
  try {
    const promptSession = await db.promptSession.create({
      data: {
        sessionId: data.sessionId,
        userId: data.userId,
        originPrompt: data.originPrompt,
        status: data.status,
        resultData: data.resultData ? JSON.stringify(data.resultData) : null,
        errorMessage: data.errorMessage,
      },
    });

    return promptSession;
  } catch (error) {
    console.error("Failed to log prompt session:", error);
    throw error;
  }
}

/**
 * Update an existing prompt session status and results
 * @param sessionId The session ID to update
 * @param updates The fields to update
 * @returns The updated prompt session record
 */
export async function updatePromptSession(
  sessionId: string,
  updates: Partial<{
    status: PromptSessionStatus;
    resultData: any;
    errorMessage: string;
  }>
) {
  try {
    const promptSession = await db.promptSession.update({
      where: { sessionId },
      data: {
        ...updates,
        resultData: updates.resultData ? JSON.stringify(updates.resultData) : undefined,
        updatedAt: new Date(),
      },
    });

    return promptSession;
  } catch (error) {
    console.error("Failed to update prompt session:", error);
    throw error;
  }
}

/**
 * Get all prompt sessions for a specific user
 * @param userId The user ID to fetch sessions for
 * @param limit Maximum number of sessions to return
 * @returns Array of prompt sessions
 */
export async function getUserPromptSessions(userId: string, limit: number = 50) {
  try {
    const sessions = await db.promptSession.findMany({
      where: { userId },
      orderBy: { createdAt: "desc" },
      take: limit,
      include: {
        user: {
          select: {
            name: true,
            email: true,
          },
        },
      },
    });

    return sessions;
  } catch (error) {
    console.error("Failed to fetch user prompt sessions:", error);
    throw error;
  }
}

/**
 * Get all prompt sessions (admin only)
 * @param limit Maximum number of sessions to return
 * @returns Array of prompt sessions with user info
 */
export async function getAllPromptSessions(limit: number = 100) {
  try {
    const sessions = await db.promptSession.findMany({
      orderBy: { createdAt: "desc" },
      take: limit,
      include: {
        user: {
          select: {
            name: true,
            email: true,
            role: true,
          },
        },
      },
    });

    return sessions;
  } catch (error) {
    console.error("Failed to fetch all prompt sessions:", error);
    throw error;
  }
}

/**
 * Get prompt session statistics
 * @returns Statistics object with counts and percentages
 */
export async function getPromptSessionStats() {
  try {
    const [total, pending, parsed, done, error] = await Promise.all([
      db.promptSession.count(),
      db.promptSession.count({ where: { status: "pending" } }),
      db.promptSession.count({ where: { status: "parsed" } }),
      db.promptSession.count({ where: { status: "done" } }),
      db.promptSession.count({ where: { status: "error" } }),
    ]);

    return {
      total,
      pending,
      parsed,
      done,
      error,
      successRate: total > 0 ? ((done / total) * 100).toFixed(1) : "0",
    };
  } catch (error) {
    console.error("Failed to fetch prompt session stats:", error);
    throw error;
  }
}

/**
 * Log a new scraper task to the database
 * @param data The scraper task data to log
 * @returns The created scraper task record
 */
export async function logScrapeTask(data: ScrapeTaskData) {
  try {
    const scrapeTask = await db.scrapeTaskLog.create({
      data: {
        taskId: data.taskId || undefined, // Will use default cuid() if not provided
        productName: data.productName,
        site: data.site,
        taskType: data.taskType,
        status: data.status,
        sessionId: data.sessionId,
        resultData: data.resultData ? JSON.stringify(data.resultData) : null,
        errorMessage: data.errorMessage,
      },
    });

    return scrapeTask;
  } catch (error) {
    console.error("Failed to log scrape task:", error);
    throw error;
  }
}

/**
 * Update an existing scraper task status and results
 * @param taskId The task ID to update
 * @param updates The fields to update
 * @returns The updated scraper task record
 */
export async function updateScrapeTask(
  taskId: string,
  updates: Partial<{
    status: ScrapeTaskStatus;
    resultData: any;
    errorMessage: string;
  }>
) {
  try {
    const scrapeTask = await db.scrapeTaskLog.update({
      where: { taskId },
      data: {
        ...updates,
        resultData: updates.resultData ? JSON.stringify(updates.resultData) : undefined,
        updatedAt: new Date(),
      },
    });

    return scrapeTask;
  } catch (error) {
    console.error("Failed to update scrape task:", error);
    throw error;
  }
}

/**
 * Get all scraper tasks (admin only)
 * @param limit Maximum number of tasks to return
 * @returns Array of scraper tasks with session info
 */
export async function getAllScrapeTasks(limit: number = 100) {
  try {
    const tasks = await db.scrapeTaskLog.findMany({
      orderBy: { createdAt: "desc" },
      take: limit,
      include: {
        session: {
          select: {
            sessionId: true,
            originPrompt: true,
            user: {
              select: {
                name: true,
                email: true,
              },
            },
          },
        },
      },
    });

    return tasks;
  } catch (error) {
    console.error("Failed to fetch all scraper tasks:", error);
    throw error;
  }
}

/**
 * Get scraper task statistics
 * @returns Statistics object with counts and percentages
 */
export async function getScrapeTaskStats() {
  try {
    const [total, pending, scraped, error] = await Promise.all([
      db.scrapeTaskLog.count(),
      db.scrapeTaskLog.count({ where: { status: "pending" } }),
      db.scrapeTaskLog.count({ where: { status: "scraped" } }),
      db.scrapeTaskLog.count({ where: { status: "error" } }),
    ]);

    return {
      total,
      pending,
      scraped,
      error,
      successRate: total > 0 ? ((scraped / total) * 100).toFixed(1) : "0",
    };
  } catch (error) {
    console.error("Failed to fetch scraper task stats:", error);
    throw error;
  }
}
