"use client"

import { AdminSidebar, AdminView } from "@/components/admin/admin-sidebar"
import { DataUpdate } from "@/components/admin/data-update"
import { KnowledgeGraph } from "@/components/admin/knowledge-graph"
import { UserManagement } from "@/components/admin/user-management"
import { ProtectedRoute } from "@/components/protected-route"
import { useState } from "react"

function AdminDashboard() {
    const [activeView, setActiveView] = useState<AdminView>("users")

    return (
        <div className="flex bg-background min-h-screen">
            <AdminSidebar activeView={activeView} onViewChange={setActiveView} />
            <div className="flex-1 p-8 overflow-auto h-[calc(100vh-4rem)]">
                {activeView === "users" && <UserManagement />}
                {activeView === "graph" && <KnowledgeGraph />}
                {activeView === "update" && <DataUpdate />}
            </div>
        </div>
    )
}

export default function AdminPage() {
    return (
        <ProtectedRoute requireAdmin={true}>
            <AdminDashboard />
        </ProtectedRoute>
    )
}
