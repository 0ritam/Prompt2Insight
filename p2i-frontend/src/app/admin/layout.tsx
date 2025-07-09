import { redirect } from "next/navigation";
import { type ReactNode } from "react";
import { auth } from "~/server/auth";
import NavHeader from "~/components/nav-header";

export default async function AdminLayout({
  children,
}: {
  children: ReactNode;
}) {
  const session = await auth();

  if (!session?.user?.id) {
    redirect("/login");
  }

  if (!session.user?.email) {
    redirect("/login");
  }

  if (session.user.role !== "admin") {
    redirect("/dashboard"); // Not authorized, redirect to dashboard
  }

  return (
    <div className="flex min-h-screen flex-col">
      <NavHeader email={session.user.email} userRole={session.user.role} />
      <main className="container mx-auto flex-1 py-6">
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900">Admin Panel</h1>
          <p className="text-gray-600 mt-2">
            Welcome to the admin dashboard. Manage users, settings, and system configuration.
          </p>
        </div>
        {children}
      </main>
    </div>
  );
}
