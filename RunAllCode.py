import subprocess
import time
import signal
import sys

# รายการไฟล์สคริปต์ที่ต้องรันพร้อมกัน
processes_to_run = [
    ["python", "TeacherAnswer.py"],
    ["python", "StudentAnswer.py"],
    ["python", "DeleteAnswer.py"],
    ["python", "RouterApp.py"],
    ["python", "Get_scores.py"],
    ["python", "Score_server.py"],
]

processes = []

def start_processes():
    for cmd in processes_to_run:
        print(f"Starting: {' '.join(cmd)}")
        p = subprocess.Popen(cmd)
        processes.append(p)

def stop_processes():
    print("\nStopping all processes...")
    for p in processes:
        p.terminate()
    for p in processes:
        p.wait()
    print("All stopped.")

def signal_handler(sig, frame):
    stop_processes()
    sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)  

    start_processes()

    print("All services running. Press Ctrl+C to stop.")

    # รัน loop รอรับ Ctrl+C
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        stop_processes()