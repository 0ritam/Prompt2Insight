"use client";

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
 * Log a new prompt session via API
 * @param data The prompt session data to log
 * @returns Promise with the response
 */
export async function logPromptSession(data: PromptSessionData) {
  try {
    const response = await fetch("/api/prompt-sessions", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || "Failed to log prompt session");
    }

    return await response.json();
  } catch (error) {
    console.error("Failed to log prompt session:", error);
    // Don't throw error to avoid breaking the main flow
    return { success: false, error };
  }
}

/**
 * Update an existing prompt session via API
 * @param sessionId The session ID to update
 * @param updates The fields to update
 * @returns Promise with the response
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
    const response = await fetch("/api/prompt-sessions", {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        sessionId,
        ...updates,
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || "Failed to update prompt session");
    }

    return await response.json();
  } catch (error) {
    console.error("Failed to update prompt session:", error);
    // Don't throw error to avoid breaking the main flow
    return { success: false, error };
  }
}

/**
 * Log a new scrape task via API
 * @param data The scrape task data to log
 * @returns Promise with the response
 */
export async function logScrapeTask(data: ScrapeTaskData) {
  try {
    const response = await fetch("/api/scrape-tasks", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || "Failed to log scrape task");
    }

    return await response.json();
  } catch (error) {
    console.error("Failed to log scrape task:", error);
    // Don't throw error to avoid breaking the main flow
    return { success: false, error };
  }
}

/**
 * Update an existing scrape task via API
 * @param taskId The task ID to update
 * @param updates The fields to update
 * @returns Promise with the response
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
    const response = await fetch("/api/scrape-tasks", {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        taskId,
        ...updates,
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || "Failed to update scrape task");
    }

    return await response.json();
  } catch (error) {
    console.error("Failed to update scrape task:", error);
    // Don't throw error to avoid breaking the main flow
    return { success: false, error };
  }
}
