import { NextRequest, NextResponse } from "next/server";
import { z } from "zod";
import { v4 as uuidv4 } from "uuid";
import { buildScrapeInstructions } from "~/agents/routerAgent";
import { type ScrapeSession } from "~/types";

// Schema for validating individual scrape tasks
const scrapeTaskSchema = z.object({
  productName: z.string(),
  site: z.enum(["flipkart", "croma", "91mobiles"]),
  taskType: z.enum(["listing", "detail"]),
  filters: z.object({
    price: z.string().optional(),
    brand: z.string().optional(),
  }).optional(),
  attributes: z.array(z.string()).optional(),
});

// Schema for validating the scrape session
const scrapeSessionSchema = z.object({
  sessionId: z.string().uuid(),
  originPrompt: z.string(),
  tasks: z.array(scrapeTaskSchema),
});

// Input validation schema matching ParsedPrompt type
const parsedPromptSchema = z.object({
  intent: z.enum(["compare", "search", "recommend"]),
  products: z.array(z.string()).min(1),
  filters: z.object({
    price: z.string().optional(),
    brand: z.string().optional(),
  }).nullable(),
  attributes: z.array(z.string()).nullable(),
});

export async function POST(request: NextRequest) {
  try {
    // Parse and validate the request body
    const body = await request.json();
    const parsedPrompt = parsedPromptSchema.parse(body);

    // Build scrape instructions
    const scrapeTasks = buildScrapeInstructions(parsedPrompt);

    // Validate individual tasks
    for (const task of scrapeTasks) {
      try {
        scrapeTaskSchema.parse(task);
      } catch (validationError) {
        if (validationError instanceof z.ZodError) {
          return NextResponse.json(
            {
              error: "Invalid scrape task format",
              task: task,
              details: validationError.issues,
            },
            { status: 400 }
          );
        }
      }
    }

    // Create the session wrapper
    const scrapeSession: ScrapeSession = {
      sessionId: uuidv4(),
      originPrompt: parsedPrompt.products.join(" "), // Using products as origin prompt for now
      tasks: scrapeTasks,
    };

    // Validate the entire session
    try {
      scrapeSessionSchema.parse(scrapeSession);
    } catch (validationError) {
      if (validationError instanceof z.ZodError) {
        return NextResponse.json(
          {
            error: "Invalid scrape session format",
            details: validationError.issues,
          },
          { status: 400 }
        );
      }
    }

    // Return the validated session
    return NextResponse.json(scrapeSession);
  } catch (error) {
    console.error("Error building route instructions:", error);

    // Handle validation errors
    if (error instanceof z.ZodError) {
      return NextResponse.json(
        {
          error: "Invalid request format",
          details: error.issues,
          message: error.issues
            .map((issue) => `${issue.path.join(".")}: ${issue.message}`)
            .join(", "),
        },
        { status: 400 }
      );
    }

    // Handle other errors
    return NextResponse.json(
      {
        error: "Failed to build route instructions",
        message: error instanceof Error ? error.message : "Unknown error",
      },
      { status: 500 }
    );
  }
}
