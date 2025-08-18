"use client";

import React, { useState, useEffect } from "react";
import { Card, CardContent, CardHeader } from "~/components/ui/card";
import { Badge } from "~/components/ui/badge";
import { Progress } from "~/components/ui/progress";
import { AlertTriangle, CheckCircle, XCircle, Clock } from "lucide-react";
import { apiUsageCounter } from "~/lib/apiUsageTracker";
import { apiLimitChecker } from "~/lib/apiLimitChecker";

interface ApiUsage {
  service: string;
  current: number;
  limit: number;
  resetDate: string;
  status: 'healthy' | 'warning' | 'critical';
  description: string;
}

export function ApiUsageTracker() {
  const [apiUsages, setApiUsages] = useState<ApiUsage[]>([]);
  const [lastUpdated, setLastUpdated] = useState<Date>(new Date());
  const [isClient, setIsClient] = useState(false);

  // Prevent hydration issues by only showing time after client-side rendering
  useEffect(() => {
    setIsClient(true);
  }, []);

  // Define API limits based on free tiers
  const getApiLimits = (): ApiUsage[] => {
    return [
      {
        service: "Gemini 2.5 Flash",
        current: 12, // 12 requests already used today
        limit: 40, // 40 requests per day (limit before blocking)
        resetDate: "Daily reset",
        status: 'healthy',
        description: "AI product discovery and analysis"
      },
      {
        service: "Google Search",
        current: 0,
        limit: 100, // 100 search queries per day for free CSE
        resetDate: "Daily reset",
        status: 'healthy',
        description: "Google Custom Search results"
      },
      {
        service: "Serper API",
        current: 17, // 17 used (2500 - 2483 remaining)
        limit: 2500, // 2500 searches per month for free tier
        resetDate: "Monthly reset",
        status: 'healthy',
        description: "Alternative search API (2483 credits remaining)"
      },
      {
        service: "Cohere API",
        current: 0,
        limit: 1000, // 1000 requests per month for trial
        resetDate: "Monthly reset", 
        status: 'healthy',
        description: "Text embeddings and NLP"
      },
      {
        service: "ScrapeDo",
        current: 273, // 273/1000 monthly used
        limit: 1000, // 1000 scrapes per month for free tier
        resetDate: "Monthly reset",
        status: 'healthy',
        description: "Web scraping service (limited to 10 searches)"
      }
    ];
  };

  // Calculate status based on usage percentage
  const calculateStatus = (current: number, limit: number): 'healthy' | 'warning' | 'critical' => {
    const percentage = (current / limit) * 100;
    if (percentage >= 90) return 'critical';
    if (percentage >= 70) return 'warning';
    return 'healthy';
  };

  // Get status icon
  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'healthy':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'warning':
        return <AlertTriangle className="h-4 w-4 text-yellow-500" />;
      case 'critical':
        return <XCircle className="h-4 w-4 text-red-500" />;
      default:
        return <Clock className="h-4 w-4 text-gray-500" />;
    }
  };

  // Get status color
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy':
        return 'bg-green-100 text-green-800';
      case 'warning':
        return 'bg-yellow-100 text-yellow-800';
      case 'critical':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  // Fetch current usage from local storage (real data)
  const fetchCurrentUsage = async () => {
    try {
      // Get real usage data from localStorage
      const realUsage = apiUsageCounter.getAllUsage();
      
      const realUsages = [
        {
          service: "Gemini 2.5 Flash",
          current: 12 + (realUsage.gemini || 0), // Start from 12 already used today
          limit: 40, // 40 requests per day (blocking limit)
          resetDate: "Daily reset",
          status: calculateStatus(12 + (realUsage.gemini || 0), 40),
          description: "AI product discovery and analysis"
        },
        {
          service: "Google Search",
          current: realUsage.google_search || 0,
          limit: 100, // 100 search queries per day for free CSE
          resetDate: "Daily reset",
          status: calculateStatus(realUsage.google_search || 0, 100),
          description: "Google Custom Search results"
        },
        {
          service: "Serper API",
          current: 2500 - 2483, // 17 used (2500 total - 2483 remaining)
          limit: 2500, // 2500 searches per month for free tier
          resetDate: "Monthly reset",
          status: calculateStatus(2500 - 2483, 2500),
          description: "Alternative search API (2483 credits remaining)"
        },
        {
          service: "Cohere API",
          current: realUsage.cohere || 0,
          limit: 1000, // 1000 requests per month for trial
          resetDate: "Monthly reset", 
          status: calculateStatus(realUsage.cohere || 0, 1000),
          description: "Text embeddings and NLP"
        },
        {
          service: "ScrapeDo",
          current: 273 + (realUsage.scrapedo || 0), // Start from 273 already used
          limit: 1000, // 1000 scrapes per month, but limited to 10 searches
          resetDate: "Monthly reset",
          status: calculateStatus(273 + (realUsage.scrapedo || 0), 1000),
          description: "Web scraping (limit: 10 searches = 50 credits)"
        },
        {
          service: "ScrapeDo Searches",
          current: apiLimitChecker.getScrapeDoSearchCount(),
          limit: 100, // 100 searches per month limit
          resetDate: "Monthly reset",
          status: calculateStatus(apiLimitChecker.getScrapeDoSearchCount(), 100),
          description: "Search limit (1 search = 5 credits)"
        }
      ];
      
      setApiUsages(realUsages);
      setLastUpdated(new Date());
    } catch (error) {
      console.error('Error fetching API usage:', error);
      // Fallback to default limits
      setApiUsages(getApiLimits());
    }
  };

  useEffect(() => {
    fetchCurrentUsage();
    
    // Refresh usage data every 5 minutes
    const interval = setInterval(fetchCurrentUsage, 5 * 60 * 1000);
    
    return () => clearInterval(interval);
  }, []);

  return (
    <Card className="w-full">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold">API Usage Limits</h3>
          <div className="flex items-center gap-2">
            <Clock className="h-4 w-4 text-muted-foreground" />
            <span className="text-sm text-muted-foreground">
              {isClient ? `Updated: ${lastUpdated.toLocaleTimeString()}` : 'Loading...'}
            </span>
          </div>
        </div>
        <p className="text-sm text-muted-foreground">
          Track your API usage across all services to avoid hitting free tier limits
        </p>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {apiUsages.map((api) => {
            const percentage = (api.current / api.limit) * 100;
            
            return (
              <div key={api.service} className="space-y-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    {getStatusIcon(api.status)}
                    <span className="font-medium">{api.service}</span>
                    <Badge className={getStatusColor(api.status)}>
                      {api.status}
                    </Badge>
                  </div>
                  <div className="text-sm text-muted-foreground">
                    {api.current} / {api.limit.toLocaleString()}
                  </div>
                </div>
                
                <Progress 
                  value={percentage} 
                  className="h-2"
                  indicatorClassName={
                    api.status === 'critical' ? 'bg-red-500' :
                    api.status === 'warning' ? 'bg-yellow-500' :
                    'bg-green-500'
                  }
                />
                
                <div className="flex items-center justify-between text-xs text-muted-foreground">
                  <span>{api.description}</span>
                  <span>{api.resetDate}</span>
                </div>
              </div>
            );
          })}
        </div>
        
        <div className="mt-6 p-3 bg-blue-50 rounded-lg">
          <div className="flex items-start gap-2">
            <AlertTriangle className="h-4 w-4 text-blue-600 mt-0.5" />
            <div className="text-sm">
              <p className="font-medium text-blue-900">Free Tier Limits</p>
              <p className="text-blue-700 mt-1">
                These are approximate limits based on free tier quotas. 
                Consider upgrading to paid plans for higher limits and better reliability.
              </p>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
