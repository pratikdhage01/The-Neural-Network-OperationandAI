'use client';

import { useEffect, useState } from 'react';
import { Header } from '@/components/layout/header';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from '@/components/ui/table';
import { suppliersAPI, Supplier, SupplierQuery } from '@/lib/api';
import { Truck, Phone, Mail, MapPin, Star, Clock, MessageSquare } from 'lucide-react';

const categoryColors: Record<string, string> = {
    jewelry: 'bg-amber-500/20 text-amber-400 border-amber-500/30',
    kitchen_appliances: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
    makeup: 'bg-pink-500/20 text-pink-400 border-pink-500/30',
};

export default function SuppliersPage() {
    const [suppliers, setSuppliers] = useState<Supplier[]>([]);
    const [selectedSupplier, setSelectedSupplier] = useState<Supplier | null>(null);
    const [queries, setQueries] = useState<SupplierQuery[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        async function fetchData() {
            try {
                const suppliersData = await suppliersAPI.list();
                setSuppliers(suppliersData);
                if (suppliersData.length > 0) {
                    setSelectedSupplier(suppliersData[0]);
                }
            } catch (error) {
                console.error('Failed to fetch suppliers:', error);
            } finally {
                setLoading(false);
            }
        }
        fetchData();
    }, []);

    useEffect(() => {
        async function fetchQueries() {
            if (selectedSupplier) {
                try {
                    const queriesData = await suppliersAPI.getQueries(selectedSupplier._id);
                    setQueries(queriesData);
                } catch (error) {
                    console.error('Failed to fetch queries:', error);
                }
            }
        }
        fetchQueries();
    }, [selectedSupplier]);

    const getReliabilityColor = (score: number) => {
        if (score >= 0.9) return 'text-green-400';
        if (score >= 0.7) return 'text-yellow-400';
        return 'text-red-400';
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
            <Header title="Suppliers" subtitle="Manage supplier relationships and communication" />

            <div className="p-6 space-y-6">
                {/* Stats */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <Card className="bg-zinc-900/50 border-zinc-800">
                        <CardContent className="p-4">
                            <div className="flex items-center gap-3">
                                <Truck className="h-8 w-8 text-violet-400" />
                                <div>
                                    <p className="text-sm text-zinc-400">Total Suppliers</p>
                                    <p className="text-2xl font-bold text-white">{suppliers.length}</p>
                                </div>
                            </div>
                        </CardContent>
                    </Card>
                    <Card className="bg-zinc-900/50 border-zinc-800">
                        <CardContent className="p-4">
                            <div className="flex items-center gap-3">
                                <Star className="h-8 w-8 text-amber-400" />
                                <div>
                                    <p className="text-sm text-zinc-400">Avg. Reliability</p>
                                    <p className="text-2xl font-bold text-white">
                                        {(suppliers.reduce((acc, s) => acc + s.reliability_score, 0) / suppliers.length * 100).toFixed(0)}%
                                    </p>
                                </div>
                            </div>
                        </CardContent>
                    </Card>
                    <Card className="bg-zinc-900/50 border-zinc-800">
                        <CardContent className="p-4">
                            <div className="flex items-center gap-3">
                                <Clock className="h-8 w-8 text-blue-400" />
                                <div>
                                    <p className="text-sm text-zinc-400">Avg. Response Time</p>
                                    <p className="text-2xl font-bold text-white">
                                        {(suppliers.reduce((acc, s) => acc + s.avg_response_time_hours, 0) / suppliers.length).toFixed(0)}h
                                    </p>
                                </div>
                            </div>
                        </CardContent>
                    </Card>
                    <Card className="bg-zinc-900/50 border-zinc-800">
                        <CardContent className="p-4">
                            <div className="flex items-center gap-3">
                                <MessageSquare className="h-8 w-8 text-green-400" />
                                <div>
                                    <p className="text-sm text-zinc-400">Pending Queries</p>
                                    <p className="text-2xl font-bold text-white">
                                        {queries.filter(q => q.status === 'pending').length}
                                    </p>
                                </div>
                            </div>
                        </CardContent>
                    </Card>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    {/* Supplier List */}
                    <Card className="bg-zinc-900/50 border-zinc-800">
                        <CardHeader>
                            <CardTitle className="text-lg font-medium text-white">Suppliers</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <ScrollArea className="h-[500px]">
                                <div className="space-y-2">
                                    {suppliers.map((supplier) => (
                                        <div
                                            key={supplier._id}
                                            onClick={() => setSelectedSupplier(supplier)}
                                            className={`p-3 rounded-lg border cursor-pointer transition-all ${selectedSupplier?._id === supplier._id
                                                    ? 'border-violet-500 bg-violet-500/10'
                                                    : 'border-zinc-800 bg-zinc-900/50 hover:border-zinc-700'
                                                }`}
                                        >
                                            <div className="flex items-start justify-between mb-2">
                                                <p className="font-medium text-white">{supplier.name}</p>
                                                <Badge className={supplier.is_active ? 'bg-green-500/20 text-green-400' : 'bg-zinc-700 text-zinc-400'}>
                                                    {supplier.is_active ? 'Active' : 'Inactive'}
                                                </Badge>
                                            </div>
                                            <p className="text-xs text-zinc-500 mb-2">{supplier.contact_person}</p>
                                            <div className="flex flex-wrap gap-1">
                                                {supplier.categories.map((cat) => (
                                                    <Badge key={cat} className={`text-xs ${categoryColors[cat]}`}>
                                                        {cat.replace('_', ' ')}
                                                    </Badge>
                                                ))}
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </ScrollArea>
                        </CardContent>
                    </Card>

                    {/* Supplier Details */}
                    <Card className="bg-zinc-900/50 border-zinc-800 lg:col-span-2">
                        <CardHeader>
                            <CardTitle className="text-lg font-medium text-white">
                                {selectedSupplier?.name || 'Select a Supplier'}
                            </CardTitle>
                        </CardHeader>
                        <CardContent>
                            {selectedSupplier ? (
                                <div className="space-y-6">
                                    {/* Contact Info */}
                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                        <div className="flex items-center gap-3 p-3 rounded-lg bg-zinc-800/50">
                                            <Phone className="h-5 w-5 text-zinc-400" />
                                            <div>
                                                <p className="text-xs text-zinc-500">Phone</p>
                                                <p className="text-sm text-white">{selectedSupplier.phone}</p>
                                            </div>
                                        </div>
                                        <div className="flex items-center gap-3 p-3 rounded-lg bg-zinc-800/50">
                                            <Mail className="h-5 w-5 text-zinc-400" />
                                            <div>
                                                <p className="text-xs text-zinc-500">Email</p>
                                                <p className="text-sm text-white">{selectedSupplier.email}</p>
                                            </div>
                                        </div>
                                        <div className="flex items-center gap-3 p-3 rounded-lg bg-zinc-800/50">
                                            <MapPin className="h-5 w-5 text-zinc-400" />
                                            <div>
                                                <p className="text-xs text-zinc-500">Address</p>
                                                <p className="text-sm text-white">{selectedSupplier.address}</p>
                                            </div>
                                        </div>
                                        <div className="flex items-center gap-3 p-3 rounded-lg bg-zinc-800/50">
                                            <Star className="h-5 w-5 text-zinc-400" />
                                            <div>
                                                <p className="text-xs text-zinc-500">Reliability</p>
                                                <p className={`text-sm font-medium ${getReliabilityColor(selectedSupplier.reliability_score)}`}>
                                                    {(selectedSupplier.reliability_score * 100).toFixed(0)}%
                                                </p>
                                            </div>
                                        </div>
                                    </div>

                                    {/* Products Offered */}
                                    <div>
                                        <p className="text-sm font-medium text-zinc-400 mb-2">Products Offered</p>
                                        <div className="flex flex-wrap gap-2">
                                            {selectedSupplier.products_offered.map((product, i) => (
                                                <Badge key={i} variant="outline" className="border-zinc-700 text-zinc-300">
                                                    {product}
                                                </Badge>
                                            ))}
                                        </div>
                                    </div>

                                    {/* Recent Queries */}
                                    <div>
                                        <p className="text-sm font-medium text-zinc-400 mb-2">Recent Queries</p>
                                        <ScrollArea className="h-48">
                                            <Table>
                                                <TableHeader>
                                                    <TableRow className="border-zinc-800 hover:bg-transparent">
                                                        <TableHead className="text-zinc-400">Product</TableHead>
                                                        <TableHead className="text-zinc-400">Qty</TableHead>
                                                        <TableHead className="text-zinc-400">Status</TableHead>
                                                        <TableHead className="text-zinc-400">Date</TableHead>
                                                    </TableRow>
                                                </TableHeader>
                                                <TableBody>
                                                    {queries.map((query) => (
                                                        <TableRow key={query._id} className="border-zinc-800 hover:bg-zinc-800/50">
                                                            <TableCell className="text-white">{query.product_name}</TableCell>
                                                            <TableCell className="text-zinc-300">{query.quantity_needed}</TableCell>
                                                            <TableCell>
                                                                <Badge className={
                                                                    query.status === 'pending' ? 'bg-yellow-500/20 text-yellow-400' :
                                                                        query.status === 'available' ? 'bg-green-500/20 text-green-400' :
                                                                            'bg-red-500/20 text-red-400'
                                                                }>
                                                                    {query.status}
                                                                </Badge>
                                                            </TableCell>
                                                            <TableCell className="text-zinc-500">
                                                                {new Date(query.created_at).toLocaleDateString()}
                                                            </TableCell>
                                                        </TableRow>
                                                    ))}
                                                    {queries.length === 0 && (
                                                        <TableRow>
                                                            <TableCell colSpan={4} className="text-center text-zinc-500 py-4">
                                                                No queries found
                                                            </TableCell>
                                                        </TableRow>
                                                    )}
                                                </TableBody>
                                            </Table>
                                        </ScrollArea>
                                    </div>
                                </div>
                            ) : (
                                <p className="text-zinc-500 text-center py-8">Select a supplier to view details</p>
                            )}
                        </CardContent>
                    </Card>
                </div>
            </div>
        </div>
    );
}
