"use client"

import { Button } from "@/components/ui/button"
import { sendChatMessage } from "@/lib/api"
import { LogOut, Menu, MessageCircle, Send, Settings, X } from "lucide-react"
import Link from "next/link"
import type React from "react"
import { useEffect, useRef, useState } from "react"

interface Message {
  id: string
  role: "user" | "assistant"
  content: string
  timestamp: Date
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      role: "assistant",
      content:
        "Xin chào! Tôi là trợ lý AI AusVisa của bạn. Tôi có thể giúp bạn tìm hiểu về định cư Úc, du học, visa, và nhiều hơn nữa. Hỏi tôi bất kỳ điều gì!",
      timestamp: new Date(),
    },
  ])
  const [inputValue, setInputValue] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [sidebarOpen, setSidebarOpen] = useState(true)
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
    setIsLoading(true)

    try {
      // Call backend API
      const result = await sendChatMessage(currentInput)

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: result.response,
        timestamp: new Date(),
      }

      setMessages((prev) => [...prev, assistantMessage])
    } catch (error) {
      console.error('Error:', error)

      // Show error message
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: "Xin lỗi, tôi gặp lỗi khi xử lý câu hỏi của bạn. Vui lòng thử lại sau.",
        timestamp: new Date(),
      }

      setMessages((prev) => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const suggestedQuestions = [
    { icon: "🎓", title: "Du học Úc", description: "Tìm hiểu về visa du học" },
    { icon: "🏠", title: "Định cư", description: "Đường dẫn định cư Úc" },
    { icon: "✈️", title: "Visa visa", description: "Loại visa và yêu cầu" },
  ]

  return (
    <div
      className="h-screen flex bg-background"
      style={{
        backgroundImage: "url('/professional-ai-chatbot-interface-background-with-.jpg')",
        backgroundSize: "cover",
        backgroundPosition: "center",
        backgroundAttachment: "fixed",
      }}
    >
      {/* Sidebar */}
      <div
        className={`${sidebarOpen ? "w-64" : "w-0"} transition-all duration-300 border-r border-border flex flex-col bg-card/95 backdrop-blur-sm overflow-hidden`}
      >
        <div className="p-4 border-b border-border">
          <Link href="/" className="flex items-center gap-2 hover:opacity-80 transition-opacity">
            <div className="w-8 h-8 rounded-lg bg-primary flex items-center justify-center">
              <span className="text-primary-foreground font-bold">A</span>
            </div>
            <span className="font-bold text-foreground truncate">AusVisa</span>
          </Link>
        </div>

        <div className="flex-1 overflow-y-auto p-4 space-y-2">
          <Button variant="ghost" className="w-full justify-start gap-2 text-muted-foreground hover:text-foreground">
            <MessageCircle className="w-4 h-4" />
            <span className="truncate">New Chat</span>
          </Button>
          <div className="text-xs font-semibold text-muted-foreground px-2 py-2 mt-4">LỊCH SỬ</div>
          <Button
            variant="ghost"
            className="w-full justify-start gap-2 text-muted-foreground hover:text-foreground text-sm"
          >
            <span className="truncate">Thông tin về visa điểm</span>
          </Button>
          <Button
            variant="ghost"
            className="w-full justify-start gap-2 text-muted-foreground hover:text-foreground text-sm"
          >
            <span className="truncate">Yêu cầu kỹ năng du học</span>
          </Button>
        </div>

        <div className="p-4 border-t border-border space-y-2">
          <Button variant="ghost" className="w-full justify-start gap-2 text-muted-foreground hover:text-foreground">
            <Settings className="w-4 h-4" />
            <span>Cài đặt</span>
          </Button>
          <Button variant="ghost" className="w-full justify-start gap-2 text-muted-foreground hover:text-foreground">
            <LogOut className="w-4 h-4" />
            <span>Đăng xuất</span>
          </Button>
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col bg-background/80 backdrop-blur-sm">
        {/* Header */}
        <div className="border-b border-border bg-card/95 backdrop-blur-sm px-6 py-4 flex items-center justify-between">
          <Button variant="ghost" size="icon" onClick={() => setSidebarOpen(!sidebarOpen)} className="lg:hidden">
            {sidebarOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </Button>
          <h1 className="text-lg font-semibold text-foreground">Tư vấn visa Úc AI</h1>
          <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center">
            <span className="text-sm font-bold text-primary">U</span>
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

          {isLoading && (
            <div className="flex gap-4">
              <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0">
                <span className="text-sm font-bold">A</span>
              </div>
              <div className="bg-card border border-border px-4 py-3 rounded-lg">
                <div className="flex gap-2">
                  <div className="w-2 h-2 rounded-full bg-muted-foreground animate-bounce"></div>
                  <div
                    className="w-2 h-2 rounded-full bg-muted-foreground animate-bounce"
                    style={{ animationDelay: "0.2s" }}
                  ></div>
                  <div
                    className="w-2 h-2 rounded-full bg-muted-foreground animate-bounce"
                    style={{ animationDelay: "0.4s" }}
                  ></div>
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
                  disabled={isLoading}
                />
              </div>
              <Button
                type="submit"
                disabled={isLoading || !inputValue.trim()}
                className="bg-primary hover:bg-primary/90 text-primary-foreground"
              >
                <Send className="w-4 h-4" />
              </Button>
            </div>
          </form>
          <p className="text-xs text-muted-foreground text-center mt-3">
            AusVisa AI có thể mắc lỗi. Xin vui lòng kiểm tra thông tin quan trọng.
          </p>
        </div>
      </div>
    </div>
  )
}
