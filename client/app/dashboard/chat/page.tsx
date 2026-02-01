'use client';

import { useEffect, useRef, useState } from 'react';
import { Header } from '@/components/layout/header';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Badge } from '@/components/ui/badge';
import { chatAPI, Message, Conversation } from '@/lib/api';
import { Send, Bot, User, MessageSquare, Plus, Sparkles } from 'lucide-react';

export default function ChatPage() {
    const [conversations, setConversations] = useState<Conversation[]>([]);
    const [activeConversationId, setActiveConversationId] = useState<string | null>(null);
    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const [sending, setSending] = useState(false);
    const scrollRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        async function fetchConversations() {
            try {
                const data = await chatAPI.listConversations(20, 'consumer');
                setConversations(data);
            } catch (error) {
                console.error('Failed to fetch conversations:', error);
            } finally {
                setLoading(false);
            }
        }
        fetchConversations();
    }, []);

    useEffect(() => {
        if (activeConversationId) {
            const conv = conversations.find((c) => c.conversation_id === activeConversationId);
            if (conv) {
                setMessages(conv.messages || []);
            }
        }
    }, [activeConversationId, conversations]);

    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [messages]);

    const startNewConversation = () => {
        setActiveConversationId(null);
        setMessages([]);
        setInput('');
    };

    const sendMessage = async () => {
        if (!input.trim() || sending) return;

        const userMessage: Message = {
            role: 'user',
            content: input,
            timestamp: new Date().toISOString(),
        };

        setMessages((prev) => [...prev, userMessage]);
        setInput('');
        setSending(true);

        try {
            const response = await chatAPI.sendConsumerMessage(input, activeConversationId || undefined);

            const assistantMessage: Message = {
                role: 'assistant',
                content: response.response,
                timestamp: new Date().toISOString(),
            };

            setMessages((prev) => [...prev, assistantMessage]);

            if (!activeConversationId) {
                setActiveConversationId(response.conversation_id);
                const updatedConversations = await chatAPI.listConversations(20, 'consumer');
                setConversations(updatedConversations);
            }
        } catch (error) {
            console.error('Failed to send message:', error);
            const errorMessage: Message = {
                role: 'assistant',
                content: 'Sorry, I encountered an error. Please try again.',
                timestamp: new Date().toISOString(),
            };
            setMessages((prev) => [...prev, errorMessage]);
        } finally {
            setSending(false);
        }
    };

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    };

    return (
        <div className="h-screen flex flex-col overflow-hidden">
            <Header title="Consumer Chat" subtitle="AI-powered customer service" />

            <div className="p-6 flex-1 overflow-hidden">
                <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 h-full">
                    {/* Conversations List */}
                    <Card className="bg-zinc-900/50 border-zinc-800">
                        {/* WhatsApp QR Section */}
                        <div className="p-4 border-b border-zinc-800">
                            <div className="text-center">
                                <p className="text-xs text-zinc-400 mb-2">Scan to chat via WhatsApp</p>
                                <div className="bg-white rounded-lg p-2 inline-block">
                                    <img
                                        src="/qr twilio.svg"
                                        alt="WhatsApp QR Code"
                                        className="w-32 h-32"
                                    />
                                </div>
                                <p className="text-xs text-zinc-500 mt-2">Or use the chat below</p>
                            </div>
                        </div>

                        <CardHeader className="pb-2">
                            <div className="flex items-center justify-between">
                                <CardTitle className="text-lg font-medium text-white">Conversations</CardTitle>
                                <Button size="icon" variant="ghost" onClick={startNewConversation}>
                                    <Plus className="h-4 w-4" />
                                </Button>
                            </div>
                        </CardHeader>
                        <CardContent>
                            <ScrollArea className="h-[calc(100vh-24rem)]">
                                <div className="space-y-2">
                                    {conversations.map((conv) => (
                                        <div
                                            key={conv.conversation_id}
                                            onClick={() => setActiveConversationId(conv.conversation_id)}
                                            className={`p-3 w-56 rounded-lg cursor-pointer transition-all ${activeConversationId === conv.conversation_id
                                                ? 'bg-violet-500/20 border border-violet-500/30'
                                                : 'bg-zinc-800/50 hover:bg-zinc-800 border border-transparent'
                                                }`}
                                        >
                                            <div className="flex items-center gap-2 mb-1">
                                                <MessageSquare className="h-4 w-4 text-zinc-400" />
                                                <span className="text-sm font-medium text-white truncate">
                                                    {conv.conversation_id.slice(0, 15)}...
                                                </span>
                                            </div>
                                            <p className="text-xs text-zinc-500 truncate">
                                                {conv.messages?.[conv.messages.length - 1]?.content || 'No messages'}
                                            </p>
                                            <p className="text-xs text-zinc-600 mt-1">
                                                {new Date(conv.updated_at).toLocaleDateString()}
                                            </p>
                                        </div>
                                    ))}
                                    {conversations.length === 0 && (
                                        <p className="text-sm text-zinc-500 text-center py-4">No conversations yet</p>
                                    )}
                                </div>
                            </ScrollArea>
                        </CardContent>
                    </Card>

                    {/* Chat Area */}
                    <Card className="bg-zinc-900/50 border-zinc-800 lg:col-span-3 flex flex-col overflow-hidden">
                        <CardHeader className="border-b border-zinc-800 pb-4">
                            <div className="flex items-center gap-3">
                                <div className="h-10 w-10 rounded-full bg-gradient-to-br from-violet-500 to-purple-600 flex items-center justify-center">
                                    <Sparkles className="h-5 w-5 text-white" />
                                </div>
                                <div>
                                    <CardTitle className="text-lg font-medium text-white">MSME Assistant</CardTitle>
                                    <p className="text-xs text-zinc-500">Powered by AI • Available 24/7</p>
                                </div>
                                <Badge className="ml-auto bg-green-500/20 text-green-400">Online</Badge>
                            </div>
                        </CardHeader>

                        <CardContent className="flex-1 flex flex-col p-0 min-h-0">
                            {/* Messages - scrollable area */}
                            <div className="flex-1 overflow-y-auto p-4" ref={scrollRef}>
                                <div className="space-y-4">
                                    {messages.length === 0 && (
                                        <div className="text-center py-12">
                                            <Bot className="h-12 w-12 text-zinc-700 mx-auto mb-4" />
                                            <h3 className="text-lg font-medium text-zinc-400 mb-2">Start a Conversation</h3>
                                            <p className="text-sm text-zinc-500 max-w-md mx-auto">
                                                Ask about products, place orders, check stock availability,
                                                or get help with any questions about our service.
                                            </p>
                                        </div>
                                    )}

                                    {messages.map((msg, idx) => (
                                        <div
                                            key={idx}
                                            className={`flex gap-3 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                                        >
                                            {msg.role === 'assistant' && (
                                                <div className="h-8 w-8 rounded-full bg-gradient-to-br from-violet-500 to-purple-600 flex items-center justify-center shrink-0">
                                                    <Bot className="h-4 w-4 text-white" />
                                                </div>
                                            )}
                                            <div
                                                className={`max-w-[70%] rounded-2xl px-4 py-2 ${msg.role === 'user'
                                                    ? 'bg-violet-600 text-white'
                                                    : 'bg-zinc-800 text-zinc-200'
                                                    }`}
                                            >
                                                <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                                                <p className={`text-xs mt-1 ${msg.role === 'user' ? 'text-violet-300' : 'text-zinc-500'}`}>
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
                                            <div className="h-8 w-8 rounded-full bg-gradient-to-br from-violet-500 to-purple-600 flex items-center justify-center">
                                                <Bot className="h-4 w-4 text-white" />
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
                            <div className="p-4 border-t text-white border-zinc-800 bg-zinc-900/80 shrink-0">
                                <div className="flex gap-2">
                                    <Input
                                        value={input}
                                        onChange={(e) => setInput(e.target.value)}
                                        onKeyDown={handleKeyDown}
                                        placeholder="Type your message..."
                                        className="bg-zinc-800 border-zinc-700 focus:border-violet-500"
                                        disabled={sending}
                                    />
                                    <Button
                                        onClick={sendMessage}
                                        disabled={!input.trim() || sending}
                                        className="bg-violet-600 hover:bg-violet-700"
                                    >
                                        <Send className="h-4 w-4" />
                                    </Button>
                                </div>
                            </div>
                        </CardContent>
                    </Card>
                </div>
            </div>
        </div>
    );
}
