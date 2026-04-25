import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { AlertCircleIcon, LogIn } from "lucide-react"
import { useNavigate } from "react-router-dom"

export default function Login() {
  const navigate = useNavigate()
  const [username, setUsername] = useState("")
  const [password, setPassword] = useState("")
  const [error, setError] = useState(false)
  const [errorMsg, setErrorMsg] = useState("")
  const [loading, setLoading] = useState(false)

  // 監聽 Enter 鍵
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Enter") {
        e.preventDefault()
        if (error) {
          setError(false)
        } else {
          handleLogin()
        }
      }
    }
    window.addEventListener("keydown", handleKeyDown)
    return () => window.removeEventListener("keydown", handleKeyDown)
  }, [username, password, error, loading])

  const handleLogin = async () => {
    if (loading) return

    if (!username || !password) {
      setErrorMsg("帳號與密碼不能為空")
      setError(true)
      return
    }

    setLoading(true)

    try {
      const res = await fetch("http://127.0.0.1:8000/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
      })

      const data = await res.json()

      if (data.msg === "success") {
        // ✅ 儲存憑證與權限資訊
        localStorage.setItem("token", "ok")
        localStorage.setItem("username", username)
        localStorage.setItem("role", data.role) // 儲存後端回傳的角色 (admin 或 user)
        
        navigate("/") 
      } else {
        setErrorMsg("帳號或密碼錯誤")
        setError(true)
      }
    } catch {
      setErrorMsg("系統錯誤，請稍後再試")
      setError(true)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex items-center justify-center min-h-auto">
      <Card className="w-full max-w-sm shadow-xl">
        <CardHeader>
          <CardTitle className="text-2xl text-center font-bold">系統登入</CardTitle>
        </CardHeader>

        <CardContent className="space-y-4">
          {/* ❌ Error Modal */}
          {error && (
            <div className="fixed inset-0 m-0 z-50 flex items-center justify-center p-4">
              <div
                className="absolute inset-0 bg-black/60 backdrop-blur-sm"
                onClick={() => setError(false)}
              />
              <div className="relative z-10 w-full max-w-sm rounded-2xl bg-white dark:bg-zinc-900 shadow-2xl p-6 border border-red-500 animate-in zoom-in duration-200">
                <div className="flex items-center gap-3 mb-4">
                  <div className="bg-red-500/10 p-2 rounded-full">
                    <AlertCircleIcon className="h-6 w-6 text-red-500" />
                  </div>
                  <h3 className="text-xl font-bold text-red-500">登入失敗</h3>
                </div>
                <p className="text-muted-foreground leading-relaxed">{errorMsg}</p>
                <Button 
                  className="w-full mt-6 bg-red-500 hover:bg-red-600 font-bold text-white"
                  autoFocus 
                  onClick={() => setError(false)}
                >
                  確認
                </Button>
              </div>
            </div>
          )}

          <div className="space-y-2">
            <Input
              placeholder="帳號"
              value={username}
              onChange={(e) => {
                setError(false)
                setUsername(e.target.value)
              }}
            />
            <Input
              type="password"
              placeholder="密碼"
              value={password}
              onChange={(e) => {
                setError(false)
                setPassword(e.target.value)
              }}
            />
          </div>

          <Button
            className="w-full h-11 font-bold gap-2"
            onClick={handleLogin}
            disabled={loading}
          >
            <LogIn className="h-4 w-4" />
            {loading ? "登入中..." : "立即登入"}
          </Button>

          <div className="grid grid-cols-2 gap-3 pt-2">
            <Button
              variant="outline"
              className="text-xs"
              onClick={() => navigate("/register")}
            >
              前往註冊
            </Button>
            <Button
              variant="outline"
              className="text-xs"
              onClick={() => navigate("/")}
            >
              返回首頁
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}