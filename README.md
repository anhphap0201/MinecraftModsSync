# 🎮 Minecraft Mods Synchronizer

Ứng dụng đồng bộ mods Minecraft giữa Server và Client qua mạng LAN/Internet.

## ✨ Tính năng

- 🔍 **Quét và so sánh** mods giữa server và client
- 📥 **Tự động tải** mods thiếu hoặc cũ
- 🗑️ **Tự động xóa** mods thừa không có trên server
- 📊 **Giao diện trực quan** với Tkinter
- 🚀 **Client độc lập** - File EXE không cần cài Python
- 🌐 **Server FastAPI** - Nhanh và hiện đại

## 📁 Cấu trúc dự án

```
CheckUpdate/
├── client/              # Client application
│   ├── client.py       # Source code chính
│   ├── build.bat       # Script build EXE
│   └── dist/           # File EXE (sau khi build)
├── server/              # Server FastAPI
│   └── server.py       # API server
└── mods/               # Thư mục chứa mods (server)
```

## 🚀 Cài đặt và Sử dụng

### **Server**

1. **Cài đặt dependencies:**
```bash
pip install fastapi uvicorn
```

2. **Đặt mods vào thư mục `mods/`** (chỉ file .jar)

3. **Chạy server:**
```bash
cd server
python server.py
```

Server sẽ chạy tại: `http://0.0.0.0:5000`

### **Client**

#### **Cách 1: Dùng file EXE (Khuyến nghị)**

1. Tải file `MinecraftModsSync.exe` từ:
   - Thư mục `client/dist/`
   - Hoặc từ server: `http://SERVER_IP:5000/download-client`

2. Chạy file EXE và sử dụng!

#### **Cách 2: Chạy từ source code**

1. **Cài đặt dependencies:**
```bash
pip install requests
```

2. **Chạy client:**
```bash
cd client
python client.py
```

#### **Cách 3: Build EXE từ source**

1. **Cài đặt PyInstaller:**
```bash
pip install pyinstaller
```

2. **Build:**
```bash
cd client
pyinstaller --onefile --windowed --name="MinecraftModsSync" client.py
```

File EXE sẽ nằm trong `client/dist/`

## 🔧 Cấu hình

### **Client**

- **Server URL:** Mặc định `http://26.35.131.42:5000` (sửa trong `client.py`)
- **Mods Folder:** Chọn thông qua giao diện hoặc sửa trong `config.json`

### **Server**

Server tự động quét thư mục `mods/` và phục vụ tất cả file `.jar`

## 📡 API Endpoints

| Endpoint | Method | Mô tả |
|----------|--------|-------|
| `/` | GET | Thông tin server và danh sách endpoints |
| `/mods` | GET | Lấy danh sách mods và hash |
| `/download/{mod_name}` | GET | Tải mod cụ thể |
| `/download-client` | GET | Tải client.exe |
| `/docs` | GET | Swagger API documentation |

## 🎯 Cách hoạt động

1. **Client** kết nối tới **Server** và lấy danh sách mods
2. So sánh hash SHA256 của từng mod
3. Phát hiện:
   - ❌ Mods thiếu
   - 🔄 Mods cũ (khác hash)
   - ➕ Mods thừa (client có nhưng server không)
4. Người dùng xác nhận đồng bộ
5. Tự động tải mods mới/cũ và xóa mods thừa

## 🛠️ Công nghệ sử dụng

### **Client**
- Python 3.x
- Tkinter (GUI)
- Requests (HTTP client)
- PyInstaller (Build EXE)

### **Server**
- Python 3.x
- FastAPI (Web framework)
- Uvicorn (ASGI server)

## 📝 Yêu cầu hệ thống

- **Python:** 3.7+ (chỉ cần cho development)
- **OS:** Windows (Client EXE), Linux/Windows (Server)
- **Network:** LAN hoặc Internet giữa client và server

## 🔐 Bảo mật

- ✅ Kiểm tra hash SHA256 để đảm bảo tính toàn vẹn file
- ✅ Path traversal protection
- ✅ Chỉ cho phép file .jar

## 📄 License

MIT License

## 👤 Tác giả

Dự án Minecraft Mods Synchronizer

## 🤝 Đóng góp

Pull requests được chào đón! Với những thay đổi lớn, vui lòng mở issue trước để thảo luận.

## 📞 Liên hệ

- Issues: [GitHub Issues](https://github.com/YOUR_USERNAME/CheckUpdate/issues)

---

Made with ❤️ for Minecraft modding community
