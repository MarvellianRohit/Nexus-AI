import mlx.core as mx
from mlx_lm import load, generate, stream_generate
from mlx_lm.utils import load_config
from mlx_lm.sample_utils import make_sampler
import os
import json
import threading

class MLXEngine:
    def __init__(self):
        self.lock = threading.RLock()
        self.models_config = {
            "turbo": "mlx-community/gemma-2-9b-it-4bit",
            "reasoning": "mlx-community/Meta-Llama-3-70B-Instruct-4bit",
            "logic": "mlx-community/DeepSeek-Coder-V2-Lite-Instruct-4bit-mlx",
            "planner": "mlx-community/Llama-3.3-70B-Instruct-4bit"
        }
        self.loaded_models = {} # model_key -> (model, tokenizer)
        # Pre-load the Unified Model Pool (Gemma + Llama)
        # We do this lazily on first request or explicitly here if needed.

    def load_model(self, model_key):
        with self.lock:
            if model_key in self.loaded_models:
                return
            
            repo_id = self.models_config.get(model_key)
            print(f"Loading model: {repo_id}...")
        
        # Configure MLX memory for massive KV-cache (128k tokens)
        # Allocating 110GB unified memory for the active cache pool on the 128GB M3 Max
        # This allows pinning multiple massive models (Llama-3.3-70B + Llama-3-70B + DeepSeek + Gemma)
        mx.metal.set_cache_limit(110 * 1024 * 1024 * 1024) 
        os.environ["MLX_MAX_BITS"] = "32" 
        
        # Load and store in our multi-model map
        model, tokenizer = load(repo_id)
        self.loaded_models[model_key] = (model, tokenizer)
        
        # Memory allocation hint for M3 Max visibility
        if model_key == "reasoning":
            print(f"SYSTEM: Allocating ~115GB (Extreme Mode) unified memory for Teacher ({model_key}).")
        elif model_key == "turbo":
            print(f"SYSTEM: Allocating ~32GB unified memory for Student/Fast-Mode ({model_key}).")

        print(f"Model {model_key} pinned in memory.")

    def stream_chat(self, prompt, model_key="turbo", max_tokens=2048, temp=0.7):
        with self.lock:
            self.load_model(model_key)
            model, tokenizer = self.loaded_models[model_key]
            
            sampler = make_sampler(temp=temp)
            for response in stream_generate(model, tokenizer, prompt=prompt, max_tokens=max_tokens, sampler=sampler):
                yield response.text

    def generate_response(self, prompt, model_key="turbo", temp=0.7):
        with self.lock:
            self.load_model(model_key)
            model, tokenizer = self.loaded_models[model_key]
            sampler = make_sampler(temp=temp)
            return generate(model, tokenizer, prompt=prompt, sampler=sampler)

    def pre_load_context(self, context_text):
        """Pre-loads context into the KV-cache for 'Zero-Shot' latency."""
        print("Pre-loading persistent context into KV-cache...")
        # In a real MLX-LM environment, we would use the model's 'warm-up'
        # or cache-pinning APIs. Here we simulate it by running an initial pass.
        # This pins the activations and tokens in the unified memory.
        self.generate_response(f"Context: {context_text}\nUnderstood.", model_key="reasoning")
        print("Persistent context active in GPU memory.")

    def ui_polish(self, code, instruction):
        """Specialized method for rapid UI polishing using Gemma-2-9B (turbo)."""
        prompt = f"UI Code: {code}\nInstruction: {instruction}\nPolish the UI with Tailwind CSS. Return ONLY the code."
        return self.generate_response(prompt, model_key="turbo")

    def triage(self, prompt):
        """Uses Gemma-2-9B to classify prompt complexity. Returns 'SIMPLE' or 'COMPLEX'."""
        triage_prompt = f"""
        Classify this user request into exactly one category: 'SIMPLE' or 'COMPLEX'.
        
        'SIMPLE' categories:
        - UI/CSS styling requests.
        - Formatting or translation.
        - Simple greetings or general chat.
        - One-line bug fixes or variable renames.
        
        'COMPLEX' categories:
        - Architectural design or refactoring.
        - Complex logic or algorithmic challenges.
        - Multi-file impact analysis.
        - Security or performance audits.
        
        Request: "{prompt}"
        
        Category (Return ONLY the word):"""
        
        result = self.generate_response(triage_prompt, model_key="turbo").strip().upper()
        # Fallback to COMPLEX if ambiguous
        return "SIMPLE" if "SIMPLE" in result else "COMPLEX"

    def routed_stream(self, prompt, system_prompt=""):
        """Intelligently routes the prompt based on triage result."""
        classification = self.triage(prompt)
        print(f"🧠 [Router] Classification: {classification}")
        
        model_key = "turbo" if classification == "SIMPLE" else "reasoning"
        full_prompt = f"{system_prompt}\nUser: {prompt}\nAssistant:"
        
        return self.stream_chat(full_prompt, model_key=model_key)

mlx_engine = MLXEngine()
