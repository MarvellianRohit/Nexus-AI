"use client";

import React, { useState } from "react";
import { motion } from "framer-motion";
import {
    MessageSquare,
    LayoutDashboard,
    Cpu,
    Folder,
    Image as ImageIcon,
    Users,
    Settings,
    LogOut,
    ChevronLeft,
    Menu,
    Globe
} from "lucide-react";
import { cn } from "@/lib/utils";
import Link from "next/link";

interface SidebarProps {
    onCollapse?: (collapsed: boolean) => void;
}

export function Sidebar({ onCollapse }: SidebarProps) {
    const [collapsed, setCollapsed] = useState(false);

    const toggleCollapse = () => {
        setCollapsed(!collapsed);
        onCollapse?.(!collapsed);
    };

    const navItems = [
        { icon: LayoutDashboard, label: "Overview", href: "/studio" },
        { icon: Globe, label: "General Assistant", href: "/studio/general" }, // New
        { icon: MessageSquare, label: "Deep Research", href: "/studio/chat" },
        { icon: Cpu, label: "Agent Workforce", href: "/studio/agents" },
        { icon: ImageIcon, label: "Vision Projector", href: "/studio/vision" },
        { icon: Folder, label: "Knowledge", href: "/knowledge" },
        { icon: Users, label: "Team", href: "/team" },
    ];

    return (
        <motion.div
            initial={{ width: 240 }}
            animate={{ width: collapsed ? 80 : 240 }}
            transition={{ type: "spring", stiffness: 300, damping: 30 }}
            className="relative z-20 flex h-screen flex-col border-r border-white/10 bg-slate-900/50 backdrop-blur-xl"
        >
            <div className="flex h-16 items-center justify-between px-4 border-b border-white/10">
                {!collapsed && (
                    <motion.span
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        className="text-lg font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-purple-400"
                    >
                        Nexus AI
                    </motion.span>
                )}
                <button
                    onClick={toggleCollapse}
                    className="rounded-lg p-2 hover:bg-white/10 text-muted-foreground hover:text-white transition-colors"
                >
                    {collapsed ? <Menu className="h-5 w-5" /> : <ChevronLeft className="h-5 w-5" />}
                </button>
            </div>

            <nav className="flex-1 space-y-2 p-4">
                {navItems.map((item, index) => (
                    <Link key={index} href={item.href} className="block">
                        <div className={cn(
                            "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-all group hover:bg-primary/10 hover:text-primary",
                            collapsed ? "justify-center" : ""
                        )}>
                            <item.icon className="h-5 w-5 group-hover:scale-110 transition-transform" />
                            {!collapsed && (
                                <motion.span
                                    initial={{ opacity: 0 }}
                                    animate={{ opacity: 1 }}
                                >
                                    {item.label}
                                </motion.span>
                            )}
                        </div>
                    </Link>
                ))}
            </nav>

            <div className="border-t border-white/10 p-4">
                <div className={cn("flex items-center gap-3", collapsed ? "justify-center" : "")}>
                    <div className="h-9 w-9 rounded-full bg-gradient-to-tr from-purple-500 to-blue-500 flex items-center justify-center text-white font-bold text-xs ring-2 ring-white/10">
                        JD
                    </div>
                    {!collapsed && (
                        <div className="flex flex-col">
                            <span className="text-sm font-medium text-white">John Doe</span>
                            <span className="text-xs text-muted-foreground">Pro Plan</span>
                        </div>
                    )}
                </div>
            </div>
        </motion.div>
    );
}
