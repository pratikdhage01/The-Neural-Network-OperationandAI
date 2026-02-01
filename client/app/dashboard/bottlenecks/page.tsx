'use client';

import { useEffect, useState } from 'react';
import { Header } from '@/components/layout/header';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { analyticsAPI, Bottleneck } from '@/lib/api';
import {
    AlertTriangle,
    Package,
    Users,
    Truck,
    ShoppingCart,
    CheckCircle2,
    RefreshCw,
    Lightbulb,
    Clock,
} from 'lucide-react';

const typeIcons: Record<string, React.ElementType> = {
    order_backlog: ShoppingCart,
    low_stock: Package,
    out_of_stock: Package,
    workload_imbalance: Users,
    supplier_delay: Truck,
};

const severityColors: Record<string, string> = {
    critical: 'bg-red-500/20 text-red-400 border-red-500/30',
    high: 'bg-orange-500/20 text-orange-400 border-orange-500/30',
    medium: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
    low: 'bg-green-500/20 text-green-400 border-green-500/30',
};

const severityBgColors: Record<string, string> = {
    critical: 'bg-red-500/10 border-red-500/30',
    high: 'bg-orange-500/10 border-orange-500/30',
    medium: 'bg-yellow-500/10 border-yellow-500/30',
    low: 'bg-green-500/10 border-green-500/30',
};

export default function BottlenecksPage() {
    const [bottlenecks, setBottlenecks] = useState<Bottleneck[]>([]);
    const [analysis, setAnalysis] = useState<string>('');
    const [loading, setLoading] = useState(true);
    const [analyzing, setAnalyzing] = useState(false);

    const fetchData = async () => {
        try {
            const data = await analyticsAPI.getBottlenecks();
            setBottlenecks(data);
        } catch (error) {
            console.error('Failed to fetch bottlenecks:', error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchData();
        const interval = setInterval(fetchData, 30000);
        return () => clearInterval(interval);
    }, []);

    const runAnalysis = async () => {
        setAnalyzing(true);
        try {
            const result = await analyticsAPI.analyzeBottlenecks();
            setAnalysis(result.analysis);
            setBottlenecks(result.bottlenecks);
        } catch (error) {
            console.error('Failed to analyze:', error);
        } finally {
            setAnalyzing(false);
        }
    };

    const resolveBottleneck = async (id: string) => {
        try {
            await analyticsAPI.resolveBottleneck(id);
            setBottlenecks(bottlenecks.filter((b) => b._id !== id));
        } catch (error) {
            console.error('Failed to resolve bottleneck:', error);
        }
    };

    const groupedBottlenecks = bottlenecks.reduce((acc, bn) => {
        const severity = bn.severity;
        if (!acc[severity]) acc[severity] = [];
        acc[severity].push(bn);
        return acc;
    }, {} as Record<string, Bottleneck[]>);

    const severityOrder = ['critical', 'high', 'medium', 'low'];

    if (loading) {
        return (
            <div className="flex h-screen items-center justify-center">
                <div className="h-8 w-8 animate-spin rounded-full border-4 border-violet-500 border-t-transparent" />
            </div>
        );
    }

    return (
        <div className="min-h-screen">
            <Header title="Bottleneck Analysis" subtitle="Identify and resolve operational bottlenecks" />

            <div className="p-6 space-y-6">
                {/* Summary Cards */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    {severityOrder.map((severity) => (
                        <Card key={severity} className={`${severityBgColors[severity]} border`}>
                            <CardContent className="p-4">
                                <div className="flex items-center justify-between">
                                    <div>
                                        <p className="text-sm text-zinc-400 capitalize">{severity}</p>
                                        <p className="text-2xl font-bold text-white">
                                            {groupedBottlenecks[severity]?.length || 0}
                                        </p>
                                    </div>
                                    <AlertTriangle className={`h-8 w-8 ${severityColors[severity].split(' ')[1]}`} />
                                </div>
                            </CardContent>
                        </Card>
                    ))}
                </div>

                {/* Analysis Button */}
                <div className="flex justify-between items-center">
                    <div>
                        <h2 className="text-lg font-semibold text-white">Active Bottlenecks</h2>
                        <p className="text-sm text-zinc-500">Real-time operational issues detection</p>
                    </div>
                    <Button
                        onClick={runAnalysis}
                        disabled={analyzing}
                        className="bg-violet-600 hover:bg-violet-700"
                    >
                        {analyzing ? (
                            <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                        ) : (
                            <RefreshCw className="h-4 w-4 mr-2" />
                        )}
                        Run Analysis
                    </Button>
                </div>

                {/* Analysis Result */}
                {analysis && (
                    <Card className="bg-violet-500/10 border-violet-500/30">
                        <CardContent className="p-4">
                            <div className="flex items-start gap-3">
                                <Lightbulb className="h-5 w-5 text-violet-400 mt-0.5" />
                                <div>
                                    <p className="text-sm font-medium text-violet-300 mb-1">AI Analysis</p>
                                    <p className="text-sm text-zinc-300">{analysis}</p>
                                </div>
                            </div>
                        </CardContent>
                    </Card>
                )}

                {/* Bottlenecks List */}
                {bottlenecks.length === 0 ? (
                    <Card className="bg-zinc-900/50 border-zinc-800">
                        <CardContent className="p-12 text-center">
                            <CheckCircle2 className="h-16 w-16 text-green-500 mx-auto mb-4" />
                            <h3 className="text-xl font-semibold text-white mb-2">All Clear!</h3>
                            <p className="text-zinc-400">No active bottlenecks detected. Operations running smoothly.</p>
                        </CardContent>
                    </Card>
                ) : (
                    <div className="space-y-6">
                        {severityOrder.map((severity) => {
                            const items = groupedBottlenecks[severity];
                            if (!items || items.length === 0) return null;

                            return (
                                <div key={severity}>
                                    <h3 className={`text-sm font-medium mb-3 capitalize ${severityColors[severity].split(' ')[1]}`}>
                                        {severity} Priority ({items.length})
                                    </h3>
                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                        {items.map((bn) => {
                                            const Icon = typeIcons[bn.type] || AlertTriangle;
                                            return (
                                                <Card key={bn._id} className={`${severityBgColors[severity]} border`}>
                                                    <CardContent className="p-4">
                                                        <div className="flex items-start gap-3">
                                                            <div className="p-2 rounded-lg bg-zinc-800/50">
                                                                <Icon className="h-5 w-5 text-zinc-300" />
                                                            </div>
                                                            <div className="flex-1">
                                                                <div className="flex items-start justify-between mb-2">
                                                                    <div>
                                                                        <p className="font-medium text-white">{bn.title}</p>
                                                                        <p className="text-xs text-zinc-500 flex items-center gap-1 mt-0.5">
                                                                            <Clock className="h-3 w-3" />
                                                                            {new Date(bn.detected_at).toLocaleString()}
                                                                        </p>
                                                                    </div>
                                                                    <Badge className={severityColors[bn.severity]}>
                                                                        {bn.severity}
                                                                    </Badge>
                                                                </div>
                                                                <p className="text-sm text-zinc-400 mb-3">{bn.description}</p>

                                                                {/* Affected Resources */}
                                                                {bn.affected_resources.length > 0 && (
                                                                    <div className="mb-3">
                                                                        <p className="text-xs text-zinc-500 mb-1">Affected Resources:</p>
                                                                        <div className="flex flex-wrap gap-1">
                                                                            {bn.affected_resources.slice(0, 3).map((res, i) => (
                                                                                <Badge key={i} variant="outline" className="text-xs text-white/50 border-zinc-700">
                                                                                    {res}
                                                                                </Badge>
                                                                            ))}
                                                                            {bn.affected_resources.length > 3 && (
                                                                                <Badge variant="outline" className="text-xs border-zinc-700">
                                                                                    +{bn.affected_resources.length - 3} more
                                                                                </Badge>
                                                                            )}
                                                                        </div>
                                                                    </div>
                                                                )}

                                                                {/* Suggested Actions */}
                                                                {bn.suggested_actions.length > 0 && (
                                                                    <div className="mb-3 p-2 rounded-lg bg-zinc-800/50">
                                                                        <p className="text-xs text-violet-400 flex items-center gap-1 mb-1">
                                                                            <Lightbulb className="h-3 w-3" />
                                                                            Suggested Action
                                                                        </p>
                                                                        <p className="text-xs text-zinc-300">{bn.suggested_actions[0]}</p>
                                                                    </div>
                                                                )}

                                                                <Button
                                                                    size="sm"
                                                                    variant="outline"
                                                                    onClick={() => resolveBottleneck(bn._id)}
                                                                    className="border-zinc-700 hover:bg-zinc-800"
                                                                >
                                                                    <CheckCircle2 className="h-3 w-3 mr-1" />
                                                                    Mark Resolved
                                                                </Button>
                                                            </div>
                                                        </div>
                                                    </CardContent>
                                                </Card>
                                            );
                                        })}
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                )}
            </div>
        </div>
    );
}
