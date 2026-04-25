import { useEffect, useState } from "react"
import { Button } from "@/components/ui/button"
import { Sun, Moon, Waves, ShieldCheck } from "lucide-react"

export default function AuthLayout({ children }: { children: React.ReactNode }) {
  const [dark, setDark] = useState(() => {
    const saved = localStorage.getItem("theme")
    return saved ? saved === "dark" : true
  })

  useEffect(() => {
    if (dark) {
      document.documentElement.classList.add("dark")
      localStorage.setItem("theme", "dark")
    } else {
      document.documentElement.classList.remove("dark")
      localStorage.setItem("theme", "light")
    }
  }, [dark])

  const toggleTheme = () => setDark(prev => !prev)

  return (
    <div className="min-h-screen flex flex-col bg-background text-foreground relative overflow-hidden">
      
      <div className="absolute top-0 left-0 w-full h-full overflow-hidden -z-10 pointer-events-none">
        <div className="absolute -top-[10%] -left-[10%] w-[40%] h-[40%] bg-blue-500/5 rounded-full blur-[120px]" />
        <div className="absolute -bottom-[10%] -right-[10%] w-[40%] h-[40%] bg-indigo-500/5 rounded-full blur-[120px]" />
      </div>

      <header className="h-16 flex items-center justify-between px-6 lg:px-4  bg-background/50 backdrop-blur-md border-b">
        <div 
          className="flex items-center gap-2 font-bold text-lg cursor-pointer"
          onClick={() => window.location.href = "/"}
        >
          <span className="tracking-tight">智慧蝦隻辨識系統</span>
        </div>

        <div className="flex items-center gap-2">
          <Button variant="ghost" size="icon" onClick={toggleTheme} className="rounded-full">
            {dark ? <Moon size={18} /> : <Sun size={18} />}
          </Button>
        </div>
      </header>

      <main className="flex-1 flex flex-col items-center justify-center px-4 py-12 relative">
        <div className="mb-8 text-center space-y-2">
          <h2 className="text-2xl font-bold tracking-tight">身分驗證</h2>
          <p className="text-sm text-muted-foreground">
            請登入您的帳號以進入智慧管理後台
          </p>
        </div>

        <div className="w-full max-w-md animate-in fade-in zoom-in duration-300">
          {children}
        </div>
      </main>

      <footer className="py-6 border-t flex flex-col items-center justify-center gap-2 bg-background/50 backdrop-blur-md">
        <div className="flex gap-6 text-xs text-muted-foreground mb-1">
          <span className="cursor-pointer hover:text-blue-500 transition-colors">隱私權政策</span>
          <span className="cursor-pointer hover:text-blue-500 transition-colors">服務條款</span>
          <span className="cursor-pointer hover:text-blue-500 transition-colors">聯絡支援</span>
        </div>
        <p className="text-[12px] text-muted-foreground/60 uppercase tracking-widest">
          © 2026 智慧蝦隻辨識系統．版權所有
        </p>
      </footer>

    </div>
  )
}