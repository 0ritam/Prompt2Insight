class ApiUsageCounter {
  private storage = typeof window !== 'undefined' ? localStorage : null;
  private today = new Date().toDateString();

  // Get current usage for a service
  getUsage(service: string): number {
    if (!this.storage) return 0;
    
    const data = this.storage.getItem(`api_usage_${service}`);
    if (!data) return 0;
    
    const parsed = JSON.parse(data);
    
    // Reset if it's a new day
    if (parsed.date !== this.today) {
      this.resetUsage(service);
      return 0;
    }
    
    return parsed.count || 0;
  }

  // Increment usage for a service
  incrementUsage(service: string): void {
    if (!this.storage) return;
    
    const current = this.getUsage(service);
    const newData = {
      date: this.today,
      count: current + 1
    };
    
    this.storage.setItem(`api_usage_${service}`, JSON.stringify(newData));
  }

  // Reset usage for a service
  resetUsage(service: string): void {
    if (!this.storage) return;
    
    const newData = {
      date: this.today,
      count: 0
    };
    
    this.storage.setItem(`api_usage_${service}`, JSON.stringify(newData));
  }

  // Get all usage data
  getAllUsage(): Record<string, number> {
    const services = ['gemini', 'google_search', 'serper', 'cohere', 'scrapedo'];
    const usage: Record<string, number> = {};
    
    services.forEach(service => {
      usage[service] = this.getUsage(service);
    });
    
    return usage;
  }
}

export const apiUsageCounter = new ApiUsageCounter();
