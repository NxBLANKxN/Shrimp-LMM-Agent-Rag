import { useState, useEffect } from "react"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { AlertCircleIcon, UserPlus, CheckCircle2 } from "lucide-react"
import { useNavigate } from "react-router-dom"

export default function Register() {
  const navigate = useNavigate()
  const [form, setForm] = useState({
    username: "",
    password: "",
    confirmPassword: "",
    name: "",
    phone: "",
    address: "",
  })

  const [error, setError] = useState(false)
  const [errorMsg, setErrorMsg] = useState("")
  const [success, setSuccess] = useState(false)
  const [loading, setLoading] = useState(false)

  // 統一處理成功跳轉：註冊成功後導向登入頁
  const handleSuccessRedirect = () => {
    setSuccess(false)
    navigate("/login")
  }

  useEffect(() => {
    const handleGlobalKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Enter") {
        if (success) {
          e.preventDefault()
          handleSuccessRedirect()
        } else if (error) {
          e.preventDefault()
          setError(false)
        }
      }
    }

    if (success || error) {
      window.addEventListener("keydown", handleGlobalKeyDown)
    }
    return () => window.removeEventListener("keydown", handleGlobalKeyDown)
  }, [success, error])

  const clean = (str: string) => str.replace(/[<>{}]/g, "")

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setError(false)
    setForm({ ...form, [e.target.name]: e.target.value })
  }
  
  const handleRegister = async () => {
    if (loading) return

    // 1. 必填驗證
    if (!form.username || !form.password || !form.confirmPassword) {
      setErrorMsg("帳號與密碼為必填項目")
      setError(true)
      return
    }

    // 2. 密碼一致性檢查 (新增)
    if (form.password !== form.confirmPassword) {
      setErrorMsg("兩次輸入的密碼不一致")
      setError(true)
      return
    }

    setLoading(true)

    try {
      const payload = {
        username: clean(form.username),
        password: clean(form.password),
        name: clean(form.name),
        phone: clean(form.phone),
        address: clean(form.address),
      }

      const res = await fetch("http://127.0.0.1:8000/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      })

      const data = await res.json()

      if (data.msg === "success") {
        setSuccess(true)
        return
      }

      setErrorMsg(data.msg === "exists" ? "帳號已存在" : "系統錯誤")
      setError(true)

    } catch {
      setErrorMsg("網路錯誤，請稍後再試")
      setError(true)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex items-center justify-center min-h-auto p-4">
      <Card className="w-full max-w-md shadow-xl border-none ring-1 ring-zinc-200 dark:ring-zinc-800">
        <CardHeader>
          <CardTitle className="text-2xl font-bold flex items-center gap-2">
            <UserPlus className="h-6 w-6 text-blue-500" />
            註冊新帳號
          </CardTitle>
        </CardHeader>
        <CardContent>
          <form
            onSubmit={(e) => {
              e.preventDefault()
              handleRegister()
            }}
            className="space-y-4"
          >
            <div className="space-y-2">
              <Input name="username" placeholder="* 帳號 (Username)" onChange={handleChange} />
              <div className="grid grid-cols-2 gap-2">
                <Input name="password" type="password" placeholder="* 密碼" onChange={handleChange} />
                <Input name="confirmPassword" type="password" placeholder="* 確認密碼" onChange={handleChange} />
              </div>
            </div>

            <hr className="opacity-50" />

            <div className="space-y-2">
              <Input name="name" placeholder="真實姓名" onChange={handleChange} />
              <Input name="phone" placeholder="電話號碼" onChange={handleChange} />
              <Input name="address" placeholder="聯絡地址" onChange={handleChange} />
            </div>

            <Button type="submit" className="w-full h-11 font-bold" disabled={loading}>
              {loading ? "處理中..." : "確認註冊"}
            </Button>
          </form>

          <Button
            variant="ghost"
            className="w-full mt-4 text-sm text-muted-foreground"
            onClick={() => navigate("/login")}
          >
            已有帳號？返回登入頁面
          </Button>
        </CardContent>
      </Card>

      {/* ❌ Error Modal */}
      {error && (
        <div className="fixed inset-0 flex items-center justify-center z-50 p-4">
          <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={() => setError(false)} />
          <div className="relative bg-white dark:bg-zinc-900 p-6 rounded-2xl w-full max-w-sm shadow-2xl border border-red-500 animate-in zoom-in duration-200">
            <div className="flex items-center gap-3 text-red-500 mb-4">
              <AlertCircleIcon className="h-6 w-6" />
              <h3 className="text-xl font-bold">註冊失敗</h3>
            </div>
            <p className="text-muted-foreground leading-relaxed">{errorMsg}</p>
            <Button 
              className="w-full mt-6 bg-red-500 hover:bg-red-600 font-bold"
              autoFocus 
              onClick={() => setError(false)}
            >
              返回修改
            </Button>
          </div>
        </div>
      )}

      {/* ✅ Success Modal */}
      {success && (
        <div className="fixed inset-0 flex items-center justify-center z-50 p-4">
          <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={handleSuccessRedirect} />
          <div className="relative bg-white dark:bg-zinc-900 p-8 rounded-2xl w-full max-w-sm shadow-2xl border border-green-500 text-center animate-in zoom-in duration-200">
            <div className="flex flex-col items-center">
              <div className="bg-green-500/10 p-3 rounded-full mb-4">
                <CheckCircle2 className="h-12 w-12 text-green-500" />
              </div>
              <h3 className="text-2xl font-bold text-green-500 mb-2">註冊成功！</h3>
              <p className="text-muted-foreground mb-6">您現在可以使用剛建立的帳號進行登入。</p>
            </div>
            <Button
              autoFocus 
              className="w-full h-11 bg-green-500 hover:bg-green-600 font-bold"
              onClick={handleSuccessRedirect}
            >
              前往登入 
            </Button>
          </div>
        </div>
      )}
    </div>  
  )
}