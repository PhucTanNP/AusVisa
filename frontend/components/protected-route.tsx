"use client"

import { useAuth } from '@/hooks/use-auth'
import { useRouter } from 'next/navigation'
import { useEffect } from 'react'

interface ProtectedRouteProps {
    children: React.ReactNode
    requireAdmin?: boolean
}

export function ProtectedRoute({ children, requireAdmin = false }: ProtectedRouteProps) {
    const { user, isLoading } = useAuth()
    const router = useRouter()

    useEffect(() => {
        if (!isLoading) {
            if (!user) {
                // Not authenticated, redirect to login
                router.push('/login')
            } else if (requireAdmin && user.role !== 'admin') {
                // Not admin, redirect to chat
                router.push('/chat')
            }
        }
    }, [user, isLoading, requireAdmin, router])

    // Show loading state while checking auth
    if (isLoading) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-background">
                <div className="text-center">
                    <div className="w-16 h-16 border-4 border-primary border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
                    <p className="text-muted-foreground">Đang tải...</p>
                </div>
            </div>
        )
    }

    // Don't render children if not authenticated or not authorized
    if (!user || (requireAdmin && user.role !== 'admin')) {
        return null
    }

    return <>{children}</>
}
