"use client";

import { useState } from "react";
import { toast } from "sonner";
import { PromptInsightPanel } from "~/components/prompt-insight-panel";
import { PromptDebugger } from "~/components/prompt-debugger";
import { type ParsedPrompt, type ScrapeSession } from "~/types";

export default function DashboardPage() {
  const [session, setSession] = useState<ScrapeSession | null>(null);
  const [loading, setLoading] = useState(false);

  const handlePromptSubmit = async (prompt: string) => {
    try {
      setLoading(true);

      // First, parse the prompt
      const parseResponse = await fetch("/api/prompt/parse", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt }),
      });

      if (!parseResponse.ok) {
        const error = await parseResponse.json();
        throw new Error(error.message || "Failed to parse prompt");
      }

      const parsedPrompt: ParsedPrompt = await parseResponse.json();

      // Then, get scraping instructions
      const instructionResponse = await fetch("/api/route-instruction", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(parsedPrompt),
      });

      if (!instructionResponse.ok) {
        const error = await instructionResponse.json();
        throw new Error(error.message || "Failed to generate scraping instructions");
      }

      const newSession: ScrapeSession = await instructionResponse.json();
      setSession(newSession);
      toast.success("Generated scraping instructions");

    } catch (error) {
      const message = error instanceof Error ? error.message : "An error occurred";
      toast.error(message);
      console.error("Error processing prompt:", error);
      setSession(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <PromptInsightPanel onPromptSubmit={handlePromptSubmit} isLoading={loading} />
      {process.env.NODE_ENV === "development" && session && (
        <div className="container max-w-4xl mx-auto pb-8">
          <PromptDebugger session={session} />
        </div>
      )}
    </div>
  );
}