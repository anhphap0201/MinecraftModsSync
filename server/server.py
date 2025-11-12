from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
import hashlib
import os

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

app = FastAPI()

# Đường dẫn đến thư mục chứa mods
MODS_FOLDER = os.path.join(os.path.dirname(__file__), "..", "mods")

# Đường dẫn đến file client.exe
CLIENT_EXE_PATH = os.path.join(os.path.dirname(__file__), "..", "client", "dist", "MinecraftModsSync.exe")

# Server configuration từ .env
SERVER_HOST = os.getenv("SERVER_HOST", "::")
SERVER_PORT = int(os.getenv("SERVER_PORT", "5000"))
SERVER_IPV6 = os.getenv("SERVER_IPV6", "localhost")

def get_file_hash(path):
    """Tính hash SHA256 của file"""
    sha256 = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256.update(chunk)
    return sha256.hexdigest()

def get_all_mods():
    """Lấy danh sách tất cả mods và thông tin của chúng"""
    mods = {}
    if not os.path.exists(MODS_FOLDER):
        return mods
    
    for filename in os.listdir(MODS_FOLDER):
        # Chỉ lấy file .jar (Minecraft mods)
        if filename.endswith('.jar'):
            filepath = os.path.join(MODS_FOLDER, filename)
            mods[filename] = {
                "hash": get_file_hash(filepath),
                "size": os.path.getsize(filepath)
            }
    return mods

@app.get("/")
def root():
    """Endpoint gốc"""
    return {
        "message": "Minecraft Mods Sync Server", 
        "version": "2.0",
        "endpoints": {
            "GET /mods": "Lấy danh sách mods",
            "GET /download/{mod_name}": "Tải mod cụ thể",
            "GET /download-client": "Tải client.exe"
        }
    }

@app.get("/mods")
def get_mods_list():
    """Trả về danh sách tất cả mods và hash của chúng"""
    mods = get_all_mods()
    return {
        "count": len(mods),
        "mods": mods
    }

@app.get("/download/{mod_name}")
def download_mod(mod_name: str):
    """Cho phép client tải một mod cụ thể"""
    # Kiểm tra tên file hợp lệ (chỉ .jar và không có path traversal)
    if not mod_name.endswith('.jar') or '/' in mod_name or '\\' in mod_name:
        raise HTTPException(status_code=400, detail="Invalid mod name")
    
    filepath = os.path.join(MODS_FOLDER, mod_name)
    
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Mod not found")
    
    return FileResponse(filepath, filename=mod_name, media_type="application/java-archive")

@app.get("/download-client")
def download_client():
    """Cho phép tải file client.exe"""
    if not os.path.exists(CLIENT_EXE_PATH):
        raise HTTPException(status_code=404, detail="Client not found. Please build the client first.")
    
    return FileResponse(
        CLIENT_EXE_PATH, 
        filename="MinecraftModsSync.exe",
        media_type="application/octet-stream",
        headers={
            "Content-Disposition": "attachment; filename=MinecraftModsSync.exe"
        }
    )

if __name__ == "__main__":
    import uvicorn
    
    # Kiểm tra thư mục mods tồn tại
    if not os.path.exists(MODS_FOLDER):
        print(f"❌ CẢNH BÁO: Không tìm thấy thư mục {MODS_FOLDER}")
        print(f"📁 Tạo thư mục mới...")
        os.makedirs(MODS_FOLDER, exist_ok=True)
    else:
        mods_count = len([f for f in os.listdir(MODS_FOLDER) if f.endswith('.jar')])
        print(f"✅ Thư mục mods sẵn sàng: {MODS_FOLDER}")
        print(f"📊 Số lượng mods: {mods_count}")
        
        # Tính tổng dung lượng
        total_size = sum(
            os.path.getsize(os.path.join(MODS_FOLDER, f)) 
            for f in os.listdir(MODS_FOLDER) 
            if f.endswith('.jar')
        )
        print(f"💾 Tổng dung lượng: {total_size / (1024*1024):.2f} MB")
    
    # Kiểm tra client.exe
    if os.path.exists(CLIENT_EXE_PATH):
        client_size = os.path.getsize(CLIENT_EXE_PATH)
        print(f"✅ Client EXE sẵn sàng: {client_size / (1024*1024):.2f} MB")
        print(f"📥 Link tải: http://[{SERVER_IPV6}]:{SERVER_PORT}/download-client")
    else:
        print(f"⚠️ Client EXE chưa có: {CLIENT_EXE_PATH}")
    
    print(f"🚀 Đang khởi động server tại http://[{SERVER_HOST}]:{SERVER_PORT}")
    print(f"📖 API docs: http://[{SERVER_IPV6}]:{SERVER_PORT}/docs")
    uvicorn.run("server:app", host=SERVER_HOST, port=SERVER_PORT, reload=True)
