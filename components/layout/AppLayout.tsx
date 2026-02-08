"use client";

import React from "react";
import { Sidebar } from "./Sidebar";
import { CommandPalette } from "@/components/command/CommandPalette";

import { BioOverlay } from "@/components/bio/BioOverlay";
import { LivingBorder } from "@/components/bio/LivingBorder";

// Assuming SIDEBAR_ITEMS is defined in this file or needs to be defined here
// based on the provided instruction and code edit snippet.
// Note: The icons (LayoutGrid, Search, Bot, Eye, Mic, Settings) would need to be imported
// from a library like 'lucide-react' or similar for this to be fully functional.
// For the purpose of this edit, we'll assume they are available or will be imported.
import { LayoutGrid, Search, Bot, Eye, Mic, Settings } from 'lucide-react'; // Added for the new SIDEBAR_ITEMS definition

const SIDEBAR_ITEMS = [
    { icon: LayoutGrid, label: 'Overview', href: '/studio' },
    { icon: Search, label: 'Deep Research', href: '/studio/chat' }, // New
    { icon: Bot, label: 'Agent Workforce', href: '/studio/agents' },
    { icon: Eye, label: 'Vision Projector', href: '/studio/vision' },
    { icon: Mic, label: 'Voice Mode', href: '/studio/voice' },
    { icon: Settings, label: 'Settings', href: '/studio/settings' },
];

export function AppLayout({ children }: { children: React.ReactNode }) {
    return (
        <div className="flex h-screen w-full overflow-hidden bg-background text-foreground relative">
            {/* Bio-Digital Interface Layer */}
            <BioOverlay />
            <LivingBorder />

            {/* Sidebar */}
            <Sidebar />

            {/* Main Content Area */}
            <main className="relative flex-1 flex flex-col min-w-0 overflow-hidden">
                {children}

                {/* Cmd+K Palette (Always available) */}
                <CommandPalette />
            </main>
        </div>
    );
}
