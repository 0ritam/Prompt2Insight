"use server"

import { redirect } from "next/navigation";
import type { ReactNode } from "react";
import NavHeader from "~/components/nav-header";
import { auth } from "~/server/auth";

export default async function DashboardLayout({
    children}:{children: ReactNode; 
}) {
    const session = await auth();

    if (!session?.user?.id) {
        redirect("/login");
    }

    if (!session.user?.email) {
        redirect("/login");
    }

    return <div className="flex min-h-screen flex-col">
        <NavHeader email={session.user.email} />
        <main className="container mx-auto flex-1 py-6">{children}</main>
    </div>
}