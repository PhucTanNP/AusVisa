"use client"

import { ArrowDownRight, ArrowUpRight, Play, ShieldCheck, UserPlus, Users } from "lucide-react"
import { useRouter } from "next/navigation"
import { useEffect, useMemo, useState } from "react"

import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { useAuth } from "@/hooks/use-auth"
import { useToast } from "@/hooks/use-toast"
import { deleteUser, getAdminStats, getAdminUsers, updateUserStatus, type UserStats, type UserWithStats } from "@/lib/api"

type UserStatus = "active" | "pending" | "suspended"

const statusStyle: Record<UserStatus, { label: string; variant: "secondary" | "outline"; tone: string }> = {
    active: { label: "Hoạt động", variant: "secondary", tone: "text-green-700" },
    pending: { label: "Chờ duyệt", variant: "outline", tone: "text-amber-600" },
    suspended: { label: "Tạm khóa", variant: "outline", tone: "text-red-600" },
}

export function UserManagement() {
    const router = useRouter()
    const { toast } = useToast()
    const { logout } = useAuth()
    const [search, setSearch] = useState("")
    const [statusFilter, setStatusFilter] = useState<UserStatus | "all">("all")
    const [users, setUsers] = useState<UserWithStats[]>([])
    const [stats, setStats] = useState<UserStats | null>(null)
    const [loading, setLoading] = useState(true)

    // Check authentication and load data
    useEffect(() => {
        loadData()
    }, [])

    const loadData = async () => {
        try {
            setLoading(true)
            const [usersData, statsData] = await Promise.all([
                getAdminUsers(),
                getAdminStats()
            ])
            setUsers(usersData)
            setStats(statsData)
        } catch (error) {
            toast({
                title: "Lỗi",
                description: error instanceof Error ? error.message : "Không thể tải dữ liệu",
                variant: "destructive"
            })
        } finally {
            setLoading(false)
        }
    }

    const handleToggleStatus = async (userId: number, currentStatus: boolean) => {
        try {
            await updateUserStatus(userId, !currentStatus)
            toast({
                title: "Thành công",
                description: "Đã cập nhật trạng thái người dùng"
            })
            loadData()
        } catch (error) {
            toast({
                title: "Lỗi",
                description: error instanceof Error ? error.message : "Không thể cập nhật trạng thái",
                variant: "destructive"
            })
        }
    }

    const handleDeleteUser = async (userId: number) => {
        if (!confirm("Bạn có chắc chắn muốn xóa người dùng này?")) return

        try {
            await deleteUser(userId)
            toast({
                title: "Thành công",
                description: "Đã xóa người dùng"
            })
            loadData()
        } catch (error) {
            toast({
                title: "Lỗi",
                description: error instanceof Error ? error.message : "Không thể xóa người dùng",
                variant: "destructive"
            })
        }
    }

    const getUserStatus = (user: UserWithStats): UserStatus => {
        if (!user.is_active) {
            return "suspended"
        }
        return "active"
    }

    const filteredUsers = useMemo(() => {
        const keyword = search.toLowerCase()
        return users.filter((u) => {
            const matchesKeyword = `${u.username} ${u.email} ${u.role}`.toLowerCase().includes(keyword)
            const userStatus = getUserStatus(u)
            const matchesStatus = statusFilter === "all" ? true : userStatus === statusFilter
            return matchesKeyword && matchesStatus
        })
    }, [search, statusFilter, users])

    const userStatsCards = useMemo(() => {
        if (!stats) return []
        return [
            {
                title: "Tổng người dùng",
                value: stats.total_users.toString(),
                meta: `${users.length} users`,
                trend: "up" as const,
                icon: <Users className="h-4 w-4 text-primary" />,
            },
            {
                title: "Đang hoạt động",
                value: stats.active_users.toString(),
                meta: `${Math.round((stats.active_users / stats.total_users) * 100)}% online`,
                trend: "up" as const,
                icon: <ShieldCheck className="h-4 w-4 text-green-600" />,
            },
            {
                title: "Chờ duyệt",
                value: stats.pending_users.toString(),
                meta: "yêu cầu mới",
                trend: "up" as const,
                icon: <UserPlus className="h-4 w-4 text-accent" />,
            },
            {
                title: "Bị tạm khóa",
                value: stats.suspended_users.toString(),
                meta: "users",
                trend: "down" as const,
                icon: <ArrowDownRight className="h-4 w-4 text-red-500" />,
            },
        ]
    }, [stats, users])

    if (loading) {
        return (
            <div className="h-full flex items-center justify-center">
                <p className="text-muted-foreground">Đang tải...</p>
            </div>
        )
    }

    return (
        <div className="space-y-6">
            <div className="flex flex-wrap items-center gap-3 justify-between">
                <div>
                    <h2 className="text-2xl font-bold tracking-tight">Quản lý người dùng</h2>
                    <p className="text-muted-foreground">Quản lý tài khoản và quyền truy cập.</p>
                </div>
                <div className="flex flex-wrap items-center gap-2">
                    <Button variant="outline" size="sm" className="gap-2" onClick={loadData}>
                        <Play className="h-4 w-4" />
                        Làm mới
                    </Button>
                    <Button className="bg-primary hover:bg-primary/90 text-primary-foreground gap-2 shadow-sm" onClick={() => router.push('/register?from=admin')}>
                        <UserPlus className="h-4 w-4" />
                        Thêm người dùng
                    </Button>
                </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                {userStatsCards.map((item) => (
                    <div
                        key={item.title}
                        className="border border-border/70 rounded-xl bg-gradient-to-br from-card to-muted/30 p-4 shadow-sm space-y-3"
                    >
                        <div className="flex items-center justify-between">
                            <span className="text-sm text-muted-foreground">{item.title}</span>
                            <div className="h-9 w-9 rounded-lg bg-muted flex items-center justify-center">{item.icon}</div>
                        </div>
                        <div className="flex items-end justify-between">
                            <p className="text-2xl font-semibold">{item.value}</p>
                            <span
                                className={`text-xs font-medium inline-flex items-center gap-1 ${item.trend === "up" ? "text-green-600" : item.trend === "down" ? "text-red-500" : "text-muted-foreground"
                                    }`}
                            >
                                {item.trend === "up" && <ArrowUpRight className="h-3.5 w-3.5" />}
                                {item.trend === "down" && <ArrowDownRight className="h-3.5 w-3.5" />}
                                {item.meta}
                            </span>
                        </div>
                    </div>
                ))}
            </div>

            <Card className="border-border/80 bg-card/80 backdrop-blur">
                <CardHeader className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
                    <CardTitle className="text-lg font-semibold">Danh sách người dùng</CardTitle>
                    <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:gap-3">
                        <div className="flex items-center gap-2 bg-muted/60 border border-border rounded-lg px-3 py-2">
                            <Input
                                value={search}
                                onChange={(e) => setSearch(e.target.value)}
                                placeholder="Tìm theo tên, email, vai trò..."
                                className="h-8 w-60 bg-transparent border-none px-0 focus-visible:ring-0"
                            />
                        </div>
                        <div className="flex flex-wrap gap-2">
                            {(["all", "active", "pending", "suspended"] as const).map((status) => (
                                <Badge
                                    key={status}
                                    variant={statusFilter === status ? "secondary" : "outline"}
                                    className="cursor-pointer"
                                    onClick={() => setStatusFilter(status)}
                                >
                                    {status === "all" ? "Tất cả" : statusStyle[status].label}
                                </Badge>
                            ))}
                        </div>
                    </div>
                </CardHeader>
                <CardContent>
                    <Table>
                        <TableHeader>
                            <TableRow>
                                <TableHead>Người dùng</TableHead>
                                <TableHead>Vai trò</TableHead>
                                <TableHead>Trạng thái</TableHead>
                                <TableHead>Sessions</TableHead>
                                <TableHead>Hành động</TableHead>
                            </TableRow>
                        </TableHeader>
                        <TableBody>
                            {filteredUsers.map((user) => {
                                const userStatus = getUserStatus(user)
                                return (
                                    <TableRow key={user.id}>
                                        <TableCell>
                                            <div className="flex items-center gap-3">
                                                <Avatar className="h-9 w-9">
                                                    <AvatarFallback>{user.username.slice(0, 2).toUpperCase()}</AvatarFallback>
                                                </Avatar>
                                                <div className="min-w-0">
                                                    <p className="font-medium truncate">{user.username}</p>
                                                    <p className="text-xs text-muted-foreground truncate">{user.email}</p>
                                                </div>
                                            </div>
                                        </TableCell>
                                        <TableCell className="text-sm">{user.role}</TableCell>
                                        <TableCell>
                                            <Badge variant={statusStyle[userStatus].variant} className={statusStyle[userStatus].tone}>
                                                {statusStyle[userStatus].label}
                                            </Badge>
                                        </TableCell>
                                        <TableCell>
                                            <Badge variant="outline" className="font-mono text-xs">
                                                {user.session_count}
                                            </Badge>
                                        </TableCell>
                                        <TableCell className="text-sm text-muted-foreground">
                                            <div className="flex flex-wrap gap-2">
                                                <Button
                                                    size="sm"
                                                    variant={user.is_active ? "destructive" : "secondary"}
                                                    onClick={() => handleToggleStatus(user.id, user.is_active)}
                                                >
                                                    {user.is_active ? "Block" : "Unblock"}
                                                </Button>
                                                <Button
                                                    size="sm"
                                                    variant="outline"
                                                    onClick={() => handleDeleteUser(user.id)}
                                                >
                                                    Delete
                                                </Button>
                                            </div>
                                        </TableCell>
                                    </TableRow>
                                )
                            })}
                        </TableBody>
                    </Table>
                </CardContent>
            </Card>
        </div>
    )
}
