import requests
import psutil
import time
from datetime import datetime

# Configuration
API_ENDPOINT = 'http://monitoringserverdncprivate.azurewebsites.net/api/metrics'
CLIENT_NAME = 'My Computer'  # Change this to identify your machine
INTERVAL_SECONDS = 5  # Time between metric submissions

def get_system_metrics():
    """Collect current system metrics."""
    return {
        'timestamp': datetime.now().isoformat(),
        'cpu_percent': psutil.cpu_percent(interval=1),
        'ram': {
            'used_gb': round(psutil.virtual_memory().used / (1024**3), 2),
            'total_gb': round(psutil.virtual_memory().total / (1024**3), 2),
            'percent': psutil.virtual_memory().percent
        },
        'client_name': CLIENT_NAME
    }

def send_metrics():
    """Send metrics to the monitoring server."""
    try:
        metrics = get_system_metrics()
        
        response = requests.post(
            API_ENDPOINT,
            json=metrics,
            timeout=10
        )
        
        response.raise_for_status()
        
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Metrics sent successfully")
        print(f"  CPU: {metrics['cpu_percent']}% | RAM: {metrics['ram']['percent']}%")
        
        return response.json()
        
    except requests.exceptions.RequestException as e:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Error sending metrics: {e}")
        return None
    except Exception as e:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Unexpected error: {e}")
        return None

def main():
    """Main loop to continuously send metrics."""
    print(f"Starting metrics monitor for '{CLIENT_NAME}'")
    print(f"Sending metrics every {INTERVAL_SECONDS} seconds to {API_ENDPOINT}")
    print("Press Ctrl+C to stop\n")
    
    try:
        while True:
            send_metrics()
            time.sleep(INTERVAL_SECONDS)
            
    except KeyboardInterrupt:
        print("\n\nMetrics monitor stopped by user")

if __name__ == '__main__':
    main()