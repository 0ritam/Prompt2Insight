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
  const showFallbackMessage = source === "gemini" && fallback;
  
  return (
    <div className="space-y-4">
      {showFallbackMessage && (
        <Alert className="mb-4 border-amber-500/50 bg-amber-500/10">
          <AlertTriangle className="text-amber-500" />
          <AlertTitle>Using AI-suggested results</AlertTitle>
          <AlertDescription>
            ⚠️ Could not fetch live data, showing AI-suggested results instead.
          </AlertDescription>
        </Alert>
      )}
      
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {products.map((product, index) => (
          <ProductCard 
            key={`${source}-product-${index}`} 
            product={product} 
            source={source} 
          />
        ))}
      </div>
    </div>
  );
}
