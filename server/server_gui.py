import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import os
import socket
from pathlib import Path
import sys

# Import server code
import uvicorn
from fastapi import FastAPI
from server import app, get_all_mods, MODS_FOLDER

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# =========================
# ⚙️ Cấu hình
# =========================
SERVER_HOST = os.getenv("SERVER_HOST", "::")
SERVER_PORT = int(os.getenv("SERVER_PORT", "5000"))
SERVER_IPV6 = os.getenv("SERVER_IPV6", "")

# =========================
# 🌐 Lấy địa chỉ IP
# =========================
def get_local_ipv4():
    """Lấy IPv4 local"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

def get_local_ipv6():
    """Lấy IPv6 local"""
    if SERVER_IPV6:
        return SERVER_IPV6
    try:
        s = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
        s.connect(("2001:4860:4860::8888", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "::1"

# =========================
# 🖥️ Server GUI Class
# =========================
class ServerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Minecraft Mods Sync Server")
        
        # Căn giữa cửa sổ
        window_width = 800
        window_height = 600
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.root.resizable(False, False)
        
        self.server_running = False
        self.server_thread = None
        
        # Tiêu đề
        title_label = tk.Label(root, text="🖥️ Minecraft Mods Sync Server", 
                               font=("Segoe UI", 16, "bold"))
        title_label.pack(pady=10)
        
        # Frame thông tin server
        info_frame = tk.LabelFrame(root, text="📡 Thông tin Server", 
                                   font=("Segoe UI", 10, "bold"))
        info_frame.pack(pady=5, padx=20, fill="x")
        
        # IPv4
        ipv4_frame = tk.Frame(info_frame)
        ipv4_frame.pack(pady=5, padx=10, fill="x")
        tk.Label(ipv4_frame, text="IPv4:", font=("Segoe UI", 10, "bold"), width=10, anchor="w").pack(side="left")
        self.ipv4_label = tk.Label(ipv4_frame, text=f"{get_local_ipv4()}:{SERVER_PORT}", 
                                   font=("Segoe UI", 10), fg="blue", cursor="hand2")
        self.ipv4_label.pack(side="left")
        self.ipv4_label.bind("<Button-1>", lambda e: self.copy_to_clipboard(f"{get_local_ipv4()}:{SERVER_PORT}"))
        
        # IPv6
        ipv6_frame = tk.Frame(info_frame)
        ipv6_frame.pack(pady=5, padx=10, fill="x")
        tk.Label(ipv6_frame, text="IPv6:", font=("Segoe UI", 10, "bold"), width=10, anchor="w").pack(side="left")
        self.ipv6_label = tk.Label(ipv6_frame, text=f"[{get_local_ipv6()}]:{SERVER_PORT}", 
                                   font=("Segoe UI", 10), fg="blue", cursor="hand2")
        self.ipv6_label.pack(side="left")
        self.ipv6_label.bind("<Button-1>", lambda e: self.copy_to_clipboard(f"[{get_local_ipv6()}]:{SERVER_PORT}"))
        
        # Hướng dẫn
        tk.Label(info_frame, text="💡 Nhấn vào địa chỉ để copy", 
                font=("Segoe UI", 8, "italic"), fg="gray").pack(pady=2)
        
        # Trạng thái
        status_frame = tk.Frame(root)
        status_frame.pack(pady=5)
        
        tk.Label(status_frame, text="Trạng thái:", font=("Segoe UI", 11, "bold")).pack(side="left", padx=5)
        self.status_label = tk.Label(status_frame, text="⚫ Đã dừng", 
                                     font=("Segoe UI", 11), fg="red")
        self.status_label.pack(side="left")
        
        # Nút Start/Stop
        self.control_button = tk.Button(root, text="▶️ START SERVER", 
                                       font=("Segoe UI", 12, "bold"),
                                       command=self.toggle_server, width=20, pady=10,
                                       bg="#4CAF50", fg="white", cursor="hand2",
                                       relief="raised", borderwidth=3,
                                       activebackground="#45a049")
        self.control_button.pack(pady=10)
        
        # Frame danh sách mods
        mods_frame = tk.LabelFrame(root, text="📦 Danh sách Mods", 
                                   font=("Segoe UI", 10, "bold"))
        mods_frame.pack(pady=10, padx=20, fill="both", expand=True)
        
        # Treeview cho danh sách mods
        columns = ("Tên File", "Kích thước", "Hash")
        self.mods_tree = ttk.Treeview(mods_frame, columns=columns, show="headings", height=8)
        
        self.mods_tree.heading("Tên File", text="Tên File")
        self.mods_tree.heading("Kích thước", text="Kích thước")
        self.mods_tree.heading("Hash", text="Hash (SHA256)")
        
        self.mods_tree.column("Tên File", width=300)
        self.mods_tree.column("Kích thước", width=100)
        self.mods_tree.column("Hash", width=350)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(mods_frame, orient="vertical", command=self.mods_tree.yview)
        self.mods_tree.configure(yscrollcommand=scrollbar.set)
        
        self.mods_tree.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        scrollbar.pack(side="right", fill="y", pady=5)
        
        # Nút refresh
        refresh_button = tk.Button(root, text="🔄 Làm mới danh sách", 
                                   font=("Segoe UI", 9),
                                   command=self.refresh_mods_list, width=20)
        refresh_button.pack(pady=5)
        
        # Log frame
        log_frame = tk.LabelFrame(root, text="📋 Log", font=("Segoe UI", 10, "bold"))
        log_frame.pack(pady=10, padx=20, fill="both", expand=True)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=8, 
                                                   font=("Consolas", 9), wrap=tk.WORD)
        self.log_text.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Load danh sách mods ban đầu
        self.refresh_mods_list()
        self.log("✅ Server GUI đã khởi động")
        self.log(f"📁 Thư mục mods: {MODS_FOLDER}")
        
        # Handle close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def copy_to_clipboard(self, text):
        """Copy text vào clipboard"""
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.log(f"📋 Đã copy: {text}")
        messagebox.showinfo("Copy thành công", f"Đã copy vào clipboard:\n{text}")
    
    def log(self, message):
        """Thêm log message"""
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
    
    def refresh_mods_list(self):
        """Làm mới danh sách mods"""
        # Xóa danh sách cũ
        for item in self.mods_tree.get_children():
            self.mods_tree.delete(item)
        
        # Lấy danh sách mods mới
        mods = get_all_mods()
        
        if not mods:
            self.log("⚠️ Không có mods nào trong thư mục")
            return
        
        # Thêm vào tree
        for mod_name, mod_info in mods.items():
            size_mb = mod_info["size"] / 1024 / 1024
            size_str = f"{size_mb:.2f} MB"
            hash_short = mod_info["hash"][:16] + "..."
            
            self.mods_tree.insert("", "end", values=(mod_name, size_str, hash_short))
        
        self.log(f"🔄 Đã tải {len(mods)} mods")
    
    def toggle_server(self):
        """Bật/tắt server"""
        if not self.server_running:
            self.start_server()
        else:
            self.stop_server()
    
    def start_server(self):
        """Khởi động server"""
        self.log("🚀 Đang khởi động server...")
        self.control_button.config(state="disabled")
        
        # Chạy server trong thread riêng
        self.server_thread = threading.Thread(target=self._run_server, daemon=True)
        self.server_thread.start()
        
        # Cập nhật UI
        self.server_running = True
        self.status_label.config(text="🟢 Đang chạy", fg="green")
        self.control_button.config(text="⏹️ STOP SERVER", bg="#f44336", 
                                   activebackground="#da190b", state="normal")
        
        self.log("✅ Server đã khởi động!")
        self.log(f"🌐 Client có thể kết nối tới:")
        self.log(f"   IPv4: {get_local_ipv4()}:{SERVER_PORT}")
        self.log(f"   IPv6: [{get_local_ipv6()}]:{SERVER_PORT}")
    
    def _run_server(self):
        """Chạy uvicorn server"""
        try:
            uvicorn.run(app, host=SERVER_HOST, port=SERVER_PORT, log_level="info")
        except Exception as e:
            self.log(f"❌ Lỗi server: {e}")
    
    def stop_server(self):
        """Dừng server"""
        self.log("⏹️ Đang dừng server...")
        
        # Cập nhật UI
        self.server_running = False
        self.status_label.config(text="⚫ Đã dừng", fg="red")
        self.control_button.config(text="▶️ START SERVER", bg="#4CAF50", 
                                   activebackground="#45a049")
        
        self.log("✅ Server đã dừng (cần khởi động lại ứng dụng để start lại)")
    
    def on_closing(self):
        """Xử lý khi đóng cửa sổ"""
        if self.server_running:
            if messagebox.askokcancel("Thoát", "Server đang chạy. Bạn có chắc muốn thoát?"):
                self.root.destroy()
        else:
            self.root.destroy()

# =========================
# 🚀 Main
# =========================
if __name__ == "__main__":
    root = tk.Tk()
    gui = ServerGUI(root)
    root.mainloop()
