"use client";

import React, { useState } from "react";
import type { FormEvent } from "react";
import { Textarea } from "~/components/ui/textarea";
import { Button } from "~/components/ui/button";

interface PromptInputProps {
  onSubmit: (prompt: string) => void;
  isLoading: boolean;
}

export function PromptInput({ onSubmit, isLoading }: PromptInputProps) {
  const [prompt, setPrompt] = useState("");

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (!prompt.trim()) return;
    
    onSubmit(prompt);
    setPrompt("");
  };

  return (
    <form onSubmit={handleSubmit} className="p-4 border-t">
      <div className="flex gap-2">
        <Textarea
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="Enter your prompt here..."
          className="flex-1"
          rows={1}
          disabled={isLoading}
        />
        <Button type="submit" disabled={isLoading || !prompt.trim()}>
          Generate
        </Button>
      </div>
    </form>
  );
}
