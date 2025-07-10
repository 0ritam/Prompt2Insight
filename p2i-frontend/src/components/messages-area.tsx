"use client";

import React, { useRef, useEffect } from "react";
import { ScrollArea } from "~/components/ui/scroll-area";
import { Card } from "~/components/ui/card";
import { ProductGrid } from "./product-grid";
import { type RoutedResult } from "~/agents/useIntentRouter";

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
