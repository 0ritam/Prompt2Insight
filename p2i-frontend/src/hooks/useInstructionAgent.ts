"use client";

import { useState } from "react";
import { type ParsedPrompt, type ScrapeTask } from "~/types";

export function useInstructionAgent() {
  const [tasks, setTasks] = useState<ScrapeTask[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const fetchTasks = async (parsedPrompt: ParsedPrompt) => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch("/api/route-instruction", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(parsedPrompt),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || "Failed to generate scrape tasks");
      }

      const data = await response.json();
      setTasks(data);
    } catch (e) {
      const errorMessage = e instanceof Error ? e.message : "An error occurred";
      setError(errorMessage);
      setTasks(null);
      throw e;
    } finally {
      setLoading(false);
    }
  };

  return {
    tasks,
    error,
    loading,
    fetchTasks,
  };
}
