import { NextRequest, NextResponse } from "next/server";
import { parseUserPrompt } from "~/lib/prompt-parser";
import { z } from "zod";

// Input validation schema
const requestSchema = z.object({
  prompt: z.string().min(1, "Prompt cannot be empty"),
});

export async function POST(request: NextRequest) {
  try {
    // Parse and validate the request body
    const body = await request.json();
    const { prompt } = requestSchema.parse(body);

    // Process the prompt using ts-prompt
    const result = await parseUserPrompt({
      request: {
        messages: [
          {
            // @ts-expect-error: Allow 'role' property for compatibility with LLM APIs
            role: "user",
            content: prompt,
          },
        ],
      },
    });

    // Return the structured result
    return NextResponse.json(result);
  } catch (error) {
    console.error("Prompt parsing error:", error);

    // Handle validation errors
    if (error instanceof z.ZodError) {
      return NextResponse.json(
        { 
          error: "Invalid response format", 
          details: error.issues,
          message: error.issues.map(issue => 
            `${issue.path.join('.')}: ${issue.message}`
          ).join(', ')
        },
        { status: 400 }
      );
    }

    // Handle other errors (LLM failures, etc)
    const errorMessage = error instanceof Error ? error.message : "Unknown error";
    return NextResponse.json(
      { 
        error: "Failed to parse prompt",
        message: errorMessage
      },
      { status: 500 }
    );
  }
}
