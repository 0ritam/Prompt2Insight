// API limit checker for blocking requests
class ApiLimitChecker {
  private storage = typeof window !== 'undefined' ? localStorage : null;
  private today = new Date().toDateString();

  private getGeminiUsage(): number {
    if (!this.storage) return 0;
    
    const data = this.storage.getItem('api_usage_gemini');
    if (!data) return 12; // Start from 12 requests already used today
    
    const parsed = JSON.parse(data);
    if (parsed.date !== this.today) return 12; // New day, but still start from 12
    
    return 12 + (parsed.count || 0); // Add to the 12 already used
  }

  // Check if Gemini API limit is reached (40/day)
  isGeminiLimitReached(): boolean {
    if (!this.storage) return false;
    
    const data = this.storage.getItem('api_usage_gemini');
    if (!data) return false;
    
    const parsed = JSON.parse(data);
    if (parsed.date !== this.today) return false; // New day, reset
    
    return (parsed.count || 0) >= 40;
  }

  // Check if ScrapeDo search limit is reached (100 searches = 500 credits)
  isScrapeDoSearchLimitReached(): boolean {
    if (!this.storage) return false;
    
    const data = this.storage.getItem('api_usage_scrapedo_searches');
    if (!data) return false;
    
    const parsed = JSON.parse(data);
    // Monthly limit for searches
    const currentMonth = new Date().toISOString().slice(0, 7); // YYYY-MM format
    if (parsed.month !== currentMonth) return false; // New month, reset
    
    return (parsed.searches || 0) >= 100;
  }

  // Increment ScrapeDo search count (separate from credits)
  incrementScrapeDoSearch(): void {
    if (!this.storage) return;
    
    const currentMonth = new Date().toISOString().slice(0, 7);
    const data = this.storage.getItem('api_usage_scrapedo_searches');
    
    let parsed = { month: currentMonth, searches: 0 };
    if (data) {
      parsed = JSON.parse(data);
      if (parsed.month !== currentMonth) {
        parsed = { month: currentMonth, searches: 0 }; // Reset for new month
      }
    }
    
    parsed.searches = (parsed.searches || 0) + 1;
    this.storage.setItem('api_usage_scrapedo_searches', JSON.stringify(parsed));
  }

  // Get current ScrapeDo search count
  getScrapeDoSearchCount(): number {
    if (!this.storage) return 0;
    
    const data = this.storage.getItem('api_usage_scrapedo_searches');
    if (!data) return 0;
    
    const parsed = JSON.parse(data);
    const currentMonth = new Date().toISOString().slice(0, 7);
    
    if (parsed.month !== currentMonth) return 0; // New month
    
    return parsed.searches || 0;
  }

  // Get remaining limits
  getRemainingLimits() {
    return {
      gemini: Math.max(0, 40 - this.getGeminiUsage()),
      scrapeDoSearches: Math.max(0, 100 - this.getScrapeDoSearchCount()),
      serper: 2483, // 2483 credits remaining (not used)
      scrapeDo: Math.max(0, 1000 - 273) // Current remaining credits
    };
  }
}

export const apiLimitChecker = new ApiLimitChecker();
