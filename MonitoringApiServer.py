import psutil
import requests
import time
import json
from datetime import datetime
import socket
import subprocess
import platform

class SystemMetricsMonitor:
    def __init__(self, api_url, interval=5):
        """
        Initialize the metrics monitor.
        
        Args:
            api_url: The URL endpoint to send metrics to
            interval: Time in seconds between metric collections (default: 5)
        """
        self.api_url = api_url
        self.interval = interval
        
    def get_cpu_usage(self):
        """Get current CPU usage percentage."""
        return psutil.cpu_percent(interval=1)
    
    def get_gpu_usage(self):
        """
        Get GPU usage. This is a simplified version.
        For NVIDIA GPUs, you'd need nvidia-smi or pynvml library.
        For other GPUs, different tools are needed.
        """
        try:
            # This is a placeholder - real implementation depends on your GPU
            # For NVIDIA: use nvidia-smi or pynvml
            # For AMD: use rocm-smi
            # For Intel: use intel_gpu_top
            if platform.system() == "Windows" or platform.system() == "Linux":
                # Attempt to get NVIDIA GPU usage via nvidia-smi
                result = subprocess.run(
                    ['nvidia-smi', '--query-gpu=utilization.gpu', '--format=csv,noheader,nounits'],
                    capture_output=True,
                    text=True,
                    timeout=2
                )
                if result.returncode == 0:
                    return float(result.stdout.strip())
        except Exception as e:
            pass
        
        return None  # GPU monitoring not available
    
    def get_ram_usage(self):
        """Get RAM usage information."""
        mem = psutil.virtual_memory()
        return {
            'total_gb': round(mem.total / (1024**3), 2),
            'used_gb': round(mem.used / (1024**3), 2),
            'available_gb': round(mem.available / (1024**3), 2),
            'percent': mem.percent
        }
    
    def get_ping(self, host='8.8.8.8'):
        """
        Get ping latency to a host (default: Google DNS).
        Returns latency in milliseconds or None if unreachable.
        """
        param = '-n' if platform.system().lower() == 'windows' else '-c'
        command = ['ping', param, '1', host]
        
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if platform.system().lower() == 'windows':
                # Parse Windows ping output
                for line in result.stdout.split('\n'):
                    if 'time=' in line.lower() or 'zeit=' in line.lower():
                        time_str = line.split('time=')[-1].split('ms')[0].strip()
                        return float(time_str)
            else:
                # Parse Unix/Linux ping output
                for line in result.stdout.split('\n'):
                    if 'time=' in line:
                        time_str = line.split('time=')[-1].split(' ')[0].strip()
                        return float(time_str)
        except Exception as e:
            print(f"Ping failed: {e}")
        
        return None
    
    def check_internet_connection(self):
        """Check if internet connection is available."""
        try:
            # Try to connect to Google DNS
            socket.create_connection(("8.8.8.8", 53), timeout=3)
            return True
        except OSError:
            return False
    
    def collect_metrics(self):
        """Collect all system metrics."""
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'cpu_percent': self.get_cpu_usage(),
            'gpu_percent': self.get_gpu_usage(),
            'ram': self.get_ram_usage(),
            'ping_ms': self.get_ping(),
            'internet_connected': self.check_internet_connection()
        }
        return metrics
    
    def send_metrics(self, metrics):
        """Send metrics to the configured API endpoint."""
        try:
            response = requests.post(
                self.api_url,
                json=metrics,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            response.raise_for_status()
            print(f"✓ Metrics sent successfully: {response.status_code}")
            return True
        except requests.exceptions.RequestException as e:
            print(f"✗ Failed to send metrics: {e}")
            return False
    
    def run(self):
        """Main monitoring loop."""
        print(f"Starting system metrics monitor...")
        print(f"Sending metrics to: {self.api_url}")
        print(f"Collection interval: {self.interval} seconds")
        print("Press Ctrl+C to stop\n")
        
        try:
            while True:
                # Collect metrics
                metrics = self.collect_metrics()
                
                # Display metrics
                print(f"\n--- Metrics at {metrics['timestamp']} ---")
                print(f"CPU Usage: {metrics['cpu_percent']}%")
                if metrics['gpu_percent'] is not None:
                    print(f"GPU Usage: {metrics['gpu_percent']}%")
                else:
                    print("GPU Usage: N/A")
                print(f"RAM Usage: {metrics['ram']['used_gb']}/{metrics['ram']['total_gb']} GB ({metrics['ram']['percent']}%)")
                print(f"Ping: {metrics['ping_ms']} ms" if metrics['ping_ms'] else "Ping: N/A")
                print(f"Internet: {'Connected' if metrics['internet_connected'] else 'Disconnected'}")
                
                # Send metrics
                self.send_metrics(metrics)
                
                # Wait for next collection
                time.sleep(self.interval)
                
        except KeyboardInterrupt:
            print("\n\nMonitoring stopped by user.")


if __name__ == "__main__":
    # Configuration
    API_URL = "https://your-website.com/api/metrics"  # Replace with your actual endpoint
    INTERVAL = 5  # seconds between collections
    
    # Create and run monitor
    monitor = SystemMetricsMonitor(api_url=API_URL, interval=INTERVAL)
    monitor.run()