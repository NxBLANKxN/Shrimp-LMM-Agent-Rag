import { Button } from "@/components/ui/button"
import { useEffect, useState } from "react"
import { Menu, Sun, Moon, LogIn, UserPlus, LogOut } from "lucide-react"

export default function Header({ onMenuClick }: { onMenuClick: () => void }) {
  // 主題切換狀態
  const [dark, setDark] = useState(() => {
    const saved = localStorage.getItem("theme")
    return saved ? saved === "dark" : true
  })

  // 登入狀態
  const [isLoggedIn, setIsLoggedIn] = useState(false)

  useEffect(() => {
    // 檢查是否有 token
    const token = localStorage.getItem("token")
    setIsLoggedIn(!!token)

    // 套用主題
    if (dark) {
      document.documentElement.classList.add("dark")
      localStorage.setItem("theme", "dark")
    } else {
      document.documentElement.classList.remove("dark")
      localStorage.setItem("theme", "light")
    }
  }, [dark])

  const toggleTheme = () => setDark(prev => !prev)

  const handleLogout = () => {
    localStorage.removeItem("role");  
    localStorage.removeItem("token")
    localStorage.removeItem("username")
    setIsLoggedIn(false)
    window.location.href = "/" 
  }

  return (
    <header className="h-14 border-b flex items-center px-4 bg-background justify-between">
      
      <div className="flex gap-4 items-center">
        <Button variant="ghost" size="icon" onClick={onMenuClick}>
          <Menu />
        </Button>
        <div className="font-bold text-blue-500 hidden sm:block">
          智慧蝦隻辨識系統
        </div>
      </div>

      <div className="flex gap-3 items-center">

        <Button variant="ghost" size="icon" onClick={toggleTheme}>
          {dark ? <Moon size={18} /> : <Sun size={18} />}
        </Button>


        {isLoggedIn ? (
          <Button
            variant="outline"
            size="sm"
            className="gap-2 border-red-200 hover:bg-red-50 dark:hover:bg-red-950/30 text-red-600"
            onClick={handleLogout}
          >
            <LogOut size={16} />
            登出
          </Button>
        ) : (
          <div className="flex gap-2">
            <Button
              variant="ghost"
              size="sm"
              className="gap-2"
              onClick={() => (window.location.href = "/login")}
            >
              <LogIn size={16} />
              登入
            </Button>
            <Button
              variant="default"
              size="sm"
              className="gap-2 bg-blue-600 hover:bg-blue-700"
              onClick={() => (window.location.href = "/register")}
            >
              <UserPlus size={16} />
              註冊
            </Button>
          </div>
        )}
      </div>

    </header>
  )
}