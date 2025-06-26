"use client";

import type { Message } from "~/types";
import { ScrollArea } from "~/components/ui/scroll-area";
import { Card } from "~/components/ui/card";

interface MessagesViewProps {
  messages: Message[];
  messagesEndRef: React.RefObject<HTMLDivElement>;
}

export function MessagesView({ messages, messagesEndRef }: MessagesViewProps) {
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
          <div ref={messagesEndRef} />
        </div>
      </ScrollArea>
    </div>
  );
}
