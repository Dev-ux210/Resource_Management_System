import psutil
import time
import os
import threading
from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich.panel import Panel
from rich.text import Text
from rich import box

CPU_THRESHOLD = 80
MEM_THRESHOLD = 80
DISK_THRESHOLD = 80

console = Console()

# SHARED STATE

top_procs_cache = []
procs_lock = threading.Lock()


# FUNCTIONS
def get_bar(value, width=20):
    """Return a colored ASCII progress bar."""
    filled = int((value / 100) * width)
    bar = "█" * filled + "░" * (width - filled)
    if value < 60:
        color = "green"
    elif value < 80:
        color = "yellow"
    else:
        color = "red"
    return f"[{color}]{bar}[/{color}]"


def get_color(value, threshold):
    if value < threshold:
        return "green"
    elif value < threshold + 10:
        return "yellow"
    else:
        return "red"


def get_system_usage():
    cpu    = psutil.cpu_percent(interval=None)
    memory = psutil.virtual_memory()
    disk   = psutil.disk_usage(os.path.abspath(os.sep))
    cores  = psutil.cpu_percent(interval=None, percpu=True)
    return cpu, memory, disk, cores


def get_uptime():
    boot_time = psutil.boot_time()
    uptime_seconds = time.time() - boot_time
    hours = int(uptime_seconds // 3600)
    minutes = int((uptime_seconds % 3600) // 60)
    seconds = int(uptime_seconds % 60)
    return f"{hours}h {minutes}m {seconds}s"

def update_processes():
    global top_procs_cache
    while True:
        procs = []
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                cpu = proc.cpu_percent(interval=None)
                mem = proc.memory_percent()
                procs.append({
                    'pid': proc.pid,
                    'name': proc.name(),
                    'cpu_percent': cpu,
                    'memory_percent': mem
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        procs.sort(key=lambda x: x['cpu_percent'], reverse=True)

        with procs_lock:
            top_procs_cache = procs[:15 ]

        time.sleep(2)


def build_display(cpu, memory, disk, cores):
    """Build the full Rich renderable — no prints, no flicker."""

    mem_pct  = memory.percent
    disk_pct = disk.percent

    cpu_color  = get_color(cpu,     CPU_THRESHOLD)
    mem_color  = get_color(mem_pct, MEM_THRESHOLD)
    disk_color = get_color(disk_pct, DISK_THRESHOLD)

    # Alerts
    alerts = Text()
    if cpu > CPU_THRESHOLD:
        alerts.append("  ⚠ High CPU Usage!\n",    style="bold red")
    if mem_pct > MEM_THRESHOLD:
        alerts.append("  ⚠ High Memory Usage!\n", style="bold red")
    if disk_pct > DISK_THRESHOLD:
        alerts.append("  ⚠ High Disk Usage!\n",  style="bold red")

    # Overview table
    overview = Table(box=box.SIMPLE, show_header=False, padding=(0, 1))
    overview.add_column("Metric", style="bold cyan", width=14)
    overview.add_column("Bar",    width=22)
    overview.add_column("Value",  width=12)
    overview.add_column("Extra",  style="dim")

    overview.add_row(
        "CPU",
        get_bar(cpu),
        f"[{cpu_color}]{cpu:5.1f}%[/{cpu_color}]",
        f"{psutil.cpu_count()} cores"
    )
    overview.add_row(
        "Memory",
        get_bar(mem_pct),
        f"[{mem_color}]{mem_pct:5.1f}%[/{mem_color}]",
        f"{memory.used / 1e9:.1f} / {memory.total / 1e9:.1f} GB"
    )
    overview.add_row(
        "Disk",
        get_bar(disk_pct),
        f"[{disk_color}]{disk_pct:5.1f}%[/{disk_color}]",
        f"{disk.used / 1e9:.1f} / {disk.total / 1e9:.1f} GB"
    )
    overview.add_row(
        "Uptime",
        "",
        "",
        get_uptime()
)

    # Per-core table
    core_table = Table(box=box.SIMPLE, show_header=False, padding=(0, 1))
    core_table.add_column("Core",  style="bold", width=8)
    core_table.add_column("Bar",   width=16)
    core_table.add_column("Pct",   width=7)

    for i, c in enumerate(cores):
        core_table.add_row(f"Core {i}", get_bar(c, width=14), f"{c:5.1f}%")

    # Process table
    proc_table = Table(box=box.SIMPLE, show_header=True, padding=(0, 1))
    proc_table.add_column("PID",     style="cyan",  width=7)
    proc_table.add_column("Name",    style="white", width=22)
    proc_table.add_column("CPU %",   style="yellow",width=8)
    proc_table.add_column("MEM %",   style="magenta", width=8)

    with procs_lock:
        procs_snapshot = list(top_procs_cache)

    if not procs_snapshot:
        proc_table.add_row("–", "Loading…", "–", "–")
    else:
        for p in procs_snapshot:
            cpu_pct = p.get('cpu_percent') or 0.0
            mem_pct_p = p.get('memory_percent') or 0.0
            proc_table.add_row(
                str(p['pid']),
                (p['name'] or "?")[:22],
                f"{cpu_pct:.1f}%",
                f"{mem_pct_p:.1f}%",
            )

    # Assemble layout
    from rich.layout import Layout
    layout = Layout()
    layout.split_column(
        Layout(Panel(overview,    title="[bold cyan]System Overview[/bold cyan]",  border_style="cyan"),  name="overview", size=7),
        Layout(name="mid", size=max(len(cores) + 3, 8)),
        Layout(Panel(proc_table,  title="[bold yellow]Top Processes (CPU)[/bold yellow]", border_style="yellow"), name="procs"),
    )
    layout["mid"].split_row(
        Layout(Panel(core_table,  title="[bold green]Per-Core Usage[/bold green]",  border_style="green"), name="cores"),
        Layout(Panel(alerts if alerts.plain else Text("  ✔ All systems normal", style="bold green"),
                    title="[bold red]Alerts[/bold red]", border_style="red"), name="alerts"),
    )

    return layout

# INITIALIZATION 

psutil.cpu_percent(interval=1)          # blocking 1-second warm-up — accurate from first frame
for proc in psutil.process_iter():
    try:
        proc.cpu_percent(interval=None)
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        pass

# Seed the process cache synchronously so first frame isn't empty
top_procs_cache = []

# Start background thread OUTSIDE any loop
thread = threading.Thread(target=update_processes, daemon=True)
thread.start()

# MAIN LOOP 

try:
    with Live(console=console, refresh_per_second=4, screen=True) as live:
        while True:
            cpu, memory, disk, cores = get_system_usage()
            live.update(build_display(cpu, memory, disk, cores))
            time.sleep(0.5)

except KeyboardInterrupt:
    console.print("\n[bold red]Exiting monitor…[/bold red]")