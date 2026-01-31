'use client';

import { useEffect, useState } from 'react';
import { Header } from '@/components/layout/header';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Badge } from '@/components/ui/badge';
import { Textarea } from '@/components/ui/textarea';
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from '@/components/ui/select';
import { suppliersAPI, chatAPI, Supplier, Conversation, Message } from '@/lib/api';
import { Send, Bot, User, Truck, MessageSquare, Phone, Mail } from 'lucide-react';

export default function SupplierChatPage() {
    const [suppliers, setSuppliers] = useState<Supplier[]>([]);
    const [selectedSupplier, setSelectedSupplier] = useState<Supplier | null>(null);
    const [conversations, setConversations] = useState<Conversation[]>([]);
    const [activeConversationId, setActiveConversationId] = useState<string | null>(null);
    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState('');
    const [sending, setSending] = useState(false);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        async function fetchSuppliers() {
            try {
                const data = await suppliersAPI.list();
                setSuppliers(data);
                if (data.length > 0) {
                    setSelectedSupplier(data[0]);
                }
            } catch (error) {
                console.error('Failed to fetch suppliers:', error);
            } finally {
                setLoading(false);
            }
        }
        fetchSuppliers();
    }, []);

    useEffect(() => {
        async function fetchConversations() {
            if (selectedSupplier) {
                try {
                    const data = await suppliersAPI.getChatHistory(selectedSupplier._id);
                    setConversations(data);
                    if (data.length > 0) {
                        setActiveConversationId(data[0].conversation_id);
                        setMessages(data[0].messages || []);
                    } else {
                        setActiveConversationId(null);
                        setMessages([]);
                    }
                } catch (error) {
                    console.error('Failed to fetch conversations:', error);
                }
            }
        }
        fetchConversations();
    }, [selectedSupplier]);

    const sendMessage = async () => {
        if (!input.trim() || !selectedSupplier || sending) return;

        const userMessage: Message = {
            role: 'user',
            content: input,
            timestamp: new Date().toISOString(),
        };

        setMessages((prev) => [...prev, userMessage]);
        setInput('');
        setSending(true);

        try {
            const response = await chatAPI.sendSupplierMessage(
                selectedSupplier._id,
                input,
                activeConversationId || undefined
            );

            const assistantMessage: Message = {
                role: 'assistant',
                content: response.response,
                timestamp: new Date().toISOString(),
            };

            setMessages((prev) => [...prev, assistantMessage]);

            if (!activeConversationId) {
                setActiveConversationId(response.conversation_id);
            }
        } catch (error) {
            console.error('Failed to send message:', error);
        } finally {
            setSending(false);
        }
    };

    if (loading) {
        return (
            <div className="flex h-screen items-center justify-center">
                <div className="h-8 w-8 animate-spin rounded-full border-4 border-violet-500 border-t-transparent" />
            </div>
        );
    }

    return (
        <div className="h-screen flex flex-col overflow-hidden">
            <Header title="Supplier Communication" subtitle="AI-assisted supplier chat" />

            <div className="p-6 flex-1 overflow-hidden">
                <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 h-full">
                    {/* Supplier List */}
                    <Card className="bg-zinc-900/50 border-zinc-800">
                        <CardHeader className="pb-2">
                            <CardTitle className="text-lg font-medium text-white">Suppliers</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <ScrollArea className="h-[calc(100vh-14rem)]">
                                <div className="space-y-2">
                                    {suppliers.map((supplier) => (
                                        <div
                                            key={supplier._id}
                                            onClick={() => setSelectedSupplier(supplier)}
                                            className={`p-3 w-56 rounded-lg cursor-pointer transition-all ${selectedSupplier?._id === supplier._id
                                                ? 'bg-violet-500/20 border border-violet-500/30'
                                                : 'bg-zinc-800/50 hover:bg-zinc-800 border border-transparent'
                                                }`}
                                        >
                                            <div className="flex items-center gap-2 mb-1">
                                                <Truck className="h-4 w-4 text-zinc-400" />
                                                <span className="text-sm font-medium text-white truncate">
                                                    {supplier.name}
                                                </span>
                                            </div>
                                            <p className="text-xs text-zinc-500">{supplier.contact_person}</p>
                                            <div className="flex flex-wrap gap-1 mt-2">
                                                {supplier.categories.slice(0, 2).map((cat) => (
                                                    <Badge key={cat} variant="outline" className="text-xs border-zinc-700">
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

                    {/* Chat Area */}
                    <Card className="bg-zinc-900/50 border-zinc-800 lg:col-span-3 flex flex-col overflow-hidden">
                        {selectedSupplier ? (
                            <>
                                <CardHeader className="border-b border-zinc-800 pb-4">
                                    <div className="flex items-center justify-between">
                                        <div className="flex items-center gap-3">
                                            <div className="h-10 w-10 rounded-full bg-gradient-to-br from-emerald-500 to-teal-600 flex items-center justify-center">
                                                <Truck className="h-5 w-5 text-white" />
                                            </div>
                                            <div>
                                                <CardTitle className="text-lg font-medium text-white">
                                                    {selectedSupplier.name}
                                                </CardTitle>
                                                <p className="text-xs text-zinc-500">{selectedSupplier.contact_person}</p>
                                            </div>
                                        </div>
                                        <div className="flex items-center gap-4 text-xs text-zinc-400">
                                            <span className="flex items-center gap-1">
                                                <Phone className="h-3 w-3" />
                                                {selectedSupplier.phone}
                                            </span>
                                            <span className="flex items-center gap-1">
                                                <Mail className="h-3 w-3" />
                                                {selectedSupplier.email}
                                            </span>
                                        </div>
                                    </div>
                                </CardHeader>

                                <CardContent className="flex-1 flex flex-col p-0 min-h-0">
                                    {/* Messages - scrollable area */}
                                    <div className="flex-1 overflow-y-auto p-4">
                                        <div className="space-y-4">
                                            {messages.length === 0 && (
                                                <div className="text-center py-12">
                                                    <MessageSquare className="h-12 w-12 text-zinc-700 mx-auto mb-4" />
                                                    <h3 className="text-lg font-medium text-zinc-400 mb-2">
                                                        Start Supplier Communication
                                                    </h3>
                                                    <p className="text-sm text-zinc-500 max-w-md mx-auto">
                                                        Query product availability, negotiate prices, or discuss
                                                        delivery schedules with this supplier.
                                                    </p>
                                                </div>
                                            )}

                                            {messages.map((msg, idx) => (
                                                <div
                                                    key={idx}
                                                    className={`flex gap-3 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                                                >
                                                    {msg.role === 'assistant' && (
                                                        <div className="h-8 w-8 rounded-full bg-gradient-to-br from-emerald-500 to-teal-600 flex items-center justify-center shrink-0">
                                                            <Truck className="h-4 w-4 text-white" />
                                                        </div>
                                                    )}
                                                    <div
                                                        className={`max-w-[70%] rounded-2xl px-4 py-2 ${msg.role === 'user'
                                                            ? 'bg-emerald-600 text-white'
                                                            : 'bg-zinc-800 text-zinc-200'
                                                            }`}
                                                    >
                                                        <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                                                        <p className={`text-xs mt-1 ${msg.role === 'user' ? 'text-emerald-300' : 'text-zinc-500'}`}>
                                                            {new Date(msg.timestamp).toLocaleTimeString()}
                                                        </p>
                                                    </div>
                                                    {msg.role === 'user' && (
                                                        <div className="h-8 w-8 rounded-full bg-zinc-700 flex items-center justify-center shrink-0">
                                                            <User className="h-4 w-4 text-zinc-300" />
                                                        </div>
                                                    )}
                                                </div>
                                            ))}

                                            {sending && (
                                                <div className="flex gap-3">
                                                    <div className="h-8 w-8 rounded-full bg-gradient-to-br from-emerald-500 to-teal-600 flex items-center justify-center">
                                                        <Truck className="h-4 w-4 text-white" />
                                                    </div>
                                                    <div className="bg-zinc-800 rounded-2xl px-4 py-3">
                                                        <div className="flex gap-1">
                                                            <div className="h-2 w-2 rounded-full bg-zinc-500 animate-bounce" style={{ animationDelay: '0ms' }} />
                                                            <div className="h-2 w-2 rounded-full bg-zinc-500 animate-bounce" style={{ animationDelay: '150ms' }} />
                                                            <div className="h-2 w-2 rounded-full bg-zinc-500 animate-bounce" style={{ animationDelay: '300ms' }} />
                                                        </div>
                                                    </div>
                                                </div>
                                            )}
                                        </div>
                                    </div>

                                    {/* Input - pinned at bottom */}
                                    <div className="p-4 border-t border-zinc-800 text-white bg-zinc-900/80 shrink-0">
                                        <div className="flex gap-2">
                                            <Textarea
                                                value={input}
                                                onChange={(e) => setInput(e.target.value)}
                                                placeholder={`Message ${selectedSupplier.name}...`}
                                                className="bg-zinc-800 border-zinc-700 focus:border-emerald-500 resize-none min-h-[2.5rem] max-h-24"
                                                rows={1}
                                                disabled={sending}
                                                onKeyDown={(e) => {
                                                    if (e.key === 'Enter' && !e.shiftKey) {
                                                        e.preventDefault();
                                                        sendMessage();
                                                    }
                                                }}
                                            />
                                            <Button
                                                onClick={sendMessage}
                                                disabled={!input.trim() || sending}
                                                className="bg-emerald-600 hover:bg-emerald-700"
                                            >
                                                <Send className="h-4 w-4" />
                                            </Button>
                                        </div>
                                    </div>
                                </CardContent>
                            </>
                        ) : (
                            <CardContent className="flex-1 flex items-center justify-center">
                                <p className="text-zinc-500">Select a supplier to start chatting</p>
                            </CardContent>
                        )}
                    </Card>
                </div>
            </div>
        </div>
    );
}
