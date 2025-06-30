"use client";

import { useState } from "react";
import { toast } from "sonner";
import { PromptInsightPanel } from "~/components/prompt-insight-panel";
import { PromptDebugger } from "~/components/prompt-debugger";
import { ProductGrid } from "~/components/product-grid";
import { type ParsedPrompt, type ScrapeSession } from "~/types";
import { useIntentRouter, type RoutedResult } from "~/agents/useIntentRouter";

export default function DashboardPage() {
  const [session, setSession] = useState<ScrapeSession | null>(null);
  const [loading, setLoading] = useState(false);
  const [originalPrompt, setOriginalPrompt] = useState("");
  const [result, setResult] = useState<RoutedResult | null>(null);
  
  // Use our intent router
  const { routeUserIntent, isLoading: routerLoading } = useIntentRouter();

  const handlePromptSubmit = async (prompt: string) => {
    try {
      setLoading(true);
      setOriginalPrompt(prompt);

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
      toast.success("Generated instructions");
      
      // Use our intent router to get the right data source
      try {
        toast.info(`Processing ${parsedPrompt.intent} intent...`);
        const routedResult = await routeUserIntent(parsedPrompt, prompt);
        setResult(routedResult);
        
        if (routedResult.source === "scraper") {
          toast.success(`Found ${routedResult.data.length} products from live data`);
        } else {
          toast.success(`Generated AI product suggestions`);
        }
      } catch (routerError) {
        console.error("Router error:", routerError);
        toast.error("Failed to process intent");
      }

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
      <PromptInsightPanel 
        onPromptSubmit={handlePromptSubmit} 
        isLoading={loading || routerLoading} 
      />
      
      <div className="container max-w-4xl mx-auto pb-8 px-4">
        {/* Show product grid when results are available */}
        {result && (
          <div className="mt-8">
            <h2 className="text-xl font-semibold mb-4">Results for: "{originalPrompt}"</h2>
            <ProductGrid 
              products={result.data}
              source={result.source}
              prompt={originalPrompt}
              fallback={result.fallback}
            />
          </div>
        )}
        
        {/* Debug panel in development mode */}
        {process.env.NODE_ENV === "development" && session && (
          <div className="mt-8">
            <h3 className="text-lg font-semibold mb-2">Debug Information</h3>
            <PromptDebugger session={session} />
          </div>
        )}
      </div>
    </div>
  );
}