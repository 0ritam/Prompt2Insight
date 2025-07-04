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
  
  // Google Search fallback notification when scraper failed
  const showGoogleFallbackMessage = source === "google";
  
  // Debug logging
  console.log("ProductGrid products:", products);
  
  // Ensure products is a valid array
  const validProducts = Array.isArray(products) ? products.filter(product => 
    product && typeof product === 'object' && product !== null
  ) : [];
  
  if (validProducts.length === 0) {
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
      {showGeminiFallbackMessage && (
        <Alert className="mb-4 border-amber-500/50 bg-amber-500/10">
          <AlertTriangle className="text-amber-500" />
          <AlertTitle>Using AI-suggested results</AlertTitle>
          <AlertDescription>
            ⚠️ Could not fetch live data, showing AI-suggested results instead.
          </AlertDescription>
        </Alert>
      )}
      
      {showGoogleFallbackMessage && (
        <Alert className="mb-4 border-blue-500/50 bg-blue-500/10">
          <AlertTriangle className="text-blue-500" />
          <AlertTitle>Using Google Search results</AlertTitle>
          <AlertDescription>
            🔍 Could not fetch live data, showing Google Search results instead.
          </AlertDescription>
        </Alert>
      )}
      
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {validProducts.map((product, index) => {
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
