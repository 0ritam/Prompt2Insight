/**
 * Example usage of scraper task logging functions
 * This file demonstrates how to log and update scraper tasks
 */

import { logScrapeTask, updateScrapeTask } from "~/lib/clientLogger";
import { v4 as uuidv4 } from "uuid";

/**
 * Example function showing how to log a scraper task
 * You would call this when starting a scraping operation
 */
export async function exampleLogScrapeTask(sessionId: string) {
  const taskData = {
    productName: "iPhone 15 Pro",
    site: "amazon.com",
    taskType: "search",
    status: "pending" as const,
    sessionId: sessionId,
  };

  const result = await logScrapeTask(taskData);
  
  if (result.success) {
    console.log("Scrape task logged successfully:", result.task);
    return result.task;
  } else {
    console.error("Failed to log scrape task:", result.error);
    return null;
  }
}

/**
 * Example function showing how to update a scraper task
 * You would call this when the scraping operation completes or fails
 */
export async function exampleUpdateScrapeTask(taskId: string, success: boolean, data?: any, error?: string) {
  const updates = {
    status: success ? "scraped" as const : "error" as const,
    resultData: data,
    errorMessage: error,
  };

  const result = await updateScrapeTask(taskId, updates);
  
  if (result.success) {
    console.log("Scrape task updated successfully:", result.task);
    return result.task;
  } else {
    console.error("Failed to update scrape task:", result.error);
    return null;
  }
}

/**
 * Complete example workflow for scraper task logging
 */
export async function exampleScrapeTaskWorkflow(sessionId: string) {
  // 1. Log the start of a scraping task
  const task = await exampleLogScrapeTask(sessionId);
  
  if (!task) {
    console.error("Failed to start scrape task logging");
    return;
  }

  // 2. Simulate some scraping work
  console.log("Starting scraping for:", task.productName);
  
  // 3. Simulate success or failure
  const success = Math.random() > 0.3; // 70% success rate
  
  if (success) {
    // 4a. Update with success data
    const scrapedData = {
      price: "$999.99",
      availability: "In Stock",
      rating: 4.5,
      reviews: 1234,
    };
    
    await exampleUpdateScrapeTask(task.taskId, true, scrapedData);
  } else {
    // 4b. Update with error
    await exampleUpdateScrapeTask(
      task.taskId, 
      false, 
      null, 
      "Failed to scrape product: Site is temporarily unavailable"
    );
  }
}
