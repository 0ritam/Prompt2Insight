"use client";

import { useEffect, useState } from "react";
import ScrapeTaskTable from "~/components/admin/ScrapeTaskTable";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "~/components/ui/card";

interface ScrapeTaskStats {
  total: number;
  pending: number;
  scraped: number;
  error: number;
  successRate: string;
}

interface ScrapeTask {
  id: string;
  taskId: string;
  productName: string;
  site: string;
  taskType: string;
  status: string;
  sessionId: string;
  errorMessage?: string | null;
  createdAt: string; // Changed to string to handle serialization
  session: {
    sessionId: string;
    originPrompt: string;
    user: {
      name: string | null;
      email: string | null;
    };
  };
}

function ScrapeTasksContent() {
  const [tasks, setTasks] = useState<ScrapeTask[]>([]);
  const [stats, setStats] = useState<ScrapeTaskStats>({
    total: 0,
    pending: 0,
    scraped: 0,
    error: 0,
    successRate: "0",
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [tasksResponse, statsResponse] = await Promise.all([
        fetch("/api/admin/scrape-tasks"),
        fetch("/api/admin/scrape-tasks/stats"),
      ]);

      if (!tasksResponse.ok || !statsResponse.ok) {
        throw new Error("Failed to fetch data");
      }

      const tasksData = await tasksResponse.json();
      const statsData = await statsResponse.json();

      setTasks(tasksData);
      setStats(statsData);
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
          {[...Array(5)].map((_, i) => (
            <Card key={i}>
              <CardHeader className="space-y-0 pb-2">
                <div className="h-4 bg-gray-200 rounded animate-pulse"></div>
              </CardHeader>
              <CardContent>
                <div className="h-8 bg-gray-200 rounded animate-pulse"></div>
              </CardContent>
            </Card>
          ))}
        </div>
        <Card>
          <CardHeader>
            <div className="h-6 bg-gray-200 rounded animate-pulse w-48"></div>
            <div className="h-4 bg-gray-200 rounded animate-pulse w-64"></div>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {[...Array(5)].map((_, i) => (
                <div key={i} className="h-16 bg-gray-100 rounded animate-pulse"></div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (error) {
    return (
      <Card>
        <CardContent className="p-6">
          <div className="text-center text-red-600">
            Error loading data: {error}
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Tasks</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.total}</div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Pending</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-yellow-600">{stats.pending}</div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Scraped</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">{stats.scraped}</div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Errors</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">{stats.error}</div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Success Rate</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-600">{stats.successRate}%</div>
          </CardContent>
        </Card>
      </div>

      {/* Tasks Table */}
      <ScrapeTaskTable tasks={tasks} />
    </div>
  );
}

export default function ScrapeTasksPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Scraper Tasks</h1>
        <p className="text-gray-600 mt-2">
          Monitor and analyze all scraping tasks across the platform.
        </p>
      </div>

      <ScrapeTasksContent />
    </div>
  );
}
