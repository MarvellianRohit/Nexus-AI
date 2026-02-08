import React, { useEffect, useState } from 'react';
import { Activity, Cpu, Zap, DownloadCloud, AlertCircle } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { NeuralState, neuralCore } from '@/lib/neural-core';
import { cn } from '@/lib/utils';
import { Progress } from '@/components/ui/progress';

// ... imports
import { NeuralCortex } from './NeuralCortex';
import { useMatrixDecode } from '@/lib/hooks/useMatrixDecode';

export function NeuralStatus() {
    const [state, setState] = useState<NeuralState>({
        isLoading: false,
        progress: 0,
        text: "Idle",
        isReady: false,
        error: null,
        excitement: 0,
        stress: 0,
        mode: 'LOCAL_LLM',
        ragConnected: false
    });

    const decodedText = useMatrixDecode(state.text, 3);

    useEffect(() => {
        // Subscribe to neural core updates
        const unsubscribe = neuralCore.subscribe(setState);
        return () => unsubscribe();
    }, []);

    // Also show when idle if ready, to show off the visual
    if (!state.isLoading && !state.isReady && !state.error) return null;

    return (
        <AnimatePresence>
            <motion.div
                initial={{ opacity: 0, y: -20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, scale: 0.95 }}
                className="fixed top-4 right-4 z-50 w-80"
            >
                {/* 3D Visualization Background */}
                <div className="absolute inset-0 -z-10 overflow-hidden rounded-xl">
                    <NeuralCortex neuralState={state} />
                </div>

                <div className={cn(
                    "rounded-xl border backdrop-blur-md shadow-lg p-4 transition-all duration-300 relative overflow-hidden",
                    state.error ? "bg-red-500/10 border-red-500/20" :
                        state.isReady ? "bg-green-500/5 border-green-500/20" : // Reduced opacity for visibility of 3D
                            "bg-black/60 border-white/10"
                )}>
                    <div className="flex items-center justify-between mb-3">
                        <div className="flex items-center gap-2">
                            {state.error ? (
                                <AlertCircle className="w-5 h-5 text-red-400" />
                            ) : state.isReady ? (
                                <Zap className="w-5 h-5 text-green-400" />
                            ) : (
                                <Activity className="w-5 h-5 text-blue-400 animate-pulse" />
                            )}
                            <h3 className="font-bold text-sm text-white shadow-black drop-shadow-md">
                                {state.isReady ? "Neural Core Active" : "Neural Status"}
                            </h3>
                        </div>
                        {state.isReady && (
                            <div className="flex items-center gap-1 text-[10px] text-green-400 bg-green-900/50 px-2 py-0.5 rounded-full font-mono border border-green-500/30">
                                <Cpu className="w-3 h-3" />
                                WEB_GPU
                            </div>
                        )}
                    </div>

                    <div className="space-y-3 relative z-10">
                        <div className="flex items-center justify-between text-xs text-muted-foreground">
                            <span className="text-white/80 font-mono min-h-[1.5em] block">{decodedText}</span>
                            <span className="font-mono text-white/60">{Math.round(state.progress)}%</span>
                        </div>

                        {!state.isReady && !state.error && (
                            <Progress value={state.progress} className="h-1.5 bg-white/10" />
                        )}

                        {state.isReady && (
                            <div className="grid grid-cols-2 gap-2 mt-2">
                                <button
                                    onClick={() => neuralCore.setMode(state.mode === 'LOCAL_LLM' ? 'RAG_SERVER' : 'LOCAL_LLM')}
                                    className={cn(
                                        "rounded-lg p-2 text-center border transition-all",
                                        state.mode === 'RAG_SERVER'
                                            ? "bg-purple-500/20 border-purple-500/50 text-purple-200"
                                            : "bg-black/40 border-white/5 text-muted-foreground hover:bg-white/5"
                                    )}
                                >
                                    <div className="text-[10px] uppercase tracking-wider">Mode</div>
                                    <div className="text-sm font-mono font-bold">
                                        {state.mode === 'RAG_SERVER' ? 'RAG' : 'LLM'}
                                    </div>
                                </button>

                                {state.mode === 'RAG_SERVER' ? (
                                    <button
                                        onClick={() => neuralCore.triggerIngest()}
                                        disabled={!state.ragConnected}
                                        className={cn(
                                            "rounded-lg p-2 text-center border transition-all",
                                            state.ragConnected
                                                ? "bg-blue-500/20 border-blue-500/50 text-blue-200 hover:bg-blue-500/30"
                                                : "bg-red-500/10 border-red-500/20 text-red-400 cursor-not-allowed"
                                        )}
                                    >
                                        <div className="text-[10px] uppercase tracking-wider">
                                            {state.ragConnected ? "Knowledge" : "Server API"}
                                        </div>
                                        <div className="text-sm font-mono font-bold">
                                            {state.ragConnected ? "INDEX" : "OFFLINE"}
                                        </div>
                                    </button>
                                ) : (
                                    <div className="bg-black/40 border border-white/5 rounded-lg p-2 text-center backdrop-blur-sm">
                                        <div className="text-[10px] text-white/50 uppercase tracking-wider">Privacy</div>
                                        <div className="text-sm font-mono font-bold text-green-300">100%</div>
                                    </div>
                                )}
                            </div>
                        )}
                    </div>
                </div>
            </motion.div>
        </AnimatePresence>
    );
}
