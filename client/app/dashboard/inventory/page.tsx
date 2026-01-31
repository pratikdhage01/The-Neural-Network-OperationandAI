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
import { ScrollArea } from '@/components/ui/scroll-area';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { inventoryAPI, Product, InventoryStats } from '@/lib/api';
import { Package, AlertTriangle, TrendingDown, Gem, UtensilsCrossed, Sparkles } from 'lucide-react';

const categoryIcons: Record<string, React.ElementType> = {
    jewelry: Gem,
    kitchen_appliances: UtensilsCrossed,
    makeup: Sparkles,
};

const categoryColors: Record<string, string> = {
    jewelry: 'bg-amber-500/20 text-amber-400 border-amber-500/30',
    kitchen_appliances: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
    makeup: 'bg-pink-500/20 text-pink-400 border-pink-500/30',
};

export default function InventoryPage() {
    const [products, setProducts] = useState<Product[]>([]);
    const [stats, setStats] = useState<InventoryStats | null>(null);
    const [lowStock, setLowStock] = useState<Product[]>([]);
    const [activeTab, setActiveTab] = useState('all');
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        async function fetchData() {
            try {
                const [productsData, statsData, lowStockData] = await Promise.all([
                    inventoryAPI.list(activeTab === 'all' ? undefined : activeTab),
                    inventoryAPI.getStats(),
                    inventoryAPI.getLowStock(),
                ]);
                setProducts(productsData);
                setStats(statsData);
                setLowStock(lowStockData);
            } catch (error) {
                console.error('Failed to fetch inventory:', error);
            } finally {
                setLoading(false);
            }
        }
        fetchData();
    }, [activeTab]);

    const getStockStatus = (product: Product) => {
        if (product.quantity === 0) return { label: 'Out of Stock', color: 'bg-red-500/20 text-red-400' };
        if (product.quantity <= product.low_stock_threshold) return { label: 'Low Stock', color: 'bg-orange-500/20 text-orange-400' };
        return { label: 'In Stock', color: 'bg-green-500/20 text-green-400' };
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
            <Header title="Inventory" subtitle="Manage product stock and availability" />

            <div className="p-6 space-y-6">
                {/* Low Stock Alert */}
                {lowStock.length > 0 && (
                    <Alert className="bg-orange-500/10 border-orange-500/30">
                        <AlertTriangle className="h-4 w-4 text-orange-400" />
                        <AlertDescription className="text-orange-300">
                            {lowStock.length} products are low or out of stock. Consider restocking soon.
                        </AlertDescription>
                    </Alert>
                )}

                {/* Stats */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <Card className="bg-zinc-900/50 border-zinc-800">
                        <CardContent className="p-4">
                            <div className="flex items-center gap-3">
                                <Package className="h-8 w-8 text-violet-400" />
                                <div>
                                    <p className="text-sm text-zinc-400">Total Products</p>
                                    <p className="text-2xl font-bold text-white">{stats?.total_products || 0}</p>
                                </div>
                            </div>
                        </CardContent>
                    </Card>
                    <Card className="bg-zinc-900/50 border-zinc-800">
                        <CardContent className="p-4">
                            <div className="flex items-center gap-3">
                                <TrendingDown className="h-8 w-8 text-orange-400" />
                                <div>
                                    <p className="text-sm text-zinc-400">Low Stock</p>
                                    <p className="text-2xl font-bold text-orange-400">{stats?.low_stock || 0}</p>
                                </div>
                            </div>
                        </CardContent>
                    </Card>
                    <Card className="bg-zinc-900/50 border-zinc-800">
                        <CardContent className="p-4">
                            <div className="flex items-center gap-3">
                                <AlertTriangle className="h-8 w-8 text-red-400" />
                                <div>
                                    <p className="text-sm text-zinc-400">Out of Stock</p>
                                    <p className="text-2xl font-bold text-red-400">{stats?.out_of_stock || 0}</p>
                                </div>
                            </div>
                        </CardContent>
                    </Card>
                    <Card className="bg-zinc-900/50 border-zinc-800">
                        <CardContent className="p-4">
                            <div className="flex items-center gap-3">
                                <Sparkles className="h-8 w-8 text-emerald-400" />
                                <div>
                                    <p className="text-sm text-zinc-400">Total Value</p>
                                    <p className="text-2xl font-bold text-white">₹{(stats?.total_value || 0).toLocaleString()}</p>
                                </div>
                            </div>
                        </CardContent>
                    </Card>
                </div>

                {/* Products Table */}
                <Card className="bg-zinc-900/50 border-zinc-800">
                    <CardHeader>
                        <Tabs value={activeTab} onValueChange={setActiveTab}>
                            <TabsList className="bg-zinc-800">
                                <TabsTrigger value="all">All Products</TabsTrigger>
                                <TabsTrigger value="jewelry">
                                    <Gem className="h-4 w-4 mr-1" />
                                    Jewelry
                                </TabsTrigger>
                                <TabsTrigger value="kitchen_appliances">
                                    <UtensilsCrossed className="h-4 w-4 mr-1" />
                                    Kitchen
                                </TabsTrigger>
                                <TabsTrigger value="makeup">
                                    <Sparkles className="h-4 w-4 mr-1" />
                                    Makeup
                                </TabsTrigger>
                            </TabsList>
                        </Tabs>
                    </CardHeader>
                    <CardContent>
                        <ScrollArea className="h-[500px]">
                            <Table>
                                <TableHeader>
                                    <TableRow className="border-zinc-800 hover:bg-transparent">
                                        <TableHead className="text-zinc-400">Product</TableHead>
                                        <TableHead className="text-zinc-400">Category</TableHead>
                                        <TableHead className="text-zinc-400">Price</TableHead>
                                        <TableHead className="text-zinc-400">Quantity</TableHead>
                                        <TableHead className="text-zinc-400">Status</TableHead>
                                    </TableRow>
                                </TableHeader>
                                <TableBody>
                                    {products.map((product) => {
                                        const status = getStockStatus(product);
                                        const CategoryIcon = categoryIcons[product.category] || Package;
                                        return (
                                            <TableRow key={product._id} className="border-zinc-800 hover:bg-zinc-800/50">
                                                <TableCell>
                                                    <div>
                                                        <p className="font-medium text-white">{product.name}</p>
                                                        <p className="text-xs text-zinc-500 truncate max-w-xs">{product.description}</p>
                                                    </div>
                                                </TableCell>
                                                <TableCell>
                                                    <Badge className={categoryColors[product.category]}>
                                                        <CategoryIcon className="h-3 w-3 mr-1" />
                                                        {product.category.replace('_', ' ')}
                                                    </Badge>
                                                </TableCell>
                                                <TableCell className="text-white font-medium">
                                                    ₹{product.price.toLocaleString()}
                                                </TableCell>
                                                <TableCell>
                                                    <span className={product.quantity <= product.low_stock_threshold ? 'text-orange-400' : 'text-white'}>
                                                        {product.quantity}
                                                    </span>
                                                    <span className="text-zinc-500 text-xs ml-1">
                                                        (min: {product.low_stock_threshold})
                                                    </span>
                                                </TableCell>
                                                <TableCell>
                                                    <Badge className={status.color}>
                                                        {status.label}
                                                    </Badge>
                                                </TableCell>
                                            </TableRow>
                                        );
                                    })}
                                    {products.length === 0 && (
                                        <TableRow>
                                            <TableCell colSpan={5} className="text-center text-zinc-500 py-8">
                                                No products found
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
