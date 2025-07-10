"use client";

import { useState } from "react";
import { Button } from "~/components/ui/button";
import { toast } from "sonner";
import { logScrapeTask, updateScrapeTask } from "~/lib/clientLogger";
import { generateSessionId } from "~/lib/session";

interface TestDataButtonProps {
  onDataCreated?: () => void;
}

export default function TestDataButton({ onDataCreated }: TestDataButtonProps) {
  const [isCreating, setIsCreating] = useState(false);

  const createTestData = async () => {
    setIsCreating(true);
    try {
      // Create a test session ID
      const sessionId = generateSessionId();
      
      // First create a test prompt session (required for scraper tasks)
      const sessionResult = await fetch("/api/prompt-sessions", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          sessionId,
          userId: "test-user", // You might want to use actual user ID
          originPrompt: "Find me the best smartphones under $1000",
          status: "done",
          resultData: {
            testData: true,
            generatedBy: "admin-test",
          },
        }),
      });

      if (!sessionResult.ok) {
        throw new Error("Failed to create test session");
      }
      
      // Create some sample scraper tasks
      const sampleTasks = [
        {
          productName: "iPhone 15 Pro",
          site: "amazon.com",
          taskType: "search",
          status: "pending" as const,
          sessionId,
        },
        {
          productName: "Samsung Galaxy S24",
          site: "flipkart.com",
          taskType: "search", 
          status: "pending" as const,
          sessionId,
        },
        {
          productName: "MacBook Air M3",
          site: "amazon.com",
          taskType: "compare",
          status: "pending" as const,
          sessionId,
        },
      ];

      // Log the tasks and then update them with different statuses
      const loggedTasks = [];
      
      for (const taskData of sampleTasks) {
        const result = await logScrapeTask(taskData);
        if (result.success) {
          loggedTasks.push(result.task);
        }
      }

      // Simulate different outcomes for the tasks
      if (loggedTasks.length > 0) {
        // First task: success
        if (loggedTasks[0]) {
          await updateScrapeTask(loggedTasks[0].taskId, {
            status: "scraped",
            resultData: {
              productCount: 5,
              price: "$999.99",
              availability: "In Stock",
            },
          });
        }

        // Second task: error
        if (loggedTasks[1]) {
          await updateScrapeTask(loggedTasks[1].taskId, {
            status: "error",
            errorMessage: "Site temporarily unavailable",
          });
        }

        // Third task: leave as pending
      }

      toast.success("Test data created successfully!");
      
      // Call the callback to refresh parent data
      if (onDataCreated) {
        onDataCreated();
      }
      
    } catch (error) {
      console.error("Failed to create test data:", error);
      toast.error("Failed to create test data");
    } finally {
      setIsCreating(false);
    }
  };

  return (
    <Button 
      onClick={createTestData} 
      disabled={isCreating}
      variant="outline"
      className="mb-4"
    >
      {isCreating ? "Creating..." : "Create Test Data"}
    </Button>
  );
}
