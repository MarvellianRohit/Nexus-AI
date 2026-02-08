import sys
from mlx_lm import load, lora
from datasets import load_dataset

# Configuration
# MODEL_NAME = "microsoft/Phi-3-mini-4k-instruct" # Can be fetched from HF
MODEL_PATH = "microsoft/Phi-3-mini-4k-instruct"
DATA_PATH = "backend/distillation/data/golden_dataset.jsonl"
ADAPTER_PATH = "backend/distillation/adapters"

def train_student():
    print(f"🎓 Nexus Student: Loading {MODEL_PATH} for fine-tuning...")
    
    # 1. Load Model & Tokenizer
    model, tokenizer = load(MODEL_PATH)
    
    # 2. Freeze Base Model (LoRA setup)
    # MLX handles this implicitly in lora.train, but we configure it via args.
    
    print("📂 Loading Golden Dataset...")
    # Load JSONL dataset
    dataset = load_dataset("json", data_files=DATA_PATH, split="train")
    
    # Minimal Training Configuration (Hardcoded for simplicity)
    # real mlx_lm usage often involves CLI, but we can call the library functions directly if exposed,
    # or wrap the CLI command. For stability, we'll construct a command to run mlx_lm.lora.
    
    print("⚠️ MLX Training is best run via CLI for full control.")
    print("Executing: python -m mlx_lm.lora ...")
    
    cmd = [
        sys.executable, "-m", "mlx_lm.lora",
        "--model", MODEL_PATH,
        "--train",
        "--data", "backend/distillation/data/", # Directory containing jsonl
        "--batch-size", "4",
        "--lora-layers", "16",
        "--iters", "1000",
        "--adapter-path", ADAPTER_PATH
    ]
    
    import subprocess
    subprocess.run(cmd)

if __name__ == "__main__":
    train_student()
