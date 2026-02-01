'use client';

import { useEffect, useState } from 'react';
import { Header } from '@/components/layout/header';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from '@/components/ui/table';
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from '@/components/ui/select';
import { ScrollArea } from '@/components/ui/scroll-area';
import { ordersAPI, Order, OrderStats } from '@/lib/api';
import { Package, Clock, Truck, CheckCircle, XCircle, AlertCircle } from 'lucide-react';

const statusIcons: Record<string, React.ElementType> = {
    pending: Clock,
    confirmed: AlertCircle,
    processing: Package,
    shipped: Truck,
    delivered: CheckCircle,
    cancelled: XCircle,
};

const statusColors: Record<string, string> = {
    pending: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
    confirmed: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
    processing: 'bg-purple-500/20 text-purple-400 border-purple-500/30',
    shipped: 'bg-cyan-500/20 text-cyan-400 border-cyan-500/30',
    delivered: 'bg-green-500/20 text-green-400 border-green-500/30',
    cancelled: 'bg-red-500/20 text-red-400 border-red-500/30',
    awaiting_stock: 'bg-orange-500/20 text-orange-400 border-orange-500/30',
};

export default function OrdersPage() {
    const [orders, setOrders] = useState<Order[]>([]);
    const [stats, setStats] = useState<OrderStats | null>(null);
    const [filter, setFilter] = useState<string>('all');
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        async function fetchData() {
            try {
                const [ordersData, statsData] = await Promise.all([
                    ordersAPI.list(filter === 'all' ? undefined : filter),
                    ordersAPI.getStats(),
                ]);
                setOrders(ordersData);
                setStats(statsData);
            } catch (error) {
                console.error('Failed to fetch orders:', error);
            } finally {
                setLoading(false);
            }
        }
        fetchData();
    }, [filter]);

    const handleStatusUpdate = async (orderId: string, newStatus: string) => {
        try {
            await ordersAPI.updateStatus(orderId, newStatus);
            setOrders(orders.map(order =>
                order._id === orderId ? { ...order, status: newStatus } : order
            ));
        } catch (error) {
            console.error('Failed to update status:', error);
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
            <Header title="Orders" subtitle="Manage and track customer orders" />

            <div className="p-6 space-y-6">
                {/* Stats */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <Card className="bg-zinc-900/50 border-zinc-800">
                        <CardContent className="p-4">
                            <p className="text-sm text-zinc-400">Total Orders</p>
                            <p className="text-2xl font-bold text-white">{stats?.total || 0}</p>
                        </CardContent>
                    </Card>
                    <Card className="bg-zinc-900/50 border-zinc-800">
                        <CardContent className="p-4">
                            <p className="text-sm text-zinc-400">Orders Today</p>
                            <p className="text-2xl font-bold text-white">{stats?.orders_today || 0}</p>
                        </CardContent>
                    </Card>
                    <Card className="bg-zinc-900/50 border-zinc-800">
                        <CardContent className="p-4">
                            <p className="text-sm text-zinc-400">Revenue Today</p>
                            <p className="text-2xl font-bold text-white">₹{(stats?.revenue_today || 0).toLocaleString()}</p>
                        </CardContent>
                    </Card>
                    <Card className="bg-zinc-900/50 border-zinc-800">
                        <CardContent className="p-4">
                            <p className="text-sm text-zinc-400">Pending</p>
                            <p className="text-2xl font-bold text-amber-400">{stats?.by_status?.pending || 0}</p>
                        </CardContent>
                    </Card>
                </div>

                {/* Orders Table */}
                <Card className="bg-zinc-900/50 border-zinc-800">
                    <CardHeader className="flex flex-row items-center justify-between">
                        <CardTitle className="text-lg font-medium text-white">All Orders</CardTitle>
                        <Select value={filter} onValueChange={setFilter}>
                            <SelectTrigger className="w-40 text-white bg-zinc-800 border-zinc-700">
                                <SelectValue placeholder="Filter by status" />
                            </SelectTrigger>
                            <SelectContent>
                                <SelectItem value="all">All Orders</SelectItem>
                                <SelectItem value="pending">Pending</SelectItem>
                                <SelectItem value="confirmed">Confirmed</SelectItem>
                                <SelectItem value="processing">Processing</SelectItem>
                                <SelectItem value="shipped">Shipped</SelectItem>
                                <SelectItem value="delivered">Delivered</SelectItem>
                                <SelectItem value="cancelled">Cancelled</SelectItem>
                            </SelectContent>
                        </Select>
                    </CardHeader>
                    <CardContent>
                        <ScrollArea className="h-[500px]">
                            <Table>
                                <TableHeader>
                                    <TableRow className="border-zinc-800 hover:bg-transparent">
                                        <TableHead className="text-zinc-400">Order #</TableHead>
                                        <TableHead className="text-zinc-400">Customer</TableHead>
                                        <TableHead className="text-zinc-400">Items</TableHead>
                                        <TableHead className="text-zinc-400">Total</TableHead>
                                        <TableHead className="text-zinc-400">Status</TableHead>
                                        <TableHead className="text-zinc-400">Date</TableHead>
                                        <TableHead className="text-zinc-400">Action</TableHead>
                                    </TableRow>
                                </TableHeader>
                                <TableBody>
                                    {orders.map((order) => {
                                        const StatusIcon = statusIcons[order.status] || Clock;
                                        return (
                                            <TableRow key={order._id} className="border-zinc-800 hover:bg-zinc-800/50">
                                                <TableCell className="font-medium text-white">
                                                    {order.order_number}
                                                </TableCell>
                                                <TableCell>
                                                    <div>
                                                        <p className="text-white">{order.customer_info.name}</p>
                                                        <p className="text-xs text-zinc-500">{order.customer_info.phone}</p>
                                                    </div>
                                                </TableCell>
                                                <TableCell className="text-zinc-300">
                                                    {order.items.length} items
                                                </TableCell>
                                                <TableCell className="text-white font-medium">
                                                    ₹{order.total_amount.toLocaleString()}
                                                </TableCell>
                                                <TableCell>
                                                    <Badge className={statusColors[order.status] || statusColors.pending}>
                                                        <StatusIcon className="h-3 w-3 mr-1" />
                                                        {order.status}
                                                    </Badge>
                                                </TableCell>
                                                <TableCell className="text-zinc-400">
                                                    {new Date(order.created_at).toLocaleDateString()}
                                                </TableCell>
                                                <TableCell>
                                                    <Select
                                                        value={order.status}
                                                        onValueChange={(value) => handleStatusUpdate(order._id, value)}
                                                    >
                                                        <SelectTrigger className="w-32 h-8 text-white bg-zinc-800 border-zinc-700 text-xs">
                                                            <SelectValue />
                                                        </SelectTrigger>
                                                        <SelectContent>
                                                            <SelectItem value="pending">Pending</SelectItem>
                                                            <SelectItem value="confirmed">Confirmed</SelectItem>
                                                            <SelectItem value="processing">Processing</SelectItem>
                                                            <SelectItem value="shipped">Shipped</SelectItem>
                                                            <SelectItem value="delivered">Delivered</SelectItem>
                                                            <SelectItem value="cancelled">Cancelled</SelectItem>
                                                        </SelectContent>
                                                    </Select>
                                                </TableCell>
                                            </TableRow>
                                        );
                                    })}
                                    {orders.length === 0 && (
                                        <TableRow>
                                            <TableCell colSpan={7} className="text-center text-zinc-500 py-8">
                                                No orders found
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
