"use client";

import { useState } from "react";

interface Product {
  name: string;
  url: string;
  rating?: string;
  price?: string;
  image?: string;
  description?: string;
}

interface GeminiAgentState {
  isLoading: boolean;
  error: string | null;
  data: Product[] | null;
}

interface UseGeminiAgentResult extends GeminiAgentState {
  fetchGeminiSuggestions: (prompt: string) => Promise<Product[]>;
}

// Prompt template for getting product suggestions from Gemini
const GEMINI_PROMPT_TEMPLATE = `
You are a helpful e-commerce research assistant. Based on the user's request, provide 3-5 top product suggestions.

For each product, include:
- A specific product name (including model number where applicable)
- A direct URL to the product on Flipkart or Amazon India
- An estimated price range in Indian Rupees (₹)
- A rating out of 5 stars
- A very brief description (15 words max)

Format your response as a JSON array of objects with these fields: name, url, price, rating, description.
Keep your response focused on providing accurate and helpful product information.

User Request: {prompt}
`;

export function useGeminiAgent(): UseGeminiAgentResult {
  const [state, setState] = useState<GeminiAgentState>({
    isLoading: false,
    error: null,
    data: null,
  });

  /**
   * Fetches product suggestions from Gemini API
   * @param prompt The original user prompt
   * @returns Promise with the product suggestions
   */
  const fetchGeminiSuggestions = async (prompt: string): Promise<Product[]> => {
    setState((prev) => ({ ...prev, isLoading: true, error: null }));

    try {
      // Call your API endpoint that interfaces with Gemini
      const response = await fetch("/api/gemini/suggest", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ 
          prompt: GEMINI_PROMPT_TEMPLATE.replace("{prompt}", prompt) 
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(
          errorData.error || `API error: ${response.status} ${response.statusText}`
        );
      }

      const result = await response.json();
      const suggestions = result.suggestions || [];
      
      // Transform and validate the data
      const products: Product[] = suggestions.map((item: any) => ({
        name: item.name || "Unknown Product",
        url: item.url || "#",
        rating: item.rating || "N/A",
        price: item.price || "N/A",
        image: item.image || "/placeholder-product.jpg",
        description: item.description || "",
      }));

      setState((prev) => ({ ...prev, isLoading: false, data: products }));
      return products;
    } catch (error: any) {
      const errorMessage = error.message || "Failed to fetch Gemini suggestions";
      setState((prev) => ({ 
        ...prev, 
        isLoading: false, 
        error: errorMessage 
      }));
      console.error("Gemini API Error:", errorMessage);
      
      // Return mock data on failure as a last resort
      return getMockProducts(prompt);
    }
  };

  return {
    ...state,
    fetchGeminiSuggestions,
  };
}

// Fallback mock data in case the API completely fails
function getMockProducts(prompt: string): Product[] {
  return [
    {
      name: "Sample Product 1",
      url: "https://www.flipkart.com/sample-product-1",
      rating: "4.5",
      price: "₹15,999",
      description: "This is a fallback product suggestion."
    },
    {
      name: "Sample Product 2",
      url: "https://www.amazon.in/sample-product-2",
      rating: "4.2",
      price: "₹12,999",
      description: "Another fallback product when API fails."
    }
  ];
}
