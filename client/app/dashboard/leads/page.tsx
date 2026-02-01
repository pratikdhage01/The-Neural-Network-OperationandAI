'use client';

import { useState, useEffect, useRef } from 'react';
import { Header } from '@/components/layout/header';
import {
    Card,
    CardContent,
    CardDescription,
    CardHeader,
    CardTitle,
} from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import {
    Users,
    MessageSquare,
    Send,
    Upload,
    Play,
    SkipForward,
    CheckCircle,
    XCircle,
    RefreshCw,
    Target,
} from 'lucide-react';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface Lead {
    client_id?: string;
    lead_id?: string;
    name: string;
    email: string;
    phone: string;
    company: string;
    industry: string;
    role?: string;
}

interface Message {
    role: 'agent' | 'user' | 'system' | 'potential';
    content: string;
}

interface Status {
    leads_loaded: number;
    current_index: number;
    context_set: boolean;
    potential_leads: number;
}

export default function LeadsPage() {
    const [status, setStatus] = useState<Status>({
        leads_loaded: 0,
        current_index: 0,
        context_set: false,
        potential_leads: 0,
    });
    const [salesContext, setSalesContext] = useState('');
    const [currentLead, setCurrentLead] = useState<Lead | null>(null);
    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const [conversationActive, setConversationActive] = useState(false);
    const [showQuickReplies, setShowQuickReplies] = useState(false);
    const [allLeads, setAllLeads] = useState<Lead[]>([]);
    const [finished, setFinished] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    useEffect(() => {
        fetchStatus();
        fetchAllLeads();
    }, []);

    const fetchStatus = async () => {
        try {
            const res = await fetch(`${API_BASE}/api/leads/status`);
            const data = await res.json();
            setStatus(data);
        } catch (error) {
            console.error('Error fetching status:', error);
        }
    };

    const fetchAllLeads = async () => {
        try {
            const res = await fetch(`${API_BASE}/api/leads`);
            const data = await res.json();
            // Ensure data is always an array
            setAllLeads(Array.isArray(data) ? data : []);
        } catch (error) {
            console.error('Error fetching leads:', error);
            setAllLeads([]);
        }
    };

    const setContext = async () => {
        if (!salesContext.trim()) return;
        setLoading(true);
        try {
            await fetch(`${API_BASE}/api/leads/context`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ context: salesContext }),
            });
            fetchStatus();
        } catch (error) {
            console.error('Error setting context:', error);
        }
        setLoading(false);
    };

    const loadDemo = async () => {
        setLoading(true);
        try {
            await fetch(`${API_BASE}/api/leads/load-demo`, { method: 'POST' });
            fetchStatus();
            fetchAllLeads();
        } catch (error) {
            console.error('Error loading demo:', error);
        }
        setLoading(false);
    };

    const startConversation = async () => {
        setLoading(true);
        setFinished(false);
        try {
            const res = await fetch(`${API_BASE}/api/leads/start`, {
                method: 'POST',
            });
            const data = await res.json();

            if (data.finished) {
                setFinished(true);
                setMessages([
                    {
                        role: 'system',
                        content: `All leads processed! Found ${data.total_potential_leads} potential leads.`,
                    },
                ]);
                setConversationActive(false);
            } else if (data.success) {
                setCurrentLead(data.lead);
                setMessages([{ role: 'agent', content: data.message }]);
                setConversationActive(true);
                setShowQuickReplies(true);
            }
            fetchStatus();
        } catch (error) {
            console.error('Error starting conversation:', error);
        }
        setLoading(false);
    };

    const sendMessage = async (message: string) => {
        if (!message.trim() || !currentLead) return;

        const leadId = currentLead.client_id || currentLead.lead_id;
        setMessages((prev) => [...prev, { role: 'user', content: message }]);
        setInput('');
        setShowQuickReplies(false);
        setLoading(true);

        try {
            const res = await fetch(`${API_BASE}/api/leads/${leadId}/message`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message }),
            });
            const data = await res.json();

            if (data.stopped) {
                setMessages((prev) => [
                    ...prev,
                    { role: 'agent', content: data.message },
                    { role: 'system', content: 'Lead declined. Moving to next.' },
                ]);
                setConversationActive(false);
            } else {
                setMessages((prev) => [
                    ...prev,
                    { role: 'agent', content: data.message },
                ]);

                // Show alert if lead was qualified
                if (data.alert) {
                    setMessages((prev) => [
                        ...prev,
                        { role: data.is_potential ? 'potential' : 'system', content: data.alert },
                    ]);
                }

                if (data.all_done) {
                    setFinished(true);
                    setMessages((prev) => [
                        ...prev,
                        {
                            role: 'system',
                            content: `All done! Found ${data.total_potential_leads} potential leads.`,
                        },
                    ]);
                    setConversationActive(false);
                } else if (data.conversation_ended) {
                    setConversationActive(false);
                }
            }
            fetchStatus();
            fetchAllLeads();
        } catch (error) {
            console.error('Error sending message:', error);
        }
        setLoading(false);
    };

    const skipLead = async () => {
        setLoading(true);
        try {
            const res = await fetch(`${API_BASE}/api/leads/skip`, {
                method: 'POST',
            });
            const data = await res.json();
            setMessages((prev) => [
                ...prev,
                { role: 'system', content: 'Lead skipped.' },
            ]);
            setConversationActive(false);
            if (!data.next_lead) {
                setFinished(true);
            }
            fetchStatus();
        } catch (error) {
            console.error('Error skipping lead:', error);
        }
        setLoading(false);
    };



    return (
        <div className="min-h-screen">
            <Header title="Lead Communications" subtitle="AI-powered sales outreach simulation" />

            <div className="p-6 space-y-6">
                {/* Status Bar */}
                <div className="grid grid-cols-4 gap-4">
                    <Card className="bg-zinc-900/50 border-zinc-800">
                        <CardContent className="p-4 text-center">
                            <Users className="h-6 w-6 text-blue-500 mx-auto mb-2" />
                            <div className="text-2xl font-bold text-white">
                                {status.leads_loaded}
                            </div>
                            <div className="text-xs text-zinc-500">Leads Loaded</div>
                        </CardContent>
                    </Card>
                    <Card className="bg-zinc-900/50 border-zinc-800">
                        <CardContent className="p-4 text-center">
                            <MessageSquare className="h-6 w-6 text-purple-500 mx-auto mb-2" />
                            <div className="text-2xl font-bold text-white">
                                {status.leads_loaded > 0
                                    ? `${status.current_index + 1}/${status.leads_loaded}`
                                    : '-'}
                            </div>
                            <div className="text-xs text-zinc-500">Current Lead</div>
                        </CardContent>
                    </Card>
                    <Card className="bg-zinc-900/50 border-zinc-800">
                        <CardContent className="p-4 text-center">
                            <Target className="h-6 w-6 text-green-500 mx-auto mb-2" />
                            <div className="text-2xl font-bold text-white">
                                {status.potential_leads}
                            </div>
                            <div className="text-xs text-zinc-500">Potential Leads</div>
                        </CardContent>
                    </Card>
                    <Card className="bg-zinc-900/50 border-zinc-800">
                        <CardContent className="p-4 text-center">
                            {status.context_set ? (
                                <CheckCircle className="h-6 w-6 text-green-500 mx-auto mb-2" />
                            ) : (
                                <XCircle className="h-6 w-6 text-red-500 mx-auto mb-2" />
                            )}
                            <div className="text-2xl font-bold text-white">
                                {status.context_set ? '✓' : '✗'}
                            </div>
                            <div className="text-xs text-zinc-500">Context Set</div>
                        </CardContent>
                    </Card>
                </div>

                <div className="grid grid-cols-2 gap-6">
                    {/* Left Column - Setup */}
                    <div className="space-y-4">
                        {/* Sales Context */}
                        <Card className="bg-zinc-900/50 border-zinc-800">
                            <CardHeader>
                                <CardTitle className="text-white">
                                    Step 1: Set Sales Context
                                </CardTitle>
                                <CardDescription>
                                    Describe what you're selling to guide the AI agent
                                </CardDescription>
                            </CardHeader>
                            <CardContent className="space-y-4">
                                <Textarea
                                    placeholder="Example: We are selling an AI-powered CRM solution that helps businesses automate their sales process..."
                                    value={salesContext}
                                    onChange={(e) => setSalesContext(e.target.value)}
                                    className="min-h-[100px] bg-zinc-800 border-zinc-700 text-white"
                                />
                                <Button
                                    onClick={setContext}
                                    disabled={loading || !salesContext.trim()}
                                    className="bg-purple-600 hover:bg-purple-700"
                                >
                                    Set Context
                                </Button>
                            </CardContent>
                        </Card>

                        {/* Load Leads */}
                        <Card className="bg-zinc-900/50 border-zinc-800">
                            <CardHeader>
                                <CardTitle className="text-white">
                                    Step 2: Load Leads
                                </CardTitle>
                                <CardDescription>
                                    Load demo leads or upload your own
                                </CardDescription>
                            </CardHeader>
                            <CardContent className="flex gap-4">
                                <Button
                                    onClick={loadDemo}
                                    disabled={loading}
                                    className="bg-green-600 hover:bg-green-700"
                                >
                                    <Upload className="h-4 w-4 mr-2" />
                                    {allLeads.length > 0 ? 'Reload Demo (5 Leads)' : 'Load Demo (5 Leads)'}
                                </Button>
                            </CardContent>
                        </Card>

                        {/* Potential Leads List */}
                        <Card className="bg-zinc-900/50 border-zinc-800">
                            <CardHeader>
                                <CardTitle className="text-white flex items-center gap-2">
                                    <Target className="h-5 w-5 text-green-500" />
                                    All Leads
                                </CardTitle>
                            </CardHeader>
                            <CardContent>
                                {allLeads.length === 0 ? (
                                    <p className="text-zinc-500 text-sm">
                                        No leads loaded yet
                                    </p>
                                ) : (
                                    <div className="space-y-2 max-h-[300px] overflow-y-auto">
                                        {allLeads.map((lead, i) => (
                                            <div
                                                key={i}
                                                className="p-3 bg-zinc-800 rounded-lg"
                                            >
                                                <div className="flex items-center justify-between">
                                                    <div className="font-medium text-white">
                                                        {lead.name}
                                                    </div>
                                                    <Badge
                                                        variant={
                                                            (lead as any).is_potential
                                                                ? 'default'
                                                                : 'secondary'
                                                        }
                                                        className={
                                                            (lead as any).is_potential
                                                                ? 'bg-green-600'
                                                                : ''
                                                        }
                                                    >
                                                        {(lead as any).status || 'pending'}
                                                    </Badge>
                                                </div>
                                                <div className="text-sm text-zinc-400">
                                                    {lead.company} • {lead.industry}
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                )}
                            </CardContent>
                        </Card>
                    </div>

                    {/* Right Column - Conversation */}
                    <Card className="bg-zinc-900/50 border-zinc-800">
                        <CardHeader>
                            <CardTitle className="text-white">
                                Step 3: Conversations
                            </CardTitle>
                            <CardDescription>
                                Simulate sales conversations with leads
                            </CardDescription>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            {/* Current Lead Info */}
                            {currentLead && (
                                <div className="p-4 bg-purple-600/20 rounded-lg border border-purple-500/30">
                                    <h4 className="font-semibold text-white mb-2">
                                        Current Lead
                                    </h4>
                                    <div className="text-sm text-zinc-300 space-y-1">
                                        <p>
                                            <strong>Name:</strong> {currentLead.name}
                                        </p>
                                        <p>
                                            <strong>Company:</strong> {currentLead.company}
                                        </p>
                                        <p>
                                            <strong>Industry:</strong> {currentLead.industry}
                                        </p>
                                        <p>
                                            <strong>Role:</strong> {currentLead.role || 'N/A'}
                                        </p>
                                    </div>
                                </div>
                            )}

                            {/* Chat Messages */}
                            <div className="h-[300px] bg-zinc-800 rounded-lg p-4 overflow-y-auto">
                                {messages.length === 0 ? (
                                    <p className="text-zinc-500 text-center">
                                        Start a conversation to begin
                                    </p>
                                ) : (
                                    <div className="space-y-3">
                                        {messages.map((msg, i) => (
                                            <div
                                                key={i}
                                                className={`p-3 rounded-lg max-w-[85%] ${msg.role === 'agent'
                                                    ? 'bg-purple-600 text-white'
                                                    : msg.role === 'user'
                                                        ? 'bg-zinc-700 text-white ml-auto'
                                                        : msg.role === 'potential'
                                                            ? 'bg-green-600 text-white text-center mx-auto'
                                                            : 'bg-yellow-600 text-black text-center mx-auto'
                                                    }`}
                                            >
                                                {msg.content}
                                            </div>
                                        ))}
                                        <div ref={messagesEndRef} />
                                    </div>
                                )}
                            </div>

                            {/* Quick Replies */}
                            {showQuickReplies && (
                                <div className="flex gap-2">
                                    <Button
                                        onClick={() => sendMessage('CONTINUE')}
                                        className="bg-green-600 hover:bg-green-700"
                                    >
                                        <CheckCircle className="h-4 w-4 mr-2" />
                                        CONTINUE
                                    </Button>
                                    <Button
                                        onClick={() => sendMessage('STOP')}
                                        variant="destructive"
                                    >
                                        <XCircle className="h-4 w-4 mr-2" />
                                        STOP
                                    </Button>
                                </div>
                            )}

                            {/* Input */}
                            {conversationActive && !showQuickReplies && (
                                <div className="flex gap-2">
                                    <Input
                                        value={input}
                                        onChange={(e) => setInput(e.target.value)}
                                        onKeyPress={(e) =>
                                            e.key === 'Enter' && sendMessage(input)
                                        }
                                        placeholder="Type your response..."
                                        className="bg-zinc-800 border-zinc-700 text-white"
                                    />
                                    <Button
                                        onClick={() => sendMessage(input)}
                                        disabled={loading}
                                        className="bg-purple-600 hover:bg-purple-700"
                                    >
                                        <Send className="h-4 w-4" />
                                    </Button>
                                    <Button
                                        onClick={skipLead}
                                        variant="outline"
                                        className="border-zinc-700"
                                    >
                                        <SkipForward className="h-4 w-4" />
                                    </Button>
                                </div>
                            )}

                            {/* Action Buttons */}
                            <div className="flex gap-2">
                                {!conversationActive && !finished && (
                                    <Button
                                        onClick={startConversation}
                                        disabled={
                                            loading ||
                                            !status.context_set ||
                                            status.leads_loaded === 0
                                        }
                                        className="bg-purple-600 hover:bg-purple-700"
                                    >
                                        <Play className="h-4 w-4 mr-2" />
                                        {status.current_index > 0
                                            ? 'Next Lead'
                                            : 'Start Conversations'}
                                    </Button>
                                )}
                            </div>
                        </CardContent>
                    </Card>
                </div>
            </div>
        </div>
    );
}
