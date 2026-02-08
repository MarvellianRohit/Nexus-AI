'use client';

import React, { useState, useRef, useEffect } from 'react';
import { Send, Sparkles, User, Bot, Globe, Search } from 'lucide-react';
import { cn } from '@/lib/utils';
import { motion, AnimatePresence } from 'framer-motion';

interface Message {
    role: 'user' | 'assistant';
    content: string;
    isThinking?: boolean;
}

export function GeneralChat() {
    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const scrollRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [messages]);

    const handleSend = async () => {
        if (!input.trim() || isLoading) return;

        const userMsg = input;
        setInput('');
        setMessages(prev => [...prev, { role: 'user', content: userMsg }]);
        setIsLoading(true);

        // Add placeholder for AI response
        setMessages(prev => [...prev, { role: 'assistant', content: '', isThinking: true }]);

        try {
            const res = await fetch('http://localhost:8000/api/general/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: userMsg })
            });

            if (!res.body) throw new Error("No response body");

            const reader = res.body.getReader();
            const decoder = new TextDecoder();
            let accumulatedResponse = "";

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                const chunk = decoder.decode(value);
                accumulatedResponse += chunk;

                // Streaming update
                setMessages(prev => {
                    const newMsgs = [...prev];
                    const lastMsg = newMsgs[newMsgs.length - 1];
                    if (lastMsg.role === 'assistant') {
                        lastMsg.content = accumulatedResponse;
                        lastMsg.isThinking = false;
                    }
                    return newMsgs;
                });
            }

        } catch (e) {
            setMessages(prev => {
                const newMsgs = [...prev];
                const lastMsg = newMsgs[newMsgs.length - 1];
                lastMsg.content = "Error: Failed to connect to General Search Service.";
                lastMsg.isThinking = false;
                return newMsgs;
            });
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="flex flex-col h-full bg-background relative overflow-hidden">
            {/* Background Effects */}
            <div className="absolute top-0 right-0 w-full h-96 bg-emerald-500/5 rounded-full blur-3xl -translate-y-1/2 pointer-events-none" />

            {/* Header */}
            <div className="p-6 border-b border-white/5 flex items-center justify-between z-10 bg-background/50 backdrop-blur-sm">
                <div className="flex items-center gap-3">
                    <div className="p-2 bg-emerald-500/10 rounded-lg">
                        <Globe className="w-6 h-6 text-emerald-400" />
                    </div>
                    <div>
                        <h2 className="text-xl font-bold">General Assistant</h2>
                        <p className="text-xs text-muted-foreground">Gemini 2.5 Pro + Flash Fallback</p>
                    </div>
                </div>
            </div>

            {/* Chat Area */}
            <div className="flex-1 overflow-y-auto p-4 space-y-6" ref={scrollRef}>
                {messages.length === 0 && (
                    <div className="h-full flex flex-col items-center justify-center opacity-40 space-y-4">
                        <Search className="w-16 h-16" />
                        <p className="text-xl font-medium">Search the web or ask general questions</p>
                    </div>
                )}

                <AnimatePresence>
                    {messages.map((msg, i) => (
                        <motion.div
                            key={i}
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            className={cn(
                                "flex gap-4 max-w-4xl mx-auto w-full",
                                msg.role === 'user' ? "flex-row-reverse" : "flex-row"
                            )}
                        >
                            <div className={cn(
                                "w-10 h-10 rounded-full flex items-center justify-center shrink-0",
                                msg.role === 'user' ? "bg-white/10" : "bg-emerald-500/20"
                            )}>
                                {msg.role === 'user' ? <User className="w-5 h-5" /> : <Bot className="w-5 h-5 text-emerald-400" />}
                            </div>

                            <div className={cn(
                                "rounded-2xl p-4 max-w-[80%]",
                                msg.role === 'user' ? "bg-white/10" : "bg-transparent border border-white/5"
                            )}>
                                <div className="prose prose-invert prose-sm whitespace-pre-wrap">
                                    {msg.content}
                                    {msg.isThinking && (
                                        <span className="inline-block w-2 h-4 ml-1 bg-emerald-400/50 animate-pulse" />
                                    )}
                                </div>
                            </div>
                        </motion.div>
                    ))}
                </AnimatePresence>
            </div>

            {/* Input Area */}
            <div className="p-6 z-10 bg-background/50 backdrop-blur-sm">
                <div className="max-w-4xl mx-auto relative group">
                    <div className="absolute inset-0 bg-gradient-to-r from-emerald-500/20 to-teal-500/20 rounded-2xl blur-lg transition-opacity opacity-0 group-hover:opacity-100" />
                    <div className="relative bg-black/40 border border-white/10 rounded-xl flex items-center p-2 focus-within:border-emerald-500/50 transition-colors">
                        <input
                            type="text"
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                            placeholder="Ask absolutely anything..."
                            className="flex-1 bg-transparent border-none outline-none px-4 py-3 placeholder:text-muted-foreground/50 text-lg"
                        />
                        <button
                            onClick={handleSend}
                            disabled={isLoading || !input.trim()}
                            className="p-3 bg-emerald-600 hover:bg-emerald-500 rounded-lg text-white transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            {isLoading ? <Sparkles className="w-5 h-5 animate-spin" /> : <Send className="w-5 h-5" />}
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}
