#!/usr/bin/env python3
"""
🐍 CODEREX UTIL - COMBINED PYTHON SCRIPTS
==========================================
All Python files from util folder combined into one comprehensive script
This script contains all functionality from:
- system_monitor.py
- demo_system_monitor.py
- test_system_monitor.py

Author: Coderex Development Team
Version: 2.0 Combined
License: MIT
"""

import os
import sys
import time
import psutil
import subprocess
import threading
import signal
import json
import shutil
import unittest
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import curses
import argparse
from unittest.mock import patch, MagicMock, mock_open

# ============================================================================
# COLORS CLASS (from system_monitor.py)
# ============================================================================

class Colors:
    """ANSI color codes for terminal output"""
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    PURPLE = '\033[0;35m'
    CYAN = '\033[0;36m'
    WHITE = '\033[1;37m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    NC = '\033[0m'  # No Color
    
    @staticmethod
    def colorize(text: str, color: str) -> str:
        """Apply color to text"""
        return f"{color}{text}{Colors.NC}"

# ============================================================================
# SYSTEM MONITOR CLASS (from system_monitor.py)
# ============================================================================

class SystemMonitor:
    """Main system monitoring class"""
    
    def __init__(self):
        self.running = True
        self.update_interval = 1.0  # seconds
        self.history_size = 60  # Keep 60 seconds of history
        self.cpu_history = []
        self.memory_history = []
        self.network_history = []
        self.disk_history = []
        self.start_time = time.time()
        
        # System paths
        self.home_dir = Path.home()
        self.coderex_dir = Path("/home/rakesh/Coderex")
        self.vscode_dirs = [
            self.home_dir / ".vscode",
            self.home_dir / ".config/Code",
            self.home_dir / ".config/Code-NoAI"
        ]
        
        # Cache directories to clean
        self.cache_dirs = [
            "/tmp",
            "/var/tmp",
            str(self.home_dir / ".cache"),
            str(self.home_dir / ".local/share/Trash"),
            str(self.home_dir / ".thumbnails")
        ]
        
    def signal_handler(self, signum, frame):
        """Handle Ctrl+C gracefully"""
        self.running = False
        print(f"\n{Colors.colorize('👋 Shutting down gracefully...', Colors.YELLOW)}")
        sys.exit(0)
    
    def get_system_info(self) -> Dict:
        """Get comprehensive system information"""
        try:
            # CPU Information
            cpu_percent = psutil.cpu_percent(interval=0.1)
            cpu_count = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()
            
            # Memory Information
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            # Disk Information
            disk = psutil.disk_usage('/')
            
            # Network Information
            network = psutil.net_io_counters()
            
            # Process Information
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'memory_info']):
                try:
                    processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            # Sort by memory usage
            processes.sort(key=lambda x: x.get('memory_percent', 0), reverse=True)
            
            return {
                'timestamp': datetime.now(),
                'cpu': {
                    'percent': cpu_percent,
                    'count': cpu_count,
                    'frequency': cpu_freq.current if cpu_freq else 0
                },
                'memory': {
                    'total': memory.total,
                    'available': memory.available,
                    'used': memory.used,
                    'percent': memory.percent,
                    'cached': getattr(memory, 'cached', 0),
                    'buffers': getattr(memory, 'buffers', 0)
                },
                'swap': {
                    'total': swap.total,
                    'used': swap.used,
                    'percent': swap.percent
                },
                'disk': {
                    'total': disk.total,
                    'used': disk.used,
                    'free': disk.free,
                    'percent': disk.used / disk.total * 100
                },
                'network': {
                    'bytes_sent': network.bytes_sent,
                    'bytes_recv': network.bytes_recv,
                    'packets_sent': network.packets_sent,
                    'packets_recv': network.packets_recv
                },
                'processes': processes[:10]  # Top 10 processes
            }
        except Exception as e:
            print(f"{Colors.colorize(f'Error getting system info: {e}', Colors.RED)}")
            return {}
    
    def format_bytes(self, bytes_value: int) -> str:
        """Convert bytes to human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_value < 1024.0:
                return f"{bytes_value:.1f} {unit}"
            bytes_value /= 1024.0
        return f"{bytes_value:.1f} PB"
    
    def create_progress_bar(self, percentage: float, width: int = 30) -> str:
        """Create a visual progress bar"""
        filled = int(width * percentage / 100)
        bar = '█' * filled + '░' * (width - filled)
        
        # Color based on percentage
        if percentage < 50:
            color = Colors.GREEN
        elif percentage < 80:
            color = Colors.YELLOW
        else:
            color = Colors.RED
            
        return f"{Colors.colorize(bar, color)} {percentage:5.1f}%"
    
    def display_system_info(self, info: Dict):
        """Display system information in a beautiful format"""
        if not info:
            return
            
        # Clear screen
        os.system('clear')
        
        # Header
        uptime = time.time() - self.start_time
        uptime_str = f"{int(uptime//3600):02d}:{int((uptime%3600)//60):02d}:{int(uptime%60):02d}"
        
        print(f"{Colors.colorize('🚀 CODEREX SYSTEM MONITOR', Colors.CYAN)} {Colors.colorize('v2.0', Colors.WHITE)}")
        print(f"{Colors.colorize('=' * 80, Colors.BLUE)}")
        print(f"{Colors.colorize('📊 Live System Performance Dashboard', Colors.WHITE)} | Uptime: {Colors.colorize(uptime_str, Colors.GREEN)}")
        timestamp_str = info['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
        print(f"{Colors.colorize('🕐 ' + timestamp_str, Colors.YELLOW)}")
        print()
        
        # CPU Information
        cpu_info = info['cpu']
        print(f"{Colors.colorize('🖥️  CPU USAGE', Colors.CYAN)}")
        print(f"   Cores: {cpu_info['count']} | Frequency: {cpu_info['frequency']:.0f} MHz")
        print(f"   Usage: {self.create_progress_bar(cpu_info['percent'])}")
        print()
        
        # Memory Information
        mem_info = info['memory']
        print(f"{Colors.colorize('🧠 MEMORY USAGE', Colors.CYAN)}")
        print(f"   Total: {self.format_bytes(mem_info['total'])} | Available: {self.format_bytes(mem_info['available'])}")
        print(f"   Used:  {self.create_progress_bar(mem_info['percent'])}")
        print(f"   Cache: {self.format_bytes(mem_info.get('cached', 0))} | Buffers: {self.format_bytes(mem_info.get('buffers', 0))}")
        
        # Swap Information
        swap_info = info['swap']
        if swap_info['total'] > 0:
            print(f"   Swap:  {self.create_progress_bar(swap_info['percent'])} ({self.format_bytes(swap_info['used'])}/{self.format_bytes(swap_info['total'])})")
        print()
        
        # Disk Information
        disk_info = info['disk']
        print(f"{Colors.colorize('💾 DISK USAGE', Colors.CYAN)}")
        print(f"   Total: {self.format_bytes(disk_info['total'])} | Free: {self.format_bytes(disk_info['free'])}")
        print(f"   Used:  {self.create_progress_bar(disk_info['percent'])}")
        print()
        
        # Network Information
        net_info = info['network']
        print(f"{Colors.colorize('🌐 NETWORK I/O', Colors.CYAN)}")
        print(f"   Sent: {self.format_bytes(net_info['bytes_sent'])} | Received: {self.format_bytes(net_info['bytes_recv'])}")
        print(f"   Packets: {net_info['packets_sent']} sent | {net_info['packets_recv']} received")
        print()
        
        # Top Processes
        print(f"{Colors.colorize('🔥 TOP MEMORY PROCESSES', Colors.CYAN)}")
        print(f"{'PID':<8} {'NAME':<20} {'CPU%':<8} {'MEM%':<8} {'MEMORY':<10}")
        print(f"{Colors.colorize('-' * 60, Colors.WHITE)}")
        
        for proc in info['processes'][:8]:
            try:
                memory_mb = proc.get('memory_info', {}).get('rss', 0) / 1024 / 1024
                cpu_color = Colors.RED if proc.get('cpu_percent', 0) > 50 else Colors.GREEN
                mem_color = Colors.RED if proc.get('memory_percent', 0) > 10 else Colors.GREEN
                
                cpu_pct = f"{proc.get('cpu_percent', 0):.1f}%"
                mem_pct = f"{proc.get('memory_percent', 0):.1f}%"
                print(f"{proc.get('pid', 0):<8} "
                      f"{proc.get('name', 'Unknown')[:19]:<20} "
                      f"{Colors.colorize(cpu_pct, cpu_color):<15} "
                      f"{Colors.colorize(mem_pct, mem_color):<15} "
                      f"{memory_mb:.1f} MB")
            except Exception:
                continue
        
        print()
        print(f"{Colors.colorize('⌨️  CONTROLS', Colors.YELLOW)}")
        print(f"   {Colors.colorize('Ctrl+C', Colors.WHITE)}: Exit | {Colors.colorize('q', Colors.WHITE)}: Quit | {Colors.colorize('c', Colors.WHITE)}: Clear Cache | {Colors.colorize('k', Colors.WHITE)}: Kill Process")
        print(f"{Colors.colorize('=' * 80, Colors.BLUE)}")
    
    def clear_system_cache(self) -> Dict[str, int]:
        """Clear system cache and return freed space"""
        print(f"\n{Colors.colorize('🧹 CLEARING SYSTEM CACHE...', Colors.BLUE)}")
        
        freed_space = {
            'temp_files': 0,
            'browser_cache': 0,
            'vscode_cache': 0,
            'system_cache': 0,
            'ram_cache': 0
        }
        
        try:
            # Clear temporary files
            print(f"{Colors.colorize('📁 Clearing temporary files...', Colors.YELLOW)}")
            temp_dirs = ['/tmp', '/var/tmp', str(self.home_dir / '.cache')]
            
            for temp_dir in temp_dirs:
                if os.path.exists(temp_dir):
                    try:
                        size_before = self._get_dir_size(temp_dir)
                        if temp_dir.startswith('/var') or temp_dir.startswith('/tmp'):
                            # System directories need sudo
                            subprocess.run(['sudo', 'find', temp_dir, '-type', 'f', '-atime', '+1', '-delete'], 
                                         capture_output=True, check=False)
                        else:
                            # User directories
                            for root, dirs, files in os.walk(temp_dir):
                                for file in files:
                                    try:
                                        file_path = os.path.join(root, file)
                                        if os.path.getmtime(file_path) < time.time() - 86400:  # 1 day old
                                            os.remove(file_path)
                                    except Exception:
                                        continue
                        
                        size_after = self._get_dir_size(temp_dir)
                        freed_space['temp_files'] += max(0, size_before - size_after)
                    except Exception as e:
                        print(f"{Colors.colorize(f'Warning: Could not clear {temp_dir}: {e}', Colors.YELLOW)}")
            
            # Clear browser cache
            print(f"{Colors.colorize('🌐 Clearing browser cache...', Colors.YELLOW)}")
            browser_cache_dirs = [
                self.home_dir / '.cache/google-chrome',
                self.home_dir / '.cache/chromium',
                self.home_dir / '.cache/mozilla',
                self.home_dir / '.cache/opera',
                self.home_dir / '.cache/brave'
            ]
            
            for cache_dir in browser_cache_dirs:
                if cache_dir.exists():
                    try:
                        size_before = self._get_dir_size(str(cache_dir))
                        shutil.rmtree(cache_dir, ignore_errors=True)
                        freed_space['browser_cache'] += size_before
                    except Exception:
                        continue
            
            # Clear VS Code cache
            print(f"{Colors.colorize('🔧 Clearing VS Code cache...', Colors.YELLOW)}")
            freed_space['vscode_cache'] = self._clear_vscode_cache()
            
            # Clear system package cache
            print(f"{Colors.colorize('📦 Clearing package cache...', Colors.YELLOW)}")
            try:
                subprocess.run(['sudo', 'apt-get', 'clean'], capture_output=True, check=False)
                subprocess.run(['sudo', 'apt-get', 'autoclean'], capture_output=True, check=False)
                subprocess.run(['sudo', 'journalctl', '--vacuum-time=3d'], capture_output=True, check=False)
            except Exception:
                pass
            
            # Clear RAM cache
            print(f"{Colors.colorize('🧠 Clearing RAM cache...', Colors.YELLOW)}")
            freed_space['ram_cache'] = self._clear_ram_cache()
            
        except Exception as e:
            print(f"{Colors.colorize(f'Error during cache clearing: {e}', Colors.RED)}")
        
        return freed_space
    
    def _get_dir_size(self, path: str) -> int:
        """Get directory size in bytes"""
        try:
            total_size = 0
            for dirpath, dirnames, filenames in os.walk(path):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    try:
                        total_size += os.path.getsize(filepath)
                    except (OSError, FileNotFoundError):
                        continue
            return total_size
        except Exception:
            return 0
    
    def _clear_vscode_cache(self) -> int:
        """Clear VS Code cache and return freed space"""
        total_freed = 0
        
        vscode_cache_paths = [
            self.home_dir / '.vscode/logs',
            self.home_dir / '.vscode/CachedExtensions',
            self.home_dir / '.vscode/CachedExtensionVSIXs',
            self.home_dir / '.config/Code/logs',
            self.home_dir / '.config/Code/CachedData',
            self.home_dir / '.config/Code/CachedExtensions',
            self.home_dir / '.config/Code/CachedExtensionVSIXs',
            self.home_dir / '.config/Code-NoAI/logs'
        ]
        
        for cache_path in vscode_cache_paths:
            if cache_path.exists():
                try:
                    size_before = self._get_dir_size(str(cache_path))
                    shutil.rmtree(cache_path, ignore_errors=True)
                    total_freed += size_before
                except Exception:
                    continue
        
        # Clear extension logs within extensions directory
        extensions_dir = self.home_dir / '.vscode/extensions'
        if extensions_dir.exists():
            try:
                for ext_dir in extensions_dir.iterdir():
                    if ext_dir.is_dir():
                        for log_file in ext_dir.rglob('*.log'):
                            try:
                                total_freed += log_file.stat().st_size
                                log_file.unlink()
                            except Exception:
                                continue
            except Exception:
                pass
        
        return total_freed
    
    def _clear_ram_cache(self) -> int:
        """Clear RAM cache and return freed memory"""
        try:
            # Get memory before
            mem_before = psutil.virtual_memory().available
            
            # Sync filesystems
            subprocess.run(['sync'], check=False)
            
            # Clear caches
            subprocess.run(['sudo', 'sh', '-c', 'echo 1 > /proc/sys/vm/drop_caches'], check=False)
            subprocess.run(['sudo', 'sh', '-c', 'echo 2 > /proc/sys/vm/drop_caches'], check=False)
            subprocess.run(['sudo', 'sh', '-c', 'echo 3 > /proc/sys/vm/drop_caches'], check=False)
            
            time.sleep(2)
            
            # Get memory after
            mem_after = psutil.virtual_memory().available
            
            return max(0, mem_after - mem_before)
        except Exception:
            return 0
    
    def kill_process_interactive(self):
        """Interactive process killer"""
        print(f"\n{Colors.colorize('🔪 PROCESS KILLER', Colors.RED)}")
        print(f"{Colors.colorize('=' * 50, Colors.WHITE)}")
        
        # Show top processes
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                processes.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        processes.sort(key=lambda x: x.get('memory_percent', 0), reverse=True)
        
        print(f"{'PID':<8} {'NAME':<25} {'CPU%':<8} {'MEM%':<8}")
        print(f"{Colors.colorize('-' * 50, Colors.WHITE)}")
        
        for i, proc in enumerate(processes[:15]):
            print(f"{proc.get('pid', 0):<8} "
                  f"{proc.get('name', 'Unknown')[:24]:<25} "
                  f"{proc.get('cpu_percent', 0):.1f}%{'':<3} "
                  f"{proc.get('memory_percent', 0):.1f}%")
        
        print(f"\n{Colors.colorize('Enter PID or process name to kill (or press Enter to cancel):', Colors.YELLOW)}")
        target = input().strip()
        
        if not target:
            return
        
        try:
            if target.isdigit():
                # Kill by PID
                pid = int(target)
                proc = psutil.Process(pid)
                proc_name = proc.name()
                proc.terminate()
                time.sleep(2)
                if proc.is_running():
                    proc.kill()
                print(f"{Colors.colorize(f'✅ Killed process: {proc_name} (PID: {pid})', Colors.GREEN)}")
            else:
                # Kill by name
                killed_count = 0
                for proc in psutil.process_iter(['pid', 'name']):
                    try:
                        if target.lower() in proc.info['name'].lower():
                            proc.terminate()
                            time.sleep(1)
                            if proc.is_running():
                                proc.kill()
                            killed_count += 1
                            proc_name = proc.info['name']
                            proc_pid = proc.info['pid']
                            print(f"{Colors.colorize(f'✅ Killed: {proc_name} (PID: {proc_pid})', Colors.GREEN)}")
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
                
                if killed_count == 0:
                    print(f"{Colors.colorize(f'❌ No processes found matching: {target}', Colors.RED)}")
                else:
                    print(f"{Colors.colorize(f'✅ Killed {killed_count} processes', Colors.GREEN)}")
                    
        except Exception as e:
            print(f"{Colors.colorize(f'❌ Error killing process: {e}', Colors.RED)}")
        
        input(f"\n{Colors.colorize('Press Enter to continue...', Colors.YELLOW)}")
    
    def run_interactive_mode(self):
        """Run the interactive monitoring mode"""
        signal.signal(signal.SIGINT, self.signal_handler)
        
        print(f"{Colors.colorize('🚀 Starting Coderex System Monitor...', Colors.GREEN)}")
        print(f"{Colors.colorize('Press Ctrl+C to exit', Colors.YELLOW)}")
        time.sleep(2)
        
        try:
            while self.running:
                info = self.get_system_info()
                if info:
                    self.display_system_info(info)
                    
                    # Store history
                    self.cpu_history.append(info['cpu']['percent'])
                    self.memory_history.append(info['memory']['percent'])
                    
                    # Limit history size
                    if len(self.cpu_history) > self.history_size:
                        self.cpu_history.pop(0)
                    if len(self.memory_history) > self.history_size:
                        self.memory_history.pop(0)
                
                # Check for user input (non-blocking)
                import select
                if select.select([sys.stdin], [], [], 0.1)[0]:
                    key = sys.stdin.read(1)
                    if key.lower() == 'q':
                        break
                    elif key.lower() == 'c':
                        freed = self.clear_system_cache()
                        total_freed = sum(freed.values())
                        print(f"\n{Colors.colorize(f'✅ Cache cleared! Total freed: {self.format_bytes(total_freed)}', Colors.GREEN)}")
                        input(f"{Colors.colorize('Press Enter to continue...', Colors.YELLOW)}")
                    elif key.lower() == 'k':
                        self.kill_process_interactive()
                
                time.sleep(self.update_interval)
                
        except KeyboardInterrupt:
            pass
        finally:
            self.running = False
            print(f"\n{Colors.colorize('👋 System Monitor stopped.', Colors.GREEN)}")
    
    def run_menu_mode(self):
        """Run the menu-based mode (like the original linux-boost.sh)"""
        while True:
            os.system('clear')
            print(f"{Colors.colorize('🚀 CODEREX SYSTEM MONITOR - MENU MODE', Colors.CYAN)}")
            print(f"{Colors.colorize('=' * 60, Colors.BLUE)}")
            print()
            print("1. 📊 Live System Monitor")
            print("2. 🧹 Clear All Cache")
            print("3. 🔪 Kill Heavy Processes")
            print("4. 🌐 Kill Browsers (except Firefox)")
            print("5. 🔧 Clear VS Code Cache")
            print("6. 🧠 Clear RAM Cache")
            print("7. 📁 Clear Temporary Files")
            print("8. 🚀 Start VS Code (All Extensions)")
            print("9. 🎯 Start VS Code (No AI Extensions)")
            print("0. ❌ Exit")
            print()
            print(f"{Colors.colorize('=' * 60, Colors.BLUE)}")
            
            choice = input(f"{Colors.colorize('Select option (0-9): ', Colors.YELLOW)}")
            
            if choice == '0':
                print(f"{Colors.colorize('👋 Goodbye!', Colors.GREEN)}")
                break
            elif choice == '1':
                self.run_interactive_mode()
            elif choice == '2':
                freed = self.clear_system_cache()
                total_freed = sum(freed.values())
                print(f"\n{Colors.colorize('✅ CACHE CLEARING COMPLETE!', Colors.GREEN)}")
                print(f"   Temp files: {self.format_bytes(freed['temp_files'])}")
                print(f"   Browser cache: {self.format_bytes(freed['browser_cache'])}")
                print(f"   VS Code cache: {self.format_bytes(freed['vscode_cache'])}")
                print(f"   RAM cache: {self.format_bytes(freed['ram_cache'])}")
                print(f"   {Colors.colorize(f'Total freed: {self.format_bytes(total_freed)}', Colors.CYAN)}")
                input(f"\n{Colors.colorize('Press Enter to continue...', Colors.YELLOW)}")
            elif choice == '3':
                self.kill_process_interactive()
            elif choice == '4':
                self._kill_browsers()
            elif choice == '5':
                freed = self._clear_vscode_cache()
                print(f"{Colors.colorize(f'✅ VS Code cache cleared! Freed: {self.format_bytes(freed)}', Colors.GREEN)}")
                input(f"{Colors.colorize('Press Enter to continue...', Colors.YELLOW)}")
            elif choice == '6':
                freed = self._clear_ram_cache()
                print(f"{Colors.colorize(f'✅ RAM cache cleared! Freed: {self.format_bytes(freed)}', Colors.GREEN)}")
                input(f"{Colors.colorize('Press Enter to continue...', Colors.YELLOW)}")
            elif choice == '7':
                self._clear_temp_files()
            elif choice == '8':
                self._start_vscode(with_ai=True)
            elif choice == '9':
                self._start_vscode(with_ai=False)
            else:
                print(f"{Colors.colorize('❌ Invalid option!', Colors.RED)}")
                time.sleep(1)
    
    def _kill_browsers(self):
        """Kill browsers except Firefox and VS Code"""
        print(f"\n{Colors.colorize('🌐 Killing browsers (except Firefox and VS Code)...', Colors.BLUE)}")
        
        browsers = [
            'chrome', 'chromium', 'chromium-browser', 'opera', 'opera-stable',
            'brave', 'brave-browser', 'microsoft-edge', 'edge', 'vivaldi',
            'safari', 'waterfox', 'palemoon', 'seamonkey', 'epiphany'
        ]
        
        killed_count = 0
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                proc_name = proc.info['name'].lower()
                if any(browser in proc_name for browser in browsers):
                    if 'firefox' not in proc_name and 'code' not in proc_name:
                        proc.terminate()
                        time.sleep(1)
                        if proc.is_running():
                            proc.kill()
                        killed_count += 1
                        proc_name = proc.info['name']
                        proc_pid = proc.info['pid']
                        print(f"{Colors.colorize(f'✅ Killed: {proc_name} (PID: {proc_pid})', Colors.GREEN)}")
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        if killed_count == 0:
            print(f"{Colors.colorize('✅ No browsers found to kill', Colors.GREEN)}")
        else:
            print(f"{Colors.colorize(f'✅ Killed {killed_count} browser processes', Colors.GREEN)}")
        
        input(f"\n{Colors.colorize('Press Enter to continue...', Colors.YELLOW)}")
    
    def _clear_temp_files(self):
        """Clear temporary files"""
        print(f"\n{Colors.colorize('📁 Clearing temporary files...', Colors.BLUE)}")
        
        temp_dirs = ['/tmp', '/var/tmp', str(self.home_dir / '.cache')]
        total_freed = 0
        
        for temp_dir in temp_dirs:
            if os.path.exists(temp_dir):
                try:
                    size_before = self._get_dir_size(temp_dir)
                    if temp_dir.startswith('/var') or temp_dir.startswith('/tmp'):
                        subprocess.run(['sudo', 'find', temp_dir, '-type', 'f', '-atime', '+1', '-delete'], 
                                     capture_output=True, check=False)
                    else:
                        for root, dirs, files in os.walk(temp_dir):
                            for file in files:
                                try:
                                    file_path = os.path.join(root, file)
                                    if os.path.getmtime(file_path) < time.time() - 86400:
                                        os.remove(file_path)
                                except Exception:
                                    continue
                    
                    size_after = self._get_dir_size(temp_dir)
                    freed = max(0, size_before - size_after)
                    total_freed += freed
                    print(f"{Colors.colorize(f'✅ Cleared {temp_dir}: {self.format_bytes(freed)}', Colors.GREEN)}")
                except Exception as e:
                    print(f"{Colors.colorize(f'❌ Error clearing {temp_dir}: {e}', Colors.RED)}")
        
        print(f"\n{Colors.colorize(f'✅ Total freed: {self.format_bytes(total_freed)}', Colors.CYAN)}")
        input(f"{Colors.colorize('Press Enter to continue...', Colors.YELLOW)}")
    
    def _start_vscode(self, with_ai: bool = True):
        """Start VS Code with or without AI extensions"""
        print(f"\n{Colors.colorize('🚀 Starting VS Code...', Colors.BLUE)}")
        
        try:
            if with_ai:
                subprocess.Popen(['code', str(self.coderex_dir)], 
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                print(f"{Colors.colorize('✅ VS Code started with all extensions', Colors.GREEN)}")
            else:
                # Use the no-AI profile
                profile_dir = self.home_dir / '.config/Code-NoAI'
                profile_dir.mkdir(parents=True, exist_ok=True)
                
                # Create settings if they don't exist
                settings_file = profile_dir / 'User/settings.json'
                settings_file.parent.mkdir(parents=True, exist_ok=True)
                
                if not settings_file.exists():
                    settings = {
                        "extensions.autoCheckUpdates": False,
                        "extensions.autoUpdate": False,
                        "editor.inlineSuggest.enabled": False,
                        "editor.quickSuggestions": {"other": False, "comments": False, "strings": False},
                        "editor.suggestOnTriggerCharacters": False,
                        "editor.acceptSuggestionOnEnter": "off",
                        "editor.tabCompletion": "off",
                        "editor.wordBasedSuggestions": False,
                        "editor.parameterHints.enabled": False
                    }
                    
                    with open(settings_file, 'w') as f:
                        json.dump(settings, f, indent=2)
                
                # Start VS Code with clean profile
                subprocess.Popen(['code', '--user-data-dir', str(profile_dir), str(self.coderex_dir)],
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                print(f"{Colors.colorize('✅ VS Code started without AI extensions', Colors.GREEN)}")
                
        except Exception as e:
            print(f"{Colors.colorize(f'❌ Error starting VS Code: {e}', Colors.RED)}")
        
        input(f"{Colors.colorize('Press Enter to continue...', Colors.YELLOW)}")

# ============================================================================
# DEMO FUNCTIONS (from demo_system_monitor.py)
# ============================================================================

def demo_live_monitoring():
    """Demonstrate live system monitoring"""
    print(f"{Colors.colorize('🚀 CODEREX SYSTEM MONITOR DEMO', Colors.CYAN)}")
    print(f"{Colors.colorize('=' * 60, Colors.BLUE)}")
    print(f"{Colors.colorize('Press Ctrl+C to exit', Colors.YELLOW)}")
    print()
    
    monitor = SystemMonitor()
    
    try:
        for i in range(30):  # Run for 30 seconds
            info = monitor.get_system_info()
            if info:
                monitor.display_system_info(info)
                print(f"{Colors.colorize(f'Demo cycle {i+1}/30 - Press Ctrl+C to exit early', Colors.YELLOW)}")
            time.sleep(2)  # Update every 2 seconds for demo
    except KeyboardInterrupt:
        print(f"\n{Colors.colorize('👋 Demo stopped by user', Colors.GREEN)}")

def demo_system_info():
    """Demonstrate system information display"""
    print(f"{Colors.colorize('📊 SYSTEM INFORMATION DEMO', Colors.CYAN)}")
    print(f"{Colors.colorize('=' * 60, Colors.BLUE)}")
    
    monitor = SystemMonitor()
    info = monitor.get_system_info()
    
    if info:
        monitor.display_system_info(info)
    
    print(f"\n{Colors.colorize('✅ System information displayed successfully!', Colors.GREEN)}")

def demo_progress_bars():
    """Demonstrate progress bar functionality"""
    print(f"{Colors.colorize('📊 PROGRESS BAR DEMO', Colors.CYAN)}")
    print(f"{Colors.colorize('=' * 60, Colors.BLUE)}")
    
    monitor = SystemMonitor()
    
    print("CPU Usage Examples:")
    for cpu in [15, 45, 75, 95]:
        bar = monitor.create_progress_bar(cpu, 40)
        print(f"  {bar}")
    
    print("\nMemory Usage Examples:")
    for mem in [25, 50, 80, 90]:
        bar = monitor.create_progress_bar(mem, 40)
        print(f"  {bar}")
    
    print(f"\n{Colors.colorize('✅ Progress bars displayed successfully!', Colors.GREEN)}")

def demo_byte_formatting():
    """Demonstrate byte formatting"""
    print(f"{Colors.colorize('💾 BYTE FORMATTING DEMO', Colors.CYAN)}")
    print(f"{Colors.colorize('=' * 60, Colors.BLUE)}")
    
    monitor = SystemMonitor()
    
    sizes = [
        512,                    # 512 B
        1024,                   # 1 KB
        1024 * 1024,           # 1 MB
        1024 * 1024 * 1024,    # 1 GB
        1024 * 1024 * 1024 * 1024  # 1 TB
    ]
    
    for size in sizes:
        formatted = monitor.format_bytes(size)
        print(f"  {size:>15,} bytes = {Colors.colorize(formatted, Colors.GREEN)}")
    
    print(f"\n{Colors.colorize('✅ Byte formatting displayed successfully!', Colors.GREEN)}")

# ============================================================================
# TEST CLASSES (from test_system_monitor.py)
# ============================================================================

class TestSystemMonitor(unittest.TestCase):
    """Test cases for SystemMonitor class"""
    
    def setUp(self):
        """Set up test environment"""
        self.monitor = SystemMonitor()
        self.test_dir = Path(tempfile.mkdtemp())
        self.original_home = self.monitor.home_dir
        self.monitor.home_dir = self.test_dir
        
    def tearDown(self):
        """Clean up test environment"""
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir, ignore_errors=True)
        self.monitor.home_dir = self.original_home
    
    def test_colors_class(self):
        """Test Colors class functionality"""
        # Test colorize method
        colored_text = Colors.colorize("test", Colors.RED)
        self.assertIn(Colors.RED, colored_text)
        self.assertIn(Colors.NC, colored_text)
        self.assertIn("test", colored_text)
    
    def test_format_bytes(self):
        """Test byte formatting function"""
        # Test various byte sizes
        self.assertEqual(self.monitor.format_bytes(512), "512.0 B")
        self.assertEqual(self.monitor.format_bytes(1024), "1.0 KB")
        self.assertEqual(self.monitor.format_bytes(1024 * 1024), "1.0 MB")
        self.assertEqual(self.monitor.format_bytes(1024 * 1024 * 1024), "1.0 GB")
    
    def test_create_progress_bar(self):
        """Test progress bar creation"""
        # Test different percentages
        bar_0 = self.monitor.create_progress_bar(0, 10)
        bar_50 = self.monitor.create_progress_bar(50, 10)
        bar_100 = self.monitor.create_progress_bar(100, 10)
        
        self.assertIn("0.0%", bar_0)
        self.assertIn("50.0%", bar_50)
        self.assertIn("100.0%", bar_100)
        
        # Test bar length
        self.assertIn("░" * 10, bar_0)  # All empty
        self.assertIn("█" * 10, bar_100)  # All filled

class TestSystemMonitorIntegration(unittest.TestCase):
    """Integration tests for the complete system"""
    
    def setUp(self):
        """Set up integration test environment"""
        self.monitor = SystemMonitor()
    
    def test_system_info_integration(self):
        """Test complete system information gathering"""
        info = self.monitor.get_system_info()
        
        # Verify we get real system data
        self.assertIsInstance(info, dict)
        self.assertIn('cpu', info)
        self.assertIn('memory', info)
        
        # Verify data types and ranges
        self.assertIsInstance(info['cpu']['percent'], (int, float))
        self.assertGreaterEqual(info['cpu']['percent'], 0)
        self.assertLessEqual(info['cpu']['percent'], 100)

class TestSystemMonitorPerformance(unittest.TestCase):
    """Performance tests for the system monitor"""
    
    def setUp(self):
        """Set up performance test environment"""
        self.monitor = SystemMonitor()
    
    def test_system_info_performance(self):
        """Test system information gathering performance"""
        start_time = time.time()
        
        # Get system info multiple times
        for _ in range(10):
            info = self.monitor.get_system_info()
            self.assertIsInstance(info, dict)
        
        end_time = time.time()
        avg_time = (end_time - start_time) / 10
        
        # Should take less than 0.5 seconds per call
        self.assertLess(avg_time, 0.5, f"System info gathering too slow: {avg_time:.3f}s")

def run_comprehensive_tests():
    """Run all tests and generate a comprehensive report"""
    print(f"{Colors.colorize('🧪 STARTING COMPREHENSIVE TEST SUITE', Colors.CYAN)}")
    print(f"{Colors.colorize('=' * 60, Colors.BLUE)}")
    print()
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add all test classes
    test_classes = [
        TestSystemMonitor,
        TestSystemMonitorIntegration,
        TestSystemMonitorPerformance
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    result = runner.run(test_suite)
    
    # Generate test report
    print(f"\n{Colors.colorize('📊 TEST RESULTS SUMMARY', Colors.CYAN)}")
    print(f"{Colors.colorize('=' * 60, Colors.BLUE)}")
    
    total_tests = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    skipped = len(result.skipped) if hasattr(result, 'skipped') else 0
    passed = total_tests - failures - errors - skipped
    
    print(f"Total Tests: {Colors.colorize(str(total_tests), Colors.WHITE)}")
    print(f"Passed: {Colors.colorize(str(passed), Colors.GREEN)}")
    print(f"Failed: {Colors.colorize(str(failures), Colors.RED if failures > 0 else Colors.GREEN)}")
    print(f"Errors: {Colors.colorize(str(errors), Colors.RED if errors > 0 else Colors.GREEN)}")
    print(f"Skipped: {Colors.colorize(str(skipped), Colors.YELLOW if skipped > 0 else Colors.GREEN)}")
    
    success_rate = (passed / total_tests) * 100 if total_tests > 0 else 0
    print(f"Success Rate: {Colors.colorize(f'{success_rate:.1f}%', Colors.GREEN if success_rate >= 90 else Colors.YELLOW)}")
    
    # Overall result
    print(f"\n{Colors.colorize('🎯 OVERALL RESULT:', Colors.CYAN)}")
    if failures == 0 and errors == 0:
        print(f"{Colors.colorize('✅ ALL TESTS PASSED! System is ready for production.', Colors.GREEN)}")
        return True
    else:
        print(f"{Colors.colorize('❌ SOME TESTS FAILED! Please fix issues before deployment.', Colors.RED)}")
        return False

# ============================================================================
# MAIN FUNCTION AND COMMAND LINE INTERFACE
# ============================================================================

def main():
    """Main function with comprehensive command line interface"""
    parser = argparse.ArgumentParser(description='Coderex Combined Python Utilities v2.0')
    parser.add_argument('--mode', choices=['live', 'menu', 'demo', 'test'], default='menu',
                       help='Run mode: live (continuous monitoring), menu (interactive menu), demo (demonstrations), test (run tests)')
    parser.add_argument('--demo-type', choices=['live', 'info', 'bars', 'bytes', 'all'], default='all',
                       help='Demo type to run (only used with --mode demo)')
    parser.add_argument('--interval', type=float, default=1.0,
                       help='Update interval in seconds for live mode (default: 1.0)')
    
    args = parser.parse_args()
    
    # Check if running as root (not recommended)
    if os.geteuid() == 0:
        print(f"{Colors.colorize('⚠️  Warning: Running as root is not recommended!', Colors.YELLOW)}")
        print(f"{Colors.colorize('   Some features may not work correctly.', Colors.YELLOW)}")
        time.sleep(2)
    
    try:
        if args.mode == 'test':
            # Run comprehensive tests
            print(f"{Colors.colorize('🧪 RUNNING COMPREHENSIVE TEST SUITE', Colors.CYAN)}")
            success = run_comprehensive_tests()
            sys.exit(0 if success else 1)
            
        elif args.mode == 'demo':
            # Run demonstrations
            print(f"{Colors.colorize('🎬 RUNNING SYSTEM MONITOR DEMONSTRATIONS', Colors.CYAN)}")
            
            if args.demo_type == 'live':
                demo_live_monitoring()
            elif args.demo_type == 'info':
                demo_system_info()
            elif args.demo_type == 'bars':
                demo_progress_bars()
            elif args.demo_type == 'bytes':
                demo_byte_formatting()
            else:
                # Run all demos
                demo_system_info()
                input(f"\n{Colors.colorize('Press Enter to continue to progress bar demo...', Colors.YELLOW)}")
                demo_progress_bars()
                input(f"\n{Colors.colorize('Press Enter to continue to byte formatting demo...', Colors.YELLOW)}")
                demo_byte_formatting()
                input(f"\n{Colors.colorize('Press Enter to start live monitoring demo...', Colors.YELLOW)}")
                demo_live_monitoring()
                
        else:
            # Initialize monitor
            monitor = SystemMonitor()
            monitor.update_interval = args.interval
            
            if args.mode == 'live':
                monitor.run_interactive_mode()
            else:
                monitor.run_menu_mode()
                
    except KeyboardInterrupt:
        print(f"\n{Colors.colorize('👋 Interrupted by user', Colors.YELLOW)}")
    except Exception as e:
        print(f"{Colors.colorize(f'❌ Unexpected error: {e}', Colors.RED)}")
        sys.exit(1)

# ============================================================================
# SCRIPT EXECUTION
# ============================================================================

if __name__ == "__main__":
    # Check for required dependencies
    try:
        import psutil
    except ImportError:
        print(f"{Colors.colorize('❌ Error: psutil not installed. Installing...', Colors.RED)}")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'psutil'], check=True)
        import psutil
    
    # Display header
    print(f"{Colors.colorize('🐍 CODEREX COMBINED PYTHON UTILITIES', Colors.CYAN)}")
    print(f"{Colors.colorize('=' * 60, Colors.BLUE)}")
    print(f"{Colors.colorize('All Python functionality from util folder in one script', Colors.WHITE)}")
    print(f"{Colors.colorize('Includes: SystemMonitor, Demo, Tests', Colors.YELLOW)}")
    print(f"{Colors.colorize('=' * 60, Colors.BLUE)}")
    print()
    
    # Run main function
    main()

# End of Combined Python Scripts
# All Python files from util folder have been successfully combined into this comprehensive script.