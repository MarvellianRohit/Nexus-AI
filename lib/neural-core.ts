import { CreateMLCEngine, MLCEngine, InitProgressCallback } from "@mlc-ai/web-llm";

// Configuration for the model
// Llama-3-8B-Instruct is a good balance of performance and quality for M-series Macs
const SELECTED_MODEL = "Llama-3-8B-Instruct-q4f32_1-MLC";

export interface NeuralState {
    isLoading: boolean;
    progress: number;
    text: string;
    isReady: boolean;
    error: string | null;
    excitement: number; // 0-1, represents "heart rate" or generation speed
    stress: number;   // 0-1, represents "cognitive load" or error rate 
    mode: 'LOCAL_LLM' | 'RAG_SERVER';
    ragConnected: boolean;
}

export type NeuralSubscriber = (state: NeuralState) => void;

class NeuralCore {
    private engine: MLCEngine | null = null;
    private state: NeuralState = {
        isLoading: false,
        progress: 0,
        text: "Idle",
        isReady: false,
        error: null,
        excitement: 0,
        stress: 0,
        mode: 'LOCAL_LLM',
        ragConnected: false
    };
    private subscribers: NeuralSubscriber[] = [];

    // Singleton instance
    private static instance: NeuralCore;

    private constructor() {
        this.checkRagHealth();
    }

    public static getInstance(): NeuralCore {
        if (!NeuralCore.instance) {
            NeuralCore.instance = new NeuralCore();
        }
        return NeuralCore.instance;
    }

    public subscribe(callback: NeuralSubscriber) {
        this.subscribers.push(callback);
        callback(this.state); // Initial emission
        return () => {
            this.subscribers = this.subscribers.filter(sub => sub !== callback);
        };
    }

    private updateState(updates: Partial<NeuralState>) {
        this.state = { ...this.state, ...updates };
        this.subscribers.forEach(sub => sub(this.state));
    }

    public async checkRagHealth() {
        try {
            const res = await fetch('http://localhost:8000/');
            if (res.ok) {
                this.updateState({ ragConnected: true });
            } else {
                this.updateState({ ragConnected: false });
            }
        } catch (e) {
            this.updateState({ ragConnected: false });
        }
    }

    public setMode(mode: 'LOCAL_LLM' | 'RAG_SERVER') {
        this.updateState({ mode });
        if (mode === 'RAG_SERVER') {
            this.checkRagHealth();
        }
    }

    public async initialize() {
        if (this.engine || this.state.isLoading) return;

        this.updateState({ isLoading: true, error: null, text: "Initializing Neural Core..." });

        try {
            const initProgressCallback: InitProgressCallback = (report) => {
                const progress = parseFloat(report.progress.toFixed(2)); // handle very long decimals
                this.updateState({
                    progress: progress * 100,
                    text: report.text
                });
            };

            this.engine = await CreateMLCEngine(
                SELECTED_MODEL,
                { initProgressCallback }
            );

            this.updateState({
                isLoading: false,
                isReady: true,
                text: "Neural Core Online",
                progress: 100
            });

        } catch (error: any) {
            console.error("Neural Core Init Error:", error);
            this.updateState({
                isLoading: false,
                error: error.message || "Failed to initialize Neural Core",
                text: "Initialization Failed"
            });
        }
    }

    public async generateStream(
        messages: { role: string; content: string }[],
        onUpdate: (chunk: string) => void
    ) {
        if (this.state.mode === 'RAG_SERVER') {
            return this.generateStreamRAG(messages, onUpdate);
        }

        if (!this.engine) {
            throw new Error("Neural Core is not initialized");
        }

        // Adapted for MLC format
        // Ensure roles are supported (system, user, assistant)
        const mlcMessages = messages.map(m => ({
            role: m.role === "model" ? "assistant" : m.role, // Map 'model' to 'assistant'
            content: m.content
        })) as any[];

        const stream = await this.engine.chat.completions.create({
            messages: mlcMessages,
            stream: true,
        });

        let lastTokenTime = performance.now();
        let tokenCount = 0;

        // Peak excitement at start of generation
        this.updateState({ excitement: 0.8, stress: 0.2 });

        for await (const chunk of stream) {
            const content = chunk.choices[0]?.delta?.content || "";
            if (content) {
                const now = performance.now();
                const delta = now - lastTokenTime;
                lastTokenTime = now;
                tokenCount++;

                // Calculate excitement based on speed (lower delta = higher excitement)
                // Normal speed is ~20-50ms per token.
                // 20ms -> 1.0 excitement
                // 100ms -> 0.2 excitement
                const speed = 1000 / delta; // tokens per second roughly (or chars)
                const targetExcitement = Math.min(Math.max(speed / 50, 0.3), 1.0);

                // Stress increases if generation is very slow (high latency)
                const runningStress = delta > 200 ? 0.7 : 0.1;

                // Smooth updates to avoid jitter
                this.updateState({
                    excitement: targetExcitement,
                    stress: runningStress
                });

                onUpdate(content);
            }
        }

        // Cooldown
        this.updateState({ excitement: 0.1, stress: 0 });
    }

    private async generateStreamRAG(
        messages: { role: string; content: string }[],
        onUpdate: (chunk: string) => void
    ) {
        const lastMessage = messages[messages.length - 1].content;

        try {
            this.updateState({ excitement: 0.5, stress: 0.1, text: "Querying RAG..." });

            const response = await fetch('http://localhost:8000/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: lastMessage })
            });

            if (!response.body) throw new Error("No response body");

            const reader = response.body.getReader();
            const decoder = new TextDecoder();

            let lastTokenTime = performance.now();

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                const chunk = decoder.decode(value);
                const now = performance.now();
                const delta = now - lastTokenTime;
                lastTokenTime = now;

                const speed = 1000 / delta;
                const targetExcitement = Math.min(Math.max(speed / 30, 0.4), 1.0); // RAG might be slower/chunkier

                this.updateState({
                    excitement: targetExcitement,
                });

                onUpdate(chunk);
            }

            this.updateState({ excitement: 0.1, stress: 0, text: "RAG Complete" });

        } catch (e: any) {
            console.error("RAG Error:", e);
            this.updateState({ error: "RAG Connection Failed", stress: 1 });
        }
    }

    public isReady() {
        return this.state.isReady || (this.state.mode === 'RAG_SERVER' && this.state.ragConnected);
    }

    public async triggerIngest() {
        try {
            this.updateState({ text: "Indexing Documents..." });
            const res = await fetch('http://localhost:8000/api/ingest', { method: 'POST' });
            const data = await res.json();
            this.updateState({ text: `Indexed ${data.chunks} chunks`, ragConnected: true });
            return data;
        } catch (e) {
            this.updateState({ error: "Ingestion Failed" });
        }
    }
}

export const neuralCore = NeuralCore.getInstance();
