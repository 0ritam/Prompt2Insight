import { db } from "~/server/db";

export type PromptSessionStatus = "pending" | "parsed" | "done" | "error";

export interface PromptSessionData {
  sessionId: string;
  userId: string;
  originPrompt: string;
  status: PromptSessionStatus;
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
