'use client';

import { Bell, Search } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';

interface HeaderProps {
    title: string;
    subtitle?: string;
}

export function Header({ title, subtitle }: HeaderProps) {
    return (
        <header className="sticky top-0 z-30 flex h-16 items-center justify-between border-b border-zinc-800 bg-zinc-950/80 backdrop-blur-sm px-6">
            <div>
                <h1 className="text-xl font-semibold text-white">{title}</h1>
                {subtitle && (
                    <p className="text-sm text-zinc-400">{subtitle}</p>
                )}
            </div>

            <div className="flex items-center gap-4">
                {/* Notifications */}
                <button className="relative rounded-lg p-2 text-zinc-400 hover:bg-zinc-800 hover:text-white transition-colors">
                    <Bell className="h-5 w-5" />
                    <span className="absolute right-1 top-1 h-2 w-2 rounded-full bg-violet-500" />
                </button>

                {/* Avatar */}
                <Avatar className="h-8 w-8">
                    <AvatarFallback className="bg-gradient-to-br from-violet-500 to-purple-600 text-white text-sm">
                        MS
                    </AvatarFallback>
                </Avatar>
            </div>
        </header>
    );
}
