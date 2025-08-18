"use client";

import { useEffect, useState, useRef } from "react";
import { toast } from "sonner";
import { Button } from "~/components/ui/button";
import { PromptInsightPanel, type PromptInsightPanelRef } from "~/components/prompt-insight-panel";
import { PromptDebugger } from "~/components/prompt-debugger";
import { ProductGrid } from "~/components/product-grid";
import { DevModeToggle } from "~/components/dev-mode-toggle";
import { ApiUsageTracker } from "~/components/api-usage-tracker";
import { apiUsageCounter } from "~/lib/apiUsageTracker";
import { apiLimitChecker } from "~/lib/apiLimitChecker";
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
  const promptPanelRef = useRef<PromptInsightPanelRef>(null);
  
  // Use our intent router
  const { routeUserIntent, isLoading: routerLoading } = useIntentRouter();
  const { data: authSession } = useSession();

  const handlePromptSubmit = async (prompt: string) => {
    try {
      // Check API limits before proceeding
      if (apiLimitChecker.isGeminiLimitReached()) {
        toast.error("Daily Gemini API limit reached (40 requests). Please try again tomorrow.");
        return;
      }

      if (apiLimitChecker.isScrapeDoSearchLimitReached()) {
        toast.error("Monthly ScrapeDo search limit reached (100 searches). Please try next month.");
        return;
      }

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

      // Track API usage - increment for main query
      apiUsageCounter.incrementUsage('gemini'); // AI Discovery
      apiUsageCounter.incrementUsage('google_search'); // Google Search
      
      // Increment ScrapeDo search count (1 search = 5 credits)
      apiLimitChecker.incrementScrapeDoSearch();

      // NEW: Call the unified Central Query Handler endpoint
      const response = await fetch("http://localhost:8001/api/v1/query/handle_query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
          query: prompt,
          max_results: 5 // Reduced to 5 results
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
        console.log("=== DEBUG: Raw Backend Response ===");
        console.log("Full queryResult:", JSON.stringify(queryResult, null, 2));
        console.log("Backend queryResult:", queryResult); // Debug log
        console.log("Raw products:", queryResult.products); // Debug individual products
        console.log("Raw links:", queryResult.links); // Debug individual links
        console.log("Query type:", queryResult.type);
        console.log("Amazon ready:", queryResult.amazon_ready);
        console.log("Fallback status:", queryResult.fallback || queryResult.google_fallback);
        console.log("Price chart image:", queryResult.price_chart_image ? "EXISTS" : "MISSING");
        console.log("Specs chart image:", queryResult.specs_chart_image ? "EXISTS" : "MISSING");
        console.log("=== END DEBUG ===");
        
        // The backend returns PRODUCTS (AI Discovery) and LINKS (Google Search) separately
        // Products = AI Discovery results with specifications, prices, etc.
        // Links = Google Search results with titles, URLs, descriptions
        const aiProducts = queryResult.products || []; // AI products with specifications
        const googleLinks = queryResult.links || []; // Google search results with URLs
        
        console.log("AI Products:", aiProducts.length, "Google Links:", googleLinks.length);
        
        // Check if this is a fallback scenario
        const isFallback = queryResult.fallback === true || queryResult.google_fallback === true;
        
        // First, add AI Discovery results if we have them
        if (aiProducts.length > 0) {
          const aiResult: RoutedResult = {
            source: "gemini",
            data: aiProducts.slice(0, 4), // Limit AI to 4 products, no links needed
            originalPrompt: prompt,
            fallback: isFallback,
            amazonReady: queryResult.amazon_ready || false,
            amazonQueryData: queryResult.amazon_query_data || null,
            // ADD: Server-generated chart images
            price_chart_image: queryResult.price_chart_image || null,
            specs_chart_image: queryResult.specs_chart_image || null,
          };
          setResult(aiResult);
          promptPanelRef.current?.addResult(aiResult, prompt);
          toast.success(`Found ${aiProducts.length} AI Discovery results`);
        }
        
        // Then, add Google Search results if we have them (after a short delay)
        if (googleLinks.length > 0) {
          setTimeout(() => {
            const googleResult: RoutedResult = {
              source: "google",
              data: googleLinks.slice(0, 5), // Use Google links, limit to 5
              originalPrompt: prompt,
              fallback: isFallback,
              amazonReady: queryResult.amazon_ready || false,
              amazonQueryData: queryResult.amazon_query_data || null,
            };
            
            promptPanelRef.current?.addResult(googleResult, prompt);
            toast.success(`Found ${googleLinks.length} Google Search results`);
          }, 1000);
        }
        
        // Remove the fallback additional API call logic since we now have both types
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
        promptPanelRef.current?.addResult(routedResult, prompt);
        
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
        ref={promptPanelRef}
        onPromptSubmit={handlePromptSubmit} 
        isLoading={loading || routerLoading}
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
          
          {/* API Usage Tracker */}
          <div className="mb-8">
            <ApiUsageTracker />
          </div>
        </div>
      </div>
    </div>
  );
}