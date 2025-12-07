"use client"

import { Button } from "@/components/ui/button"
import { Checkbox } from "@/components/ui/checkbox"
import { Label } from "@/components/ui/label"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { useToast } from "@/hooks/use-toast"
import { getNeo4jStats, Neo4jStats } from "@/lib/api"
import { Play } from "lucide-react"
import { useEffect, useMemo, useState } from "react"
import { Bar, BarChart, CartesianGrid, Cell, LabelList, Legend, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts"

// Vibrant, Premium Colors
const COLORS = [
    '#3b82f6', // Bright Blue
    '#8b5cf6', // Violet
    '#ec4899', // Pink
    '#f43f5e', // Rose
    '#f97316', // Orange
    '#eab308', // Yellow
    '#10b981', // Emerald
    '#06b6d4', // Cyan
    '#6366f1', // Indigo
];

type ChartType = 'bar' | 'pie';

const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
        return (
            <div className="bg-card border border-border p-3 rounded-lg shadow-lg">
                <p className="font-semibold mb-1 text-card-foreground">{label}</p>
                <div className="flex items-center gap-2">
                    <span
                        className="block w-3 h-3 rounded-full"
                        style={{ backgroundColor: payload[0].payload.fill || payload[0].stroke }}
                    ></span>
                    <span className="text-sm">
                        Số lượng: <span className="font-bold">{payload[0].value}</span>
                    </span>
                </div>
            </div>
        );
    }
    return null;
};

export function KnowledgeGraph() {
    const { toast } = useToast()
    const [stats, setStats] = useState<Neo4jStats | null>(null)
    const [loading, setLoading] = useState(true)

    // Analytics State
    const [chartType, setChartType] = useState<ChartType>('bar')
    const [selectedLabels, setSelectedLabels] = useState<string[]>([])

    useEffect(() => {
        loadData()
    }, [])

    const loadData = async () => {
        try {
            setLoading(true)
            const statsData = await getNeo4jStats()
            setStats(statsData)

            // Default selection: Visa, University, SettlementPage
            setSelectedLabels(['Visa', 'University', 'SettlementPage'])
        } catch (error) {
            toast({
                title: "Lỗi",
                description: error instanceof Error ? error.message : "Không thể tải dữ liệu Knowledge Graph",
                variant: "destructive"
            })
        } finally {
            setLoading(false)
        }
    }

    const handleRefresh = () => {
        loadData()
    }

    const filteredNodeStats = useMemo(() => {
        if (!stats) return []
        return stats.node_counts.filter(item => selectedLabels.includes(item.label))
    }, [stats, selectedLabels])

    const toggleLabel = (label: string) => {
        setSelectedLabels(prev =>
            prev.includes(label)
                ? prev.filter(l => l !== label)
                : [...prev, label]
        )
    }

    const selectAllLabels = () => {
        if (stats) {
            setSelectedLabels(stats.node_counts.map(i => i.label))
        }
    }

    const clearAllLabels = () => {
        setSelectedLabels([])
    }

    const renderChart = () => {
        if (!stats) return null
        if (selectedLabels.length === 0) {
            return (
                <div className="flex flex-col items-center justify-center h-full text-muted-foreground">
                    <p className="mb-2">Chưa chọn dữ liệu để hiển thị.</p>
                    <p className="text-sm">Vui lòng chọn các loại Node từ danh sách bên trái.</p>
                </div>
            )
        }

        const CommonAxis = () => (
            <>
                <CartesianGrid strokeDasharray="3 3" opacity={0.2} vertical={false} />
                <XAxis dataKey="label" fontSize={12} tickLine={false} axisLine={false} />
                <YAxis fontSize={12} tickLine={false} axisLine={false} />
                <Tooltip content={<CustomTooltip />} cursor={{ fill: 'transparent' }} />
                <Legend />
            </>
        )

        switch (chartType) {
            case 'bar':
                return (
                    <BarChart data={filteredNodeStats} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#9ca3af" strokeWidth={1} />
                        <XAxis dataKey="label" fontSize={12} tickLine={false} axisLine={false} />
                        <YAxis fontSize={12} tickLine={false} axisLine={false} />
                        <Tooltip content={<CustomTooltip />} cursor={false} />
                        <Bar
                            dataKey="count"
                            name="Số lượng"
                            radius={[4, 4, 0, 0]}
                            // Highlighting effect on hover
                            activeBar={{
                                fillOpacity: 1,
                                stroke: 'hsl(var(--foreground))',
                                strokeWidth: 2,
                                style: {
                                    transform: "scale(1.02)",
                                    transformOrigin: "center bottom",
                                    transition: "transform 0.2s ease"
                                }
                            }}
                            maxBarSize={80}
                        >
                            {filteredNodeStats.map((entry, index) => (
                                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                            ))}
                            <LabelList dataKey="count" position="top" fill="hsl(var(--foreground))" fontSize={12} fontWeight="bold" />
                        </Bar>
                    </BarChart>
                )
            case 'pie':
                return (
                    <PieChart>
                        <Pie
                            data={filteredNodeStats}
                            cx="50%"
                            cy="50%"
                            innerRadius={60}
                            outerRadius={100}
                            paddingAngle={5}
                            dataKey="count"
                            nameKey="label"
                            label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                        >
                            {filteredNodeStats.map((entry, index) => (
                                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                            ))}
                        </Pie>
                        <Tooltip content={<CustomTooltip />} />
                        <Legend />
                    </PieChart>
                )
            default:
                return null
        }
    }

    return (
        <div className="space-y-4 h-full flex flex-col">
            <div className="flex justify-between items-center">
                <div>
                    <h2 className="text-2xl font-bold tracking-tight">Trực quan hóa dữ liệu</h2>
                    <p className="text-muted-foreground">Phân tích và hiển thị dữ liệu từ Neo4j.</p>
                </div>
                <div className="flex gap-2">
                    <Button variant="outline" size="sm" onClick={handleRefresh}>
                        <Play className="h-4 w-4 mr-2" />
                        Làm mới
                    </Button>
                </div>
            </div>

            <Tabs defaultValue="charts" className="flex-1 flex flex-col">
                <TabsList>
                    <TabsTrigger value="charts">Biểu đồ thống kê</TabsTrigger>
                </TabsList>

                <div className="flex-1 mt-4 bg-card border border-border rounded-xl p-4 overflow-hidden">
                    <TabsContent value="charts" className="h-[500px] flex flex-col gap-4">
                        {loading ? (
                            <div className="flex items-center justify-center h-full text-muted-foreground">
                                <span className="animate-pulse">Đang tải thống kê...</span>
                            </div>
                        ) : stats ? (
                            <div className="flex flex-col h-full gap-4">
                                {/* Top Controls & Stats */}
                                <div className="flex justify-between items-center bg-muted/30 p-3 rounded-lg border">
                                    <div className="flex items-center gap-4">
                                        <div className="flex items-center gap-2">
                                            <Label className="text-muted-foreground">Hiển thị:</Label>
                                            <Select value={chartType} onValueChange={(v: ChartType) => setChartType(v)}>
                                                <SelectTrigger className="w-[180px] h-8 text-sm">
                                                    <SelectValue placeholder="Chọn loại biểu đồ" />
                                                </SelectTrigger>
                                                <SelectContent>
                                                    <SelectItem value="bar">Biểu đồ Cột (Bar)</SelectItem>
                                                    <SelectItem value="pie">Biểu đồ Tròn (Pie)</SelectItem>
                                                </SelectContent>
                                            </Select>
                                        </div>
                                        <div className="h-4 w-px bg-border mx-2"></div>
                                        <div className="flex gap-2 text-sm">
                                            <div className="flex items-center gap-1.5 px-2 bg-background rounded-md border text-muted-foreground">
                                                <span className="font-semibold text-foreground">{stats.node_counts.reduce((a, b) => a + b.count, 0)}</span> Nodes
                                            </div>
                                            <div className="flex items-center gap-1.5 px-2 bg-background rounded-md border text-muted-foreground">
                                                <span className="font-semibold text-foreground">{stats.rel_counts.reduce((a, b) => a + b.count, 0)}</span> Links
                                            </div>
                                        </div>
                                    </div>

                                    <div className="flex items-center gap-2">
                                        <Button variant="ghost" size="sm" className="h-8 px-2 text-xs" onClick={selectAllLabels}>All</Button>
                                        <Button variant="ghost" size="sm" className="h-8 px-2 text-xs" onClick={clearAllLabels}>Clear</Button>
                                    </div>
                                </div>

                                {/* Main Content: Filter & Chart */}
                                <div className="flex-1 grid grid-cols-12 gap-4 min-h-0">
                                    {/* Filter Sidebar (Left) */}
                                    <div className="col-span-3 border rounded-lg overflow-hidden flex flex-col bg-card/50 min-h-0">
                                        <div className="p-2 border-b bg-muted/20 text-xs font-semibold uppercase tracking-wider text-muted-foreground flex-none">
                                            Filter Nodes
                                        </div>
                                        <ScrollArea className="flex-1 h-full">
                                            <div className="p-2 space-y-1">
                                                {stats.node_counts.map((item, index) => (
                                                    <div
                                                        key={item.label}
                                                        className="flex items-center space-x-2 rounded-md hover:bg-muted/50 p-1.5 transition-colors cursor-pointer group"
                                                        onClick={() => toggleLabel(item.label)}
                                                    >
                                                        <Checkbox
                                                            id={`filter-${item.label}`}
                                                            checked={selectedLabels.includes(item.label)}
                                                            onCheckedChange={() => toggleLabel(item.label)}
                                                            className="h-4 w-4 data-[state=checked]:bg-primary"
                                                            style={{
                                                                borderColor: selectedLabels.includes(item.label) ? COLORS[index % COLORS.length] : undefined,
                                                                backgroundColor: selectedLabels.includes(item.label) ? COLORS[index % COLORS.length] : undefined
                                                            }}
                                                        />
                                                        <Label htmlFor={`filter-${item.label}`} className="text-sm cursor-pointer flex-1 flex justify-between items-center">
                                                            <span className="truncate pr-2 text-muted-foreground group-hover:text-foreground transition-colors">{item.label}</span>
                                                            <span className="text-[10px] font-mono bg-muted px-1.5 py-0.5 rounded-full min-w-[24px] text-center">{item.count}</span>
                                                        </Label>
                                                    </div>
                                                ))}
                                            </div>
                                        </ScrollArea>
                                    </div>

                                    {/* Chart Area (Right) */}
                                    <div className="col-span-9 bg-gradient-to-br from-background to-muted/10 rounded-xl border border-dashed flex flex-col overflow-hidden relative">
                                        <div className="flex-1 w-full min-h-0 pt-4 pr-4">
                                            <ResponsiveContainer width="100%" height="100%">
                                                {renderChart()!}
                                            </ResponsiveContainer>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        ) : (
                            <div className="flex items-center justify-center h-full text-muted-foreground">Không có dữ liệu thống kê</div>
                        )}
                    </TabsContent>


                </div>
            </Tabs>
        </div>
    )
}
