"use client";

import React, { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Send, Sparkles, Paperclip, X, Image as ImageIcon, Zap } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";
import { MessageBubble } from "@/components/MessageBubble";
import { cn } from "@/lib/utils";
import { NeuralStatus } from "@/components/neural/NeuralStatus";
import { ArtifactPanel } from "./studio/ArtifactPanel";
import { WorkbenchPanel } from "./studio/WorkbenchPanel";

interface Message {
    role: "user" | "model";
    content: string;
    images?: string[];
    thought?: string;
    isThinking?: boolean;
    traceId?: string;
    feedback?: number | null;
}

interface ArtifactVersion {
    id: string;
    content: string;
    timestamp: number;
}

interface Artifact {
    id: string;
    title: string;
    content: string;
    language: string;
    versions: ArtifactVersion[];
}

interface ChatInterfaceProps {
    isInStudio?: boolean;
    onCodeGenerated?: (code: string) => void;
}

export function ChatInterface({ isInStudio = false, onCodeGenerated }: ChatInterfaceProps) {
    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState("");
    const [isLoading, setIsLoading] = useState(false);
    const [dragActive, setDragActive] = useState(false);
    const [selectedFile, setSelectedFile] = useState<File | null>(null);
    const [isTurbo, setIsTurbo] = useState(false);
    const [isDualAgent, setIsDualAgent] = useState(false);
    const [activeArtifact, setActiveArtifact] = useState<Artifact | null>(null);
    const [isWorkbenchOpen, setIsWorkbenchOpen] = useState(false);

    const messagesEndRef = useRef<HTMLDivElement>(null);
    const fileInputRef = useRef<HTMLInputElement>(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const handleDrag = (e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        if (e.type === "dragenter" || e.type === "dragover") {
            setDragActive(true);
        } else if (e.type === "dragleave") {
            setDragActive(false);
        }
    };

    const handleDrop = (e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        setDragActive(false);
        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            const file = e.dataTransfer.files[0];
            if (file.type.startsWith('image/')) {
                setSelectedFile(file);
            } else {
                alert("Currently only images are supported for analysis.");
            }
        }
    };

    const clearFile = () => setSelectedFile(null);

    const convertFileToBase64 = (file: File): Promise<string> => {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onloadend = () => resolve(reader.result as string);
            reader.onerror = reject;
            reader.readAsDataURL(file);
        });
    };

    // Helper to extract the last code block from markdown
    const extractLastCodeBlock = (text: string): string | null => {
        const codeBlockRegex = /```(?:jsx|tsx|javascript|js|react)?\s*([\s\S]*?)```/g;
        let match;
        let lastCode = null;

        while ((match = codeBlockRegex.exec(text)) !== null) {
            lastCode = match[1];
        }
        return lastCode;
    };

    const [isNeuralMode, setIsNeuralMode] = useState(false);

    const handleFeedback = async (traceId: string, score: number, messageIndex: number) => {
        try {
            const response = await fetch("/api/feedback", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ trace_id: traceId, score }),
            });
            if (response.ok) {
                setMessages((prev) => {
                    const next = [...prev];
                    next[messageIndex] = { ...next[messageIndex], feedback: score };
                    return next;
                });
            }
        } catch (error) {
            console.error("Feedback error:", error);
        }
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if ((!input.trim() && !selectedFile) || isLoading) return;

        let userContent = input;
        let images: string[] = [];

        if (selectedFile) {
            // Convert to base64
            const base64 = await convertFileToBase64(selectedFile);
            images = [base64];
            userContent += `\n\n[Attached Image: ${selectedFile.name}]`;
        }

        const userMessage: Message = { role: "user", content: userContent, images };
        setMessages((prev) => [...prev, userMessage]);
        setInput("");
        setSelectedFile(null);
        setIsLoading(true);

        try {
            // Prepare messages for API (include images if present)
            const apiMessages = [...messages, userMessage];

            let aiMessage: Message = { role: "model", content: "" };
            let fullResponse = ""; // Accumulator for raw stream parsing

            setMessages((prev) => [...prev, aiMessage]);

            if (isNeuralMode) {
                // --- LOCAL NEURAL CORE EXECUTION ---
                const { neuralCore } = await import('@/lib/neural-core');

                // Initialize if needed (this might trigger the download)
                if (!neuralCore.isReady()) {
                    await neuralCore.initialize();
                }

                await neuralCore.generateStream(apiMessages, (chunk) => {
                    fullResponse += chunk;

                    // Simple passthrough for now, Neural Core doesn't support <thinking> tags natively yet
                    // But we can add that prompt engineering later
                    const newContent = aiMessage.content + chunk;
                    aiMessage = { ...aiMessage, content: newContent };

                    setMessages((prev) => [
                        ...prev.slice(0, -1),
                        { ...aiMessage },
                    ]);

                    // LIVE PREVIEW UPDATE
                    // Check if there's a code block and update the studio
                    if (onCodeGenerated) {
                        const code = extractLastCodeBlock(newContent);
                        if (code) {
                            onCodeGenerated(code);
                        }
                    }
                });

            } else {
                // --- CLOUD/LOCAL MLX EXECUTION ---
                const endpoint = isDualAgent ? "/api/chat/dual-loop" : "/api/chat";
                const response = await fetch(endpoint, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        message: userContent,
                        turbo: isTurbo,
                        use_mlx: true
                    }),
                });

                if (!response.ok) throw new Error("Failed to send message");
                if (!response.body) throw new Error("No response body");

                const reader = response.body.getReader();

                while (true) {
                    const { done, value } = await reader.read();
                    if (done) break;
                    const text = new TextDecoder().decode(value);

                    // --- TRACE ID PARSING ---
                    if (text.startsWith("__TRACE_ID__:")) {
                        const line = text.split('\n')[0];
                        const id = line.replace("__TRACE_ID__:", "");
                        aiMessage = { ...aiMessage, traceId: id };
                        setMessages((prev) => [
                            ...prev.slice(0, -1),
                            { ...aiMessage },
                        ]);
                        // Continue processing the rest of the text if any
                        const remaining = text.substring(line.length + 1);
                        if (!remaining) continue;
                        fullResponse += remaining;
                    } else {
                        fullResponse += text;
                    }

                    // --- THOUGHT PARSING LOGIC ---
                    const thoughtStart = fullResponse.indexOf('<thinking>');
                    const thoughtEnd = fullResponse.indexOf('</thinking>');

                    let thoughtContent = '';
                    let finalContent = fullResponse;
                    let isThinking = false;

                    if (thoughtStart !== -1) {
                        if (thoughtEnd !== -1) {
                            thoughtContent = fullResponse.substring(thoughtStart + 10, thoughtEnd);
                            finalContent = fullResponse.substring(0, thoughtStart) + fullResponse.substring(thoughtEnd + 11);
                            isThinking = false;
                        } else {
                            thoughtContent = fullResponse.substring(thoughtStart + 10);
                            finalContent = fullResponse.substring(0, thoughtStart);
                            isThinking = true;
                        }
                    } else {
                        // No thought tags found yet, standard streaming
                        finalContent = fullResponse;
                    }

                    setMessages((prev) => [
                        ...prev.slice(0, -1),
                        { ...aiMessage },
                    ]);

                    // STREAM TO STUDIO WATCHER
                    fetch("http://localhost:8080/api/studio/write", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ content: fullResponse })
                    }).catch(console.error);

                    if (onCodeGenerated) {
                        const code = extractLastCodeBlock(finalContent);
                        if (code) {
                            onCodeGenerated(code);
                            setActiveArtifact(prev => {
                                const version: ArtifactVersion = {
                                    id: Date.now().toString(),
                                    content: code,
                                    timestamp: Date.now()
                                };

                                if (prev && prev.title === "Generated Code") {
                                    // If same artifact, add version
                                    return {
                                        ...prev,
                                        content: code,
                                        versions: [...prev.versions, version]
                                    };
                                } else {
                                    // new artifact
                                    return {
                                        id: Date.now().toString(),
                                        title: "Generated Code",
                                        content: code,
                                        language: "tsx",
                                        versions: [version]
                                    };
                                }
                            });
                        }
                    }
                }
            }
        } catch (error) {
            console.error("Error:", error);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div
            className={cn(
                "flex flex-col w-full h-full mx-auto",
                isInStudio ? "max-w-none" : "max-w-5xl"
            )}
            onDragEnter={handleDrag}
        >
            <NeuralStatus />

            {/* Full Screen Drag Overlay */}
            <AnimatePresence>
                {dragActive && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        className="fixed inset-0 z-50 flex items-center justify-center bg-primary/20 backdrop-blur-sm border-2 border-dashed border-primary m-4 rounded-xl max-w-5xl mx-auto"
                        onDragLeave={handleDrag}
                        onDragOver={handleDrag}
                        onDrop={handleDrop}
                    >
                        <div className="bg-background/80 p-6 rounded-xl text-center pointer-events-none">
                            <Paperclip className="h-12 w-12 mx-auto mb-2 text-primary" />
                            <h3 className="text-xl font-bold">Drop files here to attach</h3>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>

            {/* Messages Area - Scrollable container that fills space above input */}
            <div className="h-full overflow-y-auto p-4 pb-32 space-y-6 scrollbar-thin scrollbar-thumb-muted scrollbar-track-transparent">
                <AnimatePresence initial={false}>
                    {messages.length === 0 ? (
                        <motion.div
                            initial={{ opacity: 0, scale: 0.9 }}
                            animate={{ opacity: 1, scale: 1 }}
                            className="flex flex-col items-center justify-center text-center opacity-70 min-h-[calc(100vh-200px)]"
                        >
                            <div className="mb-6 rounded-full bg-primary/10 p-6 ring-1 ring-primary/20">
                                <Sparkles className="h-12 w-12 text-primary" />
                            </div>
                            <h2 className="text-2xl font-bold tracking-tight">How can I help you today?</h2>
                            <p className="mt-2 text-muted-foreground">
                                Ask me anything regarding coding, writing, or analysis.
                            </p>
                        </motion.div>
                    ) : (
                        messages.map((msg, index) => (
                            <MessageBubble
                                key={index}
                                role={msg.role}
                                content={msg.content}
                                thought={msg.thought}
                                isThinking={msg.isThinking}
                                onFeedback={msg.traceId ? (score: number) => handleFeedback(msg.traceId!, score, index) : undefined}
                                feedback={msg.feedback}
                            />
                        ))
                    )}
                </AnimatePresence>
                {isLoading && messages[messages.length - 1]?.role !== "model" && (
                    <div className="flex items-center gap-2 text-muted-foreground text-sm ml-2">
                        <span className="animate-pulse">Thinking...</span>
                    </div>
                )}
                <div ref={messagesEndRef} />
            </div>

            {/* Input Area - FIXED to viewport bottom */}
            <div className={cn(
                "fixed bottom-0 left-0 right-0 p-4 border-t border-white/10 bg-black/80 backdrop-blur-md z-10",
                isInStudio ? "absolute w-full" : "fixed max-w-5xl mx-auto"
            )}>
                {/* File Preview */}
                <AnimatePresence>
                    {selectedFile && (
                        <motion.div
                            initial={{ opacity: 0, y: 10, height: 0 }}
                            animate={{ opacity: 1, y: 0, height: 'auto' }}
                            exit={{ opacity: 0, y: 10, height: 0 }}
                            className="mb-3 flex items-center gap-2"
                        >
                            <div className="relative group">
                                <div className="flex items-center gap-2 rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-sm text-gray-300">
                                    <ImageIcon className="h-4 w-4 text-blue-400" />
                                    <span className="max-w-[200px] truncate">{selectedFile.name}</span>
                                    <span className="text-xs text-gray-500">({(selectedFile.size / 1024 / 1024).toFixed(2)} MB)</span>
                                </div>
                                <button
                                    onClick={clearFile}
                                    className="absolute -top-2 -right-2 rounded-full bg-red-500 p-1 text-white shadow-sm opacity-0 group-hover:opacity-100 transition-opacity"
                                >
                                    <X className="h-3 w-3" />
                                </button>
                            </div>
                        </motion.div>
                    )}
                </AnimatePresence>

                <form onSubmit={handleSubmit} className="relative flex items-center gap-2">
                    <input
                        type="file"
                        className="hidden"
                        ref={fileInputRef}
                        onChange={(e) => {
                            if (e.target.files?.[0]) setSelectedFile(e.target.files[0]);
                        }}
                    />
                    <Button
                        type="button"
                        variant="ghost"
                        size="icon"
                        className="absolute left-2 text-muted-foreground hover:text-white hover:bg-white/10 rounded-full"
                        onClick={() => fileInputRef.current?.click()}
                    >
                        <Paperclip className="h-5 w-5" />
                    </Button>

                    <Input
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        placeholder={isNeuralMode ? "Ask Neural Core (Local)..." : "Type a message..."}
                        className={cn(
                            "pl-12 pr-80 py-6 text-base rounded-full border-white/5 focus-visible:ring-primary/50 transition-colors",
                            isNeuralMode ? "bg-green-950/20 border-green-500/20 placeholder:text-green-500/50" : "bg-secondary/50"
                        )}
                        disabled={isLoading}
                        autoFocus
                    />

                    {/* Turbo Mode Toggle */}
                    <div className="absolute right-32 top-1/2 -translate-y-1/2 flex items-center gap-2">
                        <button
                            type="button"
                            onClick={() => setIsTurbo(!isTurbo)}
                            className={cn(
                                "flex items-center gap-1.5 px-2 py-1 rounded-full text-[10px] font-mono font-bold border transition-all",
                                isTurbo
                                    ? "bg-orange-500/20 text-orange-400 border-orange-500/50"
                                    : "bg-white/5 text-muted-foreground border-white/10 hover:bg-white/10"
                            )}
                            title="Toggle Turbo Mode (Gemma-2-9B)"
                        >
                            <Zap className={cn("w-3 h-3", isTurbo && "fill-current")} />
                            {isTurbo ? "TURBO:ON" : "TURBO:OFF"}
                        </button>
                    </div>

                    {/* Dual Agent Toggle */}
                    <div className="absolute right-52 top-1/2 -translate-y-1/2 flex items-center gap-2">
                        <button
                            type="button"
                            onClick={() => setIsDualAgent(!isDualAgent)}
                            className={cn(
                                "flex items-center gap-1.5 px-2 py-1 rounded-full text-[10px] font-mono font-bold border transition-all",
                                isDualAgent
                                    ? "bg-purple-500/20 text-purple-400 border-purple-500/50"
                                    : "bg-white/5 text-muted-foreground border-white/10 hover:bg-white/10"
                            )}
                            title="Toggle Dual-Agent Verification (Architect + Auditor)"
                        >
                            <Sparkles className={cn("w-3 h-3", isDualAgent && "fill-current")} />
                            {isDualAgent ? "DUAL:ON" : "DUAL:OFF"}
                        </button>
                    </div>

                    {/* Neural Toggle */}
                    <div className="absolute right-14 top-1/2 -translate-y-1/2">
                        <button
                            type="button"
                            onClick={() => setIsNeuralMode(!isNeuralMode)}
                            className={cn(
                                "flex items-center gap-1.5 px-2 py-1 rounded-full text-[10px] font-mono font-bold border transition-all",
                                isNeuralMode
                                    ? "bg-green-500/20 text-green-400 border-green-500/50"
                                    : "bg-white/5 text-muted-foreground border-white/10 hover:bg-white/10"
                            )}
                            title="Toggle Local Neural Core (WebGPU)"
                        >
                            <Zap className={cn("w-3 h-3", isNeuralMode && "fill-current")} />
                            {isNeuralMode ? "CORE:ON" : "CLOUD"}
                        </button>
                    </div>

                    <Button
                        type="submit"
                        size="icon"
                        disabled={isLoading || (!input.trim() && !selectedFile)}
                        className={cn(
                            "absolute right-1.5 rounded-full h-9 w-9 transition-all hover:scale-105",
                            isNeuralMode ? "bg-green-600 hover:bg-green-500" : "bg-primary hover:bg-primary/90"
                        )}
                    >
                        <Send className="h-4 w-4" />
                        <span className="sr-only">Send</span>
                    </Button>
                </form>
                <div className="mt-2 text-center text-xs text-muted-foreground">
                    {isNeuralMode ? "Running locally on WebGPU (Project OVERCLOCK)" : "AI may display inaccurate info, please double check."}
                </div>
            </div>
            {/* Artifact Side Panel Overlay */}
            {activeArtifact && (
                <div className="fixed inset-y-0 right-0 w-1/3 z-50 bg-background/95 backdrop-blur-xl border-l border-border shadow-2xl">
                    <ArtifactPanel
                        artifact={activeArtifact}
                        onClose={() => setActiveArtifact(null)}
                    />
                </div>
            )}

            {/* Workbench Panel Overlay */}
            <WorkbenchPanel
                isOpen={isWorkbenchOpen}
                onClose={() => setIsWorkbenchOpen(false)}
            />
        </div >
    );
}
