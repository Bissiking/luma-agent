import psutil
from .record_alert import record_alert
from ..config.thresholds import MEMORY_THRESHOLD, CPU_THRESHOLD

def monitor_system(alerts):
    current_time = time.time()
    mem = psutil.virtual_memory()
    cpu_load = psutil.getloadavg()[0]

    if mem.percent > MEMORY_THRESHOLD:
        record_alert('Mémoire', current_time, alerts)
    else:
        alerts.pop('Mémoire', None)

    if cpu_load > CPU_THRESHOLD:
        record_alert('CPU', current_time, alerts)
    else:
        alerts.pop('CPU', None)
