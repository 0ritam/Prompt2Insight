import { Sparkles, Search, BarChart3 } from "lucide-react";
import Link from "next/link";

export default function HomePage() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center bg-gradient-to-b from-[#2e026d] to-[#15162c] text-white">
      <div className="container flex flex-col items-center justify-center gap-8 px-4 py-16">
        <h1 className="text-5xl font-extrabold tracking-tight text-white sm:text-[4rem]">
          Prompt<span className="text-[hsl(280,100%,70%)]">💡</span>Insight
        </h1>
        <p className="text-lg text-center max-w-xl text-white/80">
          Discover, compare, and analyze products with AI-powered insights. Start a conversation to get personalized recommendations and analytics.
        </p>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 mt-8 w-full max-w-3xl">
          <div className="flex flex-col items-center bg-white/10 rounded-xl p-6 shadow hover:bg-white/20 transition">
            <Sparkles className="h-8 w-8 text-[hsl(280,100%,70%)] mb-2" />
            <h3 className="font-bold text-lg mb-1">AI-Powered Insights</h3>
            <p className="text-sm text-white/70 text-center">Get smart, data-driven product recommendations and comparisons instantly.</p>
          </div>
          <div className="flex flex-col items-center bg-white/10 rounded-xl p-6 shadow hover:bg-white/20 transition">
            <Search className="h-8 w-8 text-[hsl(280,100%,70%)] mb-2" />
            <h3 className="font-bold text-lg mb-1">Conversational Search</h3>
            <p className="text-sm text-white/70 text-center">Chat naturally to find, filter, and analyze products tailored to your needs.</p>
          </div>
          <div className="flex flex-col items-center bg-white/10 rounded-xl p-6 shadow hover:bg-white/20 transition">
            <BarChart3 className="h-8 w-8 text-[hsl(280,100%,70%)] mb-2" />
            <h3 className="font-bold text-lg mb-1">Admin Analytics</h3>
            <p className="text-sm text-white/70 text-center">Track scraping tasks and view analytics in a dedicated admin dashboard.</p>
          </div>
        </div>
        <div className="flex gap-4 mt-10">
          <a
            href="/dashboard"
            className="px-6 py-3 rounded-lg bg-[hsl(280,100%,70%)] text-[#15162c] font-semibold text-lg shadow hover:bg-[hsl(280,100%,60%)] transition"
          >
            Get Started
          </a>
        </div>
        {/* <footer className="mt-12 text-xs text-white/40">&copy; {new Date().getFullYear()} Prompt2Insight. All rights reserved.</footer> */}
      </div>
    </main>
  );
}
