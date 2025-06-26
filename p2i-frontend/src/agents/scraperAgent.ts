import { type ScrapeTask } from "~/types";

const SCRAPE_DELAY = 300; // milliseconds between scrapes

export async function simulateScrapeTasks(tasks: ScrapeTask[]): Promise<void> {
  for (const task of tasks) {
    // Add delay between logs
    await new Promise(resolve => setTimeout(resolve, SCRAPE_DELAY));

    // Format filters for display
    const filtersStr = task.filters 
      ? JSON.stringify(task.filters)
      : "none";

    // Format attributes for display
    const attributesStr = task.attributes 
      ? task.attributes.join(", ") 
      : "none";

    // Log the task details
    console.log(
      `🔍 Scraping Task:
  Product: ${task.productName}
  Site: ${task.site}
  Type: ${task.taskType}
  Filters: ${filtersStr}
  Attributes: ${attributesStr}
      `
    );
  }

  console.log(`✅ Completed ${tasks.length} scraping tasks`);
}
