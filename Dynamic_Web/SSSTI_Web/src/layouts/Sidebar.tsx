import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"
import {
  X,
  Home,
  LayoutDashboard,
  Users,
  Settings,
  Terminal,
  Database,
  MenuIcon,
  MessageCircle,
  Eye
} from "lucide-react"
import { useNavigate, useLocation } from "react-router-dom"

export default function Sidebar({
  open,
  onClose,
}: {
  open: boolean
  onClose: () => void
}) {
  const navigate = useNavigate()
  const location = useLocation()
  const [role, setRole] = useState<string | null>(null)

  useEffect(() => {
    // 每次打開側邊欄時重新確認 localStorage 中的角色狀態
    const currentRole = localStorage.getItem("role")
    setRole(currentRole)
  }, [open, location.pathname])

  const isLoggedIn = !!role; // 是否已登入
  const isAdmin = role === "admin"
  const isActive = (path: string) => location.pathname === path

  const handleNav = (path: string) => {
    navigate(path)
    onClose()
  }

  return (
    <aside
      className={cn(
        "fixed top-0 left-0 h-full w-64 bg-background border-r z-50 transition-transform duration-300 ease-in-out",
        open ? "translate-x-0" : "-translate-x-full"
      )}
    >
      {/* Header */}
      <div className="p-4 flex items-center justify-between border-b bg-zinc-50/50 dark:bg-zinc-900/50">
        <div className="flex items-center gap-2 font-semibold text-zinc-700 dark:text-zinc-200">
          <MenuIcon className="h-5 w-5 text-blue-500" />
          <span className="tracking-wide font-bold">系統導覽</span>
        </div>
        <Button variant="ghost" size="icon" onClick={onClose} className="hover:rotate-90 transition-transform">
          <X className="h-5 w-5" />
        </Button>
      </div>

      <div className="px-3 py-4 space-y-6 overflow-y-auto h-[calc(100%-70px)]">

        {/* --- 1. 公共功能 (所有人可見，包含未登入) --- */}
        <div>
          <p className="px-4 mb-2 text-[10px] font-bold text-muted-foreground uppercase tracking-widest">
            General
          </p>
          <div className="space-y-1">
            <Button
              variant={isActive("/") ? "secondary" : "ghost"}
              className={cn("w-full justify-start gap-3", isActive("/") && "bg-blue-50 text-blue-600 dark:bg-blue-900/30")}
              onClick={() => handleNav("/")}
            >
              <Home className="h-4 w-4" /> 首頁
            </Button>

            <Button
              variant={isActive("/systempreview") ? "secondary" : "ghost"}
              className={cn("w-full justify-start gap-3", isActive("/systempreview") && "bg-blue-50 text-blue-600 dark:bg-blue-900/30")}
              onClick={() => handleNav("/systempreview")}
            >
              <Eye className="h-4 w-4 text-purple-500" /> 系統特色預覽
            </Button>

            <Button
              variant={isActive("/chat") ? "secondary" : "ghost"}
              className={cn("w-full justify-start gap-3", isActive("/chat") && "bg-blue-50 text-blue-600 dark:bg-blue-900/30")}
              onClick={() => handleNav("/chat")}
            >
              <MessageCircle className="h-4 w-4 text-yellow-500" /> AI 智能聊天
            </Button>

            <Button
              variant={isActive("/members") ? "secondary" : "ghost"}
              className={cn("w-full justify-start gap-3", isActive("/members") && "bg-blue-50 text-blue-600 dark:bg-blue-900/30")}
              onClick={() => handleNav("/members")}
            >
              <Users className="h-4 w-4 text-emerald-500" /> 成員展示
            </Button>
          </div>
        </div>

        {/* --- 2. 使用者功能 (登入後可見：一般使用者 & 管理員) --- */}
        {isLoggedIn && (
          <div className="animate-in fade-in slide-in-from-left-4 duration-300">
            <p className="px-4 mb-2 text-[10px] font-bold text-blue-500 uppercase tracking-widest border-t pt-4">
              Main Services
            </p>
            <div className="space-y-1">
              <Button
                variant={isActive("/dashboard") ? "secondary" : "ghost"}
                className={cn("w-full justify-start gap-3", isActive("/dashboard") && "bg-blue-50 text-blue-600 dark:bg-blue-900/30")}
                onClick={() => handleNav("/dashboard")}
              >
                <LayoutDashboard className="h-4 w-4 text-blue-500" /> 後端儀表板
              </Button>
            </div>
          </div>
        )}

        {/* --- 3. 管理員專屬功能 (僅 Admin 可見) --- */}
        {isAdmin && (
          <div className="animate-in fade-in slide-in-from-left-4 duration-500">
            <p className="px-4 mb-2 text-[10px] font-bold text-red-500 uppercase tracking-widest border-t pt-4">
              System Management
            </p>
            <div className="space-y-1">
              <Button variant="ghost" className="w-full justify-start gap-3 text-muted-foreground/60 hover:text-foreground">
                <Database className="h-4 w-4" /> 資料庫狀態
              </Button>

              <Button variant="ghost" className="w-full justify-start gap-3 text-muted-foreground/60 hover:text-foreground">
                <Terminal className="h-4 w-4" /> API 日誌
              </Button>

              <Button
                variant={isActive("/settings") ? "secondary" : "ghost"}
                className={cn("w-full justify-start gap-3", isActive("/settings") && "bg-blue-50 text-blue-600 dark:bg-blue-900/30")}
                onClick={() => handleNav("/settings")}
              >
                <Settings className="h-4 w-4 text-zinc-500" /> 系統設定
              </Button>
            </div>
          </div>
        )}
      </div>

      {/* Footer 狀態顯示 */}
      <div className="absolute bottom-0 w-full p-4 border-t bg-zinc-50/80 dark:bg-zinc-900/80 backdrop-blur-sm">
        <div className="flex items-center gap-2 px-2">
          <div className={cn(
            "h-2 w-2 rounded-full",
            isAdmin ? "bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.6)]" :
              isLoggedIn ? "bg-blue-400" : "bg-zinc-300"
          )} />
          <span className="text-[11px] font-medium text-muted-foreground italic">
            {isAdmin ? "超級管理員" : isLoggedIn ? "一般使用者" : "訪客模式 (未登入)"}
          </span>
        </div>
      </div>
    </aside>
  )
}