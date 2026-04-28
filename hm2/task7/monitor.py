import time
import datetime
import os


LOG_FILE = "/var/log/system_stats.txt"


def get_cpu_usage():
    with open('/proc/stat', 'r') as f:
        line = f.readline()

    parts = line.split()
    user = int(parts[1])
    nice = int(parts[2])
    system = int(parts[3])
    idle = int(parts[4])
    iowait = int(parts[5])
    irq = int(parts[6])
    softirq = int(parts[7])
    steal = int(parts[8])
    guest = int(parts[9])
    guest_nice = int(parts[10])

    return {'total': user + nice + system + idle + iowait + irq + softirq + steal + guest + guest_nice, 'idle': idle}


def get_cpu_data():
    stat1 = get_cpu_usage()
    time.sleep(1)
    stat2 = get_cpu_usage()
    
    total_diff = stat2['total'] - stat1['total']
    idle_diff = stat2['idle'] - stat1['idle']
    
    cpu_percent_usage = 0

    if total_diff > 0:
        cpu_percent_usage = 100 * (total_diff - idle_diff) / total_diff
    
    return {'cpu_absolute_usage': (total_diff - idle_diff) / 100, 'cpu_percent_usage': cpu_percent_usage}


def get_memory_info():
    mem_info = {}
    with open('/proc/meminfo', 'r') as f:
        for line in f:
            parts = line.split()
            if parts[0] in ['MemTotal:', 'MemAvailable:']:
                mem_info[parts[0][:-1]] = int(parts[1])
    
    total = mem_info['MemTotal']
    available = mem_info['MemAvailable']
    used = total - available
    percent = (used / total) * 100
    
    return {
        'percent': percent,
        'used': used // 1024,
        'total': total // 1024
    }


def get_process_count():
    entries = os.listdir('/proc')
    processes = [e for e in entries if e.isdigit()]
    return len(processes)


print(f"Мониторинг запущен")
print(f"Файл лога: {LOG_FILE}")

timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
cpu = get_cpu_data()
mem = get_memory_info()
processes = get_process_count()
        
log_line = f"{timestamp} | CPU: {cpu['cpu_percent_usage']:.1f}% | CPU {cpu['cpu_absolute_usage']:.1f}s per 1s | RAM: {mem['percent']:.1f}% ({mem['used']}MB/{mem['total']}MB) | Processes: {processes}\n"
        
with open(LOG_FILE, 'a') as f:
    f.write(log_line)
