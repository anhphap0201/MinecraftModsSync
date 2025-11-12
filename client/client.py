import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import requests
import hashlib
import os
import threading
import json
from pathlib import Path

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv không bắt buộc cho client

# =========================
# ⚙️ Cấu hình
# =========================
CONFIG_FILE = "config.json"
SERVER_IPV6 = os.getenv("SERVER_IPV6", "localhost")
SERVER_PORT = os.getenv("SERVER_PORT", "5000")
SERVER_URL = f"http://[{SERVER_IPV6}]:{SERVER_PORT}" if ":" in SERVER_IPV6 else f"http://{SERVER_IPV6}:{SERVER_PORT}"
DEFAULT_MODS_FOLDER = os.getenv("DEFAULT_MODS_FOLDER", r"C:\Users\YourUsername\AppData\Roaming\.minecraft\mods")

# Đọc hoặc tạo file cấu hình
def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return config.get("mods_folder", DEFAULT_MODS_FOLDER), config.get("launcher_type", "curseforge")
        except:
            pass
    return DEFAULT_MODS_FOLDER, "curseforge"

def save_config(mods_folder, launcher_type=None):
    config = {"mods_folder": mods_folder}
    if launcher_type:
        config["launcher_type"] = launcher_type
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

# Tải cấu hình
MODS_FOLDER, LAUNCHER_TYPE = load_config()

# Tạo thư mục mods nếu chưa tồn tại (chỉ khi đường dẫn hợp lệ)
if os.path.exists(os.path.dirname(MODS_FOLDER)):
    os.makedirs(MODS_FOLDER, exist_ok=True)

# =========================
# 🔍 Detect Launcher Paths
# =========================
def detect_launcher_base_path(launcher_type):
    """Detect base path cho launcher"""
    if launcher_type == "prism":
        # Tìm PrismLauncher trong các thư mục phổ biến
        possible_paths = [
            Path(os.getenv("APPDATA")) / "PrismLauncher",
            Path("C:/Program Files/PrismLauncher"),
            Path("C:/Program Files (x86)/PrismLauncher"),
            Path.home() / "PrismLauncher",
        ]
        for path in possible_paths:
            instances_path = path / "instances"
            if instances_path.exists():
                return str(instances_path)
        return str(Path(os.getenv("APPDATA")) / "PrismLauncher" / "instances")
    
    elif launcher_type == "curseforge":
        # Tìm CurseForge
        possible_paths = [
            Path(os.getenv("APPDATA")) / "curseforge" / "minecraft" / "Instances",
            Path("C:/curseforge/minecraft/Instances"),
            Path.home() / "curseforge" / "minecraft" / "Instances",
        ]
        for path in possible_paths:
            if path.exists():
                return str(path)
        return str(Path(os.getenv("APPDATA")) / "curseforge" / "minecraft" / "Instances")
    
    return ""

def get_suggested_path(launcher_type):
    """Lấy suggested path pattern cho launcher"""
    base = detect_launcher_base_path(launcher_type)
    if launcher_type == "prism":
        return f"{base}\\<tên instance>\\minecraft\\mods"
    else:  # curseforge
        return f"{base}\\<tên instance>\\mods"

def validate_mods_path(path, launcher_type):
    """Kiểm tra xem path có phải là folder mods hợp lệ không"""
    path_obj = Path(path)
    
    # Kiểm tra folder có tồn tại không
    if not path_obj.exists():
        return False, "❌ Thư mục không tồn tại"
    
    # Kiểm tra có phải folder "mods" không
    if path_obj.name.lower() != "mods":
        return False, "❌ Thư mục phải có tên 'mods'"
    
    # Kiểm tra cấu trúc path theo launcher
    path_str = str(path_obj).lower()
    
    if launcher_type == "prism":
        # Prism: ...instances\<instance>\minecraft\mods
        if "instances" not in path_str:
            return False, "❌ Không tìm thấy 'instances' trong đường dẫn"
        if "minecraft" not in path_str:
            return False, "❌ Không tìm thấy 'minecraft' trong đường dẫn"
    else:  # curseforge
        # CurseForge: ...Instances\<instance>\mods
        if "instances" not in path_str:
            return False, "❌ Không tìm thấy 'Instances' trong đường dẫn"
    
    return True, "✅ Đường dẫn hợp lệ"

# =========================
# 🔒 Hàm tiện ích
# =========================
def get_file_hash(path):
    """Tính hash SHA256 của file"""
    sha256 = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256.update(chunk)
    return sha256.hexdigest()

def get_local_mods():
    """Lấy danh sách mod local và hash của chúng"""
    local_mods = {}
    if os.path.exists(MODS_FOLDER):
        for filename in os.listdir(MODS_FOLDER):
            if filename.endswith('.jar'):
                filepath = os.path.join(MODS_FOLDER, filename)
                local_mods[filename] = {
                    "hash": get_file_hash(filepath),
                    "size": os.path.getsize(filepath)
                }
    return local_mods

# =========================
# 🔍 Kiểm tra cập nhật
# =========================
missing_mods = []
outdated_mods = []
extra_mods = []

def check_update():
    global missing_mods, outdated_mods, extra_mods, MODS_FOLDER
    
    # Lấy launcher type hiện tại
    launcher_type = launcher_var.get()
    
    # Validate path trước khi quét
    is_valid, msg = validate_mods_path(MODS_FOLDER, launcher_type)
    if not is_valid:
        status_label.config(text=msg, fg="red")
        messagebox.showerror("Đường dẫn không hợp lệ", 
                            f"{msg}\n\n"
                            f"Đường dẫn đúng cho {launcher_type.upper()}:\n"
                            f"{get_suggested_path(launcher_type)}")
        return
    
    status_label.config(text="🔄 Đang kiểm tra mods...", fg="blue")
    log_text.delete(1.0, tk.END)
    
    # Ẩn nút đồng bộ trước khi kiểm tra
    try:
        sync_button.pack_forget()
    except:
        pass
    
    root.update_idletasks()

    try:
        # Lấy danh sách mods từ server
        resp = requests.get(f"{SERVER_URL}/mods", timeout=5)
        resp.raise_for_status()
        server_mods = resp.json()["mods"]
        
        # Lấy danh sách mods local
        local_mods = get_local_mods()
        
        # So sánh
        missing_mods = []
        outdated_mods = []
        extra_mods = []
        
        log_text.insert(tk.END, f"📊 Server có: {len(server_mods)} mods\n")
        log_text.insert(tk.END, f"💾 Local có: {len(local_mods)} mods\n\n")
        
        # Kiểm tra mods thiếu hoặc cũ
        for mod_name, mod_info in server_mods.items():
            if mod_name not in local_mods:
                missing_mods.append(mod_name)
                log_text.insert(tk.END, f"❌ Thiếu: {mod_name}\n", "missing")
            elif local_mods[mod_name]["hash"] != mod_info["hash"]:
                outdated_mods.append(mod_name)
                log_text.insert(tk.END, f"🔄 Cũ: {mod_name}\n", "outdated")
        
        # Kiểm tra mods thừa (có local nhưng không có trên server)
        for mod_name in local_mods:
            if mod_name not in server_mods:
                extra_mods.append(mod_name)
                log_text.insert(tk.END, f"➕ Thừa: {mod_name}\n", "extra")
        
        # Cấu hình màu chữ
        log_text.tag_config("missing", foreground="red")
        log_text.tag_config("outdated", foreground="orange")
        log_text.tag_config("extra", foreground="purple")
        log_text.tag_config("success", foreground="green")
        log_text.tag_config("warning", foreground="orange")
        log_text.tag_config("info", foreground="blue")
        
        # Hiển thị kết quả
        total_need_update = len(missing_mods) + len(outdated_mods)
        
        if total_need_update == 0 and len(extra_mods) == 0:
            # Không có thay đổi - hiện chữ xanh
            status_label.config(text="✅ Không có cập nhật, mọi thứ đã đồng bộ!", fg="green")
            log_text.insert(tk.END, f"\n✅ Tất cả mods đã cập nhật!\n", "success")
        else:
            # Có thay đổi - hiện nút đồng bộ
            status_label.config(text="🟡 Phát hiện thay đổi!", fg="orange")
            
            # Tạo text thông tin
            info_text = []
            if total_need_update > 0:
                info_text.append(f"📥 {total_need_update} mods cần tải/cập nhật")
            if len(extra_mods) > 0:
                info_text.append(f"🗑️ {len(extra_mods)} mods thừa")
            
            log_text.insert(tk.END, f"\n⚠️ {' | '.join(info_text)}\n", "warning")
            log_text.insert(tk.END, "💡 Nhấn nút XANH LÁ bên dưới để đồng bộ\n\n", "info")
            
            # Hiện nút đồng bộ to và rõ ràng
            sync_button.pack(pady=5, padx=20, fill="x")
            root.update_idletasks()
        
    except Exception as e:
        status_label.config(text=f"❌ Lỗi kết nối server", fg="red")
        log_text.insert(tk.END, f"❌ Lỗi: {e}\n")
        messagebox.showerror("Lỗi kết nối", f"❌ Không thể kết nối server:\n{e}")

# =========================
# � Thực hiện đồng bộ
# =========================
def start_sync():
    """Bắt đầu đồng bộ khi người dùng nhấn nút"""
    sync_button.pack_forget()  # Ẩn nút đồng bộ
    threading.Thread(target=_perform_sync, daemon=True).start()

# =========================
# ⬇️ Tải mods cần cập nhật
# =========================
def _perform_sync():
    """Thực hiện đồng bộ: tải mods mới/cũ và xóa mods thừa"""
    try:
        status_label.config(text="🔄 Đang đồng bộ...", fg="blue")
        
        # Bước 1: Tải mods thiếu và cũ
        mods_to_download = missing_mods + outdated_mods
        if mods_to_download:
            total_mods = len(mods_to_download)
            progress_bar["maximum"] = total_mods + len(extra_mods)
            progress_bar["value"] = 0
            
            log_text.insert(tk.END, f"\n📥 Bắt đầu tải {total_mods} mods...\n", "info")
            
            for idx, mod_name in enumerate(mods_to_download, 1):
                log_text.insert(tk.END, f"⬇️ [{idx}/{total_mods}] {mod_name}...\n")
                log_text.see(tk.END)
                root.update_idletasks()
                
                # Tải mod từ server
                r = requests.get(f"{SERVER_URL}/download/{mod_name}", stream=True)
                r.raise_for_status()
                
                # Lưu file
                filepath = os.path.join(MODS_FOLDER, mod_name)
                with open(filepath, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                
                progress_bar["value"] = idx
                progress_label.config(text=f"Đang tải: {idx}/{total_mods}")
                log_text.insert(tk.END, f"   ✅ Hoàn tất\n", "success")
                root.update_idletasks()
        
        # Bước 2: Xóa mods thừa
        if extra_mods:
            log_text.insert(tk.END, f"\n🗑️ Đang xóa {len(extra_mods)} mods thừa...\n", "warning")
            for idx, mod_name in enumerate(extra_mods, 1):
                filepath = os.path.join(MODS_FOLDER, mod_name)
                try:
                    os.remove(filepath)
                    log_text.insert(tk.END, f"🗑️ Đã xóa: {mod_name}\n")
                    progress_bar["value"] = len(mods_to_download) + idx
                    root.update_idletasks()
                except Exception as e:
                    log_text.insert(tk.END, f"❌ Lỗi xóa {mod_name}: {e}\n")
        
        # Hoàn tất
        progress_bar["value"] = progress_bar["maximum"]
        progress_label.config(text="✅ Hoàn tất đồng bộ!")
        status_label.config(text="✅ Đồng bộ thành công!", fg="green")
        log_text.insert(tk.END, f"\n✅ Đã đồng bộ hoàn tất!\n", "success")
        log_text.see(tk.END)
        
        messagebox.showinfo("Thành công", "✅ Đã đồng bộ mods thành công!")
        
    except Exception as e:
        status_label.config(text="❌ Lỗi đồng bộ", fg="red")
        progress_label.config(text="Thất bại")
        log_text.insert(tk.END, f"\n❌ Lỗi: {e}\n")
        messagebox.showerror("Lỗi đồng bộ", f"❌ Không thể đồng bộ:\n{e}")

# =========================
# ⚙️ Chọn thư mục
# =========================
def on_launcher_change():
    """Khi người dùng chọn launcher khác"""
    global MODS_FOLDER
    launcher_type = launcher_var.get()
    
    # Cập nhật suggested path
    suggested = get_suggested_path(launcher_type)
    path_entry.delete(0, tk.END)
    path_entry.insert(0, suggested)
    path_entry.config(fg="gray", font=("Segoe UI", 8, "italic"))
    
    # Lưu launcher type
    save_config(MODS_FOLDER, launcher_type)
    
    log_text.delete(1.0, tk.END)
    log_text.insert(tk.END, f"💡 Đã chọn launcher: {launcher_type.upper()}\n", "info")
    log_text.insert(tk.END, f"📁 Đường dẫn mẫu: {suggested}\n\n", "info")
    log_text.insert(tk.END, "👉 Vui lòng chọn đúng thư mục 'mods' của instance bạn muốn đồng bộ\n", "warning")

def browse_folder():
    """Chọn thư mục mods mới"""
    global MODS_FOLDER
    
    launcher_type = launcher_var.get()
    base_path = detect_launcher_base_path(launcher_type)
    
    folder = filedialog.askdirectory(initialdir=base_path, title=f"Chọn thư mục Mods - {launcher_type.upper()}")
    if folder:
        # Validate path
        is_valid, msg = validate_mods_path(folder, launcher_type)
        
        if is_valid:
            MODS_FOLDER = folder
            save_config(MODS_FOLDER, launcher_type)
            os.makedirs(MODS_FOLDER, exist_ok=True)
            
            # Hiển thị path đã chọn
            path_entry.delete(0, tk.END)
            path_entry.insert(0, MODS_FOLDER)
            path_entry.config(fg="black", font=("Segoe UI", 8, "normal"))
            
            log_text.insert(tk.END, f"✅ Đã chọn thư mục: {MODS_FOLDER}\n", "success")
            messagebox.showinfo("Thành công", "✅ Đã thay đổi thư mục mods!")
        else:
            messagebox.showerror("Đường dẫn không hợp lệ", 
                               f"{msg}\n\n"
                               f"Đường dẫn đúng cho {launcher_type.upper()}:\n"
                               f"{get_suggested_path(launcher_type)}")

# =========================
# 🖼️ Giao diện Tkinter
# =========================
root = tk.Tk()
root.title("Minecraft Mods Sync Client")

# Căn giữa cửa sổ
window_width = 700
window_height = 550
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x = (screen_width - window_width) // 2
y = (screen_height - window_height) // 2
root.geometry(f"{window_width}x{window_height}+{x}+{y}")
root.resizable(False, False)

# Tiêu đề
title_label = tk.Label(root, text="🎮 Minecraft Mods Synchronizer", font=("Segoe UI", 14, "bold"))
title_label.pack(pady=10)

# Frame cho launcher selection
launcher_frame = tk.LabelFrame(root, text="🚀 Chọn Launcher", font=("Segoe UI", 10, "bold"))
launcher_frame.pack(pady=5, padx=20, fill="x")

# Radio buttons cho launcher
launcher_var = tk.StringVar(value=LAUNCHER_TYPE)

radio_frame = tk.Frame(launcher_frame)
radio_frame.pack(pady=5)

prism_radio = tk.Radiobutton(radio_frame, text="🔷 Prism Launcher", 
                              variable=launcher_var, value="prism",
                              font=("Segoe UI", 10), command=on_launcher_change)
prism_radio.pack(side="left", padx=20)

curseforge_radio = tk.Radiobutton(radio_frame, text="🔶 CurseForge", 
                                   variable=launcher_var, value="curseforge",
                                   font=("Segoe UI", 10), command=on_launcher_change)
curseforge_radio.pack(side="left", padx=20)

# Frame cho đường dẫn
path_frame = tk.LabelFrame(root, text="📁 Đường dẫn Mods", font=("Segoe UI", 10, "bold"))
path_frame.pack(pady=5, padx=20, fill="x")

# Entry hiển thị path với placeholder
path_inner_frame = tk.Frame(path_frame)
path_inner_frame.pack(pady=5, padx=5, fill="x")

path_entry = tk.Entry(path_inner_frame, font=("Segoe UI", 8), fg="gray")
path_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))

# Hiển thị path hiện tại hoặc suggested path
if MODS_FOLDER and MODS_FOLDER != DEFAULT_MODS_FOLDER:
    path_entry.insert(0, MODS_FOLDER)
    path_entry.config(fg="black", font=("Segoe UI", 8, "normal"))
else:
    suggested = get_suggested_path(LAUNCHER_TYPE)
    path_entry.insert(0, suggested)
    path_entry.config(fg="gray", font=("Segoe UI", 8, "italic"))

browse_button = tk.Button(path_inner_frame, text="📂 Chọn", font=("Segoe UI", 9), 
                          command=browse_folder, width=10)
browse_button.pack(side="left")

# Trạng thái
status_label = tk.Label(root, text="Chưa kiểm tra", font=("Segoe UI", 11))
status_label.pack(pady=5)

# Nút kiểm tra (giữa màn hình)
check_button = tk.Button(root, text="🔍 Quét kiểm tra", font=("Segoe UI", 11, "bold"), 
                         command=check_update, width=20, pady=5, bg="#2196F3", fg="white")
check_button.pack(pady=10)

# Khung cho nút đồng bộ (để giữ vị trí cố định)
sync_frame = tk.Frame(root)
sync_frame.pack(pady=5)

# Nút đồng bộ (ẩn mặc định, chỉ hiện khi có thay đổi)
sync_button = tk.Button(sync_frame, text="✅ ĐỒNG BỘ NGAY", font=("Segoe UI", 13, "bold"), 
                        command=start_sync, width=25, pady=10, bg="#4CAF50", fg="white",
                        cursor="hand2", relief="raised", borderwidth=3,
                        activebackground="#45a049")
# Không pack ngay, chỉ pack khi có thay đổi

# Log text
log_frame = tk.LabelFrame(root, text="📋 Chi tiết", font=("Segoe UI", 10, "bold"))
log_frame.pack(pady=10, padx=20, fill="both", expand=True)

log_text = scrolledtext.ScrolledText(log_frame, height=15, font=("Consolas", 9), wrap=tk.WORD)
log_text.pack(fill="both", expand=True, padx=5, pady=5)

# Thanh tiến trình
progress_bar = ttk.Progressbar(root, length=400, mode="determinate")
progress_bar.pack(pady=5)

progress_label = tk.Label(root, text="", font=("Segoe UI", 9))
progress_label.pack()

# Nút thoát
exit_button = tk.Button(root, text="❌ Thoát", command=root.destroy, font=("Segoe UI", 9))
exit_button.pack(side="bottom", pady=10)

root.mainloop()
