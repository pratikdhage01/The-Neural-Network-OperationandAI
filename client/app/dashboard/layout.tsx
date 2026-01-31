import { Sidebar } from '@/components/layout/sidebar';

export default function DashboardLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <div className="min-h-screen bg-zinc-950">
            <Sidebar />
            <main className="ml-64">
                {children}
            </main>
        </div>
    );
}
