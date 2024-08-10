import time
from functions.monitor_system import monitor_system

alerts = {}

if __name__ == "__main__":
    while True:
        monitor_system(alerts)
        time.sleep(10)
