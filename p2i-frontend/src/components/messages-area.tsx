"use client";

import React, { useRef, useEffect, useState } from "react";
import { ScrollArea } from "~/components/ui/scroll-area";
import { Card } from "~/components/ui/card";
import { Button } from "~/components/ui/button";
import { ProductGrid } from "./product-grid";
import { type RoutedResult } from "~/agents/useIntentRouter";
import { type Message } from "~/types";
import { toast } from "sonner";

interface MessagesAreaProps {
  messages: Message[];
  // Remove the separate result prop since results are now embedded in messages
}

export function MessagesArea({ messages }: MessagesAreaProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [isScrapingAmazon, setIsScrapingAmazon] = useState<{[key: string]: boolean}>({});
  const [amazonResults, setAmazonResults] = useState<{[key: string]: any[]}>({});
  const [showCharts, setShowCharts] = useState<{[key: string]: { price: boolean; specs: boolean }}>({});

  const handleShowPriceChart = (messageId: string) => {
    setShowCharts(prev => ({ 
      ...prev, 
      [messageId]: { 
        price: true, 
        specs: prev[messageId]?.specs || false 
      } 
    }));
  };

  const handleShowSpecsChart = (messageId: string) => {
    setShowCharts(prev => ({ 
      ...prev, 
      [messageId]: { 
        price: prev[messageId]?.price || false,
        specs: true 
      } 
    }));
  };

  const handleHideCharts = (messageId: string) => {
    setShowCharts(prev => ({ ...prev, [messageId]: { price: false, specs: false } }));
  };

  const handleAmazonScrape = async (messageId: string, result: RoutedResult) => {
    if (!result?.amazonQueryData) {
      toast.error("No Amazon query data available");
      return;
    }

    try {
      setIsScrapingAmazon(prev => ({ ...prev, [messageId]: true }));
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
      setAmazonResults(prev => ({ ...prev, [messageId]: amazonData.products || [] }));
      
      toast.success(`🎉 Found ${amazonData.products?.length || 0} live Amazon results!`);
    } catch (error) {
      const message = error instanceof Error ? error.message : "Failed to scrape Amazon";
      toast.error(message);
      console.error("Amazon scraping error:", error);
    } finally {
      setIsScrapingAmazon(prev => ({ ...prev, [messageId]: false }));
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
            <div key={message.id}>
              {/* Regular message display */}
              <div
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

              {/* Show ProductGrid if this system message has result data */}
              {message.role === "system" && message.result && message.originalPrompt && (
                <div className="flex justify-start mt-2">
                  <div className="max-w-[95%] w-full">
                    <Card className="bg-muted p-4">
                      <ProductGrid 
                        products={message.result.data}
                        source={message.result.source}
                        prompt={message.originalPrompt}
                        fallback={message.result.fallback || message.result.googleFallback}
                      />
                      
                      {/* Server-side Chart Images - Only show for AI Discovery results with chart data */}
                      {(message.result.source === "gemini" || message.result.source === "ai_discoverer") && (message.result.price_chart_image || message.result.specs_chart_image) && (
                        <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                          <div className="flex items-center justify-between mb-3">
                            <div>
                              <p className="text-blue-800 font-medium text-sm">
                                📊 Visualize Your Results
                              </p>
                              <p className="text-blue-600 text-xs mt-1">
                                Server-generated chart comparisons
                              </p>
                            </div>
                            <div className="flex gap-2">
                              {message.result.price_chart_image && (
                                <Button
                                  onClick={() => handleShowPriceChart(message.id)}
                                  variant="outline"
                                  size="sm"
                                  className="border-blue-300 text-blue-700 hover:bg-blue-100"
                                >
                                  📊 Price Chart
                                </Button>
                              )}
                              {message.result.specs_chart_image && (
                                <Button
                                  onClick={() => handleShowSpecsChart(message.id)}
                                  variant="outline"
                                  size="sm"
                                  className="border-blue-300 text-blue-700 hover:bg-blue-100"
                                >
                                  ⚙️ Specs Chart
                                </Button>
                              )}
                              {(showCharts[message.id]?.price || showCharts[message.id]?.specs) && (
                                <Button
                                  onClick={() => handleHideCharts(message.id)}
                                  variant="outline"
                                  size="sm"
                                  className="border-gray-300 text-gray-600 hover:bg-gray-100"
                                >
                                  ✖️ Hide Charts
                                </Button>
                              )}
                            </div>
                          </div>
                          
                          {/* Price Chart Image */}
                          {showCharts[message.id]?.price && message.result.price_chart_image && (
                            <div className="mt-4">
                              <h4 className="text-lg font-semibold mb-2">Price Comparison Chart</h4>
                              <img 
                                src={`data:image/png;base64,${message.result.price_chart_image}`}
                                alt="Product Price Comparison Chart"
                                className="w-full h-auto border border-gray-300 rounded-lg shadow-sm"
                              />
                            </div>
                          )}
                          
                          {/* Specs Chart Image */}
                          {showCharts[message.id]?.specs && message.result.specs_chart_image && (
                            <div className="mt-4">
                              <h4 className="text-lg font-semibold mb-2">Specifications Comparison Chart</h4>
                              <img 
                                src={`data:image/png;base64,${message.result.specs_chart_image}`}
                                alt="Product Specifications Comparison Chart"
                                className="w-full h-auto border border-gray-300 rounded-lg shadow-sm"
                              />
                            </div>
                          )}
                        </div>
                      )}
                      
                      {/* Success message after ProductGrid */}
                      <div className="mt-4 p-3 bg-green-50 border border-green-200 rounded-lg">
                        <p className="text-green-800 font-medium text-sm">
                          ✅ Your prompt has been successfully processed!
                        </p>
                        <p className="text-green-600 text-xs mt-1">
                          Found {message.result.data.length} results from {message.result.source === "scraper" ? "live data" : message.result.source === "google" ? "Google Search" : "AI suggestions"}
                        </p>
                      </div>

                      {/* Amazon Integration Button */}
                      {message.result.amazonReady && !amazonResults[message.id] && (
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
                              onClick={() => handleAmazonScrape(message.id, message.result!)}
                              disabled={isScrapingAmazon[message.id] || false}
                              className="bg-orange-500 hover:bg-orange-600 text-white"
                              size="sm"
                            >
                              {isScrapingAmazon[message.id] ? "🔄 Searching..." : "🛒 Search Amazon"}
                            </Button>
                          </div>
                        </div>
                      )}

                      {/* Amazon Results */}
                      {amazonResults[message.id] && amazonResults[message.id]!.length > 0 && (
                        <div className="mt-4">
                          <div className="mb-3 p-3 bg-orange-50 border border-orange-200 rounded-lg">
                            <p className="text-orange-800 font-medium text-sm">
                              🎉 Live Amazon Results ({amazonResults[message.id]!.length} products found)
                            </p>
                            <p className="text-orange-600 text-xs mt-1">
                              Fresh data scraped directly from Amazon
                            </p>
                          </div>
                          <ProductGrid 
                            products={amazonResults[message.id]!}
                            source="amazon"
                            prompt={message.originalPrompt}
                            fallback={false}
                          />
                        </div>
                      )}
                    </Card>
                  </div>
                </div>
              )}
            </div>
          ))}
          
          <div ref={messagesEndRef} />
        </div>
      </ScrollArea>
    </div>
  );
}
