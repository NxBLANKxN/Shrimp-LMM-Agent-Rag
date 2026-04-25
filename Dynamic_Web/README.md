# Dynamic_Web

## 🦐 Smart Shrimp Spawning Tracking Web

一個結合影像辨識與 Web 系統的智慧蝦隻產卵辨識與追蹤平台。

---

# 📦 環境需求

## 🔹 Backend

* Python >= 3.10
* FastAPI
* Uvicorn
* bcrypt

## 🔹 Frontend

* Bun

---

# ⚙️ 後端啟動（FastAPI）

## 1️⃣ 進入後端資料夾

```bash
cd Api_Server
```

## 2️⃣ 安裝套件

```bash
pip install fastapi uvicorn bcrypt
```

## 3️⃣ 啟動後端

```bash
python main.py
```

## 🔗 後端網址

```
http://127.0.0.1:8000
```

---

# 🌐 前端啟動（React + Bun）

## 1️⃣ 進入前端資料夾

```bash
cd SSSTI_Web
```

## 2️⃣ 安裝 Bun（若尚未安裝）

### Linux
```bash
curl -fsSL https://bun.sh/install | bash
```

### windows

```bash
powershell -c "irm bun.sh/install.ps1 | iex"
```

## 3️⃣ 安裝專案套件

```bash
bun install
```

## 4️⃣ 啟動前端

```bash
bun run dev
```

## 🔗 前端網址

```
http://localhost:5173
```

---

# 🔐 測試流程

1. 啟動後端（FastAPI）
2. 啟動前端（Bun）
3. 開啟瀏覽器進入：

   ```
   http://localhost:5173
   ```
4. 註冊帳號 → 登入 → 進入 Dashboard

---

# 📁 專案結構

```
Dynamic_Web/
│
├── Api_Server/        # FastAPI 後端
│   ├── main.py
│   └── user.db
│
├── SSSTI_Web/         # React 前端（Bun + Vite）
│   ├── src/
│   ├── package.json
│   ├── bun.lockb
│   ├── components.json
|   ├── eslint.config.js
|   ├── index.html
|   ├── package.json
|   ├── tsconfig.app.json
|   ├── tsconfig.json
|   ├── tsconfig.node.json
|   └── vite.config.ts
|
└── README.md
```

---

# 🚨 注意事項

* 前端 API 預設連接：

  ```
  http://127.0.0.1:8000
  ```
* 請確保後端先啟動，否則登入/註冊會失敗
* 若出現錯誤可嘗試重新安裝套件：

## 前端

```bash
bun install
```

## 後端

```bash
pip install -r requirements.txt
```

（若尚未建立 requirements.txt 可忽略）

---

# 🛠 常見問題

## ❓ 無法登入 / 註冊

* 確認後端是否啟動
* 檢查 API URL 是否正確

## ❓ 出現 Invalid salt

* 刪除舊資料庫：

```bash
rm user.db
```

（Windows）

```bash
del user.db
```

## ❓ 405 / CORS 錯誤

* 確認 FastAPI 已啟用 CORS
* 確認請求方法為 POST

---

# 🚀 技術架構

* Frontend：React + TypeScript + Vite + Bun
* UI：Tailwind CSS + shadcn/ui
* Backend：FastAPI
* Database：SQLite