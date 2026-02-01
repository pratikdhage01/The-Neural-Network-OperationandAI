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
  Zap,
  Shield,
  BarChart3,
  Bot,
  CheckCircle,
} from 'lucide-react';

export default function HomePage() {
  return (
    <div className="min-h-screen bg-zinc-950 text-white overflow-hidden">
      {/* Background Pattern */}
      <div className="fixed inset-0 -z-10">
        {/* Grid Pattern */}
        <div
          className="absolute inset-0 opacity-[0.03]"
          style={{
            backgroundImage: `linear-gradient(rgba(255,255,255,0.1) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.1) 1px, transparent 1px)`,
            backgroundSize: '60px 60px',
          }}
        />
        {/* Gradient Orbs */}
        <div className="absolute top-0 left-1/4 w-[600px] h-[600px] bg-violet-600/20 rounded-full blur-[120px]" />
        <div className="absolute top-1/3 right-1/4 w-[500px] h-[500px] bg-purple-600/15 rounded-full blur-[100px]" />
        <div className="absolute bottom-0 left-1/2 w-[800px] h-[400px] bg-indigo-600/10 rounded-full blur-[120px]" />
      </div>

      {/* Navbar */}
      <nav className="relative z-50 border-b border-white/5 backdrop-blur-xl bg-zinc-950/50">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="h-9 w-9 rounded-lg bg-gradient-to-br from-violet-500 to-purple-600 flex items-center justify-center">
              <Package className="h-5 w-5 text-white" />
            </div>
            <span className="text-xl font-bold bg-gradient-to-r from-white to-zinc-400 bg-clip-text text-transparent">
              ManageX
            </span>
          </div>
          <div className="hidden md:flex items-center gap-8">
            <a href="#features" className="text-sm text-zinc-400 hover:text-white transition-colors">Features</a>
            <a href="#agents" className="text-sm text-zinc-400 hover:text-white transition-colors">AI Agents</a>
            <a href="#categories" className="text-sm text-zinc-400 hover:text-white transition-colors">Categories</a>
          </div>
          <Link href="/dashboard">
            <Button size="sm" className="bg-white text-zinc-900 hover:bg-zinc-200 font-medium">
              Open Dashboard
            </Button>
          </Link>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative pt-20 pb-32">
        {/* Floating WhatsApp QR Code */}
        <div className="hidden lg:block absolute top-8 right-8 xl:right-24 z-20">
          <div className="relative group">
            {/* Glow effect */}
            <div className="absolute inset-0 bg-gradient-to-br from-green-500/30 to-emerald-500/30 rounded-2xl blur-xl group-hover:blur-2xl transition-all duration-300" />

            {/* Card */}
            <div className="relative bg-zinc-900/90 backdrop-blur-xl border border-white/10 rounded-2xl p-4 shadow-2xl">
              <div className="flex items-center gap-2 mb-3">
                <div className="h-6 w-6 rounded-full bg-green-500 flex items-center justify-center">
                  <MessageSquare className="h-3.5 w-3.5 text-white" />
                </div>
                <span className="text-sm font-medium text-white">Try via WhatsApp</span>
              </div>

              <div className="bg-white flex justify-center items-center rounded-xl p-2 py-4 mb-3">
                <img
                  src="/qr twilio.svg"
                  alt="WhatsApp QR Code"
                  className="w-28 h-28"
                />
              </div>

              <p className="text-xs text-zinc-400 text-center">
                Scan to chat with our AI
              </p>
            </div>
          </div>
        </div>

        <div className="max-w-7xl mx-auto px-6">
          <div className="flex flex-col items-center text-center">
            {/* Badge */}
            <div className="inline-flex items-center gap-2 bg-gradient-to-r from-violet-500/10 to-purple-500/10 border border-violet-500/20 rounded-full px-4 py-1.5 mb-8">
              <Sparkles className="h-4 w-4 text-violet-400" />
              <span className="text-sm text-violet-300 font-medium">AI-Powered Operations Platform</span>
            </div>

            {/* Heading */}
            <h1 className="text-5xl md:text-7xl lg:text-8xl font-bold tracking-tight mb-6">
              <span className="bg-gradient-to-b from-white via-white to-zinc-500 bg-clip-text text-transparent">
                Automate Your
              </span>
              <br />
              <span className="bg-gradient-to-r from-violet-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
                Business Operations
              </span>
            </h1>

            {/* Subtitle */}
            <p className="text-lg md:text-xl text-zinc-400 max-w-2xl mb-10 leading-relaxed">
              Decision-centric AI agents that handle orders, inventory, suppliers, and customer service.
              Built for MSMEs who want to scale without the complexity.
            </p>

            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row gap-4">
              <Link href="/dashboard">
                <Button size="lg" className="bg-gradient-to-r from-violet-600 to-purple-600 hover:from-violet-500 hover:to-purple-500 text-white px-8 h-12 text-base font-medium shadow-lg shadow-violet-600/25">
                  <LayoutDashboard className="h-5 w-5 mr-2" />
                  Get Started Free
                  <ArrowRight className="h-4 w-4 ml-2" />
                </Button>
              </Link>
              <Button size="lg" variant="outline" className="border-white/10 bg-white/5 hover:bg-white/10 text-white px-8 h-12 text-base font-medium backdrop-blur-sm">
                <MessageSquare className="h-5 w-5 mr-2" />
                Watch Demo
              </Button>
            </div>

            {/* Stats */}
            <div className="flex items-center gap-12 mt-16 pt-8 border-t border-white/5">
              <div className="text-center">
                <div className="text-3xl font-bold text-white">6+</div>
                <div className="text-sm text-zinc-500">AI Agents</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-white">24/7</div>
                <div className="text-sm text-zinc-500">Automation</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-white">100%</div>
                <div className="text-sm text-zinc-500">Customizable</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="relative py-24">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-16">
            <div className="inline-flex items-center gap-2 bg-emerald-500/10 border border-emerald-500/20 rounded-full px-3 py-1 mb-4">
              <Zap className="h-3.5 w-3.5 text-emerald-400" />
              <span className="text-xs text-emerald-400 font-medium uppercase tracking-wider">Features</span>
            </div>
            <h2 className="text-3xl md:text-4xl font-bold mb-4">Intelligent Operations at Scale</h2>
            <p className="text-zinc-400 max-w-xl mx-auto">
              Our AI agents work together seamlessly to automate and optimize every aspect of your MSME operations.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <FeatureCard
              icon={MessageSquare}
              title="AI Customer Service"
              description="Natural language processing for customer inquiries, product recommendations, and instant order placement."
              gradient="from-violet-500/10 to-purple-500/10"
              iconColor="text-violet-400"
            />
            <FeatureCard
              icon={ShoppingCart}
              title="Smart Order Management"
              description="Automated order processing, real-time tracking, and intelligent task assignment to staff."
              gradient="from-blue-500/10 to-cyan-500/10"
              iconColor="text-blue-400"
            />
            <FeatureCard
              icon={Package}
              title="Inventory Intelligence"
              description="Real-time stock tracking with automated low-stock alerts and predictive reordering."
              gradient="from-emerald-500/10 to-green-500/10"
              iconColor="text-emerald-400"
            />
            <FeatureCard
              icon={Truck}
              title="Supplier Coordination"
              description="AI-powered multi-supplier communication for pricing comparisons and availability checks."
              gradient="from-amber-500/10 to-yellow-500/10"
              iconColor="text-amber-400"
            />
            <FeatureCard
              icon={Users}
              title="Workload Balancing"
              description="Smart task distribution across team members based on capacity, skills, and priorities."
              gradient="from-pink-500/10 to-rose-500/10"
              iconColor="text-pink-400"
            />
            <FeatureCard
              icon={AlertTriangle}
              title="Bottleneck Detection"
              description="Proactive identification of operational issues with AI-suggested resolutions."
              gradient="from-red-500/10 to-orange-500/10"
              iconColor="text-red-400"
            />
          </div>
        </div>
      </section>

      {/* AI Agents Section */}
      <section id="agents" className="relative py-24">
        <div className="absolute inset-0 bg-gradient-to-b from-transparent via-violet-600/5 to-transparent" />
        <div className="max-w-7xl mx-auto px-6 relative">
          <div className="grid lg:grid-cols-2 gap-16 items-center">
            <div>
              <div className="inline-flex items-center gap-2 bg-violet-500/10 border border-violet-500/20 rounded-full px-3 py-1 mb-4">
                <Bot className="h-3.5 w-3.5 text-violet-400" />
                <span className="text-xs text-violet-400 font-medium uppercase tracking-wider">AI Agents</span>
              </div>
              <h2 className="text-3xl md:text-4xl font-bold mb-6">
                Autonomous Agents That
                <br />
                <span className="text-violet-400">Actually Work</span>
              </h2>
              <p className="text-zinc-400 mb-8 leading-relaxed">
                Our AI agents don't just respond — they make decisions, take actions, and learn from every interaction.
                From handling customer queries to coordinating with suppliers, they work 24/7 so you don't have to.
              </p>
              <div className="space-y-4">
                <AgentFeature text="Consumer agent handles orders via WhatsApp & web chat" />
                <AgentFeature text="Supplier agent negotiates pricing and checks availability" />
                <AgentFeature text="Lead qualification agent automates sales outreach" />
                <AgentFeature text="Operations agent detects and resolves bottlenecks" />
              </div>
            </div>
            <div className="relative">
              <div className="absolute inset-0 bg-gradient-to-br from-violet-600/20 to-purple-600/20 rounded-3xl blur-2xl" />
              <Card className="relative bg-zinc-900/80 border-white/10 backdrop-blur-xl rounded-2xl overflow-hidden">
                <CardContent className="p-8">
                  <div className="flex items-center gap-3 mb-6">
                    <div className="h-10 w-10 rounded-full bg-gradient-to-br from-violet-500 to-purple-600 flex items-center justify-center">
                      <Bot className="h-5 w-5 text-white" />
                    </div>
                    <div>
                      <div className="font-medium text-white">ManageX AI</div>
                      <div className="text-xs text-zinc-500">Active • Processing</div>
                    </div>
                  </div>
                  <div className="space-y-4">
                    <ChatBubble role="user" message="I need 30 pairs of silver anklets" />
                    <ChatBubble role="assistant" message="I found Silver Anklet Pairs in stock! 🎉 Would you like me to place an order for 30 pairs at ₹899 each?" />
                    <ChatBubble role="user" message="Yes, please confirm" />
                    <ChatBubble role="assistant" message="Order ORD-20260201-1DCBCF created! ✅ Contacting suppliers for stock confirmation..." />
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </section>

      {/* Categories Section */}
      <section id="categories" className="relative py-24">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-16">
            <div className="inline-flex items-center gap-2 bg-amber-500/10 border border-amber-500/20 rounded-full px-3 py-1 mb-4">
              <Package className="h-3.5 w-3.5 text-amber-400" />
              <span className="text-xs text-amber-400 font-medium uppercase tracking-wider">Categories</span>
            </div>
            <h2 className="text-3xl md:text-4xl font-bold mb-4">Multi-Category Inventory</h2>
            <p className="text-zinc-400 max-w-xl mx-auto">
              Managing diverse product lines with intelligent categorization and tracking.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <CategoryCard
              emoji="💎"
              title="Jewelry"
              description="Gold, silver, and fashion jewelry including necklaces, earrings, rings, and anklets."
              gradient="from-amber-500/20 via-yellow-500/10 to-transparent"
            />
            <CategoryCard
              emoji="🍳"
              title="Kitchen Appliances"
              description="Mixers, toasters, air fryers, blenders, and essential kitchen equipment."
              gradient="from-blue-500/20 via-cyan-500/10 to-transparent"
            />
            <CategoryCard
              emoji="💄"
              title="Makeup & Cosmetics"
              description="Lipsticks, foundations, eyeshadows, and complete beauty collections."
              gradient="from-pink-500/20 via-rose-500/10 to-transparent"
            />
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-white/5 py-12">
        <div className="max-w-7xl mx-auto px-6">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <div className="h-8 w-8 rounded-lg bg-gradient-to-br from-violet-500 to-purple-600 flex items-center justify-center">
                <Package className="h-4 w-4 text-white" />
              </div>
              <span className="font-semibold text-white">ManageX</span>
            </div>
            <p className="text-sm text-zinc-500">© 2026 ManageX. AI-Powered MSME Operations Platform.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}

// Feature Card Component
function FeatureCard({
  icon: Icon,
  title,
  description,
  gradient,
  iconColor
}: {
  icon: React.ElementType;
  title: string;
  description: string;
  gradient: string;
  iconColor: string;
}) {
  return (
    <Card className={`group bg-gradient-to-br ${gradient} border-white/5 hover:border-white/10 transition-all duration-300 hover:-translate-y-1`}>
      <CardContent className="p-6">
        <div className={`h-10 w-10 rounded-lg bg-white/5 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform`}>
          <Icon className={`h-5 w-5 ${iconColor}`} />
        </div>
        <h3 className="text-lg font-semibold text-white mb-2">{title}</h3>
        <p className="text-sm text-zinc-400 leading-relaxed">{description}</p>
      </CardContent>
    </Card>
  );
}

// Category Card Component
function CategoryCard({
  emoji,
  title,
  description,
  gradient
}: {
  emoji: string;
  title: string;
  description: string;
  gradient: string;
}) {
  return (
    <Card className={`group bg-gradient-to-b ${gradient} border-white/5 hover:border-white/10 transition-all duration-300 overflow-hidden`}>
      <CardContent className="p-8 text-center">
        <div className="text-4xl mb-4">{emoji}</div>
        <h3 className="text-xl font-semibold text-white mb-3">{title}</h3>
        <p className="text-sm text-zinc-400">{description}</p>
      </CardContent>
    </Card>
  );
}

// Agent Feature Item
function AgentFeature({ text }: { text: string }) {
  return (
    <div className="flex items-start gap-3">
      <CheckCircle className="h-5 w-5 text-emerald-400 mt-0.5 flex-shrink-0" />
      <span className="text-zinc-300">{text}</span>
    </div>
  );
}

// Chat Bubble Component
function ChatBubble({ role, message }: { role: 'user' | 'assistant'; message: string }) {
  return (
    <div className={`flex ${role === 'user' ? 'justify-end' : 'justify-start'}`}>
      <div className={`max-w-[80%] rounded-2xl px-4 py-2.5 text-sm ${role === 'user'
        ? 'bg-violet-600 text-white rounded-br-none'
        : 'bg-zinc-800 text-zinc-100 rounded-bl-none'
        }`}>
        {message}
      </div>
    </div>
  );
}
