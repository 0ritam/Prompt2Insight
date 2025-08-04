"use client";

import { useEffect, useState } from "react";
import { toast } from "sonner";
import { PromptInsightPanel } from "~/components/prompt-insight-panel";
import { PromptDebugger } from "~/components/prompt-debugger";
import { ProductGrid } from "~/components/product-grid";
import { DevModeToggle } from "~/components/dev-mode-toggle";
import { type ParsedPrompt, type ScrapeSession } from "~/types";
import { useIntentRouter, type RoutedResult, type ProductSource } from "~/agents/useIntentRouter";
import { generateSessionId } from "~/lib/session";
import { logPromptSession, updatePromptSession } from "~/lib/clientLogger";
import { useSession } from "next-auth/react";

export default function DashboardPage() {
  const [session, setSession] = useState<ScrapeSession | null>(null);
  const [loading, setLoading] = useState(false);
  const [originalPrompt, setOriginalPrompt] = useState("");
  const [result, setResult] = useState<RoutedResult | null>(null);
  const [googleResults, setGoogleResults] = useState<any[]>([]);
  const [forceAI, setForceAI] = useState(false);
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);
  
  // Use our intent router
  const { routeUserIntent, isLoading: routerLoading } = useIntentRouter();
  const { data: authSession } = useSession();

  const handlePromptSubmit = async (prompt: string) => {
    try {
      setLoading(true);
      setOriginalPrompt(prompt);

      // Generate a new session ID for this prompt
      const sessionId = generateSessionId();
      setCurrentSessionId(sessionId);

      // Log the initial prompt session
      if (authSession?.user?.id) {
        await logPromptSession({
          sessionId,
          userId: authSession.user.id,
          originPrompt: prompt,
          status: "pending",
        });
      }

      toast.info("Processing your query...");

      // NEW: Call the unified Central Query Handler endpoint
      const response = await fetch("http://localhost:8001/api/v1/query/handle_query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
          query: prompt,
          max_results: 5
        }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || "Failed to process query");
      }

      const queryResult = await response.json();
      
      // Update session with success
      if (authSession?.user?.id && sessionId) {
        await updatePromptSession(sessionId, {
          status: "done",
          resultData: {
            source: queryResult.type,
            dataCount: queryResult.type === "discovery_result" ? 
              (queryResult.products?.length || 0) + (queryResult.links?.length || 0) :
              1,
            responseType: queryResult.type,
          },
        });
      }

      // Convert backend response to frontend format
      if (queryResult.type === "discovery_result") {
        // Discovery result - show products and optional Amazon button
        const routedResult: RoutedResult = {
          source: "google" as ProductSource, // Indicates it came from discovery workflow
          data: [...(queryResult.products || []), ...(queryResult.links || [])],
          originalPrompt: prompt,
          fallback: false,
          amazonReady: queryResult.amazon_ready || false,
          amazonQueryData: queryResult.amazon_query_data || null,
        };
        setResult(routedResult);
        
        toast.success(`Found ${routedResult.data.length} results from discovery workflow`);
      } else if (queryResult.type === "analysis_result") {
        // Analysis result - show AI answer
        const routedResult: RoutedResult = {
          source: "analysis" as ProductSource,
          data: [{
            type: "analysis",
            answer: queryResult.answer,
            persona: queryResult.persona,
            execution_time: queryResult.execution_time,
          }],
          originalPrompt: prompt,
          fallback: false,
        };
        setResult(routedResult);
        
        toast.success("Analysis completed successfully");
      }

    } catch (error) {
      const message = error instanceof Error ? error.message : "An error occurred";
      toast.error(message);
      console.error("Error processing prompt:", error);
      
      // Update session with error
      if (authSession?.user?.id && currentSessionId) {
        await updatePromptSession(currentSessionId, {
          status: "error",
          errorMessage: message,
        });
      }
      
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
        result={result}
        originalPrompt={originalPrompt}
      />
      
      <div className="container max-w-4xl mx-auto pb-8 px-4">
        {/* Debug panel in development mode */}
        {process.env.NODE_ENV === "development" && (
          <div className="mt-8">
            <h3 className="text-lg font-semibold mb-2">Debug Information</h3>
            {session && <PromptDebugger session={session} />}
            {result && (
              <div className="mt-4 p-4 bg-gray-50 rounded-lg">
                <h4 className="font-medium mb-2">Result Debug</h4>
                <p className="text-sm text-gray-600 mb-2">
                  Source: <span className="font-mono">{result.source}</span>
                </p>
                <p className="text-sm text-gray-600 mb-2">
                  Products: {result.data.length}
                </p>
                {result.fallback && (
                  <p className="text-sm text-amber-600 mb-2">
                    ⚠️ Fallback method was used (scraper/AI instead of Google Search)
                  </p>
                )}
                {result.googleFallback && (
                  <p className="text-sm text-blue-600 mb-2">
                    🔍 Google Search was used as fallback from scraper
                  </p>
                )}
                <details className="mt-2">
                  <summary className="cursor-pointer text-sm text-gray-600">
                    View raw data
                  </summary>
                  <pre className="mt-2 text-xs bg-gray-100 p-2 rounded overflow-auto max-h-48">
                    {JSON.stringify(result.data, null, 2)}
                  </pre>
                </details>
              </div>
            )}
          </div>
        )}

        {/* Main Dashboard Content */}
        <div className="mt-8">
          <div className="flex justify-between items-center mb-6">
            <h1 className="text-2xl font-bold">Dashboard</h1>
            <div className="flex gap-2">
              <DevModeToggle forceAI={forceAI} onToggle={setForceAI} />
              {authSession?.user?.role === "admin" && (
                <a 
                  href="/admin" 
                  className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
                >
                  Admin Panel
                </a>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}