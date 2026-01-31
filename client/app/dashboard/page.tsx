'use client';

import { useEffect, useState } from 'react';
import { Header } from '@/components/layout/header';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { ScrollArea } from '@/components/ui/scroll-area';
import { analyticsAPI, DashboardStats, Bottleneck, AgentActivity, WorkloadDistribution } from '@/lib/api';
import {
    ShoppingCart,
    Package,
    AlertTriangle,
    Users,
    TrendingUp,
    Clock,
    Activity,
    CheckCircle2,
} from 'lucide-react';

export default function DashboardPage() {
    const [stats, setStats] = useState<DashboardStats | null>(null);
    const [bottlenecks, setBottlenecks] = useState<Bottleneck[]>([]);
    const [activities, setActivities] = useState<AgentActivity[]>([]);
    const [workload, setWorkload] = useState<WorkloadDistribution[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        async function fetchData() {
            try {
                const [statsData, bottlenecksData, activitiesData, workloadData] = await Promise.all([
                    analyticsAPI.getOverview(),
                    analyticsAPI.getBottlenecks(),
                    analyticsAPI.getAgentActivity(10),
                    analyticsAPI.getWorkload(),
                ]);
                setStats(statsData);
                setBottlenecks(bottlenecksData);
                setActivities(activitiesData);
                setWorkload(workloadData.distribution);
            } catch (error) {
                console.error('Failed to fetch dashboard data:', error);
            } finally {
                setLoading(false);
            }
        }
        fetchData();
        const interval = setInterval(fetchData, 30000); // Refresh every 30s
        return () => clearInterval(interval);
    }, []);

    const getSeverityColor = (severity: string) => {
        switch (severity) {
            case 'critical': return 'bg-red-500/20 text-red-400 border-red-500/30';
            case 'high': return 'bg-orange-500/20 text-orange-400 border-orange-500/30';
            case 'medium': return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30';
            default: return 'bg-green-500/20 text-green-400 border-green-500/30';
        }
    };

    if (loading) {
        return (
            <div className="flex h-screen items-center justify-center">
                <div className="h-8 w-8 animate-spin rounded-full border-4 border-violet-500 border-t-transparent" />
            </div>
        );
    }

    return (
        <div className="min-h-screen">
            <Header title="Dashboard" subtitle="Real-time operations overview" />

            <div className="p-6 space-y-6">
                {/* Stats Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                    <StatsCard
                        title="Total Orders"
                        value={stats?.total_orders || 0}
                        subtitle={`${stats?.orders_today || 0} today`}
                        icon={ShoppingCart}
                        trend={+12}
                        color="violet"
                    />
                    <StatsCard
                        title="Pending Orders"
                        value={stats?.pending_orders || 0}
                        subtitle={`${stats?.processing_orders || 0} processing`}
                        icon={Clock}
                        color="amber"
                    />
                    <StatsCard
                        title="Inventory Items"
                        value={stats?.total_products || 0}
                        subtitle={`${stats?.low_stock_count || 0} low stock`}
                        icon={Package}
                        color="emerald"
                    />
                    <StatsCard
                        title="Active Bottlenecks"
                        value={stats?.active_bottlenecks || 0}
                        subtitle="Needs attention"
                        icon={AlertTriangle}
                        color={stats?.active_bottlenecks ? 'red' : 'green'}
                    />
                </div>

                {/* Staff Utilization */}
                <Card className="bg-zinc-900/50 border-zinc-800">
                    <CardHeader className="pb-2">
                        <CardTitle className="text-lg font-medium text-white flex items-center gap-2">
                            <Users className="h-5 w-5 text-violet-400" />
                            Staff Utilization
                            <Badge variant="secondary" className="ml-auto">
                                {stats?.staff_utilization.toFixed(0)}% Overall
                            </Badge>
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="space-y-4">
                            {workload.map((staff) => (
                                <div key={staff.staff_id} className="space-y-2">
                                    <div className="flex justify-between text-sm">
                                        <span className="text-zinc-300">{staff.staff_name}</span>
                                        <span className="text-zinc-500">
                                            {staff.current_tasks}/{staff.max_capacity} tasks ({staff.utilization_percent.toFixed(0)}%)
                                        </span>
                                    </div>
                                    <Progress
                                        value={staff.utilization_percent}
                                        className="h-2 bg-zinc-800"
                                    />
                                </div>
                            ))}
                            {workload.length === 0 && (
                                <p className="text-zinc-500 text-sm text-center py-4">No staff data available</p>
                            )}
                        </div>
                    </CardContent>
                </Card>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    {/* Active Bottlenecks */}
                    <Card className="bg-zinc-900/50 border-zinc-800">
                        <CardHeader className="pb-2">
                            <CardTitle className="text-lg font-medium text-white flex items-center gap-2">
                                <AlertTriangle className="h-5 w-5 text-orange-400" />
                                Active Bottlenecks
                            </CardTitle>
                        </CardHeader>
                        <CardContent>
                            <ScrollArea className="h-64">
                                <div className="space-y-3">
                                    {bottlenecks.map((bn) => (
                                        <div
                                            key={bn._id}
                                            className="rounded-lg border border-zinc-800 bg-zinc-900/50 p-3 space-y-2"
                                        >
                                            <div className="flex items-start justify-between gap-2">
                                                <span className="text-sm font-medium text-white">{bn.title}</span>
                                                <Badge className={getSeverityColor(bn.severity)}>
                                                    {bn.severity}
                                                </Badge>
                                            </div>
                                            <p className="text-xs text-zinc-400">{bn.description}</p>
                                            {bn.suggested_actions.length > 0 && (
                                                <p className="text-xs text-violet-400">
                                                    💡 {bn.suggested_actions[0]}
                                                </p>
                                            )}
                                        </div>
                                    ))}
                                    {bottlenecks.length === 0 && (
                                        <div className="flex flex-col items-center justify-center py-8 text-center">
                                            <CheckCircle2 className="h-12 w-12 text-green-500 mb-2" />
                                            <p className="text-zinc-400">No active bottlenecks</p>
                                            <p className="text-zinc-500 text-sm">Operations running smoothly</p>
                                        </div>
                                    )}
                                </div>
                            </ScrollArea>
                        </CardContent>
                    </Card>

                    {/* Recent Agent Activity */}
                    <Card className="bg-zinc-900/50 border-zinc-800">
                        <CardHeader className="pb-2">
                            <CardTitle className="text-lg font-medium text-white flex items-center gap-2">
                                <Activity className="h-5 w-5 text-violet-400" />
                                Recent Agent Activity
                            </CardTitle>
                        </CardHeader>
                        <CardContent>
                            <ScrollArea className="h-64">
                                <div className="space-y-3">
                                    {activities.map((activity) => (
                                        <div
                                            key={activity._id}
                                            className="flex items-start gap-3 rounded-lg border border-zinc-800 bg-zinc-900/50 p-3"
                                        >
                                            <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-violet-500/20">
                                                <Activity className="h-4 w-4 text-violet-400" />
                                            </div>
                                            <div className="flex-1 space-y-1">
                                                <div className="flex items-center justify-between">
                                                    <span className="text-sm font-medium text-white">
                                                        {activity.agent_name.replace('_', ' ')}
                                                    </span>
                                                    <span className="text-xs text-zinc-500">
                                                        {new Date(activity.timestamp).toLocaleTimeString()}
                                                    </span>
                                                </div>
                                                <p className="text-xs text-zinc-400">{activity.details}</p>
                                            </div>
                                        </div>
                                    ))}
                                    {activities.length === 0 && (
                                        <p className="text-zinc-500 text-sm text-center py-8">No recent activity</p>
                                    )}
                                </div>
                            </ScrollArea>
                        </CardContent>
                    </Card>
                </div>
            </div>
        </div>
    );
}

interface StatsCardProps {
    title: string;
    value: number;
    subtitle: string;
    icon: React.ElementType;
    trend?: number;
    color: 'violet' | 'amber' | 'emerald' | 'red' | 'green';
}

function StatsCard({ title, value, subtitle, icon: Icon, trend, color }: StatsCardProps) {
    const colorClasses = {
        violet: 'from-violet-500/20 to-purple-500/20 border-violet-500/30',
        amber: 'from-amber-500/20 to-orange-500/20 border-amber-500/30',
        emerald: 'from-emerald-500/20 to-green-500/20 border-emerald-500/30',
        red: 'from-red-500/20 to-rose-500/20 border-red-500/30',
        green: 'from-green-500/20 to-emerald-500/20 border-green-500/30',
    };

    const iconColors = {
        violet: 'text-violet-400',
        amber: 'text-amber-400',
        emerald: 'text-emerald-400',
        red: 'text-red-400',
        green: 'text-green-400',
    };

    return (
        <Card className={`bg-gradient-to-br ${colorClasses[color]} border`}>
            <CardContent className="p-4">
                <div className="flex items-center justify-between">
                    <div>
                        <p className="text-sm text-zinc-400">{title}</p>
                        <p className="text-3xl font-bold text-white">{value.toLocaleString()}</p>
                        <p className="text-xs text-zinc-500 mt-1">{subtitle}</p>
                    </div>
                    <div className="flex flex-col items-end gap-2">
                        <Icon className={`h-8 w-8 ${iconColors[color]}`} />
                        {trend !== undefined && (
                            <div className="flex items-center gap-1 text-xs text-green-400">
                                <TrendingUp className="h-3 w-3" />
                                {trend}%
                            </div>
                        )}
                    </div>
                </div>
            </CardContent>
        </Card>
    );
}
