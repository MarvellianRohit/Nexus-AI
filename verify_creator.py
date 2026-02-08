import sys
import os
import time
import requests

# Add current directory to path
sys.path.append(os.getcwd())

def test_whisper_import():
    try:
        print("Testing Whisper import...")
        from backend.creator.transcribe import transcribe_video
        print("✅ Whisper import successful.")
        return True
    except Exception as e:
        print(f"❌ Whisper import failed: {e}")
        return False

def test_ollama_connection():
    print("Testing Ollama connection...")
    try:
        response = requests.get("http://localhost:11434/api/tags")
        if response.status_code == 200:
            print("✅ Ollama is running and reachable.")
            print(f"Models available: {response.json().get('models', [])}")
            # Check for llama3
            models = [m['name'] for m in response.json().get('models', [])]
            if any("llama3" in m for m in models):
                print("✅ Llama3 model found.")
            else:
                print("⚠️ Llama3 model NOT found. Please run 'ollama pull llama3'.")
            return True
        else:
            print(f"❌ Ollama returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Ollama connection failed: {e}")
        return False

if __name__ == "__main__":
    whisper_ok = test_whisper_import()
    # Wait a bit for Ollama to fully start if it just launched
    time.sleep(2)
    ollama_ok = test_ollama_connection()
    
    if whisper_ok and ollama_ok:
        print("\n🎉 Nexus Creator verification successful (Dependencies ready).")
    else:
        print("\n⚠️ Nexus Creator verification incomplete.")
