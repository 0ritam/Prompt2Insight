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
  // Handle different product data structures from different sources
  const productName = product.title || product.name || "Unknown Product";
  const productPrice = product.price || "N/A";
  const productRating = product.rating || "N/A";
  const productImage = product.image || "/placeholder-product.jpg";
  const productUrl = product.url || "#";
  const productDescription = product.description || product.specs?.description || "";
  
  // Format specs if they exist
  const specs = product.specifications || product.specs || {};
  const specsList = Object.entries(specs).filter(([key]) => 
    key !== "description" && typeof specs[key] === "string"
  ).slice(0, 3);

  return (
    <Card className="h-full flex flex-col overflow-hidden">
      <CardHeader className="pb-0 pt-4 px-4 flex flex-row justify-between items-start">
        <div>
          <h3 className="font-medium text-sm line-clamp-2">{productName}</h3>
          <div className="flex items-center gap-2 mt-1">
            <span className="font-semibold text-primary">{productPrice}</span>
            {productRating && (
              <span className="text-xs bg-muted px-1.5 py-0.5 rounded flex items-center">
                ★ {productRating}
              </span>
            )}
          </div>
        </div>
        <Badge 
          variant={source === "scraper" ? "default" : "outline"}
          className={source === "scraper" ? "bg-green-600" : "border-amber-500 text-amber-500"}
        >
          {source === "scraper" ? "Real-Time Data" : "AI-Suggested"}
        </Badge>
      </CardHeader>
      
      <CardContent className="px-4 py-2 flex-grow">
        {productImage && (
          <div className="relative w-full aspect-[4/3] mb-3 bg-muted/30 rounded-md overflow-hidden">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img 
              src={productImage} 
              alt={productName}
              className="object-contain w-full h-full"
            />
          </div>
        )}
        
        {productDescription && (
          <p className="text-xs text-muted-foreground mb-2 line-clamp-2">
            {productDescription}
          </p>
        )}
        
        {specsList.length > 0 && (
          <dl className="text-xs space-y-1">
            {specsList.map(([key, value]) => (
              <div key={key} className="flex justify-between">
                <dt className="text-muted-foreground">{key}:</dt>
                <dd className="font-medium truncate max-w-[70%] text-right">{String(value)}</dd>
              </div>
            ))}
          </dl>
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
