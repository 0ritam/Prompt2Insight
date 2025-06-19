"use client";

import React, { useState, useRef, useEffect } from "react";
import { ScrollArea } from "~/components/ui/scroll-area";
import { Button } from "~/components/ui/button";
import { Card } from "~/components/ui/card";
import { Textarea } from "~/components/ui/textarea";
import { Separator } from "~/components/ui/separator";
import { toast } from "sonner";

// Mock message type
type Message = {
  id: string;
  role: "user" | "system";
  content: string;
  timestamp: string;
};

const formatTime = () => new Date().toLocaleTimeString(undefined, {
  hour: "2-digit",
  minute: "2-digit",
  hour12: true
});

const examplePrompts = [
  "Compare iPhone 14 and Poco X5",
  "Top laptops under ₹40000",
  "Best smartwatches for fitness",
  "Gaming laptops performance comparison",
  "Smart home device recommendations",
];

const initialMessages: Message[] = [
  {
    id: "1",
    role: "system",
    content: "Hello! I'm here to help you analyze products and provide insights. What would you like to know?",
    timestamp: "",  // Empty initially, will be set in useEffect
  },
];

export function PromptInsightPanel() {
  const [messages, setMessages] = useState<Message[]>(initialMessages);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Set initial timestamp on client side only
  useEffect(() => {
    if (messages[0] && !messages[0].timestamp) {
      setMessages(messages => messages.map(msg => ({
        ...msg,
        timestamp: formatTime()
      })));
    }
  }, []);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async () => {
    if (!input.trim()) {
      toast.error("Please enter a prompt first!");
      return;
    }

    setIsLoading(true);

    // Add user message
    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: input,
      timestamp: formatTime(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");

    // Simulate API delay
    setTimeout(() => {
      // Add system response
      const systemMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "system",
        content: "This is a simulated response. In the real application, this would be replaced with actual AI-generated insights about the products you're asking about.",
        timestamp: formatTime(),
      };

      setMessages((prev) => [...prev, systemMessage]);
      setIsLoading(false);
      toast.success("Insight generated!");
    }, 1500);
  };

  const clearHistory = () => {
    setMessages(initialMessages);
    toast.success("History cleared!");
  };

  return (
    <div className="flex h-screen">
      {/* Left Sidebar */}
      <div className="w-[250px] h-screen border-r flex flex-col bg-background">
        <div className="p-4 font-semibold">Prompt History</div>
        <Separator />
        <ScrollArea className="flex-1 p-4">
          <div className="space-y-2">
            {examplePrompts.map((prompt, i) => (
              <div
                key={i}
                className="p-2 rounded-lg hover:bg-muted cursor-pointer text-sm"
                onClick={() => setInput(prompt)}
              >
                {prompt}
              </div>
            ))}
          </div>
        </ScrollArea>
        <Separator />
        <div className="p-4">
          <Button
            variant="outline"
            className="w-full"
            onClick={clearHistory}
          >
            Clear History
          </Button>
        </div>
      </div>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col h-screen">
        {/* Messages Area */}
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
                  >                    <div className="text-sm">{message.content}</div>
                    {message.timestamp && (
                      <div className="text-xs mt-2 opacity-70">
                        {message.timestamp}
                      </div>
                    )}
                  </Card>
                </div>
              ))}
              <div ref={messagesEndRef} />
            </div>
          </ScrollArea>
        </div>

        {/* Input Area */}
        <div className="p-4 border-t bg-background sticky bottom-0">
          <div className="flex gap-2">
            <Textarea
              placeholder="Enter your product analysis prompt..."
              value={input}
              onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setInput(e.target.value)}
              className="min-h-[60px]"
              onKeyDown={(e: React.KeyboardEvent<HTMLTextAreaElement>) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  handleSubmit();
                }
              }}
            />
            <Button
              onClick={handleSubmit}
              disabled={isLoading}
              className="px-6"
            >
              {isLoading ? "Generating..." : "Generate Insight"}
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
