"use client";

import { useState } from "react";
import { type ParsedPrompt, type ScrapeTask } from "~/types";
import { useScraperAgent } from "~/hooks/useScraperAgent";
// Update the import path if the file is located elsewhere, for example:
import { useGeminiAgent } from "../hooks/useGeminiAgent";
import { buildScrapeInstructions } from "~/agents/routerAgent";

export type ProductSource = "scraper" | "gemini";

export interface RoutedResult {
  source: ProductSource;
  data: any[];
  originalPrompt: string;
  fallback?: boolean;
}

interface IntentRouterState {
  isLoading: boolean;
  error: string | null;
  result: RoutedResult | null;
}

interface UseIntentRouterResult extends IntentRouterState {
  routeUserIntent: (parsedPrompt: ParsedPrompt, originPrompt: string) => Promise<RoutedResult>;
}

export function useIntentRouter(): UseIntentRouterResult {
  const [state, setState] = useState<IntentRouterState>({
    isLoading: false,
    error: null,
    result: null,
  });

  const { fetchScrapedProducts } = useScraperAgent();
  const { fetchGeminiSuggestions } = useGeminiAgent();

  /**
   * Routes the user intent to the appropriate agent based on intent
   * @param parsedPrompt The parsed user prompt with intent and products
   * @param originPrompt The original user prompt text
   * @returns Promise with the unified result
   */
  const routeUserIntent = async (
    parsedPrompt: ParsedPrompt, 
    originPrompt: string
  ): Promise<RoutedResult> => {
    setState((prev) => ({ ...prev, isLoading: true, error: null }));

    try {
      let result: RoutedResult;

      if (parsedPrompt.intent === "compare") {
        try {
          // Try to use the scraper for comparison intents
          const scrapeTasks = buildScrapeInstructions(parsedPrompt);
          console.log("Using scraper for comparison intent", scrapeTasks);
          const scrapedData = await fetchScrapedProducts(scrapeTasks);
          
          // Check if the scraper returned data
          if (scrapedData && scrapedData.length > 0) {
            result = {
              source: "scraper",
              data: scrapedData,
              originalPrompt: originPrompt
            };
          } else {
            // Empty result from scraper, fallback to Gemini
            console.error("Scraper returned empty results, falling back to Gemini");
            const suggestions = await fetchGeminiSuggestions(originPrompt);
            result = {
              source: "gemini",
              data: suggestions,
              originalPrompt: originPrompt,
              fallback: true
            };
          }
        } catch (scraperError) {
          console.error("Scraper failed, falling back to Gemini", scraperError);
          // Fallback to Gemini if scraper fails
          const suggestions = await fetchGeminiSuggestions(originPrompt);
          result = {
            source: "gemini",
            data: suggestions,
            originalPrompt: originPrompt,
            fallback: true
          };
        }
      } else {
        // For search or recommend intents, use Gemini directly
        console.log("Using Gemini for search/recommend intent");
        const suggestions = await fetchGeminiSuggestions(originPrompt);
        result = {
          source: "gemini", 
          data: suggestions,
          originalPrompt: originPrompt
        };
      }

      setState((prev) => ({ ...prev, isLoading: false, result }));
      return result;
    } catch (error: any) {
      const errorMessage = error.message || "Failed to route user intent";
      setState((prev) => ({ 
        ...prev, 
        isLoading: false, 
        error: errorMessage 
      }));
      console.error("Intent Router Error:", errorMessage);
      
      // Return empty result on failure
      const emptyResult: RoutedResult = {
        source: "gemini",
        data: [],
        originalPrompt: originPrompt,
        fallback: parsedPrompt.intent === "compare" // Set fallback flag if we were trying to compare
      };
      
      return emptyResult;
    }
  };

  return {
    ...state,
    routeUserIntent,
  };
}
