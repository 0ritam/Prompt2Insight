"use client";

import { v4 as uuidv4 } from "uuid";

/**
 * Generate a unique session ID using UUID v4
 * @returns A unique session ID string
 */
export function generateSessionId(): string {
  return uuidv4();
}

/**
 * Store session ID in sessionStorage for client-side persistence
 * @param sessionId The session ID to store
 */
export function storeSessionId(sessionId: string): void {
  if (typeof window !== "undefined") {
    sessionStorage.setItem("currentPromptSessionId", sessionId);
  }
}

/**
 * Retrieve the current session ID from sessionStorage
 * @returns The stored session ID or null if not found
 */
export function getCurrentSessionId(): string | null {
  if (typeof window !== "undefined") {
    return sessionStorage.getItem("currentPromptSessionId");
  }
  return null;
}

/**
 * Clear the current session ID from sessionStorage
 */
export function clearCurrentSessionId(): void {
  if (typeof window !== "undefined") {
    sessionStorage.removeItem("currentPromptSessionId");
  }
}

/**
 * Generate a new session ID and store it
 * @returns The newly generated session ID
 */
export function createNewSession(): string {
  const sessionId = generateSessionId();
  storeSessionId(sessionId);
  return sessionId;
}
