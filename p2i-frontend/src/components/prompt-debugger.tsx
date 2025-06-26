"use client";

import { type ScrapeSession } from "~/types";
import { Card, CardContent, CardHeader, CardTitle } from "~/components/ui/card";
import { Badge } from "~/components/ui/badge";

interface PromptDebuggerProps {
  session: ScrapeSession | null;
}

export function PromptDebugger({ session }: PromptDebuggerProps) {
  if (process.env.NODE_ENV !== "development" || !session) {
    return null;
  }

  return (
    <Card className="mt-4">
      <CardHeader>
        <div className="flex justify-between items-center">
          <CardTitle className="text-sm font-mono">Debug: {session.sessionId}</CardTitle>
          <Badge variant="outline">{session.tasks.length} tasks</Badge>
        </div>
        <p className="text-sm text-muted-foreground">
          Prompt: {session.originPrompt}
        </p>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {session.tasks.map((task, index) => (
            <Card key={index} className="p-3">
              <div className="flex items-center gap-2 mb-2">
                <span className="font-medium">{task.productName}</span>
                <Badge variant="secondary">{task.site}</Badge>
                <Badge>{task.taskType}</Badge>
              </div>

              {task.filters && (
                <div className="text-sm space-y-1">
                  <p className="text-muted-foreground text-xs">Filters:</p>
                  <div className="flex gap-2">
                    {Object.entries(task.filters).map(([key, value]) => (
                      <Badge key={key} variant="outline">
                        {key}: {value}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}

              {task.attributes && task.attributes.length > 0 && (
                <div className="text-sm space-y-1 mt-2">
                  <p className="text-muted-foreground text-xs">Attributes:</p>
                  <div className="flex flex-wrap gap-1">
                    {task.attributes.map(attr => (
                      <Badge key={attr} variant="outline">
                        {attr}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}
            </Card>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}

