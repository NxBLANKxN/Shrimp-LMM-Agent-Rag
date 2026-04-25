import { useState, useEffect } from "react"
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Code2, Globe, Database, Cpu, UserCircle } from "lucide-react"
import { API_LIST } from "@/data/api-docs" 
import { ApiCard } from "@/components/ApiCard" 
import { cn } from "@/lib/utils"

export default function Dashboard() {
  const [username] = useState(() => localStorage.getItem("username") || "User")
  const [role, setRole] = useState<string | null>(null)

  useEffect(() => {
    const currentRole = localStorage.getItem("role")
    setRole(currentRole)
  }, [])

  const isAdmin = role === "admin"

  // 根據角色篩選 API，這行現在不會報錯了
  const visibleApis = isAdmin 
    ? API_LIST 
    : API_LIST.filter(api => !api.adminOnly) 

  const stats = [
    { 
      label: "當前用戶", 
      value: username, 
      icon: (
        <Badge variant={isAdmin ? "default" : "secondary"} className={cn(isAdmin ? "bg-red-500 hover:bg-red-600" : "bg-blue-500 hover:bg-blue-600")}>
          {isAdmin ? "Admin" : "User"}
        </Badge>
      ), 
      color: "text-primary" 
    },
    { label: "後端地址", value: "127.0.0.1:8000", icon: <Globe className="h-4 w-4" />, color: "text-blue-500" },
    { label: "資料庫", value: "SQLite", icon: <Database className="h-4 w-4" />, color: "text-indigo-500" },
    { label: "API 版本", value: "v1.0-dev", icon: <Cpu className="h-4 w-4" />, color: "text-muted-foreground" },
  ]

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      
      {/* 歡迎區塊 - 已移除虛線 (border-dashed) */}
      <div className="flex items-center gap-4 bg-white dark:bg-zinc-900 p-6 rounded-2xl border border-zinc-200 dark:border-zinc-800 shadow-sm">
        <div className={cn("p-3 rounded-full bg-zinc-100 dark:bg-zinc-800", isAdmin ? "text-red-500" : "text-blue-500")}>
          <UserCircle className="h-8 w-8" />
        </div>
        <div>
          <p className="text-2xl font-bold tracking-tight">歡迎回來，{username}</p>
          <p className="text-sm text-muted-foreground">
            權限狀態：<span className={cn("font-semibold uppercase", isAdmin ? "text-red-500" : "text-blue-500")}>{role || "Loading..."}</span>
          </p>
        </div>
      </div>

      {/* 狀態卡片區 */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {stats.map((item, i) => (
          <Card key={i} className="border border-zinc-200 dark:border-zinc-800 shadow-sm bg-card/50">
            <CardContent className="p-4 flex flex-col gap-1 text-left">
              <div className="flex items-center justify-between text-xs text-muted-foreground">
                <span>{item.label}</span>
                {item.icon}
              </div>
              <div className={`text-lg font-bold ${item.color}`}>{item.value}</div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* API 文檔區 */}
      <div className="space-y-4">
        <div className="flex items-center justify-between px-1">
          <div className="flex items-center gap-2">
            <Code2 className="h-5 w-5 text-blue-500" />
            <p className="text-xl font-bold">API 接口說明</p>
          </div>
          {!isAdmin && <Badge variant="outline" className="opacity-60 text-[10px]">僅顯示公共接口</Badge>}
        </div>

        <div className="grid gap-6">
          {visibleApis.map((api, idx) => (
            <ApiCard key={idx} api={api} />
          ))}
        </div>
      </div>
    </div>
  )
}