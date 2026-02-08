'use client';

import React from 'react';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { MessageSquare, Bot, ImageIcon, BrainCircuit, ArrowRight, Globe } from 'lucide-react';
import { cn } from '@/lib/utils';

export default function StudioHome() {
    const tools = [
        {
            title: "General Assistant",
            description: "A Google-like AI search engine for answering any question.",
            icon: Globe, // Use MessageSquare or Globe if imported
            href: "/studio/general",
            color: "text-emerald-400",
            bg: "bg-emerald-400/10",
        },
        {
            title: "Deep Research",
            description: "Chat with your codebase and research files using RAG.",
            icon: MessageSquare,
            href: "/studio/chat",
            color: "text-blue-400",
            bg: "bg-blue-400/10",
        },
        {
            title: "Agent Workforce",
            description: "Deploy autonomous agents to build features and write tests.",
            icon: Bot,
            href: "/studio/agents",
            color: "text-purple-400",
            bg: "bg-purple-400/10",
        },
        {
            title: "Vision Projector",
            description: "Turn screenshots into Next.js code instantly.",
            icon: ImageIcon,
            href: "/studio/vision",
            color: "text-pink-400",
            bg: "bg-pink-400/10",
        }
    ];

    return (
        <div className="h-full w-full bg-background p-8 overflow-y-auto">
            <div className="max-w-5xl mx-auto space-y-12">

                {/* Header */}
                <div className="text-center space-y-4">
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 text-primary text-sm font-medium"
                    >
                        <BrainCircuit className="w-4 h-4" />
                        <span>Nexus-AI Studio</span>
                    </motion.div>
                    <motion.h1
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.1 }}
                        className="text-4xl md:text-5xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-white/60"
                    >
                        How would you like to build today?
                    </motion.h1>
                    <motion.p
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.2 }}
                        className="text-muted-foreground text-lg max-w-2xl mx-auto"
                    >
                        Select a neural pathway to begin. You can switch between modes at any time from the sidebar.
                    </motion.p>
                </div>

                {/* Cards */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    {tools.map((tool, i) => (
                        <Link key={tool.title} href={tool.href}>
                            <motion.div
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ delay: 0.3 + (i * 0.1) }}
                                className="group relative h-full p-6 rounded-2xl border border-white/10 bg-white/5 hover:bg-white/10 transition-all hover:scale-[1.02] cursor-pointer overflow-hidden"
                            >
                                <div className={cn("inline-flex p-3 rounded-xl mb-4", tool.bg, tool.color)}>
                                    <tool.icon className="w-8 h-8" />
                                </div>

                                <h3 className="text-xl font-bold mb-2 group-hover:text-primary transition-colors">{tool.title}</h3>
                                <p className="text-muted-foreground mb-6 line-clamp-3">{tool.description}</p>

                                <div className="flex items-center text-sm font-medium text-white/50 group-hover:text-primary transition-colors">
                                    <span>Launch</span>
                                    <ArrowRight className="w-4 h-4 ml-2 group-hover:translate-x-1 transition-transform" />
                                </div>

                                {/* Hover Glow */}
                                <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/5 to-transparent -translate-x-full group-hover:animate-shimmer" />
                            </motion.div>
                        </Link>
                    ))}
                </div>

            </div>
        </div>
    );
}
