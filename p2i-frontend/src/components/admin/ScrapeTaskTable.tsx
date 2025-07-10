"use client";

import { Badge } from "~/components/ui/badge";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "~/components/ui/card";

interface ScrapeTask {
  id: string;
  taskId: string;
  productName: string;
  site: string;
  taskType: string;
  status: string; // Changed from union type to string to match Prisma return type
  sessionId: string;
  errorMessage?: string | null;
  createdAt: string | Date; // Accept both string and Date for flexibility
  session: {
    sessionId: string;
    originPrompt: string;
    user: {
      name: string | null;
      email: string | null;
    };
  };
}

interface ScrapeTaskTableProps {
  tasks: ScrapeTask[];
}

function getStatusBadgeVariant(status: string) {
  switch (status) {
    case "pending":
      return "default";
    case "scraped":
      return "default";
    case "error":
      return "destructive";
    default:
      return "secondary";
  }
}

function getStatusColor(status: string) {
  switch (status) {
    case "pending":
      return "bg-yellow-100 text-yellow-800";
    case "scraped":
      return "bg-green-100 text-green-800";
    case "error":
      return "bg-red-100 text-red-800";
    default:
      return "bg-gray-100 text-gray-800";
  }
}

export default function ScrapeTaskTable({ tasks }: ScrapeTaskTableProps) {
  if (tasks.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Scraper Tasks</CardTitle>
          <CardDescription>
            Track all scraping tasks with their status and details
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8 text-gray-500">
            No scraper tasks found. Tasks will appear here when users start scraping.
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Scraper Tasks ({tasks.length})</CardTitle>
        <CardDescription>
          Track all scraping tasks with their status and details
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="overflow-x-auto">
          <table className="w-full border-collapse">
            <thead>
              <tr className="border-b bg-gray-50">
                <th className="text-left p-3 font-medium text-gray-700">Product</th>
                <th className="text-left p-3 font-medium text-gray-700">Site</th>
                <th className="text-left p-3 font-medium text-gray-700">Type</th>
                <th className="text-left p-3 font-medium text-gray-700">Status</th>
                <th className="text-left p-3 font-medium text-gray-700">User</th>
                <th className="text-left p-3 font-medium text-gray-700">Session</th>
                <th className="text-left p-3 font-medium text-gray-700">Created</th>
              </tr>
            </thead>
            <tbody>
              {tasks.map((task) => (
                <tr key={task.id} className="border-b hover:bg-gray-50">
                  <td className="p-3">
                    <div className="font-medium text-gray-900">
                      {task.productName}
                    </div>
                    {task.errorMessage && (
                      <div className="text-sm text-red-600 mt-1">
                        {task.errorMessage}
                      </div>
                    )}
                  </td>
                  <td className="p-3">
                    <div className="text-sm text-gray-600">{task.site}</div>
                  </td>
                  <td className="p-3">
                    <Badge variant="outline" className="text-xs">
                      {task.taskType}
                    </Badge>
                  </td>
                  <td className="p-3">
                    <Badge 
                      className={`text-xs ${getStatusColor(task.status)}`}
                      variant={getStatusBadgeVariant(task.status)}
                    >
                      {task.status}
                    </Badge>
                  </td>
                  <td className="p-3">
                    <div className="text-sm">
                      <div className="font-medium text-gray-900">
                        {task.session.user.name || "Unknown"}
                      </div>
                      <div className="text-gray-600">
                        {task.session.user.email}
                      </div>
                    </div>
                  </td>
                  <td className="p-3">
                    <div className="text-sm">
                      <div className="font-mono text-xs text-gray-600">
                        {task.sessionId.slice(0, 8)}...
                      </div>
                      <div className="text-gray-500 text-xs mt-1 max-w-32 truncate">
                        {task.session.originPrompt}
                      </div>
                    </div>
                  </td>
                  <td className="p-3">
                    <div className="text-sm text-gray-600">
                      {new Date(task.createdAt).toLocaleDateString()}
                    </div>
                    <div className="text-xs text-gray-500">
                      {new Date(task.createdAt).toLocaleTimeString()}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </CardContent>
    </Card>
  );
}
