import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import {
  ShoppingCart,
  Package,
  Users,
  Truck,
  AlertTriangle,
  MessageSquare,
  Sparkles,
  ArrowRight,
  LayoutDashboard,
} from 'lucide-react';

export default function HomePage() {
  return (
    <div className="min-h-screen bg-zinc-950 text-white">
      {/* Hero Section */}
      <div className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-violet-600/20 via-purple-600/10 to-transparent" />
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[800px] bg-violet-500/10 rounded-full blur-3xl" />

        <div className="relative max-w-6xl mx-auto px-6 py-24">
          <div className="flex flex-col items-center text-center">
            <div className="flex items-center gap-2 bg-violet-500/20 rounded-full px-4 py-1.5 mb-6">
              <Sparkles className="h-4 w-4 text-violet-400" />
              <span className="text-sm text-violet-300">AI-Powered Operations</span>
            </div>

            <h1 className="text-5xl md:text-7xl font-bold mb-6 bg-gradient-to-r from-white via-violet-200 to-purple-300 bg-clip-text text-transparent">
              MSME Central
            </h1>

            <p className="text-xl text-zinc-400 max-w-2xl mb-8">
              Decision-centric AI agent system for MSME operations.
              Intelligent order management, inventory control, supplier coordination,
              and bottleneck detection — all powered by advanced AI.
            </p>

            <div className="flex gap-4">
              <Link href="/dashboard">
                <Button size="lg" className="bg-violet-600 hover:bg-violet-700">
                  <LayoutDashboard className="h-5 w-5 mr-2" />
                  Open Dashboard
                  <ArrowRight className="h-4 w-4 ml-2" />
                </Button>
              </Link>
              <Link href="/dashboard/chat">
                <Button size="lg" variant="outline" className="border-zinc-700 hover:bg-zinc-800">
                  <MessageSquare className="h-5 w-5 mr-2" />
                  Try AI Chat
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="max-w-6xl mx-auto px-6 py-24">
        <div className="text-center mb-16">
          <h2 className="text-3xl font-bold mb-4">Intelligent Operations Management</h2>
          <p className="text-zinc-400 max-w-xl mx-auto">
            Our AI agents work together to automate and optimize every aspect of your MSME operations.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <FeatureCard
            icon={MessageSquare}
            title="AI Customer Service"
            description="Natural language processing for customer inquiries, product recommendations, and order placement."
            color="violet"
          />
          <FeatureCard
            icon={ShoppingCart}
            title="Smart Order Management"
            description="Automated order processing, tracking, and assignment to staff based on workload."
            color="blue"
          />
          <FeatureCard
            icon={Package}
            title="Inventory Intelligence"
            description="Real-time stock tracking with automated low-stock alerts and supplier notifications."
            color="emerald"
          />
          <FeatureCard
            icon={Truck}
            title="Supplier Coordination"
            description="AI-powered communication with multiple suppliers for pricing and availability queries."
            color="amber"
          />
          <FeatureCard
            icon={Users}
            title="Workload Balancing"
            description="Smart task distribution across team members based on capacity and skills."
            color="pink"
          />
          <FeatureCard
            icon={AlertTriangle}
            title="Bottleneck Detection"
            description="Proactive identification of operational issues with AI-suggested resolutions."
            color="red"
          />
        </div>
      </div>

      {/* Categories Section */}
      <div className="bg-zinc-900/50 py-24">
        <div className="max-w-6xl mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold mb-4">Product Categories</h2>
            <p className="text-zinc-400">Managing diverse inventory across multiple product lines</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <CategoryCard
              title="Jewelry"
              description="Gold, silver, and fashion jewelry including necklaces, earrings, and rings."
              gradient="from-amber-500/20 to-yellow-500/20"
              borderColor="border-amber-500/30"
            />
            <CategoryCard
              title="Kitchen Appliances"
              description="Mixers, toasters, air fryers, and other essential kitchen equipment."
              gradient="from-blue-500/20 to-cyan-500/20"
              borderColor="border-blue-500/30"
            />
            <CategoryCard
              title="Makeup & Cosmetics"
              description="Lipsticks, foundations, eyeshadows, and complete beauty collections."
              gradient="from-pink-500/20 to-rose-500/20"
              borderColor="border-pink-500/30"
            />
          </div>
        </div>
      </div>

      {/* CTA Section */}
      <div className="max-w-6xl mx-auto px-6 py-24">
        <Card className="bg-gradient-to-br from-violet-600/20 to-purple-600/20 border-violet-500/30">
          <CardContent className="p-12 text-center">
            <h2 className="text-3xl font-bold mb-4">Ready to Transform Your Operations?</h2>
            <p className="text-zinc-400 max-w-xl mx-auto mb-8">
              Experience the power of AI-driven MSME management. Access your dashboard now.
            </p>
            <Link href="/dashboard">
              <Button size="lg" className="bg-violet-600 hover:bg-violet-700">
                Get Started
                <ArrowRight className="h-4 w-4 ml-2" />
              </Button>
            </Link>
          </CardContent>
        </Card>
      </div>

      {/* Footer */}
      <footer className="border-t border-zinc-800 py-8">
        <div className="max-w-6xl mx-auto px-6 text-center text-zinc-500 text-sm">
          <p>© 2026 MSME Central. AI-Powered Operations Platform.</p>
        </div>
      </footer>
    </div>
  );
}

interface FeatureCardProps {
  icon: React.ElementType;
  title: string;
  description: string;
  color: 'violet' | 'blue' | 'emerald' | 'amber' | 'pink' | 'red';
}

function FeatureCard({ icon: Icon, title, description, color }: FeatureCardProps) {
  const colorClasses = {
    violet: 'from-violet-500/20 to-purple-500/20 border-violet-500/30',
    blue: 'from-blue-500/20 to-cyan-500/20 border-blue-500/30',
    emerald: 'from-emerald-500/20 to-green-500/20 border-emerald-500/30',
    amber: 'from-amber-500/20 to-yellow-500/20 border-amber-500/30',
    pink: 'from-pink-500/20 to-rose-500/20 border-pink-500/30',
    red: 'from-red-500/20 to-orange-500/20 border-red-500/30',
  };

  const iconColors = {
    violet: 'text-violet-400',
    blue: 'text-blue-400',
    emerald: 'text-emerald-400',
    amber: 'text-amber-400',
    pink: 'text-pink-400',
    red: 'text-red-400',
  };

  return (
    <Card className={`bg-gradient-to-br ${colorClasses[color]} border hover:scale-105 transition-transform`}>
      <CardContent className="p-6">
        <Icon className={`h-10 w-10 ${iconColors[color]} mb-4`} />
        <h3 className="text-lg font-semibold text-white mb-2">{title}</h3>
        <p className="text-sm text-zinc-400">{description}</p>
      </CardContent>
    </Card>
  );
}

interface CategoryCardProps {
  title: string;
  description: string;
  gradient: string;
  borderColor: string;
}

function CategoryCard({ title, description, gradient, borderColor }: CategoryCardProps) {
  return (
    <Card className={`bg-gradient-to-br ${gradient} ${borderColor} border overflow-hidden`}>
      <CardContent className="p-8 text-center">
        <h3 className="text-xl font-semibold text-white mb-3">{title}</h3>
        <p className="text-sm text-zinc-400">{description}</p>
      </CardContent>
    </Card>
  );
}
