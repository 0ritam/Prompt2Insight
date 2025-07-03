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
  routeUserIntent: (parsedPrompt: ParsedPrompt, originPrompt: string, forceAI?: boolean) => Promise<RoutedResult>;
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
   * @param forceAI Optional flag to force AI-generated products instead of scraping
   * @returns Promise with the unified result
   */
  const routeUserIntent = async (
    parsedPrompt: ParsedPrompt, 
    originPrompt: string,
    forceAI?: boolean
  ): Promise<RoutedResult> => {
    setState((prev) => ({ ...prev, isLoading: true, error: null }));

    try {
      // Build scrape tasks from the parsed prompt
      const scrapeTasks = buildScrapeInstructions(parsedPrompt);
      console.log("Scrape tasks:", scrapeTasks);

      // Try scraper first (unless forceAI is explicitly true)
      if (forceAI) {
        console.log("Force AI mode enabled, skipping scraper");
      } else {
        try {
          console.log("Attempting to fetch scraped products...");
          const scrapedProducts = await fetchScrapedProducts(scrapeTasks, false);
          if (scrapedProducts && scrapedProducts.length > 0) {
            const result: RoutedResult = {
              source: "scraper",
              data: scrapedProducts,
              originalPrompt: originPrompt
            };
            setState(prev => ({ ...prev, isLoading: false, result }));
            return result;
          }
        } catch (error) {
          console.error("Scraper failed, falling back to Gemini:", error);
        }
      }

      // Fallback to Gemini if scraper fails or forceAI is true
      const suggestions = await fetchGeminiSuggestions(originPrompt);
      const result: RoutedResult = {
        source: "gemini",
        data: suggestions,
        originalPrompt: originPrompt,
        fallback: true
      };
      
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
