"use client";

import React from "react";
import { ProductCard } from "./product-card";
import { Alert, AlertDescription, AlertTitle } from "~/components/ui/alert";
import { AlertTriangle } from "lucide-react";
import type { ProductSource } from "~/agents/useIntentRouter";

interface ProductGridProps {
  products: any[];
  source: ProductSource;
  isLoading?: boolean;
  error?: string | null;
  prompt?: string;
  fallback?: boolean;
}

export function ProductGrid({ 
  products, 
  source, 
  isLoading = false,
  error = null,
  prompt = "",
  fallback = false
}: ProductGridProps) {
  if (isLoading) {
    return (
      <div className="w-full py-12 flex justify-center items-center">
        <div className="flex flex-col items-center">
          <div className="h-12 w-12 rounded-full border-4 border-primary border-t-transparent animate-spin mb-4"></div>
          <p className="text-muted-foreground">Fetching product data...</p>
        </div>
      </div>
    );
  }
  
  if (error) {
    return (
      <Alert variant="destructive" className="mb-4">
        <AlertTriangle />
        <AlertTitle>Error fetching products</AlertTitle>
        <AlertDescription>{error}</AlertDescription>
      </Alert>
    );
  }
  
  if (!products || products.length === 0) {
    return (
      <Alert className="mb-4">
        <AlertTitle>No products found</AlertTitle>
        <AlertDescription>
          Try a different search or adjust your filters.
        </AlertDescription>
      </Alert>
    );
  }

  // Gemini fallback notification when scraper failed
  const showGeminiFallbackMessage = source === "gemini" && fallback;
  
  // Google Search is now a primary method, not fallback
  const showGoogleSearchMessage = source === "google" && !fallback;
  
  // Google Search fallback notification when AI discovery failed
  const showGoogleFallbackMessage = source === "google" && fallback;
  
  // Debug logging
  console.log("ProductGrid products:", products);
  
  // Ensure products is a valid array
  const validProducts = Array.isArray(products) ? products.filter(product => 
    product && typeof product === 'object' && product !== null
  ) : [];
  
  // Limit AI discovery (gemini) products to 4 items for better focus
  const displayProducts = source === "gemini" ? validProducts.slice(0, 4) : validProducts;
  
  if (displayProducts.length === 0) {
    return (
      <Alert className="mb-4">
        <AlertTitle>No valid products found</AlertTitle>
        <AlertDescription>
          Try a different search or adjust your filters.
        </AlertDescription>
      </Alert>
    );
  }
  
  return (
    <div className="space-y-4">
      {source === "gemini" && (
        <Alert className="mb-4 border-purple-500/50 bg-purple-500/10">
          <AlertTriangle className="text-purple-500" />
          <AlertTitle>🤖 AI Discovery Results</AlertTitle>
          <AlertDescription>
            Showing top 4 AI-curated product recommendations based on your query. These are intelligently selected and analyzed for relevance.
          </AlertDescription>
        </Alert>
      )}
      
      {showGeminiFallbackMessage && (
        <Alert className="mb-4 border-amber-500/50 bg-amber-500/10">
          <AlertTriangle className="text-amber-500" />
          <AlertTitle>Using AI-suggested results</AlertTitle>
          <AlertDescription>
            AI-suggested Results.
          </AlertDescription>
        </Alert>
      )}
      
      {showGoogleSearchMessage && (
        <Alert className="mb-4 border-blue-500/50 bg-blue-500/10">
          <AlertTriangle className="text-blue-500" />
          <AlertTitle>Using Google Search results</AlertTitle>
          <AlertDescription>
            🔍 Google Search Results
          </AlertDescription>
        </Alert>
      )}
      
      {showGoogleFallbackMessage && (
        <Alert className="mb-4 border-blue-500/50 bg-blue-500/10">
          <AlertTriangle className="text-blue-500" />
          <AlertTitle>Using Google Search results</AlertTitle>
          <AlertDescription>
            🔍 Could not fetch AI discovery results, showing Google Search results instead.
          </AlertDescription>
        </Alert>
      )}
      
      <div className={`grid gap-4 ${
        source === "gemini" 
          ? "grid-cols-1 sm:grid-cols-2 lg:grid-cols-2 xl:grid-cols-2" // 2x2 grid for AI discovery
          : "grid-cols-1 sm:grid-cols-2 lg:grid-cols-3" // Regular 3-column grid for others
      }`}>
        {displayProducts.map((product, index) => {
          console.log("Rendering product:", product, "at index:", index);
          try {
            return (
              <ProductCard 
                key={`${source}-product-${index}-${product.title || product.name || index}`} 
                product={product} 
                source={source} 
              />
            );
          } catch (error) {
            console.error("Error rendering product at index", index, ":", error, "Product:", product);
            return (
              <div key={`error-${index}`} className="p-4 border border-red-200 rounded">
                <p className="text-red-600 text-sm">Error rendering product {index + 1}</p>
                <pre className="text-xs text-red-500 mt-2">{JSON.stringify(product, null, 2)}</pre>
              </div>
            );
          }
        })}
      </div>
    </div>
  );
}
