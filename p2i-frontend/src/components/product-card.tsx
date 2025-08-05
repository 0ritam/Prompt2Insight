"use client";

import React, { useEffect, useState } from "react";
import { Card, CardContent, CardFooter, CardHeader } from "~/components/ui/card";
import { Badge } from "~/components/ui/badge";
import { Button } from "~/components/ui/button";
import { ExternalLink, MessageCircle } from "lucide-react";
import { RAGChat } from "./rag-chat";
import type { ProductSource } from "~/agents/useIntentRouter";
import { toast } from "sonner";

interface ProductCardProps {
  product: any;
  source: ProductSource;
}

export function ProductCard({ product, source }: ProductCardProps) {
  const [isRAGChatOpen, setIsRAGChatOpen] = useState(false);
  
  // Debug: Log the product data (only for development)
  // console.log("ProductCard received product:", product);
  
  // Add a CSS fix for any empty elements in the UI
  useEffect(() => {
    // This will hide any empty elements with just {} content
    const style = document.createElement('style');
    style.innerHTML = `
      *:empty:not(img):not(input):not(textarea):not(br):not(hr):not(canvas) {
        display: none !important;
      }
    `;
    document.head.appendChild(style);
    return () => {
      document.head.removeChild(style);
    };
  }, []);
  
  // Helper function to safely convert values to strings
  const safeString = (value: any): string => {
    if (value === null || value === undefined) return "";
    if (typeof value === "string") return value;
    if (typeof value === "number") return value.toString();
    if (typeof value === "object") return JSON.stringify(value);
    return String(value);
  };

  // Handle different product data structures from different sources
  // FIXED: Amazon scraper returns names in "name" field, titles in "title"
  const productName = safeString(product.name || product.title || "Unknown Product");
  const productPrice = safeString(product.price || "Price not available");
  const productRating = safeString(product.rating || "N/A");
  const productImage = safeString(product.image || "/placeholder-product.jpg");
  // FIXED: Amazon scraper returns URLs in "link" field
  const productUrl = safeString(product.link || product.url || product.productUrl || "#");
  const productDescription = safeString(product.description || product.specifications || product.snippet || "");
  
  // Format additional info if it exists
  const discount = safeString(product.discount || "");
  const availability = safeString(product.availability || "");
  const brand = safeString(product.brand || "");
  const sourceLabel = safeString(product.source || "");

  return (
    <Card className="h-full flex flex-col overflow-hidden">
      <CardHeader className="pb-0 pt-4 px-4 flex flex-row justify-between items-start">
        <div className="flex-1">
          <h3 className={`text-sm line-clamp-2 ${source === "gemini" ? "font-bold text-purple-900" : "font-medium"}`}>
            {productName}
          </h3>
          <div className="flex items-center gap-2 mt-1">
            <span className={`text-primary ${source === "gemini" ? "font-bold text-lg" : "font-semibold"}`}>
              {productPrice}
            </span>
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
          {sourceLabel && source === "google" && (
            <div className="text-xs text-muted-foreground mt-1">
              Source: {sourceLabel}
            </div>
          )}
        </div>
        <Badge 
          variant={source === "scraper" ? "default" : "outline"}
          className={
            source === "scraper" 
              ? "bg-green-600" 
              : source === "google" 
                ? "border-blue-500 text-blue-600 bg-blue-50"
                : source === "amazon"
                  ? "border-orange-500 text-orange-600 bg-orange-50"
                  : source === "gemini"
                    ? "border-purple-500 text-purple-600 bg-purple-50"
                    : "border-amber-500 text-amber-500"
          }
        >
          {source === "scraper" 
            ? "Live Data" 
            : source === "google" 
              ? "Web/Google Suggested" 
              : source === "amazon"
                ? "🛒 Live Amazon"
                : source === "gemini"
                  ? "🤖 AI Discovery"
                  : "AI-Suggested"}
        </Badge>
      </CardHeader>
      
      <CardContent className="px-4 py-2 flex-grow">
        {/* For AI Discovery (gemini), prioritize text content over images */}
        {source === "gemini" ? (
          <>
            {/* AI Discovery Text-Focused Layout */}
            <div className="bg-purple-50 border border-purple-200 rounded-lg p-3 mb-3">
              <h4 className="font-bold text-purple-900 text-sm mb-2">🤖 AI Analysis</h4>
              {productDescription && (
                <p className="text-sm font-medium text-purple-800 leading-relaxed">
                  {productDescription}
                </p>
              )}
            </div>
            
            {/* Optional image for AI discovery, smaller and less prominent */}
            {productImage && productImage !== "/placeholder-product.jpg" && (
              <div className="relative w-24 h-24 mx-auto mb-2 bg-muted/30 rounded-md overflow-hidden">
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img 
                  src={productImage} 
                  alt={productName}
                  className="object-contain w-full h-full opacity-70"
                  onError={(e) => {
                    const target = e.target as HTMLImageElement;
                    target.style.display = 'none';
                  }}
                />
              </div>
            )}
          </>
        ) : (
          <>
            {/* Regular layout for other sources */}
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
          </>
        )}
        
        {availability && (
          <div className="text-xs text-muted-foreground mb-2">
            Status: <span className="text-green-600">{availability}</span>
          </div>
        )}
      </CardContent>
      
      <CardFooter className="px-4 pb-4 pt-0">
        {/* For Amazon products, show View Product button instead of full URL */}
        {source === "amazon" && productUrl && productUrl !== "#" && (
          <div className="w-full mb-3">
            <div className="bg-orange-50 border border-orange-200 rounded-lg p-2">
              <p className="text-xs font-medium text-orange-800 mb-2">🛒 Amazon Product Link:</p>
              <Button
                variant="default"
                size="sm"
                className="w-full bg-orange-500 hover:bg-orange-600 text-white gap-1"
                onClick={() => window.open(productUrl, '_blank')}
              >
                <ExternalLink className="h-3 w-3" />
                View Product on Amazon
              </Button>
            </div>
          </div>
        )}
        
        <div className="flex gap-2 w-full">
          {/* AI Analysis Button */}
          <Button 
            variant="default" 
            size="sm"
            className="flex-1 gap-1 min-w-0"
            onClick={() => setIsRAGChatOpen(true)}
          >
            <MessageCircle className="h-3 w-3 shrink-0" />
            <span className="truncate">Ask AI</span>
          </Button>
          
          {/* Non-Amazon products - show regular View button */}
          {source !== "amazon" && productUrl && productUrl !== "#" && (
            <Button 
              variant="outline" 
              size="sm"
              className="flex-1 gap-1 min-w-0"
              onClick={() => window.open(productUrl, '_blank')}
            >
              <ExternalLink className="h-3 w-3 shrink-0" />
              <span className="truncate">View</span>
            </Button>
          )}
        </div>
      </CardFooter>
      
      {/* RAG Chat Modal */}
      <RAGChat 
        productName={productName}
        isOpen={isRAGChatOpen}
        onClose={() => setIsRAGChatOpen(false)}
      />
    </Card>
  );
}
