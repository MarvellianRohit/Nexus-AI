import os
import whisper
import torch

def transcribe_video(video_path: str, model_size: str = "base") -> str:
    """
    Transcribes video audio using OpenAI Whisper locally on GPU (MPS) or CPU.
    """
    print(f"🎤 Nexus Creator: Transcribing {video_path}...")
    
    # Check for MPS (Mac GPU) availability
    device = "mps" if torch.backends.mps.is_available() else "cpu"
    print(f"🚀 Whisper running on: {device}")
    
    try:
        model = whisper.load_model(model_size, device=device)
        result = model.transcribe(video_path)
        return result["text"]
    except Exception as e:
        print(f"❌ Transcription Failed: {e}")
        raise e
