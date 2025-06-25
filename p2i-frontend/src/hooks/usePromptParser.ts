"use client";

import { useState } from "react";

export type ParsedPrompt = {
  intent: "compare" | "search" | "recommend";
  products: string[];
  filters: Record<string, string> | null;
  attributes: string[] | null;
};

export function usePromptParser() {
  const [parsedData, setParsedData] = useState<ParsedPrompt | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const parsePrompt = async (prompt: string) => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch("/api/prompt/parse", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ prompt }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || "Failed to parse prompt");
      }

      const data = await response.json();
      setParsedData(data);
      return data;
    } catch (e) {
      const errorMessage = e instanceof Error ? e.message : "An error occurred";
      setError(errorMessage);
      setParsedData(null);
      throw e;
    } finally {
      setLoading(false);
    }
  };

  return {
    parsedData,
    error,
    loading,
    parsePrompt,
  };
}
