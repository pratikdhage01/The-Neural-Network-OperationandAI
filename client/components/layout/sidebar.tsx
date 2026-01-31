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
} from 'lucide-react';

const navItems = [
    { href: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { href: '/dashboard/orders', label: 'Orders', icon: ShoppingCart },
    { href: '/dashboard/inventory', label: 'Inventory', icon: Package },
    { href: '/dashboard/staff', label: 'Staff & Workload', icon: Users },
    { href: '/dashboard/suppliers', label: 'Suppliers', icon: Truck },
    { href: '/dashboard/bottlenecks', label: 'Bottlenecks', icon: AlertTriangle },
    { href: '/dashboard/chat', label: 'Consumer Chat', icon: MessageSquare },
    { href: '/dashboard/supplier-chat', label: 'Supplier Chat', icon: MessagesSquare },
];

export function Sidebar() {
    const pathname = usePathname();

    return (
        <aside className="fixed left-0 top-0 z-40 h-screen w-64 bg-gradient-to-b from-zinc-900 to-zinc-950 border-r border-zinc-800">
            {/* Logo */}
            <div className="flex h-16 items-center gap-2 border-b border-zinc-800 px-6">
                <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-violet-500 to-purple-600">
                    <Package className="h-4 w-4 text-white" />
                </div>
                <span className="text-lg font-semibold text-white">MSME Central</span>
            </div>

            {/* Navigation */}
            <nav className="flex flex-col gap-1 p-4">
                {navItems.map((item) => {
                    const isActive = pathname === item.href ||
                        (item.href !== '/dashboard' && pathname.startsWith(item.href));
                    const Icon = item.icon;

                    return (
                        <Link
                            key={item.href}
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
                })}
            </nav>

            {/* Bottom section */}
            <div className="absolute bottom-4 left-4 right-4">
                <Link
                    href="/dashboard/settings"
                    className="flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium text-zinc-400 hover:bg-zinc-800/50 hover:text-white transition-all duration-200"
                >
                    <Settings className="h-4 w-4" />
                    Settings
                </Link>
            </div>
        </aside>
    );
}
