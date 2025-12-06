"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import Link from "next/link"
import { CheckCircle } from "lucide-react"

type TabType = "immigration" | "study" | "visa"

export default function InfoPage() {
  const [activeTab, setActiveTab] = useState<TabType>("immigration")

  const immigrationContent = {
    title: "Định cư Úc",
    description: "Khám phá các đường dẫn để định cư vĩnh viễn tại Úc",
    sections: [
      {
        title: "Visa Định cư (PR)",
        icon: "🏠",
        content: "Visa Thường trú Tạm thời (PR) cho phép bạn sống, làm việc và học tập vô hạn định tại Úc.",
        details: [
          "Visa kỹ năng được chỉ định (189, 190, 491)",
          "Visa doanh nhân và đầu tư",
          "Visa gia đình",
          "Visa nhân đạo",
        ],
      },
      {
        title: "Điều kiện tối thiểu",
        icon: "✓",
        content: "Để xin visa định cư Úc, bạn thường cần:",
        details: [
          "Tuổi: Dưới 45 tuổi (cho hầu hết các visa kỹ năng)",
          "Tiếng Anh: IELTS 6.0 hoặc tương đương",
          "Kỹ năng: Trong danh sách kỹ năng được chỉ định",
          "Điểm: Đạt điểm trò chơi điểm Úc (thường 65+ điểm)",
        ],
      },
      {
        title: "Quá trình nộp đơn",
        icon: "📋",
        content: "Quá trình xin visa định cư bao gồm các bước sau:",
        details: [
          "Bước 1: Tạo hồ sơ EOI",
          "Bước 2: Nộp đơn xin visa kỹ năng",
          "Bước 3: Chờ lời mời nộp đơn (Invitation)",
          "Bước 4: Nộp đơn chi tiết",
          "Bước 5: Chờ quyết định",
        ],
      },
    ],
  }

  const studyContent = {
    title: "Du học Úc",
    description: "Tìm hiểu về cơ hội giáo dục tại các trường hàng đầu Úc",
    sections: [
      {
        title: "Visa Sinh viên (Subclass 500)",
        icon: "🎓",
        content: "Visa này cho phép bạn du học tại Úc cho các khóa học đã được phê duyệt.",
        details: [
          "Học tập từ 3 tháng đến 5 năm",
          "Làm việc thêm giờ theo luật",
          "Mang theo gia đình phụ thuộc",
          "Con đường chuyển từ học tập sang định cư",
        ],
      },
      {
        title: "Các trường hàng đầu",
        icon: "⭐",
        content: "Các đại học hàng đầu thế giới ở Úc:",
        details: ["Đại học Melbourne", "Đại học Sydney", "Đại học ANU", "Đại học Queensland", "Đại học Công nghệ RMIT"],
      },
      {
        title: "Chi phí và tài chính",
        icon: "💰",
        content: "Thông tin về chi phí học tập và các tùy chọn tài chính:",
        details: [
          "Học phí: AUD 15,000 - 45,000 mỗi năm",
          "Chi phí sinh hoạt: AUD 18,000 - 25,000 mỗi năm",
          "Các khoản vay và học bổng",
          "Hỗ trợ tài chính từ chính phủ",
        ],
      },
    ],
  }

  const visaContent = {
    title: "Các loại Visa Úc",
    description: "Hướng dẫn chi tiết về các loại visa có sẵn tại Úc",
    sections: [
      {
        title: "Visa Kỹ năng Tạm thời (TSV)",
        icon: "⚙️",
        content: "Dành cho những người có kỹ năng được chỉ định trong danh sách.",
        details: [
          "Thời lượng: 2-4 năm",
          "Cho phép làm việc trong lĩnh vực được chỉ định",
          "Có thể chuyển từ sang PR",
          "Không bao gồm gia đình phụ thuộc",
        ],
      },
      {
        title: "Visa Du lịch/Khách (Subclass 600)",
        icon: "✈️",
        content: "Cho du khách muốn thăm, công việc tạm thời hoặc học tập ngắn hạn.",
        details: [
          "Thời lượng: Tối đa 12 tháng",
          "Không cho phép làm việc (trừ các trường hợp đặc biệt)",
          "Chi phí: AUD 190",
          "Xử lý nhanh chóng",
        ],
      },
      {
        title: "Visa Gia đình",
        icon: "👨‍👩‍👧‍👦",
        content: "Cho phép gia đình bạn tham gia bạn tại Úc.",
        details: [
          "Visa Người thân phụ thuộc",
          "Visa Cha mẹ",
          "Visa Anh chị em",
          "Visa Con nuôi",
          "Thời gian xử lý: 8-22 tháng",
        ],
      },
    ],
  }

  const getCurrentContent = () => {
    switch (activeTab) {
      case "immigration":
        return immigrationContent
      case "study":
        return studyContent
      case "visa":
        return visaContent
      default:
        return immigrationContent
    }
  }

  const content = getCurrentContent()

  return (
    <div
      className="min-h-screen bg-background"
      style={{
        backgroundImage: "url('/professional-visa-immigration-information-page-bac.jpg')",
        backgroundSize: "100% 100%",
        backgroundPosition: "center",
        backgroundAttachment: "fixed",
      }}
    >
      {/* Header */}
      <header className="border-b border-border bg-card/95 backdrop-blur-sm sticky top-0 z-40">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-3 sm:py-4 flex justify-between items-center gap-4">
          <Link href="/" className="flex items-center gap-2 hover:opacity-80 transition-opacity flex-shrink-0">
            <div className="w-8 h-8 rounded-lg bg-primary flex items-center justify-center">
              <span className="text-primary-foreground font-bold text-lg">A</span>
            </div>
            <span className="text-lg sm:text-xl font-bold text-foreground hidden sm:inline">AusVisa</span>
          </Link>
          <div className="flex gap-2 sm:gap-4 ml-auto">
            <Link href="/chat">
              <Button variant="ghost" className="text-xs sm:text-base">
                Trò chuyện
              </Button>
            </Link>
            <Link href="/login">
              <Button className="bg-primary hover:bg-primary/90 text-primary-foreground text-xs sm:text-base">
                Đăng nhập
              </Button>
            </Link>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="py-8 sm:py-12 px-4 bg-gradient-to-b from-primary/10 to-transparent">
        <div className="max-w-6xl mx-auto text-white text-center">
          <h1 className="text-3xl sm:text-4xl lg:text-5xl font-bold mb-2 sm:mb-4 px-2">
            Thông tin Visa Úc
          </h1>
          <p className="text-base sm:text-lg max-w-2xl mx-auto px-2">
            Hướng dẫn chi tiết về định cư, du học, và các loại visa tại Úc
          </p>
        </div>
      </section>

      {/* Tab Navigation */}
      <div className="border-b border-border bg-card/95 backdrop-blur-sm sticky top-14 sm:top-16 z-30 overflow-x-auto">
        <div className="max-w-6xl mx-auto px-4 flex gap-0 min-w-max sm:min-w-0">
          {(["immigration", "study", "visa"] as const).map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-4 sm:px-6 py-3 sm:py-4 font-medium transition-all border-b-2 text-sm sm:text-base whitespace-nowrap ${
                activeTab === tab
                  ? "border-primary text-primary"
                  : "border-transparent text-muted-foreground hover:text-foreground"
              }`}
            >
              {tab === "immigration" && "🏠 Định cư"}
              {tab === "study" && "🎓 Du học"}
              {tab === "visa" && "✈️ Visa"}
            </button>
          ))}
        </div>
      </div>

      {/* Content */}
      <main className="py-8 sm:py-12 px-4">
        <div className="max-w-6xl mx-auto">
          <div className="mb-8 sm:mb-12 text-white">
            <h2 className="text-2xl sm:text-3xl font-bold mb-2 sm:mb-3">{content.title}</h2>
            <p className="text-base sm:text-lg">{content.description}</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6">
            {content.sections.map((section, idx) => (
              <div
                key={idx}
                className="bg-card rounded-lg border border-border p-6 hover:border-primary/50 transition-colors group"
              >
                <div className="text-2xl sm:text-3xl mb-4">{section.icon}</div>
                <h3 className="text-lg sm:text-xl font-bold text-foreground mb-3 group-hover:text-primary transition-colors">
                  {section.title}
                </h3>
                <p className="text-muted-foreground mb-4 text-sm leading-relaxed">{section.content}</p>
                <ul className="space-y-2">
                  {section.details.map((detail, i) => (
                    <li key={i} className="flex gap-2 text-xs sm:text-sm text-foreground">
                      <CheckCircle className="w-4 h-4 text-accent flex-shrink-0 mt-0.5" />
                      <span>{detail}</span>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>

          {/* CTA Section */}
          <div className="mt-12 bg-white sm:mt-16 bg-gradient-to-r from-primary/10 to-accent/10 rounded-lg border border-border p-6 sm:p-8 text-center">
            <h3 className="text-xl sm:text-2xl font-bold text-foreground mb-2 sm:mb-3">Cần tư vấn cá nhân?</h3>
            <p className="text-muted-foreground mb-4 sm:mb-6 max-w-2xl mx-auto text-sm sm:text-base px-2">
              Nói chuyện với trợ lý AI AusVisa của chúng tôi để nhận được tư vấn được cá nhân hóa dựa trên tình huống cụ
              thể của bạn.
            </p>
            <div className="flex gap-2 sm:gap-4 justify-center flex-col sm:flex-row px-2">
              <Link href="/chat">
                <Button className="w-full sm:w-auto bg-primary hover:bg-primary/90 text-primary-foreground">
                  Bắt đầu trò chuyện
                </Button>
              </Link>
              <Link href="/register">
                <Button
                  variant="outline"
                  className="w-full sm:w-auto border-primary/30 hover:bg-primary/5 bg-transparent"
                >
                  Đăng ký để được hỗ trợ đầy đủ
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-border bg-card/95 backdrop-blur-sm mt-12">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-12">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6 sm:gap-8 mb-8">
            <div className="col-span-2 md:col-span-1">
              <h4 className="font-bold text-foreground mb-4">AusVisa</h4>
              <p className="text-xs sm:text-sm text-muted-foreground">Nền tảng tư vấn visa Úc được hỗ trợ bởi AI</p>
            </div>
            <div>
              <h4 className="font-semibold text-foreground mb-4 text-sm">Thông tin</h4>
              <ul className="space-y-2 text-xs sm:text-sm text-muted-foreground">
                <li>
                  <Link href="#" className="hover:text-foreground">
                    Về chúng tôi
                  </Link>
                </li>
                <li>
                  <Link href="#" className="hover:text-foreground">
                    Blog
                  </Link>
                </li>
                <li>
                  <Link href="#" className="hover:text-foreground">
                    Hỏi đáp
                  </Link>
                </li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold text-foreground mb-4 text-sm">Pháp lý</h4>
              <ul className="space-y-2 text-xs sm:text-sm text-muted-foreground">
                <li>
                  <Link href="#" className="hover:text-foreground">
                    Điều khoản dịch vụ
                  </Link>
                </li>
                <li>
                  <Link href="#" className="hover:text-foreground">
                    Chính sách bảo mật
                  </Link>
                </li>
                <li>
                  <Link href="#" className="hover:text-foreground">
                    Liên hệ
                  </Link>
                </li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold text-foreground mb-4 text-sm">Liên kết</h4>
              <ul className="space-y-2 text-xs sm:text-sm text-muted-foreground">
                <li>
                  <Link href="#" className="hover:text-foreground">
                    Cơ quan Di trú Úc
                  </Link>
                </li>
                <li>
                  <Link href="#" className="hover:text-foreground">
                    Điểm kỹ năng
                  </Link>
                </li>
                <li>
                  <Link href="#" className="hover:text-foreground">
                    Công việc
                  </Link>
                </li>
              </ul>
            </div>
          </div>
          <div className="border-t border-border pt-6 sm:pt-8 text-center text-xs sm:text-sm text-muted-foreground">
            <p>&copy; 2025 AusVisa. Tất cả các quyền được bảo lưu.</p>
          </div>
        </div>
      </footer>
    </div>
  )
}
