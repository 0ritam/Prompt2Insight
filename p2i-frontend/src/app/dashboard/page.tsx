"use client";

import { PromptInsightPanel } from "~/components/prompt-insight-panel";

export default function DashboardPage() {
  return (
    <div className="min-h-screen bg-background">
      <PromptInsightPanel />
    </div>
  );
}