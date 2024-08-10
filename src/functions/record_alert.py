import time
import os

def record_alert(alert_type, current_time, alerts):
    log_dir = os.path.join(os.path.dirname(__file__), '../../logs')
    alert_file = os.path.join(log_dir, f'alert_{alert_type}.txt')

    if alert_type not in alerts:
        alerts[alert_type] = current_time
        with open(alert_file, 'w') as file:
            file.write(f"Alerte de type {alert_type} commencée à {time.ctime(current_time)}\n")
    else:
        duration = round(current_time - alerts[alert_type], 2)
        with open(alert_file, 'a') as file:
            file.write(f"Alerte active depuis {duration} secondes.\n")
