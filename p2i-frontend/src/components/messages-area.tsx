"use client";

import React, { useRef, useEffect, useState } from "react";
import { ScrollArea } from "~/components/ui/scroll-area";
import { Card } from "~/components/ui/card";
import { Button } from "~/components/ui/button";
import { ProductGrid } from "./product-grid";
import { type RoutedResult } from "~/agents/useIntentRouter";
import { toast } from "sonner";

export type Message = {
  id: string;
  role: "user" | "system";
  content: string;
  timestamp: string;
};

interface MessagesAreaProps {
  messages: Message[];
  result?: RoutedResult | null;
  originalPrompt?: string;
}

export function MessagesArea({ messages, result, originalPrompt }: MessagesAreaProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [isScrapingAmazon, setIsScrapingAmazon] = useState(false);
  const [amazonResults, setAmazonResults] = useState<any[] | null>(null);

  const handleAmazonScrape = async () => {
    if (!result?.amazonQueryData) {
      toast.error("No Amazon query data available");
      return;
    }

    try {
      setIsScrapingAmazon(true);
      toast.info("🛒 Searching Amazon for live results...");

      const response = await fetch("http://localhost:8001/api/v1/amazon/scrape_amazon", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(result.amazonQueryData),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || "Failed to scrape Amazon");
      }

      const amazonData = await response.json();
      setAmazonResults(amazonData.products || []);
      
      toast.success(`🎉 Found ${amazonData.products?.length || 0} live Amazon results!`);
    } catch (error) {
      const message = error instanceof Error ? error.message : "Failed to scrape Amazon";
      toast.error(message);
      console.error("Amazon scraping error:", error);
    } finally {
      setIsScrapingAmazon(false);
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  return (
    <div className="flex-1 overflow-y-auto p-4 pt-20">
      <ScrollArea className="h-full">
        <div className="space-y-4">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${
                message.role === "user" ? "justify-end" : "justify-start"
              }`}
            >
              <Card
                className={`max-w-[80%] p-4 ${
                  message.role === "user"
                    ? "bg-primary text-primary-foreground"
                    : "bg-muted"
                }`}
              >
                <div className="text-sm">{message.content}</div>
                {message.timestamp && (
                  <div className="text-xs mt-2 opacity-70">
                    {message.timestamp}
                  </div>
                )}
              </Card>
            </div>
          ))}
          
          {/* Show ProductGrid as part of the conversation flow */}
          {result && originalPrompt && (
            <div className="flex justify-start">
              <div className="max-w-[95%] w-full">
                <Card className="bg-muted p-4">
                  <div className="text-sm font-medium mb-4">
                    Results for: "{originalPrompt}"
                  </div>
                  <ProductGrid 
                    products={result.data}
                    source={result.source}
                    prompt={originalPrompt}
                    fallback={result.fallback || result.googleFallback}
                  />
                  
                  {/* Success message after ProductGrid */}
                  <div className="mt-4 p-3 bg-green-50 border border-green-200 rounded-lg">
                    <p className="text-green-800 font-medium text-sm">
                      ✅ Your prompt has been successfully processed!
                    </p>
                    <p className="text-green-600 text-xs mt-1">
                      Found {result.data.length} results from {result.source === "scraper" ? "live data" : result.source === "google" ? "Google Search" : "AI suggestions"}
                    </p>
                  </div>

                  {/* Amazon Integration Button */}
                  {result.amazonReady && !amazonResults && (
                    <div className="mt-4 p-4 bg-gradient-to-r from-orange-50 to-yellow-50 border border-orange-200 rounded-lg">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-orange-800 font-medium text-sm">
                            🔍 Want live Amazon results too?
                          </p>
                          <p className="text-orange-600 text-xs mt-1">
                            Search Amazon in real-time for this product query
                          </p>
                        </div>
                        <Button
                          onClick={handleAmazonScrape}
                          disabled={isScrapingAmazon}
                          className="bg-orange-500 hover:bg-orange-600 text-white"
                          size="sm"
                        >
                          {isScrapingAmazon ? "🔄 Searching..." : "🛒 Search Amazon"}
                        </Button>
                      </div>
                    </div>
                  )}

                  {/* Amazon Results */}
                  {amazonResults && amazonResults.length > 0 && (
                    <div className="mt-4">
                      <div className="mb-3 p-3 bg-orange-50 border border-orange-200 rounded-lg">
                        <p className="text-orange-800 font-medium text-sm">
                          🎉 Live Amazon Results ({amazonResults.length} products found)
                        </p>
                        <p className="text-orange-600 text-xs mt-1">
                          Fresh data scraped directly from Amazon
                        </p>
                      </div>
                      <ProductGrid 
                        products={amazonResults}
                        source="amazon"
                        prompt={originalPrompt}
                        fallback={false}
                      />
                    </div>
                  )}
                </Card>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>
      </ScrollArea>
    </div>
  );
}
