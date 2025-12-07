"use client"

import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"
import { LayoutDashboard, Share2, UploadCloud, Users } from "lucide-react"

export type AdminView = "users" | "graph" | "update"

interface AdminSidebarProps {
    activeView: AdminView
    onViewChange: (view: AdminView) => void
}

export function AdminSidebar({ activeView, onViewChange }: AdminSidebarProps) {
    const menuItems = [
        {
            id: "users" as AdminView,
            label: "Quản lý người dùng",
            icon: Users,
        },
        {
            id: "graph" as AdminView,
            label: "Knowledge Graph",
            icon: Share2,
        },
        {
            id: "update" as AdminView,
            label: "Cập nhật dữ liệu",
            icon: UploadCloud,
        },
    ]

    return (
        <div className="w-64 bg-card border-r border-border h-[calc(100vh-4rem)] flex flex-col p-4 gap-2">
            <div className="mb-6 px-2">
                <h2 className="text-lg font-semibold flex items-center gap-2">
                    <LayoutDashboard className="h-5 w-5" />
                    Admin Panel
                </h2>
            </div>
            {menuItems.map((item) => (
                <Button
                    key={item.id}
                    variant={activeView === item.id ? "secondary" : "ghost"}
                    className={cn(
                        "justify-start gap-3 w-full",
                        activeView === item.id && "bg-secondary"
                    )}
                    onClick={() => onViewChange(item.id)}
                >
                    <item.icon className="h-4 w-4" />
                    {item.label}
                </Button>
            ))}
        </div>
    )
}
