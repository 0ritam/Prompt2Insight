"use client";

import React, { useState } from "react";
import { Button } from "~/components/ui/button";
import { Input } from "~/components/ui/input";
import { Label } from "~/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle } from "~/components/ui/card";
import { Badge } from "~/components/ui/badge";
import { 
  Select, 
  SelectContent, 
  SelectItem, 
  SelectTrigger, 
  SelectValue 
} from "~/components/ui/select";
import { MessageCircle, Loader2, User, Bot } from "lucide-react";
import { toast } from "sonner";

interface RAGChatProps {
  productName: string;
  isOpen: boolean;
  onClose: () => void;
}

interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  persona?: string;
  timestamp: string;
}

const PERSONA_OPTIONS = [
  { 
    value: "general", 
    label: "General Analysis", 
    description: "Balanced overview for all users",
    icon: "⚖️"
  },
  { 
    value: "budget_student", 
    label: "Budget Student", 
    description: "Price-focused analysis for students",
    icon: "🎓"
  },
  { 
    value: "power_user", 
    label: "Power User", 
    description: "Technical deep-dive analysis",
    icon: "⚡"
  }
];

export function RAGChat({ productName, isOpen, onClose }: RAGChatProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputValue, setInputValue] = useState("");
  const [selectedPersona, setSelectedPersona] = useState("general");
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!inputValue.trim() || isLoading) return;

    const userMessage: ChatMessage = {
      role: "user",
      content: inputValue,
      timestamp: new Date().toLocaleTimeString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue("");
    setIsLoading(true);

    try {
      const response = await fetch("http://localhost:8001/api/v1/rag/ask", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          product_name: productName,
          question: inputValue,
          persona: selectedPersona
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      const assistantMessage: ChatMessage = {
        role: "assistant",
        content: data.answer,
        persona: data.persona_used,
        timestamp: new Date().toLocaleTimeString()
      };

      setMessages(prev => [...prev, assistantMessage]);
      
      toast.success(`Response generated in ${data.execution_time?.toFixed(2)}s`);
      
    } catch (error) {
      console.error("Error calling RAG API:", error);
      toast.error("Failed to get AI response. Please try again.");
      
      const errorMessage: ChatMessage = {
        role: "assistant",
        content: "Sorry, I encountered an error while processing your question. Please try again.",
        timestamp: new Date().toLocaleTimeString()
      };
      
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const clearChat = () => {
    setMessages([]);
    toast.success("Chat history cleared");
  };

  if (!isOpen) return null;

  const selectedPersonaOption = PERSONA_OPTIONS.find(p => p.value === selectedPersona);

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <Card className="w-full max-w-2xl h-[80vh] flex flex-col">
        <CardHeader className="flex-shrink-0 pb-4">
          <div className="flex items-center justify-between">
            <CardTitle className="text-lg flex items-center gap-2">
              <MessageCircle className="h-5 w-5" />
              Ask about {productName}
            </CardTitle>
            <Button variant="outline" size="sm" onClick={onClose}>
              ✕
            </Button>
          </div>
          
          {/* Persona Selection */}
          <div className="space-y-2">
            <Label className="text-sm font-medium">Analysis Perspective</Label>
            <Select value={selectedPersona} onValueChange={setSelectedPersona}>
              <SelectTrigger className="w-full">
                <SelectValue placeholder="Select analysis style">
                  {selectedPersonaOption && (
                    <div className="flex items-center gap-2">
                      <span>{selectedPersonaOption.icon}</span>
                      <span>{selectedPersonaOption.label}</span>
                    </div>
                  )}
                </SelectValue>
              </SelectTrigger>
              <SelectContent>
                {PERSONA_OPTIONS.map((option) => (
                  <SelectItem key={option.value} value={option.value}>
                    <div className="flex items-center gap-2">
                      <span>{option.icon}</span>
                      <div>
                        <div className="font-medium">{option.label}</div>
                        <div className="text-xs text-muted-foreground">
                          {option.description}
                        </div>
                      </div>
                    </div>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </CardHeader>

        <CardContent className="flex-1 flex flex-col overflow-hidden">
          {/* Chat Messages */}
          <div className="flex-1 overflow-y-auto space-y-4 mb-4 pr-2">
            {messages.length === 0 ? (
              <div className="text-center text-muted-foreground py-8">
                <MessageCircle className="h-12 w-12 mx-auto mb-4 opacity-50" />
                <p className="text-sm">Ask me anything about this product!</p>
                <p className="text-xs mt-2">
                  Try: "Is this good value for money?" or "What are the pros and cons?"
                </p>
              </div>
            ) : (
              messages.map((message, index) => (
                <div key={index} className={`flex gap-3 ${message.role === "user" ? "justify-end" : "justify-start"}`}>
                  {message.role === "assistant" && (
                    <div className="flex-shrink-0">
                      <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center">
                        <Bot className="h-4 w-4" />
                      </div>
                    </div>
                  )}
                  
                  <div className={`max-w-[80%] ${message.role === "user" ? "order-first" : ""}`}>
                    <div className={`rounded-lg p-3 ${
                      message.role === "user" 
                        ? "bg-primary text-primary-foreground" 
                        : "bg-muted"
                    }`}>
                      {message.role === "assistant" ? (
                        <div 
                          className="text-sm prose prose-sm max-w-none"
                          dangerouslySetInnerHTML={{
                            __html: message.content
                              .replace(/### \*\*(.*?)\*\*/g, '<h4 class="font-semibold text-base mb-2 mt-3 first:mt-0">$1</h4>')
                              .replace(/---/g, '<hr class="my-3 border-border">')
                              .replace(/\* \*\*(.*?):\*\* (.*?)(?=\n|$)/g, '<div class="mb-2"><strong class="text-foreground">$1:</strong> <span class="text-muted-foreground">$2</span></div>')
                              .replace(/\n/g, '<br/>')
                          }}
                        />
                      ) : (
                        <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                      )}
                    </div>
                    <div className="flex items-center gap-2 mt-1">
                      <span className="text-xs text-muted-foreground">{message.timestamp}</span>
                      {message.persona && (
                        <Badge variant="outline" className="text-xs">
                          {PERSONA_OPTIONS.find(p => p.value === message.persona)?.icon} {PERSONA_OPTIONS.find(p => p.value === message.persona)?.label}
                        </Badge>
                      )}
                    </div>
                  </div>
                  
                  {message.role === "user" && (
                    <div className="flex-shrink-0">
                      <div className="w-8 h-8 rounded-full bg-muted flex items-center justify-center">
                        <User className="h-4 w-4" />
                      </div>
                    </div>
                  )}
                </div>
              ))
            )}
            
            {isLoading && (
              <div className="flex justify-start gap-3">
                <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center">
                  <Bot className="h-4 w-4" />
                </div>
                <div className="bg-muted rounded-lg p-3">
                  <div className="flex items-center gap-2">
                    <Loader2 className="h-4 w-4 animate-spin" />
                    <span className="text-sm">Analyzing {productName}...</span>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Chat Input */}
          <form onSubmit={handleSubmit} className="flex gap-2">
            <Input
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              placeholder="Ask a question about this product..."
              disabled={isLoading}
              className="flex-1"
            />
            <Button type="submit" disabled={isLoading || !inputValue.trim()}>
              {isLoading ? <Loader2 className="h-4 w-4 animate-spin" /> : "Send"}
            </Button>
          </form>
          
          {messages.length > 0 && (
            <div className="flex justify-center mt-2">
              <Button variant="ghost" size="sm" onClick={clearChat}>
                Clear Chat
              </Button>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
