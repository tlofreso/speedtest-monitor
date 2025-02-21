import speedtest
import time
import logging
from datetime import datetime, UTC
from prometheus_client import start_http_server, Gauge
from typing import Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='speedtest.log'
)

# Define Prometheus metrics
DOWNLOAD_SPEED = Gauge('network_speed_download_mbps', 'Download speed in Mbps')
UPLOAD_SPEED = Gauge('network_speed_upload_mbps', 'Upload speed in Mbps')
PING = Gauge('network_latency_ms', 'Network latency in milliseconds')

class SpeedTestMonitor:
    def __init__(self):
        self.speed_test = speedtest.Speedtest()

    def perform_test(self) -> Dict[str, Any]:
        """Performs a speed test and updates Prometheus metrics."""
        try:
            logging.info("Starting speed test...")
            
            # Get best server
            self.speed_test.get_best_server()
            
            # Test download speed (bits/s)
            download_speed = self.speed_test.download()
            
            # Test upload speed (bits/s)
            upload_speed = self.speed_test.upload()
            
            # Get ping (ms)
            ping = self.speed_test.results.ping
            
            # Convert to Mbps
            download_mbps = download_speed / 1_000_000
            upload_mbps = upload_speed / 1_000_000
            
            # Update Prometheus metrics
            DOWNLOAD_SPEED.set(download_mbps)
            UPLOAD_SPEED.set(upload_mbps)
            PING.set(ping)
            
            results = {
                'timestamp': datetime.now(UTC).isoformat(),
                'download_mbps': download_mbps,
                'upload_mbps': upload_mbps,
                'ping_ms': ping
            }
            
            logging.info(f"Speed test completed: {results}")
            return results
            
        except Exception as e:
            logging.error(f"Error during speed test: {e}")
            raise

def main():
    # Configuration
    PROMETHEUS_PORT = 9516  # Port for speedtest metrics
    TEST_INTERVAL = 600   # Run test every hour (in seconds)
    
    # Start Prometheus HTTP server
    start_http_server(PROMETHEUS_PORT)
    logging.info(f"Prometheus metrics server started on port {PROMETHEUS_PORT}")
    
    monitor = SpeedTestMonitor()
    
    while True:
        try:
            monitor.perform_test()
        except Exception as e:
            logging.error(f"Error in main loop: {e}")
        finally:
            time.sleep(TEST_INTERVAL)

if __name__ == "__main__":
    main()