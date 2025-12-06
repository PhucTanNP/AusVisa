"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import Link from "next/link"
import { Calendar, User, ArrowRight, Search } from "lucide-react"

type NewsCategory = "all" | "immigration" | "study" | "visa"

interface NewsArticle {
  id: number
  title: string
  excerpt: string
  category: Omit<NewsCategory, "all">
  date: string
  author: string
  image: string
  icon: string
}

export default function NewsPage() {
  const [activeCategory, setActiveCategory] = useState<NewsCategory>("all")
  const [searchQuery, setSearchQuery] = useState("")

  const newsArticles: NewsArticle[] = [
    {
      id: 1,
      title: "2025: Những thay đổi mới trong Chương trình Di cư Kỹ năng Úc",
      excerpt:
        "Cơ quan Nội vụ Úc vừa công bố những thay đổi quan trọng trong danh sách kỹ năng được chỉ định cho năm 2025, ảnh hưởng đến hàng ngàn ứng viên.",
      category: "immigration",
      date: "2025-11-10",
      author: "Nguyễn Văn A",
      image: "/australian-immigration-skilled-migration-2025.jpg",
      icon: "🏢",
    },
    {
      id: 2,
      title: "Hướng dẫn Chi tiết: Quá trình Xin Visa 189 từ A đến Z",
      excerpt:
        "Tìm hiểu từng bước trong quá trình xin visa 189, bao gồm cách tạo tài khoản EOI, tính điểm, và những lỗi thường gặp.",
      category: "immigration",
      date: "2025-11-09",
      author: "Trần Thị B",
      image: "/visa-189-australia-application-process.jpg",
      icon: "📋",
    },
    {
      id: 3,
      title: "Top 10 Trường Đại học Tốt Nhất ở Úc cho Du học sinh Quốc tế",
      excerpt:
        "Khám phá các trường đại học hàng đầu thế giới ở Úc, học phí, các khóa học phổ biến, và cơ hội việc làm sau tốt nghiệp.",
      category: "study",
      date: "2025-11-08",
      author: "Lê Văn C",
      image: "/top-universities-australia-international-students.jpg",
      icon: "🎓",
    },
    {
      id: 4,
      title: "Du học Úc 2025: Chi Phí Thực Tế và Các Lựa Chọn Tài Chính",
      excerpt:
        "Tính toán chi phí du học tại Úc năm 2025, bao gồm học phí, chi phí sinh hoạt, bảo hiểm sức khỏe và các chương trình hỗ trợ tài chính.",
      category: "study",
      date: "2025-11-07",
      author: "Phạm Thị D",
      image: "/study-cost-australia-international-students-2025.jpg",
      icon: "💰",
    },
    {
      id: 5,
      title: "Bạn Có Đủ Điều Kiện Xin Visa 190 hay 491 Không?",
      excerpt: "Hiểu rõ điều kiện yêu cầu, điểm số cần thiết, và lợi ích của các visa 190 và 491 so với visa 189.",
      category: "visa",
      date: "2025-11-06",
      author: "Hoàng Văn E",
      image: "/visa-190-491-australia-requirements.jpg",
      icon: "✈️",
    },
    {
      id: 6,
      title: "Visa Gia Đình Úc: Đưa Người Thân Vào Cùng Nhau",
      excerpt:
        "Khám phá các loại visa gia đình, yêu cầu tài chính, thời gian xử lý và những điều bạn cần biết khi đưa gia đình đến Úc.",
      category: "visa",
      date: "2025-11-05",
      author: "Võ Thị F",
      image: "/family-visa-australia-bring-family.jpg",
      icon: "👨‍👩‍👧‍👦",
    },
    {
      id: 7,
      title: "Chuyển từ Visa Sinh viên sang Visa Định cư: Con Đường Hợp Lý",
      excerpt:
        "Chiến lược từ du học đến định cư vĩnh viễn, các công việc có tính điểm cao, và cách lập kế hoạch cho quá trình chuyển đổi.",
      category: "study",
      date: "2025-11-04",
      author: "Ngô Văn G",
      image: "/student-visa-to-permanent-residency-australia-path.jpg",
      icon: "🎯",
    },
    {
      id: 8,
      title: "IELTS và Yêu Cầu Tiếng Anh Cho Visa Úc: Bạn Cần Bao Nhiêu Điểm?",
      excerpt:
        "Giải thích các yêu cầu tiếng Anh khác nhau cho các loại visa, điểm số tối thiểu, và cách chuẩn bị thi IELTS hiệu quả.",
      category: "visa",
      date: "2025-11-03",
      author: "Lý Thị H",
      image: "/ielts-english-requirements-australia-visa.jpg",
      icon: "🗣️",
    },
    {
      id: 9,
      title: "Những Lỗi Phổ Biến Khi Nộp Đơn Xin Visa Úc và Cách Tránh",
      excerpt:
        "Tìm hiểu những sai lầm thường gặp trong quá trình nộp đơn, cách đơn bị từ chối, và các bước để ngăn chặn chúng.",
      category: "immigration",
      date: "2025-11-02",
      author: "Bùi Văn I",
      image: "/common-mistakes-australia-visa-application.jpg",
      icon: "⚠️",
    },
    {
      id: 10,
      title: "Xu Hướng Du Học Úc 2025: Ngành Học Mới và Cơ Hội Việc Làm",
      excerpt:
        "Khám phá các ngành học được ưa chuộng, nhu cầu thị trường lao động, và cơ hội việc làm tuyệt vời cho du học sinh quốc tế.",
      category: "study",
      date: "2025-11-01",
      author: "Đặng Thị J",
      image: "/study-trends-australia-international-students-2025.jpg",
      icon: "📈",
    },
  ]

  const filteredArticles = newsArticles.filter((article) => {
    const matchesCategory = activeCategory === "all" || article.category === activeCategory
    const matchesSearch =
      article.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      article.excerpt.toLowerCase().includes(searchQuery.toLowerCase())
    return matchesCategory && matchesSearch
  })

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("vi-VN", {
      year: "numeric",
      month: "long",
      day: "numeric",
    })
  }

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
            Tin Tức & Hướng Dẫn
          </h1>
          <p className="text-base sm:text-lg max-w-2xl mx-auto px-2">
            Cập nhật thông tin mới nhất về định cư, du học, và visa Úc
          </p>
        </div>
      </section>

      {/* Search and Filter Section */}
      <div className="bg-card/95 backdrop-blur-sm border-b border-border py-6 px-4 sticky top-14 sm:top-16 z-30">
        <div className="max-w-6xl mx-auto space-y-4 sm:space-y-0">
          {/* Search Bar */}
          <div className="relative mb-4 sm:mb-0">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-muted-foreground" />
            <input
              type="text"
              placeholder="Tìm kiếm bài viết..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 bg-input border border-border rounded-lg text-foreground placeholder-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/50 text-sm sm:text-base"
            />
          </div>

          {/* Category Filter */}
          <div className="flex gap-2 overflow-x-auto pb-2 sm:pb-0">
            {["all", "immigration", "study", "visa"].map((category) => (
              <button
                key={category}
                onClick={() => setActiveCategory(category as NewsCategory)}
                className={`px-3 sm:px-4 py-2 rounded-lg font-medium transition-all whitespace-nowrap text-xs sm:text-sm ${
                  activeCategory === category
                    ? "bg-primary text-primary-foreground"
                    : "bg-muted text-muted-foreground hover:bg-muted/80"
                }`}
              >
                {category === "all" && "Tất cả"}
                {category === "immigration" && "🏠 Định cư"}
                {category === "study" && "🎓 Du học"}
                {category === "visa" && "✈️ Visa"}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* News Grid */}
      <main className="py-8 sm:py-12 px-4">
        <div className="max-w-6xl mx-auto">
          {filteredArticles.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 sm:gap-8">
              {filteredArticles.map((article) => (
                <article
                  key={article.id}
                  className="bg-card rounded-lg border border-border overflow-hidden hover:border-primary/50 transition-all group hover:shadow-lg hover:-translate-y-1"
                >
                  {/* Image */}
                  <div className="relative h-40 sm:h-48 bg-muted overflow-hidden">
                    <img
                      src={article.image || "/placeholder.svg"}
                      alt={article.title}
                      className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                    />
                    <div className="absolute top-3 left-3 text-2xl sm:text-3xl bg-background/80 backdrop-blur-sm p-1 sm:p-2 rounded">
                      {article.icon}
                    </div>
                  </div>

                  {/* Content */}
                  <div className="p-4 sm:p-6 flex flex-col h-full">
                    {/* Category Badge */}
                    <div className="mb-3">
                      <span className="inline-block px-2 py-1 sm:px-3 sm:py-1.5 bg-primary/10 text-primary rounded-full text-xs font-medium">
                        {article.category === "immigration" && "Định cư"}
                        {article.category === "study" && "Du học"}
                        {article.category === "visa" && "Visa"}
                      </span>
                    </div>

                    {/* Title */}
                    <h3 className="text-base sm:text-lg font-bold text-foreground mb-2 group-hover:text-primary transition-colors line-clamp-2">
                      {article.title}
                    </h3>

                    {/* Excerpt */}
                    <p className="text-sm text-muted-foreground mb-4 flex-grow line-clamp-3">{article.excerpt}</p>

                    {/* Meta Information */}
                    <div className="space-y-2 sm:space-y-3 border-t border-border pt-3 sm:pt-4">
                      <div className="flex items-center gap-2 text-xs sm:text-sm text-muted-foreground">
                        <Calendar className="w-4 h-4" />
                        <span>{formatDate(article.date)}</span>
                      </div>
                      <div className="flex items-center gap-2 text-xs sm:text-sm text-muted-foreground">
                        <User className="w-4 h-4" />
                        <span>{article.author}</span>
                      </div>
                    </div>

                    {/* Read More Button */}
                    <button className="mt-4 flex items-center gap-2 text-primary font-medium hover:gap-3 transition-all text-sm">
                      Đọc tiếp
                      <ArrowRight className="w-4 h-4" />
                    </button>
                  </div>
                </article>
              ))}
            </div>
          ) : (
            <div className="text-center py-12">
              <p className="text-muted-foreground text-lg mb-4">Không tìm thấy bài viết phù hợp</p>
              <Button
                variant="outline"
                onClick={() => {
                  setSearchQuery("")
                  setActiveCategory("all")
                }}
              >
                Xóa bộ lọc
              </Button>
            </div>
          )}

          {/* Additional CTA Section */}
          <div className="mt-12 bg-white sm:mt-16 bg-gradient-to-r from-primary/10 to-accent/10 rounded-lg border border-border p-6 sm:p-8 text-center">
            <h3 className="text-xl sm:text-2xl font-bold text-foreground mb-2 sm:mb-3">Cần Tư Vấn Cá Nhân?</h3>
            <p className="text-muted-foreground mb-4 sm:mb-6 max-w-2xl mx-auto text-sm sm:text-base px-2">
              Để được tư vấn chi tiết về tình huống của bạn, hãy trò chuyện với trợ lý AI AusVisa.
            </p>
            <div className="flex gap-2 sm:gap-4 justify-center flex-col sm:flex-row px-2">
              <Link href="/chat">
                <Button className="w-full sm:w-auto bg-primary hover:bg-primary/90 text-primary-foreground">
                  Bắt đầu trò chuyện
                </Button>
              </Link>
              <Link href="/info">
                <Button
                  variant="outline"
                  className="w-full sm:w-auto border-primary/30 hover:bg-primary/5 bg-transparent"
                >
                  Xem thông tin chi tiết
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
                  <Link href="/news" className="hover:text-foreground">
                    Tin tức
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
