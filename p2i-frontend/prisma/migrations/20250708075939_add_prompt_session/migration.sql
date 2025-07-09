-- CreateTable
CREATE TABLE "PromptSession" (
    "id" TEXT NOT NULL PRIMARY KEY,
    "sessionId" TEXT NOT NULL,
    "userId" TEXT NOT NULL,
    "originPrompt" TEXT NOT NULL,
    "status" TEXT NOT NULL DEFAULT 'pending',
    "resultData" TEXT,
    "errorMessage" TEXT,
    "createdAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" DATETIME NOT NULL,
    CONSTRAINT "PromptSession_userId_fkey" FOREIGN KEY ("userId") REFERENCES "User" ("id") ON DELETE CASCADE ON UPDATE CASCADE
);

-- CreateIndex
CREATE UNIQUE INDEX "PromptSession_sessionId_key" ON "PromptSession"("sessionId");

-- CreateIndex
CREATE INDEX "PromptSession_userId_idx" ON "PromptSession"("userId");

-- CreateIndex
CREATE INDEX "PromptSession_createdAt_idx" ON "PromptSession"("createdAt");

-- CreateIndex
CREATE INDEX "PromptSession_status_idx" ON "PromptSession"("status");
