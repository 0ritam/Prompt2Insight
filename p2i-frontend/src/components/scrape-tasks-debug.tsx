"use client";

import { type ScrapeTask } from "~/types";
import { simulateScrapeTasks } from "~/agents/scraperAgent";

export function ScrapeTasksDebug({ tasks }: { tasks: ScrapeTask[] | null }) {
  if (!tasks) return null;

  const handleSimulate = () => {
    void simulateScrapeTasks(tasks);
  };

  return (
    <div className="mt-4 p-4 bg-muted rounded-lg">
      <div className="flex justify-between items-center mb-2">
        <h3 className="text-lg font-semibold">Scraper Instructions:</h3>
        <button
          onClick={handleSimulate}
          className="px-3 py-1 bg-primary text-primary-foreground rounded hover:bg-primary/90"
        >
          Simulate Scraping
        </button>
      </div>
      <pre className="p-4 bg-background rounded text-sm overflow-auto">
        {JSON.stringify(tasks, null, 2)}
      </pre>
    </div>
  );
}
