import os
import sys
import psutil

# Add project root to path
sys.path.append(os.getcwd())

from backend.mission_control import mission_control

def test_orchestrator_worker_loop():
    print("--- 🏁 Starting Orchestrator-Worker Mission 🏁 ---")
    
    task = "Implement a thread-safe LRU Cache in Python with a capacity limit and O(1) time complexity for get and put operations."
    
    print(f"Task: {task}")
    
    # Track model pinning state
    mem_before = psutil.virtual_memory().used / (1024**3)
    
    report = mission_control.run_mission(task)
    
    mem_after = psutil.virtual_memory().used / (1024**3)
    
    print("\n" + "="*50)
    print(report)
    print("="*50)
    
    print(f"\n🧠 Unified Memory Utilization: {mem_after:.2f}GB (Pinned all 4 models)")
    print(f"📈 Memory Delta: {mem_after - mem_before:.2f}GB")
    
    if "✅ COMPLETE" in report:
        print("\n✅ MISSION SUCCESS: Orchestrator confirmed all workers return success.")
    else:
        print("\n❌ MISSION FAILED: One or more workers reported failure.")

if __name__ == "__main__":
    test_orchestrator_worker_loop()
