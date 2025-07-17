# advanced_ram_reader_streamlit.py

import streamlit as st
import psutil
import platform
import time
import csv
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Advanced RAM Reader", layout="centered")

st.title("🧠 Advanced RAM Monitor - Streamlit")
st.markdown("This tool displays real-time memory usage using **psutil** in a Streamlit app.")

# Log to CSV
def log_ram_to_csv(file_name='ram_log.csv'):
    ram = psutil.virtual_memory()
    with open(file_name, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            round(ram.total / (1024 ** 3), 2),
            round(ram.available / (1024 ** 3), 2),
            round(ram.used / (1024 ** 3), 2),
            ram.percent
        ])

# Get system uptime
def get_system_uptime():
    boot_time = psutil.boot_time()
    uptime_seconds = time.time() - boot_time
    return time.strftime('%H:%M:%S', time.gmtime(uptime_seconds))

# Get top processes
def get_top_memory_processes(n=5):
    processes = []
    for p in psutil.process_iter(['name', 'memory_info']):
        try:
            processes.append((p.info['name'], p.info['memory_info'].rss))
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    top = sorted(processes, key=lambda x: x[1], reverse=True)[:n]
    return top

# Display RAM info
def display_ram_info():
    ram = psutil.virtual_memory()
    swap = psutil.swap_memory()

    st.subheader("📊 RAM Information")
    col1, col2 = st.columns(2)
    col1.metric("Total RAM", f"{ram.total / (1024 ** 3):.2f} GB")
    col2.metric("Used RAM", f"{ram.used / (1024 ** 3):.2f} GB", delta=f"{ram.percent}%")

    col1.metric("Available RAM", f"{ram.available / (1024 ** 3):.2f} GB")
    col2.metric("Swap Used", f"{swap.used / (1024 ** 3):.2f} GB / {swap.total / (1024 ** 3):.2f} GB")

    # Alert
    if ram.percent >= 80:
        st.error("⚠️ ALERT: High RAM usage detected!")

    # Uptime
    st.subheader("🕒 System Uptime")
    st.write(f"`{get_system_uptime()}`")

    # Top Processes
    st.subheader("🔥 Top Memory Consuming Processes")
    top_procs = get_top_memory_processes()
    df = pd.DataFrame([(i+1, p[0], round(p[1]/(1024**2), 2)) for i, p in enumerate(top_procs)],
                      columns=["Rank", "Process", "Memory (MB)"])
    st.table(df)

    # Log current reading
    log_ram_to_csv()

# Display previous logs
def display_logs():
    try:
        df = pd.read_csv("ram_log.csv", names=["Time", "Total_GB", "Available_GB", "Used_GB", "Usage_%"])
        st.subheader("📁 RAM Usage Log")
        st.line_chart(df.set_index("Time")[["Used_GB", "Available_GB"]].tail(20))
    except FileNotFoundError:
        st.info("No log file found yet.")

# Main
st.markdown("---")
if st.button("🔄 Refresh RAM Info"):
    display_ram_info()

display_logs()

st.markdown("---")
st.caption("Built with ❤️ using Python, Streamlit, and psutil.")
