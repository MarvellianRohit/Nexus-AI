'use client';

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
    Users, Terminal, ShieldCheck, PlayCircle, CheckCircle2,
    AlertCircle, FileCode, Search, RefreshCw
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button'; // Assuming button exists, or use standard html button
import { Input } from '@/components/ui/input'; // Assuming input exists

// Mock types for now, will connect to backend stream later
type AgentStatus = 'idle' | 'working' | 'success' | 'failure';

interface AgentCardProps {
    name: string;
    role: string;
    status: AgentStatus;
    logs: string[];
    icon: React.ReactNode;
}

function AgentCard({ name, role, status, logs, icon }: AgentCardProps) {
    return (
        <div className={cn(
            "rounded-xl border p-4 transition-all duration-300",
            status === 'working' ? "border-primary/50 bg-primary/5 shadow-lg shadow-primary/10" :
                status === 'success' ? "border-green-500/30 bg-green-500/5" :
                    "border-white/10 bg-black/20"
        )}>
            <div className="flex items-center gap-3 mb-3">
                <div className={cn(
                    "p-2 rounded-lg",
                    status === 'working' ? "animate-pulse bg-primary/20 text-primary" :
                        status === 'success' ? "bg-green-500/20 text-green-400" :
                            "bg-white/5 text-muted-foreground"
                )}>
                    {icon}
                </div>
                <div>
                    <h3 className="font-semibold text-sm text-foreground">{name}</h3>
                    <p className="text-xs text-muted-foreground">{role}</p>
                </div>
                {status === 'working' && <RefreshCw className="w-3 h-3 text-primary animate-spin ml-auto" />}
                {status === 'success' && <CheckCircle2 className="w-4 h-4 text-green-400 ml-auto" />}
            </div>

            <div className="bg-black/40 rounded-lg p-3 font-mono text-[10px] h-24 overflow-y-auto text-muted-foreground">
                {logs.length === 0 ? <span className="opacity-50">Waiting for tasks...</span> : (
                    <div className="flex flex-col gap-1">
                        {logs.map((log, i) => (
                            <div key={i} className="border-l-2 border-primary/20 pl-2">
                                <span className="opacity-70">{log}</span>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
}

export function AgentManager() {
    const [featureRequest, setFeatureRequest] = useState('');
    const [isProcessing, setIsProcessing] = useState(false);

    // Agent States
    const [devLogs, setDevLogs] = useState<string[]>([]);
    const [testLogs, setTestLogs] = useState<string[]>([]);
    const [auditLogs, setAuditLogs] = useState<string[]>([]);

    const [devStatus, setDevStatus] = useState<AgentStatus>('idle');
    const [testStatus, setTestStatus] = useState<AgentStatus>('idle');
    const [auditStatus, setAuditStatus] = useState<AgentStatus>('idle');
    const [socialStatus, setSocialStatus] = useState<AgentStatus>('idle');
    const [socialLogs, setSocialLogs] = useState<string[]>([]);
    const [socialResults, setSocialResults] = useState<any>(null);

    const handleRunAgents = async () => {
        // ... existing handleRunAgents logic ...
    };

    const handleSocialAgent = async () => {
        if (!featureRequest) return;
        setIsProcessing(true);
        setSocialStatus('working');
        setSocialLogs(prev => [...prev, "Spawning Multi-Modal Social Agent..."]);
        setSocialLogs(prev => [...prev, "Engaging 40-core GPU (SDXL, Whisper, Llama-3)..."]);

        try {
            const res = await fetch('http://localhost:8080/api/agents/social', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ feature_desc: featureRequest })
            });
            const data = await res.json();
            if (data.status === 'success') {
                setSocialStatus('success');
                setSocialLogs(prev => [...prev, "Campaign Generated Successfully!"]);
                setSocialResults(data.results);
            } else {
                setSocialStatus('failure');
                setSocialLogs(prev => [...prev, `Error: ${data.message}`]);
            }
        } catch (e) {
            setSocialStatus('failure');
            setSocialLogs(prev => [...prev, "Network Error. Check Backend."]);
        } finally {
            setIsProcessing(false);
        }
    };

    return (
        <div className="w-full max-w-4xl mx-auto p-6 space-y-8">
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-2xl font-bold flex items-center gap-2">
                        <Users className="w-6 h-6 text-primary" />
                        Agent Command Center
                    </h2>
                    <p className="text-muted-foreground text-sm">Orchestrate your AI workforce.</p>
                </div>
            </div>

            <div className="flex gap-2">
                <input
                    value={featureRequest}
                    onChange={(e) => setFeatureRequest(e.target.value)}
                    placeholder="Describe a feature (e.g., 'A login form with email validation')"
                    className="flex-1 bg-black/20 border border-white/10 rounded-lg px-4 py-2 text-sm focus:outline-none focus:border-primary/50 transition-all"
                />
                <button
                    onClick={handleRunAgents}
                    disabled={isProcessing || !featureRequest}
                    className="bg-primary hover:bg-primary/90 text-white rounded-lg px-6 py-2 text-sm font-medium transition-all disabled:opacity-50"
                >
                    {isProcessing ? "Agents Working..." : "Deploy Agents"}
                </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <AgentCard
                    name="Dev-01"
                    role="Senior Next.js Developer"
                    status={devStatus}
                    logs={devLogs}
                    icon={<FileCode className="w-5 h-5" />}
                />
                <AgentCard
                    name="QA-Bot"
                    role="Playwright Tester"
                    status={testStatus}
                    logs={testLogs}
                    icon={<Search className="w-5 h-5" />}
                />
                <AgentCard
                    name="Sec-Ops"
                    role="Security Auditor"
                    status={auditStatus}
                    logs={auditLogs}
                    icon={<ShieldCheck className="w-5 h-5" />}
                />
            </div>

            {/* Social Media Agent Section */}
            <div className="pt-8 border-t border-white/10">
                <div className="flex items-center justify-between mb-4">
                    <div>
                        <h3 className="text-xl font-bold flex items-center gap-2">
                            <Terminal className="w-5 h-5 text-purple-500" />
                            Autonomous Social Media Agent
                        </h3>
                        <p className="text-muted-foreground text-xs">Full multi-modal GPU campaign (Llama-3, SDXL, Whisper).</p>
                    </div>
                    <Button
                        onClick={handleSocialAgent}
                        disabled={isProcessing || !featureRequest}
                        variant="outline"
                        className="border-purple-500/30 text-purple-400 hover:bg-purple-500/10"
                    >
                        {socialStatus === 'working' ? "Generating..." : "Generate Campaign"}
                    </Button>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                    <div className="md:col-span-1">
                        <AgentCard
                            name="Social-X"
                            role="Multi-Modal Evangelist"
                            status={socialStatus}
                            logs={socialLogs}
                            icon={<Users className="w-5 h-5 text-purple-500" />}
                        />
                    </div>
                    <div className="md:col-span-3 bg-black/40 rounded-xl border border-white/10 p-4 min-h-[150px]">
                        <h4 className="text-xs font-semibold text-muted-foreground mb-2 flex items-center gap-2">
                            <PlayCircle className="w-3 h-3" />
                            Campaign Result Preview
                        </h4>
                        {!socialResults ? (
                            <div className="flex flex-col items-center justify-center h-full opacity-30 text-center py-8">
                                <Users className="w-8 h-8 mb-2" />
                                <p className="text-sm italic">No campaign generated yet.</p>
                            </div>
                        ) : (
                            <div className="space-y-4">
                                <div className="space-y-1">
                                    <p className="text-[10px] text-purple-400 font-bold uppercase tracking-widest">AI Copywriting</p>
                                    <pre className="whitespace-pre-wrap text-xs text-foreground/90 bg-white/5 p-2 rounded border border-white/5 max-h-[200px] overflow-y-auto">
                                        {socialResults.text}
                                    </pre>
                                </div>
                                <div className="space-y-1">
                                    <p className="text-[10px] text-purple-400 font-bold uppercase tracking-widest">Voiceover Script</p>
                                    <p className="text-xs text-muted-foreground italic border-l-2 border-purple-500/20 pl-2">
                                        {socialResults.voiceover}
                                    </p>
                                </div>
                                <div className="flex gap-2">
                                    {socialResults.images.map((img: string, i: number) => (
                                        <div key={i} className="flex-1 aspect-square rounded overflow-hidden border border-white/10">
                                            <img src={`http://localhost:8000/static/social/${img.split('/').pop()}`} alt="AI Generated" className="w-full h-full object-cover" />
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}
