import { Button } from "@/components/ui/button"
import Link from "next/link"

export default function LandingPage() {
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
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary to-accent">
              trở nên dễ dàng
            </span>
          </h1>

          <p className="text-lg text-muted-foreground mb-8 max-w-2xl mx-auto leading-relaxed">
            Khám phá cơ hội định cư, du học, và xin visa Úc với sự giúp đỡ của trí tuệ nhân tạo và đồ thị tri thức. Được
            tin tưởng bởi hàng ngàn người tìm kiếm tương lai tại Úc.
          </p>

          <div className="flex gap-4 justify-center flex-wrap mb-12">
            <Link href="/register">
              <Button size="lg" className="bg-primary hover:bg-primary/90 text-primary-foreground">
                Bắt đầu miễn phí
              </Button>
            </Link>
            <Link href="/chat">
              <Button size="lg" variant="outline" className="border-primary/30 hover:bg-primary/5 bg-transparent">
                Trò chuyện với AI
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
              <p className="text-sm text-muted-foreground">
                Tìm hiểu visa, khóa học, và yêu cầu nhập học từ các trường hàng đầu
              </p>
            </div>

            <div className="bg-card rounded-lg border border-border p-6 text-left hover:border-primary/50 transition-colors">
              <div className="w-12 h-12 rounded-lg bg-accent/10 flex items-center justify-center mb-4">
                <span className="text-2xl">🏠</span>
              </div>
              <h3 className="text-lg font-semibold text-foreground mb-2">Định cư Úc</h3>
              <p className="text-sm text-muted-foreground">
                Khám phá các đường dẫn định cư, yêu cầu kỹ năng, và quy trình xin visa
              </p>
            </div>

            <div className="bg-card rounded-lg border border-border p-6 text-left hover:border-primary/50 transition-colors">
              <div className="w-12 h-12 rounded-lg bg-secondary/10 flex items-center justify-center mb-4">
                <span className="text-2xl">✈️</span>
              </div>
              <h3 className="text-lg font-semibold text-foreground mb-2">Visa Úc</h3>
              <p className="text-sm text-muted-foreground">
                Hướng dẫn chi tiết về các loại visa, điều kiện, và quy trình nộp đơn
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-12 px-4 border-t border-border">
        <div className="max-w-3xl mx-auto text-center">
          <h2 className="text-3xl font-bold text-foreground mb-4">Sẵn sàng bắt đầu cuộc hành trình của bạn?</h2>
          <p className="text-muted-foreground mb-6">
            Hãy đăng ký để nhận tư vấn cá nhân từ hệ thống AI tiên tiến của chúng tôi
          </p>
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
