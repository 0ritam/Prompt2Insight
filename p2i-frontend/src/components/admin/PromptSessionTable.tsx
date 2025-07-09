"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "~/components/ui/card";
import { Badge } from "~/components/ui/badge";
import { Button } from "~/components/ui/button";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "~/components/ui/table";
import { Alert, AlertDescription } from "~/components/ui/alert";
import { Loader2, RefreshCw, Eye, Clock, CheckCircle, XCircle, AlertCircle } from "lucide-react";

interface PromptSession {
  id: string;
  sessionId: string;
  originPrompt: string;
  status: "pending" | "parsed" | "done" | "error";
  resultData: string | null;
  errorMessage: string | null;
  createdAt: string;
  updatedAt: string;
  user: {
    name: string | null;
    email: string | null;
    role: string;
  };
}

interface PromptSessionTableProps {
  limit?: number;
}

export function PromptSessionTable({ limit = 50 }: PromptSessionTableProps) {
  const [sessions, setSessions] = useState<PromptSession[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedSession, setSelectedSession] = useState<PromptSession | null>(null);

  const fetchSessions = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch(`/api/admin/prompt-sessions?limit=${limit}`);
      
      if (!response.ok) {
        throw new Error("Failed to fetch prompt sessions");
      }
      
      const data = await response.json();
      setSessions(data.sessions || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSessions();
  }, [limit]);

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "pending":
        return <Clock className="h-4 w-4 text-yellow-500" />;
      case "parsed":
        return <AlertCircle className="h-4 w-4 text-blue-500" />;
      case "done":
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case "error":
        return <XCircle className="h-4 w-4 text-red-500" />;
      default:
        return <Clock className="h-4 w-4 text-gray-500" />;
    }
  };

  const getStatusBadge = (status: string) => {
    const variants = {
      pending: "secondary",
      parsed: "default",
      done: "default",
      error: "destructive",
    } as const;

    const colors = {
      pending: "bg-yellow-100 text-yellow-800",
      parsed: "bg-blue-100 text-blue-800",
      done: "bg-green-100 text-green-800",
      error: "bg-red-100 text-red-800",
    };

    return (
      <Badge 
        variant={variants[status as keyof typeof variants] || "secondary"}
        className={colors[status as keyof typeof colors]}
      >
        <div className="flex items-center gap-1">
          {getStatusIcon(status)}
          {status}
        </div>
      </Badge>
    );
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  const truncateText = (text: string, maxLength: number = 50) => {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + "...";
  };

  if (loading) {
    return (
      <Card>
        <CardContent className="flex justify-center items-center py-12">
          <div className="flex items-center gap-2">
            <Loader2 className="h-5 w-5 animate-spin" />
            <span>Loading prompt sessions...</span>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Alert variant="destructive">
        <AlertDescription>{error}</AlertDescription>
      </Alert>
    );
  }

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <div className="flex justify-between items-center">
            <CardTitle>Prompt Sessions</CardTitle>
            <Button onClick={fetchSessions} variant="outline" size="sm">
              <RefreshCw className="h-4 w-4 mr-2" />
              Refresh
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {sessions.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              No prompt sessions found.
            </div>
          ) : (
            <div className="rounded-md border">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Session ID</TableHead>
                    <TableHead>User</TableHead>
                    <TableHead>Prompt</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Created</TableHead>
                    <TableHead>Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {sessions.map((session) => (
                    <TableRow key={session.id}>
                      <TableCell className="font-mono text-xs">
                        {session.sessionId.substring(0, 8)}...
                      </TableCell>
                      <TableCell>
                        <div className="space-y-1">
                          <p className="font-medium text-sm">
                            {session.user.name || "No name"}
                          </p>
                          <p className="text-xs text-muted-foreground">
                            {session.user.email}
                          </p>
                        </div>
                      </TableCell>
                      <TableCell>
                        <div className="max-w-xs">
                          <p className="text-sm" title={session.originPrompt}>
                            {truncateText(session.originPrompt, 60)}
                          </p>
                        </div>
                      </TableCell>
                      <TableCell>
                        {getStatusBadge(session.status)}
                      </TableCell>
                      <TableCell className="text-sm text-muted-foreground">
                        {formatDate(session.createdAt)}
                      </TableCell>
                      <TableCell>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => setSelectedSession(session)}
                        >
                          <Eye className="h-4 w-4" />
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Session Details Modal/Card */}
      {selectedSession && (
        <Card className="mt-4">
          <CardHeader>
            <div className="flex justify-between items-center">
              <CardTitle>Session Details</CardTitle>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setSelectedSession(null)}
              >
                Close
              </Button>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-sm font-medium text-muted-foreground">
                  Session ID
                </label>
                <p className="font-mono text-sm">{selectedSession.sessionId}</p>
              </div>
              <div>
                <label className="text-sm font-medium text-muted-foreground">
                  Status
                </label>
                <div className="mt-1">
                  {getStatusBadge(selectedSession.status)}
                </div>
              </div>
            </div>

            <div>
              <label className="text-sm font-medium text-muted-foreground">
                Original Prompt
              </label>
              <p className="mt-1 p-3 bg-muted rounded-md text-sm">
                {selectedSession.originPrompt}
              </p>
            </div>

            {selectedSession.resultData && (
              <div>
                <label className="text-sm font-medium text-muted-foreground">
                  Result Data
                </label>
                <pre className="mt-1 p-3 bg-muted rounded-md text-xs overflow-auto max-h-48">
                  {JSON.stringify(JSON.parse(selectedSession.resultData), null, 2)}
                </pre>
              </div>
            )}

            {selectedSession.errorMessage && (
              <div>
                <label className="text-sm font-medium text-muted-foreground">
                  Error Message
                </label>
                <p className="mt-1 p-3 bg-red-50 border border-red-200 rounded-md text-sm text-red-800">
                  {selectedSession.errorMessage}
                </p>
              </div>
            )}

            <div className="grid grid-cols-2 gap-4 text-sm text-muted-foreground">
              <div>
                <label className="font-medium">Created</label>
                <p>{formatDate(selectedSession.createdAt)}</p>
              </div>
              <div>
                <label className="font-medium">Updated</label>
                <p>{formatDate(selectedSession.updatedAt)}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
