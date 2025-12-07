"use client"

import { Button } from "@/components/ui/button"
import { useAuth } from "@/hooks/use-auth"
import { sendChatMessage } from "@/lib/api"
import { LogOut, Send, Settings } from "lucide-react"
import Link from "next/link"
import { useRouter } from "next/navigation"
import type React from "react"
import { useEffect, useRef, useState } from "react"

interface Message {
  id: string
  role: "user" | "assistant"
  content: string
  timestamp: Date
}

export default function HomePage() {
  const { user, logout, isLoading } = useAuth()
  const router = useRouter()

  // Redirect admin to admin page
  useEffect(() => {
    if (user && user.role === 'admin') {
      router.push('/admin')
    }
  }, [user, router])

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

  // If user is admin, show loading while redirecting
  if (user && user.role === 'admin') {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-primary border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-muted-foreground">Đang chuyển đến trang quản trị...</p>
        </div>
      </div>
    )
  }

  // If user is logged in (and not admin), show chatbot
  if (user) {
    return <ChatbotPage user={user} onLogout={logout} />
  }

  // Otherwise show landing page
  return <LandingPage />
}

function ChatbotPage({ user, onLogout }: { user: any; onLogout: () => void }) {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      role: "assistant",
      content: `Xin chào ${user.username}! Tôi là trợ lý AI AusVisa của bạn. Tôi có thể giúp bạn tìm hiểu về định cư Úc, du học, visa, và nhiều hơn nữa. Hỏi tôi bất kỳ điều gì!`,
      timestamp: new Date(),
    },
  ])
  const [inputValue, setInputValue] = useState("")
  const [isLoadingMsg, setIsLoadingMsg] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!inputValue.trim()) return

    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: inputValue,
      timestamp: new Date(),
    }

    setMessages((prev) => [...prev, userMessage])
    const currentInput = inputValue
    setInputValue("")
    setIsLoadingMsg(true)

    const assistantId = (Date.now() + 1).toString()
    const assistantMessage: Message = {
      id: assistantId,
      role: "assistant",
      content: "",
      timestamp: new Date(),
    }
    setMessages((prev) => [...prev, assistantMessage])

    try {
      const { streamChatMessage } = await import("@/lib/api")

      await streamChatMessage(
        currentInput,
        (chunk: string) => {
          setMessages((prev) =>
            prev.map((msg) =>
              msg.id === assistantId ? { ...msg, content: msg.content + chunk } : msg
            )
          )
        },
        () => {
          setIsLoadingMsg(false)
        },
        (error: Error) => {
          console.error("Streaming error:", error)
          setMessages((prev) =>
            prev.map((msg) =>
              msg.id === assistantId
                ? { ...msg, content: "Xin lỗi, tôi gặp lỗi khi xử lý câu hỏi của bạn. Vui lòng thử lại." }
                : msg
            )
          )
          setIsLoadingMsg(false)
        }
      )
    } catch (error) {
      try {
        const result = await sendChatMessage(currentInput)
        setMessages((prev) =>
          prev.map((msg) =>
            msg.id === assistantId ? { ...msg, content: result.response } : msg
          )
        )
      } catch (fallbackError) {
        setMessages((prev) =>
          prev.map((msg) =>
            msg.id === assistantId
              ? { ...msg, content: "Xin lỗi, tôi gặp lỗi khi xử lý câu hỏi của bạn. Vui lòng thử lại." }
              : msg
          )
        )
      }
      setIsLoadingMsg(false)
    }
  }

  const suggestedQuestions = [
    { icon: "🎓", title: "Du học Úc", description: "Tìm hiểu về visa du học" },
    { icon: "🏠", title: "Định cư", description: "Đường dẫn định cư Úc" },
    { icon: "✈️", title: "Visa", description: "Loại visa và yêu cầu" },
  ]

  return (
    <div
      className="h-screen flex flex-col bg-background"
      style={{
        backgroundImage: "url('/professional-ai-chatbot-interface-background-with-.jpg')",
        backgroundSize: "cover",
        backgroundPosition: "center",
        backgroundAttachment: "fixed",
      }}
    >
      {/* Header */}
      <div className="border-b border-border bg-card/95 backdrop-blur-sm px-6 py-4 flex items-center justify-between">
        <Link href="/" className="flex items-center gap-2 hover:opacity-80 transition-opacity">
          <div className="w-8 h-8 rounded-lg bg-primary flex items-center justify-center">
            <span className="text-primary-foreground font-bold">A</span>
          </div>
          <span className="font-bold text-foreground">AusVisa</span>
        </Link>
        <div className="flex items-center gap-4">
          <span className="text-sm text-muted-foreground">Xin chào, {user.username}</span>
          <Button variant="ghost" size="icon">
            <Settings className="w-5 h-5" />
          </Button>
          <Button variant="ghost" size="icon" onClick={onLogout}>
            <LogOut className="w-5 h-5" />
          </Button>
        </div>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6 bg-gradient-to-b from-background/80 to-muted/40">
        {messages.length === 1 && (
          <div className="space-y-6 mt-8">
            <div className="text-center mb-12">
              <h2 className="text-3xl font-bold text-foreground mb-3">Bắt đầu trò chuyện</h2>
              <p className="text-muted-foreground">Hỏi tôi bất cứ điều gì về visa, du học, hoặc định cư Úc</p>
            </div>

            <div className="grid md:grid-cols-3 gap-4 max-w-3xl mx-auto">
              {suggestedQuestions.map((question, idx) => (
                <button
                  key={idx}
                  onClick={() => setInputValue(`${question.title}: ${question.description}`)}
                  className="p-4 rounded-lg border border-border hover:border-primary bg-card hover:bg-primary/5 transition-all text-left"
                >
                  <div className="text-2xl mb-2">{question.icon}</div>
                  <h3 className="font-semibold text-foreground text-sm mb-1">{question.title}</h3>
                  <p className="text-xs text-muted-foreground">{question.description}</p>
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((message) => (
          <div key={message.id} className={`flex gap-4 ${message.role === "user" ? "flex-row-reverse" : ""}`}>
            <div
              className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${message.role === "user" ? "bg-accent/10" : "bg-primary/10"
                }`}
            >
              <span className="text-sm font-bold">{message.role === "user" ? "U" : "A"}</span>
            </div>
            <div
              className={`max-w-md lg:max-w-xl px-4 py-3 rounded-lg ${message.role === "user"
                ? "bg-primary text-primary-foreground rounded-br-none"
                : "bg-card border border-border rounded-bl-none"
                }`}
            >
              <p className="text-sm leading-relaxed whitespace-pre-wrap">{message.content}</p>
              <span className="text-xs opacity-70 mt-2 block">
                {message.timestamp.toLocaleTimeString("vi-VN", { hour: "2-digit", minute: "2-digit" })}
              </span>
            </div>
          </div>
        ))}

        {isLoadingMsg && (
          <div className="flex gap-4">
            <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0">
              <span className="text-sm font-bold">A</span>
            </div>
            <div className="bg-card border border-border px-4 py-3 rounded-lg">
              <div className="flex gap-2">
                <div className="w-2 h-2 rounded-full bg-muted-foreground animate-bounce"></div>
                <div className="w-2 h-2 rounded-full bg-muted-foreground animate-bounce" style={{ animationDelay: "0.2s" }}></div>
                <div className="w-2 h-2 rounded-full bg-muted-foreground animate-bounce" style={{ animationDelay: "0.4s" }}></div>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="border-t border-border bg-card/95 backdrop-blur-sm p-6">
        <form onSubmit={handleSendMessage} className="max-w-3xl mx-auto">
          <div className="flex gap-4 items-end">
            <div className="flex-1 relative">
              <input
                type="text"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                placeholder="Hỏi tôi bất cứ điều gì..."
                className="w-full px-4 py-3 rounded-lg border border-border bg-background text-foreground placeholder-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent transition-all"
                disabled={isLoadingMsg}
              />
            </div>
            <Button type="submit" disabled={isLoadingMsg || !inputValue.trim()} className="bg-primary hover:bg-primary/90 text-primary-foreground">
              <Send className="w-4 h-4" />
            </Button>
          </div>
        </form>
        <p className="text-xs text-muted-foreground text-center mt-3">
          AusVisa AI có thể mắc lỗi. Xin vui lòng kiểm tra thông tin quan trọng.
        </p>
      </div>
    </div>
  )
}

function LandingPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-background to-muted">
      {/* Navigation */}
      <nav className="fixed top-0 w-full z-50 bg-background/80 backdrop-blur-md border-b border-border">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-primary flex items-center justify-center">
              <span className="text-primary-foreground font-bold text-lg">A</span>
            </div>
            <span className="text-xl font-bold text-foreground">AusVisa</span>
          </div>
          <div className="flex gap-4">
            <Link href="/news">
              <Button variant="ghost">Tin tức</Button>
            </Link>
            <Link href="/login">
              <Button variant="ghost">Đăng nhập</Button>
            </Link>
            <Link href="/register">
              <Button className="bg-primary hover:bg-primary/90 text-primary-foreground">Đăng ký</Button>
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="pt-32 pb-20 px-4">
        <div className="max-w-4xl mx-auto text-center">
          <div className="inline-flex items-center gap-2 bg-secondary/10 border border-secondary/30 rounded-full px-4 py-2 mb-6">
            <div className="w-2 h-2 rounded-full bg-accent"></div>
            <span className="text-sm font-medium text-secondary-foreground">AI-Powered Advisory Platform</span>
          </div>

          <h1 className="text-5xl md:text-6xl font-bold text-foreground mb-6 leading-tight">
            Hành trình sang Australia{" "}
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary to-accent">trở nên dễ dàng</span>
          </h1>

          <p className="text-lg text-muted-foreground mb-8 max-w-2xl mx-auto leading-relaxed">
            Khám phá cơ hội định cư, du học, và xin visa Úc với sự giúp đỡ của trí tuệ nhân tạo và đồ thị tri thức. Được tin tưởng bởi hàng
            ngàn người tìm kiếm tương lai tại Úc.
          </p>

          <div className="flex gap-4 justify-center flex-wrap mb-12">
            <Link href="/register">
              <Button size="lg" className="bg-primary hover:bg-primary/90 text-primary-foreground">
                Bắt đầu miễn phí
              </Button>
            </Link>
            <Link href="/login">
              <Button size="lg" variant="outline" className="border-primary/30 hover:bg-primary/5 bg-transparent">
                Đăng nhập để chat
              </Button>
            </Link>
          </div>

          {/* Features Grid */}
          <div className="grid md:grid-cols-3 gap-6 mt-16">
            <div className="bg-card rounded-lg border border-border p-6 text-left hover:border-primary/50 transition-colors">
              <div className="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center mb-4">
                <span className="text-2xl">🎓</span>
              </div>
              <h3 className="text-lg font-semibold text-foreground mb-2">Du học Úc</h3>
              <p className="text-sm text-muted-foreground">Tìm hiểu visa, khóa học, và yêu cầu nhập học từ các trường hàng đầu</p>
            </div>

            <div className="bg-card rounded-lg border border-border p-6 text-left hover:border-primary/50 transition-colors">
              <div className="w-12 h-12 rounded-lg bg-accent/10 flex items-center justify-center mb-4">
                <span className="text-2xl">🏠</span>
              </div>
              <h3 className="text-lg font-semibold text-foreground mb-2">Định cư Úc</h3>
              <p className="text-sm text-muted-foreground">Khám phá các đường dẫn định cư, yêu cầu kỹ năng, và quy trình xin visa</p>
            </div>

            <div className="bg-card rounded-lg border border-border p-6 text-left hover:border-primary/50 transition-colors">
              <div className="w-12 h-12 rounded-lg bg-secondary/10 flex items-center justify-center mb-4">
                <span className="text-2xl">✈️</span>
              </div>
              <h3 className="text-lg font-semibold text-foreground mb-2">Visa Úc</h3>
              <p className="text-sm text-muted-foreground">Hướng dẫn chi tiết về các loại visa, điều kiện, và quy trình nộp đơn</p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-12 px-4 border-t border-border">
        <div className="max-w-3xl mx-auto text-center">
          <h2 className="text-3xl font-bold text-foreground mb-4">Sẵn sàng bắt đầu cuộc hành trình của bạn?</h2>
          <p className="text-muted-foreground mb-6">Hãy đăng ký để nhận tư vấn cá nhân từ hệ thống AI tiên tiến của chúng tôi</p>
          <Link href="/register">
            <Button size="lg" className="bg-primary hover:bg-primary/90 text-primary-foreground">
              Đăng ký ngay
            </Button>
          </Link>
        </div>
      </section>
    </div>
  )
}
