import { type ParsedPrompt, type ScrapeTask } from "~/types";

/**
 * Builds scraping instructions based on the parsed prompt
 * Creates a task for each product with appropriate filters and attributes
 */
export function buildScrapeInstructions(parsedPrompt: ParsedPrompt): ScrapeTask[] {
  return parsedPrompt.products.map((product): ScrapeTask => {
    const baseTask: ScrapeTask = {
      productName: product,
      site: "flipkart", // TODO: Add logic to determine best site for each product
      taskType: parsedPrompt.intent === "compare" ? "detail" : "listing", //This will later affect:Whether to scrape product page or category page
    };

    // Add filters if present
    if (parsedPrompt.filters) {
      baseTask.filters = {
        ...(parsedPrompt.filters.price && { price: parsedPrompt.filters.price }),
        ...(parsedPrompt.filters.brand && { brand: parsedPrompt.filters.brand }),
      };
    }

    // Add attributes if present
    if (parsedPrompt.attributes && parsedPrompt.attributes.length > 0) {
      baseTask.attributes = parsedPrompt.attributes;
    }

    return baseTask;
  });
}
