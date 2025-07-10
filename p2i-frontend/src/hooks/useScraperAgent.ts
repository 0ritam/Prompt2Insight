"use client";

import { useState } from "react";
import { type ScrapeTask } from "~/types";
import { logScrapeTask, updateScrapeTask } from "~/lib/clientLogger";

interface ScraperAgentState {
  isLoading: boolean;
  error: string | null;
  data: any[] | null;
}

interface UseScraperAgentResult extends ScraperAgentState {
  fetchScrapedProducts: (tasks: ScrapeTask[], forceAI?: boolean, sessionId?: string) => Promise<any[]>;
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
   * @param forceAI Optional flag to force AI-generated products instead of scraping
   * @param sessionId Optional session ID for logging scraper tasks
   * @returns Promise with the scraped product data
   */  
  const fetchScrapedProducts = async (tasks: ScrapeTask[], forceAI?: boolean, sessionId?: string): Promise<any[]> => {
    setState((prev) => ({ ...prev, isLoading: true, error: null }));

    // Log each scraping task
    const loggedTasks: { task: ScrapeTask; taskId?: string }[] = [];
    
    if (sessionId) {
      for (const task of tasks) {
        try {
          const logResult = await logScrapeTask({
            productName: task.productName,
            site: task.site || "unknown",
            taskType: forceAI ? "ai-generation" : "scrape",
            status: "pending",
            sessionId: sessionId,
          });
          
          if (logResult.success) {
            loggedTasks.push({ task, taskId: logResult.task.taskId });
          } else {
            loggedTasks.push({ task });
          }
        } catch (error) {
          console.error("Failed to log scrape task:", error);
          loggedTasks.push({ task });
        }
      }
    }

    try {
      console.log("Sending scrape request:", tasks, { forceAI });
      const url = new URL("http://localhost:8001/scrape-structured");
      if (forceAI) {
        url.searchParams.append("force_ai", "true");
        console.log("Added force_ai=true to URL");
      }
      console.log("Request URL:", url.toString());
      
      const response = await fetch(url.toString(), {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          intent: "search",
          products: tasks.map(task => task.productName),
          max_products_per_query: 5,
          filters: tasks.reduce((acc, task) => ({ ...acc, ...(task.filters || {}) }), {})
        })
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        const errorMessage = errorData.detail || errorData.message || `API error: ${response.status} ${response.statusText}`;
        console.error("Crawl4AI API error:", errorMessage);
        throw new Error(errorMessage);
      }

      const result = await response.json();
      console.log("Backend API response:", result);
      
      if (!result.success) {
        throw new Error(result.message || "Scraping operation failed");
      }

      // Extract products from the response data
      let scrapedData: any[] = [];
      
      console.log("Full result object:", JSON.stringify(result, null, 2));
      
      if (result.results && Array.isArray(result.results)) {
        // flipkart_api.py returns results array directly
        scrapedData = result.results;
        console.log("Using result.results:", scrapedData);
      } else if (result.data && Array.isArray(result.data)) {
        // Handle nested data structure from main.py
        scrapedData = result.data.reduce((acc: any[], taskResult: any) => {
          console.log("Processing taskResult:", taskResult);
          
          if (taskResult && taskResult.results && Array.isArray(taskResult.results)) {
            return acc.concat(taskResult.results);
          } else if (taskResult && taskResult.products && Array.isArray(taskResult.products)) {
            return acc.concat(taskResult.products);
          } else if (Array.isArray(taskResult)) {
            return acc.concat(taskResult);
          } else if (taskResult && typeof taskResult === 'object') {
            return acc.concat([taskResult]);
          }
          return acc;
        }, []);
        console.log("Using result.data processing:", scrapedData);
      } else if (result.products && Array.isArray(result.products)) {
        // Direct products array
        scrapedData = result.products;
        console.log("Using result.products:", scrapedData);
      }
      
      console.log("Extracted scraped data:", scrapedData);
      
      // Update logged tasks with success status
      if (sessionId && loggedTasks.length > 0) {
        for (const { task, taskId } of loggedTasks) {
          if (taskId) {
            try {
              await updateScrapeTask(taskId, {
                status: "scraped",
                resultData: {
                  productCount: scrapedData.length,
                  success: true,
                },
              });
            } catch (error) {
              console.error("Failed to update scrape task:", error);
            }
          }
        }
      }
      
      setState((prev) => ({ ...prev, isLoading: false, data: scrapedData }));
      return scrapedData;
    } catch (error: any) {
      const errorMessage = error.message || "Failed to fetch scraped products";
      
      // Update logged tasks with error status
      if (sessionId && loggedTasks.length > 0) {
        for (const { task, taskId } of loggedTasks) {
          if (taskId) {
            try {
              await updateScrapeTask(taskId, {
                status: "error",
                errorMessage: errorMessage,
              });
            } catch (updateError) {
              console.error("Failed to update scrape task with error:", updateError);
            }
          }
        }
      }
      
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
