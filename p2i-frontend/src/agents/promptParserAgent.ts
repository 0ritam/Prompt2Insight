import { z } from "zod";
import { GoogleGenerativeAI } from "@google/generative-ai";
import { type ParsedPrompt } from "~/types";

// Schema for validation
const responseSchema = z.object({
  intent: z.enum(["compare", "search", "recommend"]),
  products: z.array(z.string()).min(1),
  filters: z.object({
    price: z.string().optional(),
    brand: z.string().optional(),
  }).nullable(),
  attributes: z.array(z.string()).nullable(),
}) satisfies z.ZodType<ParsedPrompt>;

// Initialize Gemini
const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY!);

const PROMPT_TEMPLATE = `You are an AI that parses product queries into structured data. Return ONLY a JSON object in this exact format (no markdown, no explanation):

{
  "intent": "compare" or "search" or "recommend",
  "products": ["product1", "product2", ...],
  "filters": {
    "price": "price filter text" (optional),
    "brand": "brand filter text" (optional)
  } or null if no filters,
  "attributes": ["attribute1", "attribute2", ...] or null if no attributes
}

Example for "Compare iPhone 14 and Poco X5 under ₹20000":
{
  "intent": "compare",
  "products": ["iPhone 14", "Poco X5"],
  "filters": {
    "price": "under ₹20000"
  },
  "attributes": null
}

Rules:
1. products array must never be empty
2. filters must be null or an object with optional price/brand
3. attributes must be null or non-empty array
4. NO code blocks or extra formatting`;

export async function parseUserPrompt({ request }: { request: { messages: { content: string }[] } }) {
  try {
    const model = genAI.getGenerativeModel({ model: "gemini-2.5-flash" });
    
    // Get the user's prompt from the messages
    const userPrompt = request.messages[0]?.content;
    if (!userPrompt) {
      throw new Error("No prompt provided");
    }

    // Combine template and user prompt
    const fullPrompt = `${PROMPT_TEMPLATE}\n\nUser prompt: "${userPrompt}"`;

    // Generate response
    const result = await model.generateContent(fullPrompt);

    const response = result.response;
    let textResponse = response.text();
    
    // Clean the response of any markdown or code block formatting
    textResponse = textResponse
      .replace(/^```json\s*/, "") // Remove starting ```json
      .replace(/```$/, "")        // Remove ending ```
      .replace(/^```\s*/, "")     // Remove starting ``` without json
      .trim();                    // Remove any extra whitespace
    
    // Parse the JSON response
    let jsonResponse;
    try {
      jsonResponse = JSON.parse(textResponse);
    } catch (parseError) {
      console.error("Failed to parse JSON response:", textResponse);
      throw new Error("Invalid JSON response from AI");
    }
    
    // Validate with Zod schema
    const validated = responseSchema.parse(jsonResponse);
    return validated;
  } catch (error) {
    console.error("Error parsing prompt:", error);
    throw error;
  }
}
