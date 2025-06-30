import { NextRequest, NextResponse } from "next/server";

// Note: This is a placeholder implementation for the Gemini API endpoint
// You'll need to replace this with an actual integration with Gemini API

export async function POST(request: NextRequest) {
  try {
    const { prompt } = await request.json();

    if (!prompt) {
      return NextResponse.json({ error: "Prompt is required" }, { status: 400 });
    }

    // In a real implementation, you would call the Gemini API here
    // For now, we'll simulate a response with some delay
    await new Promise(resolve => setTimeout(resolve, 1500));

    // Generate some mock product suggestions based on the prompt
    const suggestions = generateMockSuggestions(prompt);

    return NextResponse.json({ suggestions });
  } catch (error) {
    console.error("Gemini API error:", error);
    return NextResponse.json(
      { error: "Failed to get product suggestions" },
      { status: 500 }
    );
  }
}

// Mock function to generate product suggestions
// Replace this with real Gemini API integration
function generateMockSuggestions(prompt: string) {
  const lowercasePrompt = prompt.toLowerCase();
  
  // Basic keyword matching to generate somewhat relevant suggestions
  if (lowercasePrompt.includes("iphone") || lowercasePrompt.includes("phone")) {
    return [
      {
        name: "Apple iPhone 14 (128GB) - Blue",
        url: "https://www.flipkart.com/apple-iphone-14-blue-128-gb/p/itm581e963e4f56e",
        price: "₹69,999",
        rating: "4.7",
        image: "https://rukminim2.flixcart.com/image/416/416/xif0q/mobile/3/5/l/-original-imaghx9qmgqsk9s4.jpeg",
        description: "A15 Bionic chip, 6.1-inch Super Retina XDR display"
      },
      {
        name: "Apple iPhone 13 (128GB) - Midnight",
        url: "https://www.flipkart.com/apple-iphone-13-midnight-128-gb/p/itm2b94e9703d542",
        price: "₹59,999",
        rating: "4.6",
        image: "https://rukminim2.flixcart.com/image/416/416/ktketu80/mobile/6/n/d/iphone-13-mlpf3hn-a-apple-original-imag6vpyk3w4zarg.jpeg",
        description: "A15 Bionic chip, Dual camera system"
      },
      {
        name: "Poco X5 5G (6GB RAM, 128GB) - Wildcat Blue",
        url: "https://www.flipkart.com/poco-x5-5g-wildcat-blue-128-gb/p/itm3df35892d28d9",
        price: "₹16,999",
        rating: "4.3",
        image: "https://rukminim2.flixcart.com/image/416/416/xif0q/mobile/l/8/r/-original-imagkp8frwkzxvuh.jpeg",
        description: "Snapdragon 695, 120Hz AMOLED, 5000mAh battery"
      }
    ];
  } else if (lowercasePrompt.includes("laptop") || lowercasePrompt.includes("computer")) {
    return [
      {
        name: "HP Pavilion 14 (Intel Core i5, 16GB, 512GB SSD)",
        url: "https://www.amazon.in/HP-Pavilion-i5-1155G7-Graphics-14-dv2053TU/dp/B0BSNP65PM/",
        price: "₹62,990",
        rating: "4.4",
        image: "https://m.media-amazon.com/images/I/71-i67TNufL._SL1500_.jpg",
        description: "11th Gen i5, 16GB RAM, 512GB SSD, Windows 11"
      },
      {
        name: "Lenovo IdeaPad Slim 3 (AMD Ryzen 5, 8GB, 512GB)",
        url: "https://www.flipkart.com/lenovo-ideapad-slim-3-ryzen-5-hexa-core-5500u-8-gb-512-gb-ssd-windows-11-home-15alh7-thin-light-laptop/p/itm89c11b1908e34",
        price: "₹48,990",
        rating: "4.2",
        image: "https://rukminim2.flixcart.com/image/416/416/xif0q/computer/f/a/o/-original-imaggshd5zgfe8ev.jpeg",
        description: "AMD Ryzen 5, 15.6-inch FHD, Thin & Light"
      },
      {
        name: "ASUS TUF Gaming F15 (Intel i5-11400H, RTX 3050)",
        url: "https://www.flipkart.com/asus-tuf-gaming-f15-core-i5-11th-gen-8-gb-512-gb-ssd-windows-11-home-4-graphics-nvidia-geforce-rtx-3050-fx506hc-hn061w-laptop/p/itm41c127b37e090",
        price: "₹57,990",
        rating: "4.1",
        image: "https://rukminim2.flixcart.com/image/416/416/xif0q/computer/a/c/9/-original-imagg7fpgzkzts4g.jpeg",
        description: "Gaming laptop, 144Hz display, RGB keyboard"
      }
    ];
  } else if (lowercasePrompt.includes("watch") || lowercasePrompt.includes("smartwatch")) {
    return [
      {
        name: "Apple Watch SE (2nd Gen, GPS, 40mm)",
        url: "https://www.flipkart.com/apple-watch-se-gps-40-mm-starlight-aluminium-case-sport-band-regular/p/itmfd794ac8589c7",
        price: "₹29,900",
        rating: "4.6",
        image: "https://rukminim2.flixcart.com/image/416/416/xif0q/smartwatch/h/y/j/-original-imaghxa9gd3scerp.jpeg",
        description: "Heart rate monitoring, activity tracking, water resistant"
      },
      {
        name: "Samsung Galaxy Watch4 (Bluetooth, 44mm)",
        url: "https://www.flipkart.com/samsung-galaxy-watch4-bluetooth-44-mm/p/itmc2f934cb2bbab",
        price: "₹11,999",
        rating: "4.3",
        image: "https://rukminim2.flixcart.com/image/416/416/kt8zb0w0/smartwatch/r/l/n/android-sm-r870nzkainu-samsung-yes-original-imag6zt7sgekgdss.jpeg",
        description: "Body composition analysis, ECG, sleep tracking"
      },
      {
        name: "Fitbit Versa 3 Health & Fitness Smartwatch",
        url: "https://www.amazon.in/Fitbit-Smartwatch-Midnight-Included-Tracking/dp/B08DFLG5SP/",
        price: "₹17,999",
        rating: "4.4",
        image: "https://m.media-amazon.com/images/I/61ZXwnqqOuL._SL1500_.jpg",
        description: "Built-in GPS, 6+ day battery, voice assistant"
      }
    ];
  } else {
    // Generic product suggestions
    return [
      {
        name: "boAt Airdopes 141 True Wireless Earbuds",
        url: "https://www.flipkart.com/boat-airdopes-141-bluetooth-headset/p/itm5f689bdfaace2",
        price: "₹1,299",
        rating: "4.2",
        image: "https://rukminim2.flixcart.com/image/416/416/xif0q/headphone/j/t/c/-original-imagpgcq6zgheyfm.jpeg",
        description: "42H playtime, IPX4 water resistance, ENx technology"
      },
      {
        name: "Mi Power Bank 3i 20000mAh",
        url: "https://www.flipkart.com/mi-power-bank-3i-20000-mah/p/itm4df36ef2204cd",
        price: "₹1,999",
        rating: "4.3",
        image: "https://rukminim2.flixcart.com/image/416/416/xif0q/power-bank/w/g/8/-original-imagmagy6zejebhd.jpeg",
        description: "Fast charging, 18W output, triple port output"
      },
      {
        name: "Logitech MX Master 3S Wireless Mouse",
        url: "https://www.amazon.in/Logitech-Master-Advanced-Wireless-Mouse/dp/B0B1193JZ4/",
        price: "₹8,995",
        rating: "4.7",
        image: "https://m.media-amazon.com/images/I/61ni3t1ryQL._SL1500_.jpg",
        description: "8K DPI tracking, ultra-fast scrolling, ergonomic design"
      }
    ];
  }
}
