'use client';

import React, { useState, useRef } from 'react';
import { Upload, Image as ImageIcon, Code, ArrowRight, Loader2, Maximize2 } from 'lucide-react';
import { cn } from '@/lib/utils';
import { motion, AnimatePresence } from 'framer-motion';

export function VisionProjector() {
    const [image, setImage] = useState<File | null>(null);
    const [preview, setPreview] = useState<string | null>(null);
    const [generatedCode, setGeneratedCode] = useState('');
    const [isThinking, setIsThinking] = useState(false);
    const fileInputRef = useRef<HTMLInputElement>(null);

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (file) {
            setImage(file);
            setPreview(URL.createObjectURL(file));
            setGeneratedCode('');
        }
    };

    const handleDrop = (e: React.DragEvent) => {
        e.preventDefault();
        const file = e.dataTransfer.files?.[0];
        if (file && file.type.startsWith('image/')) {
            setImage(file);
            setPreview(URL.createObjectURL(file));
            setGeneratedCode('');
        }
    };

    const handleGenerate = async () => {
        if (!image) return;

        setIsThinking(true);
        setGeneratedCode('');

        const formData = new FormData();
        formData.append('file', image);

        try {
            const res = await fetch('http://localhost:8000/api/vision/generate', {
                method: 'POST',
                body: formData,
            });

            if (!res.body) return;
            const reader = res.body.getReader();
            const decoder = new TextDecoder();

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;
                const chunk = decoder.decode(value);
                setGeneratedCode(prev => prev + chunk);
            }
        } catch (e) {
            console.error(e);
            setGeneratedCode("Error generating code. Please ensure backend is running.");
        } finally {
            setIsThinking(false);
        }
    };

    return (
        <div className="flex h-full gap-4 p-4">
            {/* Input Zone */}
            <div className="w-1/2 flex flex-col gap-4">
                <div
                    className={cn(
                        "flex-1 border-2 border-dashed rounded-xl flex flex-col items-center justify-center p-8 transition-all",
                        image ? "border-primary/50 bg-primary/5" : "border-white/10 hover:border-primary/30 hover:bg-white/5"
                    )}
                    onDragOver={(e) => e.preventDefault()}
                    onDrop={handleDrop}
                    onClick={() => fileInputRef.current?.click()}
                >
                    <input
                        type="file"
                        ref={fileInputRef}
                        className="hidden"
                        accept="image/*"
                        onChange={handleFileChange}
                    />

                    {preview ? (
                        <div className="relative w-full h-full flex items-center justify-center">
                            <img src={preview} alt="Upload" className="max-h-full max-w-full object-contain rounded-lg shadow-lg" />
                            <div className="absolute inset-0 bg-black/50 opacity-0 hover:opacity-100 transition-opacity flex items-center justify-center rounded-lg">
                                <p className="text-white font-medium">Click to replace</p>
                            </div>
                        </div>
                    ) : (
                        <div className="text-center space-y-4">
                            <div className="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center mx-auto">
                                <Upload className="w-8 h-8 text-primary" />
                            </div>
                            <div>
                                <h3 className="text-lg font-semibold">Upload Screenshot</h3>
                                <p className="text-sm text-muted-foreground">Drag & drop or click to browse</p>
                            </div>
                        </div>
                    )}
                </div>

                <button
                    onClick={handleGenerate}
                    disabled={!image || isThinking}
                    className="w-full py-4 bg-primary hover:bg-primary/90 text-white rounded-xl font-bold text-lg disabled:opacity-50 transition-all flex items-center justify-center gap-2"
                >
                    {isThinking ? (
                        <>
                            <Loader2 className="w-5 h-5 animate-spin" />
                            Analyzing UI...
                        </>
                    ) : (
                        <>
                            <Maximize2 className="w-5 h-5" />
                            Project to Code
                        </>
                    )}
                </button>
            </div>

            {/* Output Zone */}
            <div className="w-1/2 bg-black/40 border border-white/10 rounded-xl overflow-hidden flex flex-col">
                <div className="p-4 border-b border-white/10 flex items-center justify-between">
                    <div className="flex items-center gap-2">
                        <Code className="w-4 h-4 text-primary" />
                        <span className="font-mono text-sm font-bold">Generated Component</span>
                    </div>
                </div>
                <div className="flex-1 p-4 overflow-auto font-mono text-xs text-muted-foreground whitespace-pre-wrap">
                    {generatedCode || (
                        <div className="h-full flex flex-col items-center justify-center opacity-30">
                            <Code className="w-12 h-12 mb-4" />
                            <p>Code will appear here</p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
