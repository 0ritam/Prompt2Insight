import { NextRequest, NextResponse } from "next/server";

// Mock scraper endpoint to replace the FastAPI backend temporarily
export async function POST(request: NextRequest) {
  try {
    const { tasks } = await request.json();
    const forceAI = request.nextUrl.searchParams.get("force_ai") === "true";

    if (!tasks || !Array.isArray(tasks)) {
      return NextResponse.json({ error: "Tasks array is required" }, { status: 400 });
    }

    // Add artificial delay to simulate network request
    await new Promise(resolve => setTimeout(resolve, 1000));

    // Generate mock scraped products based on the tasks
    const scrapedData = tasks.map(task => ({
      taskId: task.id,
      source: forceAI ? "ai-fallback" : "scraper",
      products: generateMockProducts(task.query)
    }));

    return NextResponse.json({
      success: true,
      data: scrapedData
    });
  } catch (error) {
    console.error("Mock scraper error:", error);
    return NextResponse.json(
      { success: false, message: "Failed to process scraping request" },
      { status: 500 }
    );
  }
}

function generateMockProducts(query: string) {
  const products = [];
  const lowercaseQuery = query.toLowerCase();

  // Generate 3-5 mock products based on query keywords
  const count = Math.floor(Math.random() * 3) + 3;
  
  for (let i = 0; i < count; i++) {
    products.push({
      id: `product-${Math.random().toString(36).substr(2, 9)}`,
      name: `${query} Product ${i + 1}`,
      price: Math.floor(Math.random() * 50000) + 999,
      rating: (Math.random() * 2 + 3).toFixed(1), // Random rating between 3.0-5.0
      reviews: Math.floor(Math.random() * 1000) + 50,
      description: `High-quality ${query} with great features and specifications.`,
      url: `https://example.com/product-${i + 1}`,
      image: `https://picsum.photos/400/400?random=${i}`,
      store: "Example Store",
      inStock: Math.random() > 0.2, // 80% chance of being in stock
      specifications: {
        brand: "Example Brand",
        model: `Model ${new Date().getFullYear()}`,
        color: ["Black", "Silver", "Gold"][Math.floor(Math.random() * 3)]
      }
    });
  }

  return products;
}
