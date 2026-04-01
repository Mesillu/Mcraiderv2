#!/data/data/com.termux/files/usr/bin/python3
"""
DEVICE CLIENT - Tested Remote Connection
"""

import os
import sys
import socket
import threading
import json
import time
import subprocess
import platform

class DeviceClient:
    def __init__(self):
        self.connected = False
        self.socket = None
        self.device_name = platform.node()
        self.running = True
        self.config_file = os.path.expanduser("~/.device_config.json")
        
    def connect(self, host, port):
        """Connect to main device"""
        try:
            print(f"🔄 Connecting to {host}:{port}...")
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(30)
            self.socket.connect((host, int(port)))
            
            # Send device info
            info = {
                "device_name": self.device_name,
                "platform": platform.system(),
                "timestamp": time.time()
            }
            self.socket.send(json.dumps(info).encode())
            
            # Get response
            response = self.socket.recv(4096).decode()
            confirm = json.loads(response)
            
            if confirm.get('status') == 'connected':
                self.connected = True
                print(f"✅ CONNECTED to {host}:{port}")
                self.listen()
                return True
                
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False
            
    def listen(self):
        """Listen for commands"""
        try:
            while self.connected:
                self.socket.settimeout(60)
                try:
                    data = self.socket.recv(4096).decode()
                    if not data:
                        break
                        
                    cmd = json.loads(data)
                    if cmd.get('type') == 'command':
                        output = self.execute(cmd.get('command'))
                        self.socket.send(json.dumps({"type": "response", "output": output}).encode())
                        
                except socket.timeout:
                    # Send heartbeat
                    try:
                        self.socket.send(json.dumps({"type": "heartbeat"}).encode())
                    except:
                        break
                        
        except Exception as e:
            print(f"Error: {e}")
        finally:
            self.connected = False
            self.cleanup()
            
    def execute(self, command):
        """Execute command"""
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
            return result.stdout + result.stderr
        except:
            return "Error"
            
    def cleanup(self):
        """Cleanup"""
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
                
    def reconnect(self, host, port):
        """Auto reconnect"""
        while self.running:
            if not self.connected:
                self.connect(host, port)
            time.sleep(30)
            
    def run(self):
        """Main run"""
        print("\n" + "="*50)
        print("📱 DEVICE CLIENT")
        print("="*50)
        
        # Check for saved config
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                config = json.load(f)
            host = config['host']
            port = config['port']
            print(f"📡 Using saved connection: {host}:{port}")
        else:
            # First time setup
            print("\n📝 ENTER MAIN DEVICE CONNECTION:")
            print("(Get these from the Main Device screen)")
            print()
            host = input("🌍 IP/Host: ").strip()
            port = input("🔌 Port: ").strip()
            
            # Save
            with open(self.config_file, 'w') as f:
                json.dump({'host': host, 'port': port}, f)
            print(f"\n✅ Saved to {self.config_file}")
            
        print(f"\n🎯 Target: {host}:{port}")
        
        # Start connection thread
        threading.Thread(target=self.reconnect, args=(host, port), daemon=True).start()
        
        # Keep running
        print("\n🔄 Running in background...")
        print("Press Ctrl+C to exit")
        
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n👋 Disconnecting...")
            self.running = False
            self.cleanup()

if __name__ == "__main__":
    client = DeviceClient()
    client.run()
