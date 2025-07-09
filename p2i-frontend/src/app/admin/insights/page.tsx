"use client";

import { useState, useEffect } from "react";
import { PromptSessionTable } from "~/components/admin/PromptSessionTable";
import { Card, CardContent, CardHeader, CardTitle } from "~/components/ui/card";
import { Badge } from "~/components/ui/badge";
import { Alert, AlertDescription } from "~/components/ui/alert";
import { 
  Activity, 
  Clock, 
  CheckCircle, 
  XCircle, 
  TrendingUp,
  Users
} from "lucide-react";

interface SessionStats {
  total: number;
  pending: number;
  parsed: number;
  done: number;
  error: number;
  successRate: string;
}

export default function AdminInsightsPage() {
  const [stats, setStats] = useState<SessionStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchStats = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch("/api/admin/prompt-sessions/stats");
      
      if (!response.ok) {
        throw new Error("Failed to fetch session statistics");
      }
      
      const data = await response.json();
      setStats(data.stats);
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();
  }, []);

  const StatCard = ({ 
    title, 
    value, 
    icon: Icon, 
    color = "text-blue-600",
    bgColor = "bg-blue-50"
  }: {
    title: string;
    value: string | number;
    icon: any;
    color?: string;
    bgColor?: string;
  }) => (
    <Card>
      <CardContent className="p-6">
        <div className="flex items-center">
          <div className={`p-2 rounded-lg ${bgColor}`}>
            <Icon className={`h-6 w-6 ${color}`} />
          </div>
          <div className="ml-4">
            <p className="text-sm font-medium text-muted-foreground">{title}</p>
            <p className="text-2xl font-bold">{value}</p>
          </div>
        </div>
      </CardContent>
    </Card>
  );

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Prompt Session Insights</h1>
        <p className="text-muted-foreground mt-2">
          Monitor and analyze user prompt sessions across the platform.
        </p>
      </div>

      {error && (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Statistics Cards */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard
            title="Total Sessions"
            value={stats.total}
            icon={Activity}
            color="text-blue-600"
            bgColor="bg-blue-50"
          />
          
          <StatCard
            title="Completed"
            value={stats.done}
            icon={CheckCircle}
            color="text-green-600"
            bgColor="bg-green-50"
          />
          
          <StatCard
            title="Pending"
            value={stats.pending}
            icon={Clock}
            color="text-yellow-600"
            bgColor="bg-yellow-50"
          />
          
          <StatCard
            title="Errors"
            value={stats.error}
            icon={XCircle}
            color="text-red-600"
            bgColor="bg-red-50"
          />
        </div>
      )}

      {/* Success Rate Card */}
      {stats && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="h-5 w-5" />
              Performance Metrics
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="text-center">
                <p className="text-3xl font-bold text-green-600">{stats.successRate}%</p>
                <p className="text-sm text-muted-foreground">Success Rate</p>
              </div>
              
              <div className="text-center">
                <p className="text-3xl font-bold text-blue-600">{stats.parsed}</p>
                <p className="text-sm text-muted-foreground">Parsed Sessions</p>
              </div>
              
              <div className="text-center">
                <p className="text-3xl font-bold text-purple-600">
                  {stats.total > 0 ? ((stats.error / stats.total) * 100).toFixed(1) : 0}%
                </p>
                <p className="text-sm text-muted-foreground">Error Rate</p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Status Distribution */}
      {stats && (
        <Card>
          <CardHeader>
            <CardTitle>Session Status Distribution</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Badge className="bg-green-100 text-green-800">Done</Badge>
                  <span className="text-sm">Completed successfully</span>
                </div>
                <span className="font-medium">{stats.done}</span>
              </div>
              
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Badge className="bg-blue-100 text-blue-800">Parsed</Badge>
                  <span className="text-sm">Prompt parsed, processing</span>
                </div>
                <span className="font-medium">{stats.parsed}</span>
              </div>
              
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Badge className="bg-yellow-100 text-yellow-800">Pending</Badge>
                  <span className="text-sm">Waiting to be processed</span>
                </div>
                <span className="font-medium">{stats.pending}</span>
              </div>
              
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Badge variant="destructive">Error</Badge>
                  <span className="text-sm">Failed to process</span>
                </div>
                <span className="font-medium">{stats.error}</span>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Sessions Table */}
      <PromptSessionTable limit={100} />
    </div>
  );
}
