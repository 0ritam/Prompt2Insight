# Flipkart Scraper Maintenance Guide

## How Often to Update Code

### Weekly Monitoring (Automated)
- Run health checks: `python scraper_health_checker.py`
- Check API endpoint: `GET /health-check`
- Monitor success rates in logs

### Monthly Updates (If Needed)
- Update selectors if health check shows degraded performance
- Test with different product categories
- Update user agents and headers

### Quarterly Reviews
- Review and update selector lists
- Test against Flipkart's latest UI changes
- Update dependencies and security patches

## Warning Signs That Updates Are Needed

### 🚨 Critical (Update Immediately)
- Products found = 0 consistently
- Health check shows "critical" status
- Multiple 403/429 errors (blocked)
- Exception rates > 50%

### ⚠️ Degraded (Update Within Week)
- Products found < 50% of expected
- Price extraction failing frequently
- Health check shows "degraded" status
- Slow response times (>30s)

### ✅ Good (Monitor Only)
- Products found > 80% success rate
- Health check shows "good" status
- Response times < 15s
- Low exception rates

## Quick Fixes Without Code Changes

### 1. Config Updates (scraper_config.json)
```json
{
  "selectors": {
    "title_selectors": [
      "NEW_SELECTOR_HERE",
      "div._4rR01T",
      // ... existing selectors
    ]
  }
}
```

### 2. Header Rotation
```json
{
  "headers": {
    "User-Agent": "NEW_USER_AGENT_STRING"
  }
}
```

### 3. Request Delays
```json
{
  "scraping_config": {
    "delay_between_requests": 2  // Increase if getting blocked
  }
}
```

## Testing Commands

### Test Scraper Health
```bash
python scraper_health_checker.py
```

### Test API Health
```bash
curl http://localhost:8001/health-check
```

### Test Specific Query
```bash
curl -X POST http://localhost:8001/scrape-natural \
  -H "Content-Type: application/json" \
  -d '{"query": "test laptop", "max_products": 1}'
```

## Emergency Backup Plan

If scraping completely breaks:

1. **Use Cached Data**: Implement result caching
2. **Alternative Sites**: Add Amazon/other e-commerce APIs
3. **Manual Override**: Allow manual product data input
4. **Fallback Service**: Use third-party product APIs

## Monitoring Dashboard

Set up automated monitoring:

1. **Daily Health Checks**: Cron job running health checker
2. **Success Rate Tracking**: Log success/failure rates
3. **Performance Metrics**: Response times and product counts
4. **Alert System**: Email/Slack when health degrades

## Future-Proofing Strategies

### 1. API-First Approach
- Look for official Flipkart APIs
- Use product comparison API services
- Consider paid scraping services for backup

### 2. Machine Learning Selector Detection
- Train models to identify product elements
- Auto-adapt to layout changes
- Smart fallback selector generation

### 3. Distributed Scraping
- Multiple IP addresses/proxies
- Rotate user agents automatically
- Load balancing across instances

## Cost-Benefit Analysis

### DIY Maintenance
- **Cost**: 2-4 hours/month developer time
- **Benefits**: Full control, customization
- **Risks**: Breakage, IP blocking

### Managed Services
- **Cost**: $50-500/month for APIs
- **Benefits**: Reliable, maintained
- **Risks**: Limited customization, dependency

### Recommendation
Start with DIY + health monitoring, migrate to APIs if maintenance becomes too frequent.
