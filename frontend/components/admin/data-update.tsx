"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { UploadCloud } from "lucide-react"

export function DataUpdate() {
    return (
        <div className="space-y-6">
            <div>
                <h2 className="text-2xl font-bold tracking-tight">Cập nhật dữ liệu</h2>
                <p className="text-muted-foreground">Quản lý và cập nhật cơ sở dữ liệu Knowledge Graph.</p>
            </div>

            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                <Card className="col-span-2">
                    <CardHeader>
                        <CardTitle>Trạng thái cập nhật</CardTitle>
                        <CardDescription>Tiến trình cập nhật dữ liệu tự động.</CardDescription>
                    </CardHeader>
                    <CardContent className="flex flex-col items-center justify-center py-10 space-y-4">
                        <div className="h-20 w-20 rounded-full bg-muted flex items-center justify-center">
                            <UploadCloud className="h-10 w-10 text-muted-foreground" />
                        </div>
                        <p className="text-muted-foreground text-center max-w-sm">
                            Chức năng này đang được phát triển. Trong tương lai, bạn có thể tải lên file dữ liệu mới hoặc kích hoạt quá trình crawl dữ liệu tại đây.
                        </p>
                    </CardContent>
                </Card>
            </div>
        </div>
    )
}
