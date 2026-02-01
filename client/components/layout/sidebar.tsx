'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';
import {
    LayoutDashboard,
    ShoppingCart,
    Package,
    Users,
    Truck,
    AlertTriangle,
    MessageSquare,
    MessagesSquare,
    Settings,
    Target,
    FlaskConical,
    Info,
} from 'lucide-react';

const mainNavItems = [
    { href: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { href: '/dashboard/orders', label: 'Orders', icon: ShoppingCart },
    { href: '/dashboard/inventory', label: 'Inventory', icon: Package },
    { href: '/dashboard/staff', label: 'Staff & Workload', icon: Users },
    { href: '/dashboard/suppliers', label: 'Suppliers', icon: Truck },
    { href: '/dashboard/bottlenecks', label: 'Bottlenecks', icon: AlertTriangle },
];

const simulationItems = [
    { href: '/dashboard/chat', label: 'Consumer Chat', icon: MessageSquare },
    { href: '/dashboard/supplier-chat', label: 'Supplier Chat', icon: MessagesSquare },
    { href: '/dashboard/leads', label: 'Leads', icon: Target },
];

export function Sidebar() {
    const pathname = usePathname();

    const NavLink = ({ item }: { item: typeof mainNavItems[0] }) => {
        const isActive = pathname === item.href ||
            (item.href !== '/dashboard' && pathname.startsWith(item.href));
        const Icon = item.icon;

        return (
            <Link
                href={item.href}
                className={cn(
                    'flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-all duration-200',
                    isActive
                        ? 'bg-gradient-to-r from-violet-500/20 to-purple-500/20 text-white border border-violet-500/30'
                        : 'text-zinc-400 hover:bg-zinc-800/50 hover:text-white'
                )}
            >
                <Icon className={cn('h-4 w-4', isActive && 'text-violet-400')} />
                {item.label}
            </Link>
        );
    };

    return (
        <aside className="fixed left-0 top-0 z-40 h-screen w-64 bg-gradient-to-b from-zinc-900 to-zinc-950 border-r border-zinc-800 overflow-y-auto">
            {/* Logo */}
            <div className="flex h-16 items-center gap-2 border-b border-zinc-800 px-6">
                <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-violet-500 to-purple-600">
                    <Package className="h-4 w-4 text-white" />
                </div>
                <span className="text-lg font-semibold text-white">ManageX</span>
            </div>

            {/* Main Navigation */}
            <nav className="flex flex-col gap-1 p-4">
                {mainNavItems.map((item) => (
                    <NavLink key={item.href} item={item} />
                ))}
            </nav>

            {/* Simulation Section */}
            <div className="px-4 pb-4">
                <div className="border-t border-zinc-800 pt-4">
                    <div className="flex items-center gap-2 px-3 mb-2">
                        <FlaskConical className="h-4 w-4 text-purple-400" />
                        <span className="text-xs font-semibold text-purple-400 uppercase tracking-wider">
                            Simulation
                        </span>
                    </div>

                    <div className="flex flex-col gap-1">
                        {simulationItems.map((item) => (
                            <NavLink key={item.href} item={item} />
                        ))}
                    </div>

                    {/* Info Note */}
                    <div className="mt-3 p-2 bg-zinc-800/50 rounded-lg border border-zinc-700/50 h-60 overflow-y-auto">
                        <div className="flex items-start gap-2">
                            <Info className="h-3.5 w-3.5 text-zinc-500 mt-0.5 shrink-0" />
                            <p className="text-xs text-zinc-500 leading-relaxed">
                                Chat endpoints simulating real-world agent interactions
                            </p>
                        </div>
                        <div className="flex flex-col gap-1 text-white/50 text-xs mt-2">
                            <p>
                                • Consumer chat - It simulaes how a consumer would interact with the agent to get information about the products and services.
                            </p>
                            <p>
                                • Supplier chat - It simulaes how a supplier would interact with the agent to process the goods requirements
                            </p>
                            <p>
                                • Leads - It simulaes how a our agent would cold dm users and find if they are a potential customer or not.
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </aside>
    );
}
