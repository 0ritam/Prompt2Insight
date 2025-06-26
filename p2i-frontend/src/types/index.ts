// Types for Prompt2Insight project

export type ParsedPrompt = {
  intent: "compare" | "search" | "recommend";
  products: string[];
  filters: {
    price?: string;
    brand?: string;
  } | null;
  attributes: string[] | null;
};

export type ScrapeTask = {
  productName: string;
  site: "flipkart" | "croma" | "91mobiles";
  filters?: {
    price?: string;
    brand?: string;
  };
  attributes?: string[];
  taskType: "listing" | "detail";
};

export type ScrapeSession = {
  sessionId: string;
  originPrompt: string;
  tasks: ScrapeTask[];
};
