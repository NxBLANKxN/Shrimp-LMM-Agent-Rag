import React from "react"
import type { JSX } from "react"
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom"
import Login from "@/pages/Login"
import Register from "@/pages/Register"
import Dashboard from "@/pages/Dashboard"
import MainLayout from "@/layouts/MainLayout"
import AuthLayout from "@/layouts/AuthLayout"
import Members from "@/pages/Members"
import Home from "@/pages/Home"
import Settings from "@/pages/Settings"
import SystemPreview from "@/pages/SystemPreview"
import ChatPage from "@/pages/ChatPage"

// --- 修改後的權限攔截組件 ---
function RoleBasedRoute({
  children,
  allowedRoles
}: {
  children: JSX.Element,
  allowedRoles?: string[]
}) {
  const token = localStorage.getItem("token")
  const role = localStorage.getItem("role") // 從登入時存入的內容獲取

  // 1. 如果沒登入，通通回首頁
  if (!token) return <Navigate to="/" replace />

  // 2. 如果該頁面有指定權限限制，且當前用戶角色不符合
  if (allowedRoles && !allowedRoles.includes(role || "")) {
    alert("您的權限不足，無法進入此頁面")
    return <Navigate to="/" replace />
  }

  return children
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<AuthLayout><Login /></AuthLayout>} />
        <Route path="/register" element={<AuthLayout><Register /></AuthLayout>} />
        <Route path="/" element={<MainLayout><Home /></MainLayout>} />
        <Route path="/systemPreview" element={<MainLayout><SystemPreview /></MainLayout>} />
        <Route path="/members" element={<MainLayout><Members /></MainLayout>} />
        <Route path="/chat" element={<MainLayout><ChatPage /></MainLayout>} />
        <Route
          path="/dashboard"
          element={
            <RoleBasedRoute>
              <MainLayout>
                <Dashboard />
              </MainLayout>
            </RoleBasedRoute>
          }
        />
        <Route
          path="/settings"
          element={
            <RoleBasedRoute allowedRoles={["admin"]}>
              <MainLayout>
                <Settings />
              </MainLayout>
            </RoleBasedRoute>
          }
        />
      </Routes>
    </BrowserRouter>
  )
}