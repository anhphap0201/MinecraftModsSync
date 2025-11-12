# 🖥️ Minecraft Mods Sync Server - Hướng dẫn sử dụng

## 📦 Cách sử dụng (Người dùng cuối - Không cần install)

### Bước 1: Tải file
1. Tải file `MinecraftModsSync_Server.exe`
2. Giải nén (nếu có)
3. Đảm bảo có thư mục `mods` cùng cấp với file `.exe`

### Bước 2: Chuẩn bị mods
1. Copy tất cả file mods (`.jar`) vào thư mục `mods/`
2. Server sẽ tự động đọc và phục vụ các mods này

### Bước 3: Chạy server
1. Double-click vào `MinecraftModsSync_Server.exe`
2. Cửa sổ server sẽ hiện lên với:
   - Địa chỉ IPv4 và IPv6
   - Danh sách mods hiện có
   - Trạng thái server
3. Nhấn nút **"START SERVER"**
4. Đợi server khởi động (status chuyển sang 🟢 Đang chạy)

### Bước 4: Chia sẻ địa chỉ cho client
1. Nhấn vào địa chỉ IPv4 hoặc IPv6 để copy
2. Gửi địa chỉ cho người dùng client
3. Client sẽ nhập địa chỉ này vào `.env` file

### Bước 5: Dừng server
1. Nhấn nút **"STOP SERVER"** (nếu cần)
2. Hoặc đóng cửa sổ

## 🔧 Cấu hình (Nâng cao)

### Sử dụng file .env
Tạo file `.env` cùng cấp với `MinecraftModsSync_Server.exe`:

```env
# Server IP (mặc định :: cho dual-stack IPv6+IPv4)
SERVER_HOST=::

# Port (mặc định 5000)
SERVER_PORT=5000

# IPv6 tùy chỉnh (tùy chọn)
SERVER_IPV6=your_ipv6_here
```

## 📁 Cấu trúc thư mục

```
MinecraftModsSync_Server/
├── MinecraftModsSync_Server.exe  # File chính
├── .env                           # Config (tùy chọn)
└── mods/                          # Thư mục chứa mods
    ├── mod1.jar
    ├── mod2.jar
    └── ...
```

## ⚠️ Lưu ý

1. **Firewall**: Có thể cần cho phép ứng dụng qua Windows Firewall
2. **Port**: Đảm bảo port 5000 không bị chiếm bởi ứng dụng khác
3. **Mods**: Chỉ hỗ trợ file `.jar`
4. **Restart**: Sau khi stop, cần khởi động lại ứng dụng để start server lại

## 🎮 Tính năng

- ✅ Giao diện trực quan, dễ sử dụng
- ✅ Hiển thị danh sách mods real-time
- ✅ Copy địa chỉ server một cú click
- ✅ Log hoạt động chi tiết
- ✅ Hỗ trợ cả IPv4 và IPv6
- ✅ Không cần cài đặt Python hay dependencies

## 🆘 Khắc phục sự cố

### Server không khởi động
- Kiểm tra port 5000 có bị chiếm không
- Chạy với quyền Administrator
- Kiểm tra Windows Firewall

### Client không kết nối được
- Đảm bảo server đang chạy (🟢 Đang chạy)
- Kiểm tra địa chỉ IP đã đúng chưa
- Kiểm tra cả client và server cùng mạng
- Thử dùng IPv4 thay vì IPv6

### Không thấy mods
- Kiểm tra thư mục `mods/` có tồn tại không
- Đảm bảo file mods có đuôi `.jar`
- Nhấn nút "🔄 Làm mới danh sách"

## 📞 Hỗ trợ

Nếu gặp vấn đề, kiểm tra phần **Log** trong ứng dụng để xem thông tin lỗi chi tiết.
