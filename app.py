import ctypes
import ctypes.wintypes
import customtkinter as ctk
import threading
import time
from tkinter import ttk


# Define ctypes structures and constants
class MEMORYSTATUSEX(ctypes.Structure):
    _fields_ = [
        ("dwLength", ctypes.wintypes.DWORD),
        ("dwMemoryLoad", ctypes.wintypes.DWORD),
        ("ullTotalPhys", ctypes.c_ulonglong),
        ("ullAvailPhys", ctypes.c_ulonglong),
        ("ullTotalPageFile", ctypes.c_ulonglong),
        ("ullAvailPageFile", ctypes.c_ulonglong),
        ("ullTotalVirtual", ctypes.c_ulonglong),
        ("ullAvailVirtual", ctypes.c_ulonglong),
        ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
    ]


# Global ctypes instances
kernel32 = ctypes.WinDLL("kernel32")
psapi = ctypes.WinDLL("psapi")
mem_status = MEMORYSTATUSEX()
mem_status.dwLength = ctypes.sizeof(MEMORYSTATUSEX)


# Fetch system memory status
def get_memory_status():
    kernel32.GlobalMemoryStatusEx(ctypes.byref(mem_status))
    return {
        "Memory Load (%)": mem_status.dwMemoryLoad,
        "Total Physical (GB)": mem_status.ullTotalPhys / (1024 ** 3),
        "Available Physical (GB)": mem_status.ullAvailPhys / (1024 ** 3),
    }


# Fetch CPU time
def get_cpu_time():
    idle_time = ctypes.wintypes.FILETIME()
    kernel_time = ctypes.wintypes.FILETIME()
    user_time = ctypes.wintypes.FILETIME()

    kernel32.GetSystemTimes(
        ctypes.byref(idle_time), ctypes.byref(kernel_time), ctypes.byref(user_time)
    )

    def filetime_to_int(filetime):
        return (filetime.dwHighDateTime << 32) + filetime.dwLowDateTime

    idle = filetime_to_int(idle_time)
    kernel = filetime_to_int(kernel_time)
    user = filetime_to_int(user_time)

    return idle, kernel, user


# Fetch process list
def get_process_list():
    process_ids = (ctypes.wintypes.DWORD * 1024)()
    cb = ctypes.sizeof(process_ids)
    bytes_returned = ctypes.wintypes.DWORD()

    psapi.EnumProcesses(ctypes.byref(process_ids), cb, ctypes.byref(bytes_returned))

    num_processes = bytes_returned.value // ctypes.sizeof(ctypes.wintypes.DWORD)
    process_list = []

    for i in range(num_processes):
        pid = process_ids[i]
        process_handle = kernel32.OpenProcess(0x0410, False, pid)
        if process_handle:
            process_name = ctypes.create_string_buffer(1024)
            psapi.GetModuleBaseNameA(process_handle, None, process_name, 1024)
            process_list.append((pid, process_name.value.decode(errors="ignore")))
            kernel32.CloseHandle(process_handle)

    return process_list


# GUI Application
class TaskManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Task Manager Clone")
        self.root.geometry("1200x700")

        # Set appearance
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Tabs
        self.tab_control = ttk.Notebook(self.root)
        self.tab_processes = ctk.CTkFrame(self.tab_control)
        self.tab_performance = ctk.CTkFrame(self.tab_control)

        self.tab_control.add(self.tab_processes, text="Processes")
        self.tab_control.add(self.tab_performance, text="Performance")
        self.tab_control.pack(expand=1, fill="both")

        # Processes tab
        self.process_tree = ttk.Treeview(self.tab_processes, columns=("PID", "Name"), show="headings")
        self.process_tree.heading("PID", text="PID")
        self.process_tree.heading("Name", text="Name")
        self.process_tree.pack(fill="both", expand=True)

        # Performance tab
        self.mem_label = ctk.CTkLabel(self.tab_performance, text="Memory Stats", font=("Arial", 20, "bold"))
        self.mem_label.pack(pady=10)

        self.cpu_label = ctk.CTkLabel(self.tab_performance, text="CPU Usage", font=("Arial", 20, "bold"))
        self.cpu_label.pack(pady=10)

        # Start background updates
        threading.Thread(target=self.update_processes, daemon=True).start()
        threading.Thread(target=self.update_performance, daemon=True).start()

    def update_processes(self):
        while True:
            process_list = get_process_list()
            self.process_tree.delete(*self.process_tree.get_children())
            for pid, name in process_list:
                self.process_tree.insert("", "end", values=(pid, name))
            time.sleep(2)

    def update_performance(self):
        previous_idle, previous_kernel, previous_user = get_cpu_time()
        while True:
            memory = get_memory_status()
            current_idle, current_kernel, current_user = get_cpu_time()

            # Calculate CPU usage
            idle_diff = current_idle - previous_idle
            kernel_diff = current_kernel - previous_kernel
            user_diff = current_user - previous_user
            cpu_usage = (kernel_diff + user_diff - idle_diff) / (kernel_diff + user_diff) * 100

            # Update labels
            self.mem_label.configure(text=f"Memory Load: {memory['Memory Load (%)']}%\n Total Physical: {memory['Total Physical (GB)']:.2f} GB\n Available Physical: { memory['Available Physical (GB)']:.2f } GB" )
            self.cpu_label.configure(text=f"CPU Usage: {cpu_usage:.2f}%")

            # Update previous values
            previous_idle, previous_kernel, previous_user = current_idle, current_kernel, current_user
            time.sleep(1)


if __name__ == "__main__":
    root = ctk.CTk()
    app = TaskManagerApp(root)
    root.mainloop()







# import ctypes
# # import tkinter as tk
# from customtkinter import CTk, CTkLabel, CTkButton, CTkFrame
# from matplotlib.figure import Figure
# from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
# import random

# # Load C Library
# metrics_lib = ctypes.CDLL("./system_metrics.dll")

# class VirtualMemoryDashboard:
#     def __init__(self, root):
#         self.root = root
#         self.root.title("Virtual Memory Monitoring Dashboard")
#         self.root.geometry("1000x800")
#         self.root.configure(bg="#1c1c1c")

#         # Dashboard Layout
#         self.create_header()
#         self.create_metrics_frame()
#         self.create_graph_frame()

#         # Initialize data for graphs
#         self.cpu_data = [0] * 60
#         self.memory_data = [0] * 60
#         self.disk_data = [0] * 60

#         self.update_metrics()

#     def create_header(self):
#         header_frame = CTkFrame(self.root, height=60, fg_color="#333333")
#         header_frame.pack(fill="x")

#         header_label = CTkLabel(header_frame, text="Virtual Memory Monitoring Dashboard", font=("Arial", 20, "bold"))
#         header_label.pack(pady=10)

#     def create_metrics_frame(self):
#         self.metrics_frame = CTkFrame(self.root, height=200, fg_color="#262626")
#         self.metrics_frame.pack(fill="x", pady=10)

#         # Labels for Metrics
#         self.cpu_label = CTkLabel(self.metrics_frame, text="CPU Usage: 0%", font=("Arial", 16), anchor="w")
#         self.cpu_label.grid(row=0, column=0, padx=20, pady=10, sticky="w")

#         self.memory_label = CTkLabel(self.metrics_frame, text="Memory Usage: 0%", font=("Arial", 16), anchor="w")
#         self.memory_label.grid(row=1, column=0, padx=20, pady=10, sticky="w")

#         self.disk_label = CTkLabel(self.metrics_frame, text="Disk Usage: 0%", font=("Arial", 16), anchor="w")
#         self.disk_label.grid(row=2, column=0, padx=20, pady=10, sticky="w")

#         self.page_faults_label = CTkLabel(self.metrics_frame, text="Page Faults: 0", font=("Arial", 16), anchor="w")
#         self.page_faults_label.grid(row=3, column=0, padx=20, pady=10, sticky="w")

#     def create_graph_frame(self):
#         self.graph_frame = CTkFrame(self.root, fg_color="#1c1c1c")
#         self.graph_frame.pack(fill="both", expand=True)

#         # Create Matplotlib Figures
#         self.fig = Figure(figsize=(8, 4), dpi=100)
#         self.ax_cpu = self.fig.add_subplot(131)
#         self.ax_memory = self.fig.add_subplot(132)
#         self.ax_disk = self.fig.add_subplot(133)

#         self.ax_cpu.set_title("CPU Usage")
#         self.ax_memory.set_title("Memory Usage")
#         self.ax_disk.set_title("Disk Usage")

#         # Add Figures to GUI
#         self.canvas = FigureCanvasTkAgg(self.fig, master=self.graph_frame)
#         self.canvas_widget = self.canvas.get_tk_widget()
#         self.canvas_widget.pack(fill="both", expand=True)

#     def update_metrics(self):
#         # Fetch data from C library
#         cpu = ctypes.c_int()
#         memory = ctypes.c_int()
#         disk = ctypes.c_int()
#         gpu = ctypes.c_int()
#         page_faults = ctypes.c_int()
#         metrics_lib.get_system_metrics(ctypes.byref(cpu), ctypes.byref(memory), ctypes.byref(disk), ctypes.byref(gpu), ctypes.byref(page_faults))

#         # Update Labels
#         self.cpu_label.configure(text=f"CPU Usage: {cpu.value}%")
#         self.memory_label.configure(text=f"Memory Usage: {memory.value}%")
#         self.disk_label.configure(text=f"Disk Usage: {disk.value}%")
#         self.page_faults_label.configure(text=f"Page Faults: {page_faults.value}")

#         # Update Graph Data
#         self.cpu_data.append(cpu.value)
#         self.cpu_data.pop(0)
#         self.memory_data.append(memory.value)
#         self.memory_data.pop(0)
#         self.disk_data.append(disk.value)
#         self.disk_data.pop(0)

#         # Update Graphs
#         self.ax_cpu.clear()
#         self.ax_cpu.plot(self.cpu_data, color="cyan")
#         self.ax_memory.clear()
#         self.ax_memory.plot(self.memory_data, color="lime")
#         self.ax_disk.clear()
#         self.ax_disk.plot(self.disk_data, color="orange")

#         # Redraw Canvas
#         self.canvas.draw()

#         # Schedule next update
#         self.root.after(1000, self.update_metrics)

# if __name__ == "__main__":
#     root = CTk()
#     app = VirtualMemoryDashboard(root)
#     root.mainloop()
