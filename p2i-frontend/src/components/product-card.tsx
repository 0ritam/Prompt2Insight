"use client";

import React from "react";
import { Card, CardContent, CardFooter, CardHeader } from "~/components/ui/card";
import { Badge } from "~/components/ui/badge";
import { Button } from "~/components/ui/button";
import { ExternalLink } from "lucide-react";
import type { ProductSource } from "~/agents/useIntentRouter";

interface ProductCardProps {
  product: any;
  source: ProductSource;
}

export function ProductCard({ product, source }: ProductCardProps) {
  // Debug: Log the product data
  console.log("ProductCard received product:", product);
  
  // Helper function to safely convert values to strings
  const safeString = (value: any): string => {
    if (value === null || value === undefined) return "";
    if (typeof value === "string") return value;
    if (typeof value === "number") return value.toString();
    if (typeof value === "object") return JSON.stringify(value);
    return String(value);
  };

  // Handle different product data structures from different sources
  const productName = safeString(product.title || product.name || "Unknown Product");
  const productPrice = safeString(product.price || "N/A");
  const productRating = safeString(product.rating || "N/A");
  const productImage = safeString(product.image || "/placeholder-product.jpg");
  const productUrl = safeString(product.url || product.productUrl || "#");
  const productDescription = safeString(product.description || product.specifications || "");
  
  // Format additional info if it exists
  const discount = safeString(product.discount || "");
  const availability = safeString(product.availability || "");
  const brand = safeString(product.brand || "");

  return (
    <Card className="h-full flex flex-col overflow-hidden">
      <CardHeader className="pb-0 pt-4 px-4 flex flex-row justify-between items-start">
        <div className="flex-1">
          <h3 className="font-medium text-sm line-clamp-2">{productName}</h3>
          <div className="flex items-center gap-2 mt-1">
            <span className="font-semibold text-primary">{productPrice}</span>
            {discount && (
              <span className="text-xs bg-green-100 text-green-800 px-1.5 py-0.5 rounded">
                {discount}
              </span>
            )}
            {productRating && productRating !== "N/A" && (
              <span className="text-xs bg-muted px-1.5 py-0.5 rounded flex items-center">
                ★ {productRating}
              </span>
            )}
          </div>
          {brand && (
            <div className="text-xs text-muted-foreground mt-1">
              Brand: {brand}
            </div>
          )}
        </div>
        <Badge 
          variant={source === "scraper" ? "default" : "outline"}
          className={source === "scraper" ? "bg-green-600" : "border-amber-500 text-amber-500"}
        >
          {source === "scraper" ? "Live Data" : "AI-Suggested"}
        </Badge>
      </CardHeader>
      
      <CardContent className="px-4 py-2 flex-grow">
        {productImage && productImage !== "/placeholder-product.jpg" && (
          <div className="relative w-full aspect-[4/3] mb-3 bg-muted/30 rounded-md overflow-hidden">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img 
              src={productImage} 
              alt={productName}
              className="object-contain w-full h-full"
              onError={(e) => {
                const target = e.target as HTMLImageElement;
                target.style.display = 'none';
              }}
            />
          </div>
        )}
        
        {productDescription && (
          <p className="text-xs text-muted-foreground mb-2 line-clamp-2">
            {productDescription}
          </p>
        )}
        
        {availability && (
          <div className="text-xs text-muted-foreground mb-2">
            Status: <span className="text-green-600">{availability}</span>
          </div>
        )}
      </CardContent>
      
      <CardFooter className="px-4 pb-4 pt-0">
        {productUrl && productUrl !== "#" && (
          <Button 
            variant="outline" 
            size="sm"
            className="w-full gap-1"
            onClick={() => window.open(productUrl, '_blank')}
          >
            View Product <ExternalLink className="h-3 w-3" />
          </Button>
        )}
      </CardFooter>
    </Card>
  );
}
