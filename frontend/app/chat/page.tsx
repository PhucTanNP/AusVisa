"use client"

import { useRouter } from "next/navigation"
import { useEffect } from "react"

export default function ChatPage() {
  const router = useRouter()

  useEffect(() => {
    // Redirect to home page where chatbot is integrated
    router.push('/')
  }, [router])

  return (
    <div className="min-h-screen flex items-center justify-center bg-background">
      <div className="text-center">
        <div className="w-16 h-16 border-4 border-primary border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
        <p className="text-muted-foreground">Đang chuyển hướng...</p>
      </div>
    </div>
  )
}
