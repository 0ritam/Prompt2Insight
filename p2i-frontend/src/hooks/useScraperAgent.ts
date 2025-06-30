"use client";

import { useState } from "react";
import { type ScrapeTask } from "~/types";

interface ScraperAgentState {
  isLoading: boolean;
  error: string | null;
  data: any[] | null;
}

interface UseScraperAgentResult extends ScraperAgentState {
  fetchScrapedProducts: (tasks: ScrapeTask[]) => Promise<any[]>;
}

export function useScraperAgent(): UseScraperAgentResult {
  const [state, setState] = useState<ScraperAgentState>({
    isLoading: false,
    error: null,
    data: null,
  });

  /**
   * Fetches scraped product data from the FastAPI backend
   * @param tasks Array of scrape tasks to send to the backend
   * @returns Promise with the scraped product data
   */
  const fetchScrapedProducts = async (tasks: ScrapeTask[]): Promise<any[]> => {
    setState((prev) => ({ ...prev, isLoading: true, error: null }));

    try {
      console.log("Sending scrape request to API:", tasks);
      const response = await fetch("http://localhost:8000/scrape", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ tasks }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        const errorMessage = errorData.detail || `API error: ${response.status} ${response.statusText}`;
        console.error("Scraper API error:", errorMessage);
        throw new Error(errorMessage);
      }

      const result = await response.json();
      console.log("Scraper API response:", result);
      
      if (!result.success) {
        throw new Error("Scraping operation failed");
      }

      const scrapedData = result.data || [];
      setState((prev) => ({ ...prev, isLoading: false, data: scrapedData }));
      return scrapedData;
    } catch (error: any) {
      const errorMessage = error.message || "Failed to fetch scraped products";
      setState((prev) => ({ 
        ...prev, 
        isLoading: false, 
        error: errorMessage 
      }));
      console.error("Scraper Error:", errorMessage);
      // Re-throw the error instead of returning empty array
      // This will allow the intent router to catch it and trigger the Gemini fallback
      throw error;
    }
  };

  return {
    ...state,
    fetchScrapedProducts,
  };
}
