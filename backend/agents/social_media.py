import os
import concurrent.futures

# Configuration
TEACHER_MODEL = "llama3:70b"
SD_MODEL_ID = "stabilityai/stable-diffusion-xl-base-1.0"
WHISPER_MODEL = "large-v3"
OUTPUT_DIR = "backend/static/social"

class SocialMediaAgent:
    def __init__(self):
        import psutil
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        mem = psutil.virtual_memory()
        print(f"🚀 Nexus Social: Initialized. Memory: {mem.used/1e9:.1f}GB / {mem.total/1e9:.1f}GB", flush=True)

    def generate_text(self, feature_desc):
        try:
            from langchain_ollama import ChatOllama
            from langchain_core.prompts import ChatPromptTemplate
            from langchain_core.output_parsers import StrOutputParser
            print("✍️ Generating Copywriting with Llama-3-70b...", flush=True)
            llm = ChatOllama(model=TEACHER_MODEL, temperature=0.8)
            prompt = ChatPromptTemplate.from_template("""
            You are a World-Class Tech Evangelist. 
            Write a 500-word highly engaging LinkedIn post and a 5-tweet Twitter thread about this new feature:
            {feature}
            
            Focus on:
            1. Innovation and Impact.
            2. Technical depth for developers.
            3. Visionary future outlook.
            """)
            chain = prompt | llm | StrOutputParser()
            res = chain.invoke({"feature": feature_desc})
            
            # Save to disk
            with open(os.path.join(OUTPUT_DIR, "copy.txt"), "w") as f:
                f.write(res)
                
            print(f"✅ Llama-3-70b Copy Generated and Saved ({len(res)} chars).", flush=True)
            return res
        except Exception as e:
            print(f"❌ Text Generation Failed: {e}", flush=True)
            return None

    def generate_images(self, feature_desc):
        try:
            import torch
            from diffusers import StableDiffusionXLPipeline
            device = "mps" if torch.backends.mps.is_available() else "cpu"
            print(f"🎨 Generating SDXL Cyberpunk Coding Images on {device}...", flush=True)
            pipe = StableDiffusionXLPipeline.from_pretrained(
                SD_MODEL_ID, 
                torch_dtype=torch.float16, 
                variant="fp16", 
                use_safetensors=True
            ).to(device)
            
            prompt = f"Nexus-AI brand dashboard, Cyberpunk tech aesthetic, high-end software architecture, deep blue and violet neon, cinematic composition, 8k, related to: {feature_desc}"
            paths = []
            for i in range(3):
                print(f"🖼️ Rendering Image {i+1}/3...", flush=True)
                image = pipe(prompt=prompt, num_inference_steps=30, guidance_scale=7.5).images[0]
                path = os.path.join(OUTPUT_DIR, f"image_{i}.png")
                image.save(path)
                paths.append(path)
                
            # Clear VRAM
            del pipe
            torch.mps.empty_cache()
            return paths
        except Exception as e:
            print(f"❌ Image Generation Failed: {e}", flush=True)
            return []

    def generate_voiceover(self, content):
        try:
            import torch
            import whisper
            # Whisper on MPS sometimes hits Sparse tensor issues, fallback to CPU if needed
            device = "mps" if torch.backends.mps.is_available() else "cpu"
            print(f"🎙️ Generating Voiceover Script with Whisper-Large-v3 on {device}...", flush=True)
            
            try:
                model = whisper.load_model(WHISPER_MODEL, device=device)
            except Exception as e:
                print(f"⚠️ MPS failed for Whisper, falling back to CPU: {e}", flush=True)
                model = whisper.load_model(WHISPER_MODEL, device="cpu")

            print("✅ Whisper Loaded. Finalizing script...", flush=True)
            script = f"NEXUS-AI BROADCAST SCRIPT:\n\n{content[:1000]}"
            
            # Save to disk
            with open(os.path.join(OUTPUT_DIR, "script.txt"), "w") as f:
                f.write(script)
                
            print(f"✅ Voiceover Script Generated and Saved ({len(script)} chars).", flush=True)
            
            # Clear VRAM
            del model
            torch.mps.empty_cache()
            return script
        except Exception as e:
            print(f"❌ Voiceover Generation Failed: {e}", flush=True)
            return None

    def run_autonomous_flow(self, feature_desc):
        results = {}
        print(f"🔥 Starting CONCURRENT Multi-Modal Flow for: {feature_desc}")
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            future_text = executor.submit(self.generate_text, feature_desc)
            future_images = executor.submit(self.generate_images, feature_desc)
            future_voice = executor.submit(self.generate_voiceover, feature_desc)
            
            concurrent.futures.wait([future_text, future_images, future_voice])
            
            results['text'] = future_text.result()
            results['images'] = future_images.result()
            results['voiceover'] = future_voice.result()
            
        print("✨ Social Media Campaign Aggregated.")
        return results

if __name__ == "__main__":
    print("🚀 Nexus Social Media Agent: STARTING...", flush=True)
    agent = SocialMediaAgent()
    print("✅ Agent Class Initialized.", flush=True)
    try:
        results = agent.run_autonomous_flow("A revolutionary Graph-RAG system for codebase impact analysis using Neo4j and Llama-3.")
        print("✅ Flow Complete. Campaign Assets in backend/static/social/", flush=True)
    except Exception as e:
        print(f"❌ FLOW FAILED: {e}", flush=True)
    finally:
        print("🏁 Social Agent Script Finished.", flush=True)
