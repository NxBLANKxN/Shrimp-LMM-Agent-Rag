export interface ApiSpec {
  title: string;
  method: "POST" | "GET" | "PUT" | "DELETE";
  endpoint: string;
  desc: string;
  requestBody: object;
  response: object;
}

export const API_LIST: ApiSpec[] = [
  {
    title: "帳號註冊 (User Registration)",
    method: "POST",
    endpoint: "/register",
    desc: "建立新帳號。系統會自動紀錄註冊日誌。",
    requestBody: {
      username: "user_example",
      password: "secure_password",
      name: "使用者名稱",
      phone: "電話",
      address: "地址",
      role: "admin | user",
    },
    response: { msg: "success | exists" },
  },
  {
    title: "帳號登入 (User Login)",
    method: "POST",
    endpoint: "/login",
    desc: "驗證成功後會回傳 user_id，請存於 localStorage 以供後續關聯使用。",
    requestBody: {
      username: "user_example",
      password: "secure_password",
    },
    response: {
      msg: "success",
      user_id: 1, // <--- 新增：用於後續所有關聯操作
      username: "user_example",
      role: "admin",
    },
  },
  {
    title: "獲取帳號列表 (Get Users)",
    method: "GET",
    endpoint: "/users",
    desc: "取得系統內所有使用者。",
    requestBody: {},
    response: [{ id: 1, username: "admin", role: "admin" }],
  },
  {
    title: "刪除帳號 (Delete User)",
    method: "DELETE",
    endpoint: "/users/{user_id}?admin_id={admin_id}",
    desc: "刪除指定帳號，需帶入操作者的 admin_id 以供紀錄日誌。",
    requestBody: {},
    response: { msg: "success" },
  },
  {
    title: "獲取團隊成員列表 (Get Members)",
    method: "GET",
    endpoint: "/members",
    desc: "取得成員資訊，包含 created_by (建立者 ID)。",
    requestBody: {},
    response: [
      {
        id: 1,
        name: "姓名",
        role: "職位",
        image_url: "url",
        created_by: 1, // <--- 新增：顯示資料歸屬
      },
    ],
  },
  {
    title: "新增團隊成員 (Add Member)",
    method: "POST",
    endpoint: "/members",
    desc: "必須傳入 creator_id 以建立資料庫關聯。",
    requestBody: {
      name: "姓名",
      role: "職位",
      bio: "簡介",
      creator_id: 1, // <--- 新增：建立者關聯 (Required)
      file: "圖片檔案",
    },
    response: { msg: "success" },
  },
  {
    title: "更新團隊成員 (Update Member)",
    method: "PUT",
    endpoint: "/members/{member_id}",
    desc: "更新成員資料，需傳入 editor_id 以紀錄是誰修改的。",
    requestBody: {
      editor_id: 1, // <--- 新增：修改者紀錄 (Required)
      name: "姓名",
      role: "職位",
      bio: "簡介",
      file: "新圖片檔案",
    },
    response: { msg: "success" },
  },
  {
    title: "刪除團隊成員 (Delete Member)",
    method: "DELETE",
    endpoint: "/members/{member_id}?admin_id={admin_id}",
    desc: "刪除成員，需帶入 admin_id 紀錄日誌。",
    requestBody: {},
    response: { msg: "success" },
  },
];
