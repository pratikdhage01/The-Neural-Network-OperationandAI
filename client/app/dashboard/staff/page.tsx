'use client';

import { useEffect, useState } from 'react';
import { Header } from '@/components/layout/header';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { ScrollArea } from '@/components/ui/scroll-area';
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from '@/components/ui/table';
import { staffAPI, analyticsAPI, Staff, WorkloadDistribution } from '@/lib/api';
import { Users, UserCheck, UserX, Briefcase, CheckCircle2, Clock, AlertCircle } from 'lucide-react';

const taskStatusColors: Record<string, string> = {
    pending: 'bg-yellow-500/20 text-yellow-400',
    in_progress: 'bg-blue-500/20 text-blue-400',
    completed: 'bg-green-500/20 text-green-400',
    blocked: 'bg-red-500/20 text-red-400',
};

export default function StaffPage() {
    const [staff, setStaff] = useState<Staff[]>([]);
    const [workload, setWorkload] = useState<{ distribution: WorkloadDistribution[]; summary: { average_utilization: number; total_staff: number } } | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        async function fetchData() {
            try {
                const [staffData, workloadData] = await Promise.all([
                    staffAPI.list(),
                    analyticsAPI.getWorkload(),
                ]);
                setStaff(staffData);
                setWorkload(workloadData);
            } catch (error) {
                console.error('Failed to fetch staff data:', error);
            } finally {
                setLoading(false);
            }
        }
        fetchData();
        const interval = setInterval(fetchData, 30000);
        return () => clearInterval(interval);
    }, []);

    const getUtilizationColor = (percent: number) => {
        if (percent >= 90) return 'text-red-400';
        if (percent >= 70) return 'text-yellow-400';
        return 'text-green-400';
    };

    if (loading) {
        return (
            <div className="flex h-screen items-center justify-center">
                <div className="h-8 w-8 animate-spin rounded-full border-4 border-violet-500 border-t-transparent" />
            </div>
        );
    }

    const availableCount = staff.filter(s => s.is_available).length;
    const totalTasks = staff.reduce((acc, s) => acc + s.current_workload, 0);

    return (
        <div className="min-h-screen">
            <Header title="Staff & Workload" subtitle="Manage team and task distribution" />

            <div className="p-6 space-y-6">
                {/* Stats */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <Card className="bg-zinc-900/50 border-zinc-800">
                        <CardContent className="p-4">
                            <div className="flex items-center gap-3">
                                <Users className="h-8 w-8 text-violet-400" />
                                <div>
                                    <p className="text-sm text-zinc-400">Total Staff</p>
                                    <p className="text-2xl font-bold text-white">{staff.length}</p>
                                </div>
                            </div>
                        </CardContent>
                    </Card>
                    <Card className="bg-zinc-900/50 border-zinc-800">
                        <CardContent className="p-4">
                            <div className="flex items-center gap-3">
                                <UserCheck className="h-8 w-8 text-green-400" />
                                <div>
                                    <p className="text-sm text-zinc-400">Available</p>
                                    <p className="text-2xl font-bold text-green-400">{availableCount}</p>
                                </div>
                            </div>
                        </CardContent>
                    </Card>
                    <Card className="bg-zinc-900/50 border-zinc-800">
                        <CardContent className="p-4">
                            <div className="flex items-center gap-3">
                                <Briefcase className="h-8 w-8 text-blue-400" />
                                <div>
                                    <p className="text-sm text-zinc-400">Active Tasks</p>
                                    <p className="text-2xl font-bold text-white">{totalTasks}</p>
                                </div>
                            </div>
                        </CardContent>
                    </Card>
                    <Card className="bg-zinc-900/50 border-zinc-800">
                        <CardContent className="p-4">
                            <div className="flex items-center gap-3">
                                <AlertCircle className={`h-8 w-8 ${getUtilizationColor(workload?.summary?.average_utilization || 0)}`} />
                                <div>
                                    <p className="text-sm text-zinc-400">Avg. Utilization</p>
                                    <p className={`text-2xl font-bold ${getUtilizationColor(workload?.summary?.average_utilization || 0)}`}>
                                        {(workload?.summary?.average_utilization || 0).toFixed(0)}%
                                    </p>
                                </div>
                            </div>
                        </CardContent>
                    </Card>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    {/* Workload Distribution */}
                    <Card className="bg-zinc-900/50 border-zinc-800">
                        <CardHeader>
                            <CardTitle className="text-lg font-medium text-white">Workload Distribution</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="space-y-4">
                                {workload?.distribution.map((item) => (
                                    <div key={item.staff_id} className="space-y-2">
                                        <div className="flex justify-between items-center">
                                            <div>
                                                <p className="text-sm font-medium text-white">{item.staff_name}</p>
                                            </div>
                                            <span className={`text-sm font-medium ${getUtilizationColor(item.utilization_percent)}`}>
                                                {item.current_tasks}/{item.max_capacity} ({item.utilization_percent.toFixed(0)}%)
                                            </span>
                                        </div>
                                        <Progress
                                            value={item.utilization_percent}
                                            className="h-2 bg-zinc-800"
                                        />
                                    </div>
                                ))}
                            </div>
                        </CardContent>
                    </Card>

                    {/* Staff List */}
                    <Card className="bg-zinc-900/50 border-zinc-800">
                        <CardHeader>
                            <CardTitle className="text-lg font-medium text-white">Team Members</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <ScrollArea className="h-80">
                                <div className="space-y-3">
                                    {staff.map((member) => (
                                        <div
                                            key={member._id}
                                            className="flex items-center justify-between p-3 rounded-lg border border-zinc-800 bg-zinc-900/50"
                                        >
                                            <div className="flex items-center gap-3">
                                                <div className={`h-10 w-10 rounded-full flex items-center justify-center ${member.is_available ? 'bg-green-500/20' : 'bg-zinc-700'}`}>
                                                    <Users className={`h-5 w-5 ${member.is_available ? 'text-green-400' : 'text-zinc-500'}`} />
                                                </div>
                                                <div>
                                                    <p className="text-sm font-medium text-white">{member.name}</p>
                                                </div>
                                            </div>
                                            <div className="text-right">
                                                <Badge className={member.is_available ? 'bg-green-500/20 text-green-400' : 'bg-zinc-700 text-zinc-400'}>
                                                    {member.is_available ? 'Available' : 'Busy'}
                                                </Badge>
                                                <p className="text-xs text-zinc-500 mt-1">
                                                    {member.current_workload}/{member.max_workload} tasks
                                                </p>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </ScrollArea>
                        </CardContent>
                    </Card>
                </div>

                {/* Tasks Table */}
                <Card className="bg-zinc-900/50 border-zinc-800">
                    <CardHeader>
                        <CardTitle className="text-lg font-medium text-white">Assigned Tasks</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <ScrollArea className="h-64">
                            <Table>
                                <TableHeader>
                                    <TableRow className="border-zinc-800 hover:bg-transparent">
                                        <TableHead className="text-zinc-400">Task ID</TableHead>
                                        <TableHead className="text-zinc-400">Staff</TableHead>
                                        <TableHead className="text-zinc-400">Description</TableHead>
                                        <TableHead className="text-zinc-400">Priority</TableHead>
                                        <TableHead className="text-zinc-400">Status</TableHead>
                                    </TableRow>
                                </TableHeader>
                                <TableBody>
                                    {staff.flatMap((member) =>
                                        member.assigned_tasks.map((task) => (
                                            <TableRow key={task.task_id} className="border-zinc-800 hover:bg-zinc-800/50">
                                                <TableCell className="font-mono text-xs text-violet-400">
                                                    {task.task_id}
                                                </TableCell>
                                                <TableCell className="text-white">{member.name}</TableCell>
                                                <TableCell className="text-zinc-300">{task.description}</TableCell>
                                                <TableCell>
                                                    <Badge variant="outline" className="border-zinc-700 text-white/50">
                                                        P{task.priority}
                                                    </Badge>
                                                </TableCell>
                                                <TableCell>
                                                    <Badge className={taskStatusColors[task.status] || taskStatusColors.pending}>
                                                        {task.status.replace('_', ' ')}
                                                    </Badge>
                                                </TableCell>
                                            </TableRow>
                                        ))
                                    )}
                                    {staff.every((s) => s.assigned_tasks.length === 0) && (
                                        <TableRow>
                                            <TableCell colSpan={5} className="text-center text-zinc-500 py-8">
                                                No tasks assigned
                                            </TableCell>
                                        </TableRow>
                                    )}
                                </TableBody>
                            </Table>
                        </ScrollArea>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}
