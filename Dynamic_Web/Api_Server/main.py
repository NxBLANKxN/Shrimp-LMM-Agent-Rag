import os
import sqlite3
import bcrypt
from datetime import datetime
from typing import List, Optional
from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

app = FastAPI()

# --- 1. 配置與中介軟體 (Configuration & Middleware) ---

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")


# --- 2. 資料模型 (Pydantic Models) ---

class LoginUser(BaseModel):
    username: str
    password: str

class MemberResponse(BaseModel):
    id: int
    name: str
    role: str
    image_url: Optional[str] = None
    bio: Optional[str] = None
    created_by: Optional[int] = None


# --- 3. 資料庫核心邏輯 (Database Core) ---

DB_PATH = "user.db"

def init_db():
    """初始化資料庫表結構、預設管理員與預設成員"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # User 表
    c.execute("""
        CREATE TABLE IF NOT EXISTS User (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            name TEXT,
            phone TEXT,
            address TEXT,
            role TEXT DEFAULT 'user'
        )
    """)
    
    # Member 表
    c.execute("""
        CREATE TABLE IF NOT EXISTS Member (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            role TEXT NOT NULL,
            image_url TEXT,
            bio TEXT,
            created_by INTEGER,
            FOREIGN KEY (created_by) REFERENCES User(id) ON DELETE SET NULL
        )
    """)
    
    # AuditLog 表
    c.execute("""
        CREATE TABLE IF NOT EXISTS AuditLog (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            action TEXT,
            target_type TEXT,
            target_id INTEGER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES User(id)
        )
    """)

    # --- A. 預設管理員檢查 ---
    c.execute("SELECT id FROM User WHERE username = 'admin'")
    admin_row = c.fetchone()
    admin_id = 1
    
    if not admin_row:
        # 預設密碼: 1qaz@WSX3edc
        hashed = bcrypt.hashpw("1qaz@WSX3edc".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        c.execute("INSERT INTO User (username, password, name, phone, address, role) VALUES (?, ?, ?, ?, ?, ?)",
                  ("admin", hashed, "系統管理員", "0000", "System", "admin"))
        admin_id = c.lastrowid
    else:
        admin_id = admin_row[0]

    # --- B. 預設成員檢查 (只有在資料表為空時才寫入) ---
    c.execute("SELECT count(*) FROM Member")
    if c.fetchone()[0] == 0:
        default_members = [
            ("吳竣霆", "基佬開發者", 
             "負責系統架構設計與前後端開發。", 
             "http://127.0.0.1:8000/uploads/monkey-thinking.png", 
             admin_id),
            ("毛柏竣", "簡報製作", 
             "專注簡報的製作。", 
             "", 
             admin_id)
        ]
        c.executemany("""
            INSERT INTO Member (name, role, bio, image_url, created_by) 
            VALUES (?, ?, ?, ?, ?)
        """, default_members)
        print(">>> 系統初始化：預設成員已寫入資料庫。")
    
    conn.commit()
    conn.close()

# 啟動時自動初始化
init_db()

def log_event(user_id: int, action: str, t_type: str, t_id: int):
    """紀錄操作日誌"""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT INTO AuditLog (user_id, action, target_type, target_id) VALUES (?, ?, ?, ?)",
            (user_id, action, t_type, t_id)
        )

# --- 4. 帳號 API (Auth & Users) ---

@app.post("/login")
def login(user: LoginUser):
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("SELECT id, password, role FROM User WHERE username = ?", (user.username,))
        row = c.fetchone()
        if row and bcrypt.checkpw(user.password.encode("utf-8"), row[1].encode("utf-8")):
            log_event(row[0], "LOGIN", "User", row[0])
            return {"msg": "success", "user_id": row[0], "username": user.username, "role": row[2]}
    return {"msg": "fail"}

@app.get("/users")
def get_users():
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute("SELECT id, username, name, phone, address, role FROM User").fetchall()
        return [dict(row) for row in rows]

# --- 5. 團隊成員 API (Members CRUD) ---

@app.get("/members", response_model=List[MemberResponse])
def get_members():
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute("SELECT * FROM Member").fetchall()
        return [dict(row) for row in rows]

@app.post("/members")
async def add_member(
    name: str = Form(...), 
    role: str = Form(...), 
    bio: str = Form(""),
    creator_id: int = Form(...),
    file: Optional[UploadFile] = File(None)
):
    image_url = ""
    if file:
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())
        image_url = f"http://127.0.0.1:8000/uploads/{file.filename}"

    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("INSERT INTO Member (name, role, image_url, bio, created_by) VALUES (?, ?, ?, ?, ?)", 
                  (name, role, image_url, bio, creator_id))
        new_id = c.lastrowid
        log_event(creator_id, "CREATE_MEMBER", "Member", new_id)
    return {"msg": "success"}

@app.put("/members/{member_id}")
async def update_member(
    member_id: int,
    editor_id: int = Form(...),
    name: str = Form(...),
    role: str = Form(...),
    bio: str = Form(""),
    file: Optional[UploadFile] = File(None)
):
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        if file:
            file_path = os.path.join(UPLOAD_DIR, file.filename)
            with open(file_path, "wb") as buffer:
                buffer.write(await file.read())
            img_url = f"http://127.0.0.1:8000/uploads/{file.filename}"
            c.execute("UPDATE Member SET name=?, role=?, bio=?, image_url=? WHERE id=?", 
                      (name, role, bio, img_url, member_id))
        else:
            c.execute("UPDATE Member SET name=?, role=?, bio=? WHERE id=?", 
                      (name, role, bio, member_id))
        log_event(editor_id, "UPDATE_MEMBER", "Member", member_id)
    return {"msg": "success"}

@app.delete("/members/{member_id}")
def delete_member(member_id: int, admin_id: int):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("DELETE FROM Member WHERE id = ?", (member_id,))
        log_event(admin_id, "DELETE_MEMBER", "Member", member_id)
    return {"msg": "success"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",             # 建議用字串格式 "檔名:物件名"
        host="127.0.0.1", 
        port=8000,
    )