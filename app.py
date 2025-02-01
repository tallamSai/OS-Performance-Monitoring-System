import ctypes
import tkinter as tk
from customtkinter import CTk, CTkLabel, CTkFrame, CTkButton
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import random

# Load the C library for memory metrics
metrics_lib = ctypes.CDLL("./system_metrics.dll")

class VirtualMemoryDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("Virtual Memory Monitoring Dashboard")
        self.root.geometry("1200x800")
        self.root.configure(bg="#1e1e2f")

        self.create_header()
        self.create_metrics_section()
        self.create_graph_section()

        # Initialize data for graphs
        self.virtual_memory_data = [0] * 60
        self.physical_memory_data = [0] * 60
        self.page_faults_data = [0] * 60

        self.update_metrics()

    def create_header(self):
        header_frame = CTkFrame(self.root, height=70, fg_color="#282a36")
        header_frame.pack(fill="x")

        header_label = CTkLabel(
            header_frame,
            text="Virtual Memory Monitoring Dashboard",
            font=("Arial", 24, "bold"),
            text_color="white"
        )
        header_label.pack(pady=15)

    def create_metrics_section(self):
        self.metrics_frame = CTkFrame(self.root, fg_color="#44475a", corner_radius=10)
        self.metrics_frame.pack(fill="x", padx=20, pady=10)

        # Metrics Labels
        self.virtual_memory_label = CTkLabel(
            self.metrics_frame, text="Virtual Memory: 0%", font=("Arial", 16), text_color="white"
        )
        self.virtual_memory_label.grid(row=0, column=0, padx=20, pady=10, sticky="w")

        self.physical_memory_label = CTkLabel(
            self.metrics_frame, text="Physical Memory: 0%", font=("Arial", 16), text_color="white"
        )
        self.physical_memory_label.grid(row=1, column=0, padx=20, pady=10, sticky="w")

        self.page_faults_label = CTkLabel(
            self.metrics_frame, text="Page Faults: 0", font=("Arial", 16), text_color="white"
        )
        self.page_faults_label.grid(row=2, column=0, padx=20, pady=10, sticky="w")

        self.committed_memory_label = CTkLabel(
            self.metrics_frame, text="Committed Memory: 0%", font=("Arial", 16), text_color="white"
        )
        self.committed_memory_label.grid(row=3, column=0, padx=20, pady=10, sticky="w")

    def create_graph_section(self):
        self.graph_frame = CTkFrame(self.root, fg_color="#282a36", corner_radius=10)
        self.graph_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Create Matplotlib Figures
        self.fig = Figure(figsize=(10, 5), dpi=100)
        self.ax_virtual_memory = self.fig.add_subplot(131)
        self.ax_physical_memory = self.fig.add_subplot(132)
        self.ax_page_faults = self.fig.add_subplot(133)

        self.ax_virtual_memory.set_title("Virtual Memory")
        self.ax_physical_memory.set_title("Physical Memory")
        self.ax_page_faults.set_title("Page Faults")

        # Add Figures to GUI
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.graph_frame)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(fill="both", expand=True)

    def update_metrics(self):
        # Fetch data from C library
        virtual_memory = ctypes.c_int()
        physical_memory = ctypes.c_int()
        page_faults = ctypes.c_int()
        committed_memory = ctypes.c_int()

        metrics_lib.get_system_metrics(
            ctypes.byref(virtual_memory),
            ctypes.byref(physical_memory),
            ctypes.byref(page_faults),
            ctypes.byref(committed_memory)
        )

        # Update Labels
        self.virtual_memory_label.configure(text=f"Virtual Memory: {virtual_memory.value}%")
        self.physical_memory_label.configure(text=f"Physical Memory: {physical_memory.value}%")
        self.page_faults_label.configure(text=f"Page Faults: {page_faults.value}")
        self.committed_memory_label.configure(text=f"Committed Memory: {committed_memory.value}%")

        # Update Graph Data
        self.virtual_memory_data.append(virtual_memory.value)
        self.virtual_memory_data.pop(0)
        self.physical_memory_data.append(physical_memory.value)
        self.physical_memory_data.pop(0)
        self.page_faults_data.append(page_faults.value)
        self.page_faults_data.pop(0)

        # Update Graphs
        self.ax_virtual_memory.clear()
        self.ax_virtual_memory.plot(self.virtual_memory_data, color="cyan")
        self.ax_physical_memory.clear()
        self.ax_physical_memory.plot(self.physical_memory_data, color="lime")
        self.ax_page_faults.clear()
        self.ax_page_faults.plot(self.page_faults_data, color="orange")

        # Redraw Canvas
        self.canvas.draw()

        # Schedule next update
        self.root.after(1000, self.update_metrics)


if __name__ == "__main__":
    root = CTk()
    app = VirtualMemoryDashboard(root)
    root.mainloop()
