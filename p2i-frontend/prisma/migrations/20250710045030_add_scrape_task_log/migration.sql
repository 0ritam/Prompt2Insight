-- CreateTable
CREATE TABLE "ScrapeTaskLog" (
    "id" TEXT NOT NULL PRIMARY KEY,
    "taskId" TEXT NOT NULL,
    "productName" TEXT NOT NULL,
    "site" TEXT NOT NULL,
    "taskType" TEXT NOT NULL,
    "status" TEXT NOT NULL DEFAULT 'pending',
    "sessionId" TEXT NOT NULL,
    "resultData" TEXT,
    "errorMessage" TEXT,
    "createdAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" DATETIME NOT NULL,
    CONSTRAINT "ScrapeTaskLog_sessionId_fkey" FOREIGN KEY ("sessionId") REFERENCES "PromptSession" ("sessionId") ON DELETE CASCADE ON UPDATE CASCADE
);

-- CreateIndex
CREATE UNIQUE INDEX "ScrapeTaskLog_taskId_key" ON "ScrapeTaskLog"("taskId");

-- CreateIndex
CREATE INDEX "ScrapeTaskLog_sessionId_idx" ON "ScrapeTaskLog"("sessionId");

-- CreateIndex
CREATE INDEX "ScrapeTaskLog_createdAt_idx" ON "ScrapeTaskLog"("createdAt");

-- CreateIndex
CREATE INDEX "ScrapeTaskLog_status_idx" ON "ScrapeTaskLog"("status");

-- CreateIndex
CREATE INDEX "ScrapeTaskLog_site_idx" ON "ScrapeTaskLog"("site");
