"use client";

import React, { useState, useEffect } from "react";
import { Separator } from "~/components/ui/separator";
import { toast } from "sonner";
import { MessagesArea } from "./messages-area";
import { PromptInput } from "./prompt-input";
import type { Message } from "~/types";

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

interface PromptInsightPanelProps {
  onPromptSubmit: (prompt: string) => Promise<void>;
  isLoading: boolean;
}

export function PromptInsightPanel({ onPromptSubmit, isLoading }: PromptInsightPanelProps) {
  const [messages, setMessages] = useState<Message[]>(initialMessages);

  // Set initial timestamp on client side only
  useEffect(() => {
    if (messages[0] && !messages[0].timestamp) {
      setMessages(messages => messages.map(msg => ({
        ...msg,
        timestamp: formatTime()
      })));
    }
  }, []);

  const handleSubmit = async (promptText: string) => {
    // Add user message
    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: promptText,
      timestamp: formatTime(),
    };

    setMessages((prev) => [...prev, userMessage]);

    try {
      await onPromptSubmit(promptText);
      
      // Add success message
      const systemMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "system",
        content: "Your prompt has been processed successfully!",
        timestamp: formatTime(),
      };

      setMessages((prev) => [...prev, systemMessage]);
    } catch (error) {
      toast.error("Failed to process your prompt. Please try again.");
    }
  };

  const handleExamplePrompt = (prompt: string) => {
    handleSubmit(prompt);
  };

  const clearHistory = () => {
    setMessages([...initialMessages]);
    toast.success("History cleared!");
  };

  return (
    <div className="flex h-screen">
      {/* Left Sidebar */}
      <div className="w-[250px] h-screen border-r flex flex-col bg-background">
        <div className="p-4 font-semibold">Example Prompts</div>
        <Separator />
        <div className="flex-1 p-4">
          <div className="space-y-2">
            {examplePrompts.map((prompt, i) => (
              <div
                key={i}
                className="p-2 rounded-lg hover:bg-muted cursor-pointer text-sm"
                onClick={() => handleExamplePrompt(prompt)}
              >
                {prompt}
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col h-screen">
        <MessagesArea messages={messages} />
        <PromptInput onSubmit={handleSubmit} isLoading={isLoading} />
      </div>
    </div>
  );
}
