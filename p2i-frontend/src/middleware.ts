import { NextRequest, NextResponse } from "next/server";
import { auth } from "~/server/auth";

export default async function middleware(request: NextRequest) {
  const session = await auth();
  
  // Check if user is trying to access admin routes
  if (request.nextUrl.pathname.startsWith("/admin")) {
    if (!session) {
      // Redirect unauthenticated users to login
      return NextResponse.redirect(new URL("/login", request.url));
    }
    
    if (session.user?.role !== "admin") {
      // Redirect non-admin users to dashboard
      return NextResponse.redirect(new URL("/dashboard", request.url));
    }
  }
  
  // Check if user is trying to access dashboard routes
  if (request.nextUrl.pathname.startsWith("/dashboard")) {
    if (!session) {
      // Redirect unauthenticated users to login
      return NextResponse.redirect(new URL("/login", request.url));
    }
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    "/admin/:path*",
    "/dashboard/:path*"
  ],
};
