"use client";

import { useState } from "react";

interface GoogleSearchResult {
  title: string;
  url: string;
  description: string;
  image: string;
  source: string;
}

interface GoogleSearchState {
  isLoading: boolean;
  error: string | null;
  results: GoogleSearchResult[];
}

interface UseGoogleSearchResult extends GoogleSearchState {
  searchProducts: (query: string, numResults?: number) => Promise<GoogleSearchResult[]>;
  clearResults: () => void;
}

export function useGoogleSearch(): UseGoogleSearchResult {
  const [state, setState] = useState<GoogleSearchState>({
    isLoading: false,
    error: null,
    results: [],
  });

  /**
   * Search for products using Google Custom Search API
   * @param query Search query string
   * @param numResults Number of results to return (default: 3)
   * @returns Promise with array of search results
   */
  const searchProducts = async (
    query: string, 
    numResults: number = 3
  ): Promise<GoogleSearchResult[]> => {
    setState((prev) => ({ ...prev, isLoading: true, error: null }));

    try {
      console.log("Searching Google for:", query);
      
      const response = await fetch("http://localhost:8001/google-search", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          query,
          num_results: numResults,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        const errorMessage = errorData.detail || errorData.message || `API error: ${response.status} ${response.statusText}`;
        console.error("Google Search API error:", errorMessage);
        throw new Error(errorMessage);
      }

      const result = await response.json();
      console.log("Google Search API response:", result);
      
      if (!result.success) {
        throw new Error(result.message || "Google search operation failed");
      }

      const searchResults = result.results || [];
      setState((prev) => ({ ...prev, isLoading: false, results: searchResults }));
      return searchResults;
      
    } catch (error: any) {
      const errorMessage = error.message || "Failed to search Google";
      setState((prev) => ({ 
        ...prev, 
        isLoading: false, 
        error: errorMessage 
      }));
      console.error("Google Search Error:", errorMessage);
      throw error;
    }
  };

  /**
   * Clear search results and reset state
   */
  const clearResults = () => {
    setState({
      isLoading: false,
      error: null,
      results: [],
    });
  };

  return {
    ...state,
    searchProducts,
    clearResults,
  };
}
