import { useState, useEffect, useMemo } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardHeader } from "@/components/ui/card"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog"
import { Badge } from "@/components/ui/badge"
import { UserPlus, Pencil, Trash2, Search, ArrowUpDown, AlertCircle, MapPin, Phone } from "lucide-react"
import { cn } from "@/lib/utils"

// 帳號資料介面 (Interface)
interface Account {
  id: number
  username: string
  name: string
  phone: string
  address: string
  role: string
}

export default function Settings() {
  const [accounts, setAccounts] = useState<Account[]>([])
  const [searchTerm, setSearchTerm] = useState("")
  const [isDialogOpen, setIsDialogOpen] = useState(false)
  const [isDeleteConfirmOpen, setIsDeleteConfirmOpen] = useState(false)
  const [editingAccount, setEditingAccount] = useState<Account | null>(null)
  const [targetId, setTargetId] = useState<number | null>(null)
  const [loading, setLoading] = useState(false)
  const [errorMsg, setErrorMsg] = useState<string | null>(null)
  
  const [sortConfig, setSortConfig] = useState<{ key: keyof Account; direction: "asc" | "desc" } | null>(null)

  const [form, setForm] = useState({
    username: "",
    password: "",
    name: "",
    phone: "",
    address: "",
    role: "user"
  })

  // 取得資料列表 (Fetch Data)
  const fetchAccounts = async () => {
    try {
      const res = await fetch("http://127.0.0.1:8000/users")
      const data = await res.json()
      setAccounts(data)
    } catch (err) {
      console.error("載入失敗:", err)
    }
  }

  useEffect(() => { fetchAccounts() }, [])

  // 排序與篩選邏輯 (Filter & Sort)
  const sortedAccounts = useMemo(() => {
    const sortableItems = [...accounts].filter(acc => 
      acc.username.toLowerCase().includes(searchTerm.toLowerCase()) || 
      (acc.name && acc.name.includes(searchTerm))
    )
    if (sortConfig !== null) {
      sortableItems.sort((a, b) => {
        const valA = a[sortConfig.key] ?? ""
        const valB = b[sortConfig.key] ?? ""
        if (valA < valB) return sortConfig.direction === "asc" ? -1 : 1
        if (valA > valB) return sortConfig.direction === "asc" ? 1 : -1
        return 0
      })
    }
    return sortableItems
  }, [accounts, searchTerm, sortConfig])

  const requestSort = (key: keyof Account) => {
    let direction: "asc" | "desc" = "asc"
    if (sortConfig && sortConfig.key === key && sortConfig.direction === "asc") {
      direction = "desc"
    }
    setSortConfig({ key, direction })
  }

  // 監聽 Enter 鍵提交 (Handle Enter Key)
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !loading) handleSubmit()
  }

  // 提交表單邏輯 (Submit Logic)
  const handleSubmit = async () => {
    setErrorMsg(null)

    // 1. 必填驗證：帳號 (Username)
    if (!form.username.trim()) {
      setErrorMsg("帳號 (Username) 為必填項目")
      return
    }

    // 2. 必填驗證：密碼 (Password)
    if (!editingAccount) {
      // 新增模式：密碼必填且需滿 6 字元
      if (!form.password) {
        setErrorMsg("建立新帳號時，密碼為必填")
        return
      }
      if (form.password.length < 6) {
        setErrorMsg("密碼長度需至少 6 個字元")
        return
      }
    } else {
      // 編輯模式：若有填寫密碼，則需檢查長度
      if (form.password && form.password.length < 6) {
        setErrorMsg("密碼長度需至少 6 個字元")
        return
      }
    }

    setLoading(true)
    try {
      const url = editingAccount 
        ? `http://127.0.0.1:8000/users/${editingAccount.id}` 
        : "http://127.0.0.1:8000/register"
      
      const res = await fetch(url, {
        method: editingAccount ? "PUT" : "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(form),
      })
      
      if (res.ok) {
        setIsDialogOpen(false)
        fetchAccounts()
      } else {
        setErrorMsg("儲存失敗，請檢查帳號是否重複")
      }
    } catch (err) {
      setErrorMsg("網路連線錯誤")
    } finally {
      setLoading(false)
    }
  }

  // 刪除邏輯 (Delete Logic)
  const confirmDelete = async () => {
    if (!targetId) return
    setLoading(true)
    try {
      await fetch(`http://127.0.0.1:8000/users/${targetId}`, { method: "DELETE" })
      setIsDeleteConfirmOpen(false)
      fetchAccounts()
    } finally {
      setLoading(false)
      setTargetId(null)
    }
  }

  return (
    <div className="h-[calc(100vh-140px)] flex flex-col space-y-4 animate-in fade-in duration-500">
      
      {/* 標題與新增按鈕 (Header) */}
      <div className="flex items-center justify-between px-1">
        <div>
          <p className="text-xl text-left font-bold tracking-tight">系統帳號管理</p>
          <p className="text-xs text-muted-foreground">維護帳號、密碼權限與通訊地址。</p>
        </div>
        <Button onClick={() => { 
          setEditingAccount(null)
          setErrorMsg(null)
          setForm({username:"", password:"", name:"", phone:"", address:"", role:"user"})
          setIsDialogOpen(true) 
        }} size="sm" className="bg-blue-600 hover:bg-blue-700">
          <UserPlus className="h-4 w-4 mr-1.5" /> 新增帳號
        </Button>
      </div>

      {/* 資料表格卡片 (Table Card) */}
      <Card className="flex-1 flex flex-col overflow-hidden border-zinc-200 dark:border-zinc-800 shadow-sm">
        <CardHeader className="py-3 border-b bg-zinc-50/30 dark:bg-zinc-900/30">
          <div className="relative max-w-sm">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input 
              placeholder="搜尋名稱或帳號..." 
              className="pl-9 h-9 bg-background"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
        </CardHeader>
        
        <CardContent className="p-0 flex-1 overflow-auto">
          <Table>
            <TableHeader className="sticky top-0 bg-white dark:bg-zinc-950 z-10 border-b">
              <TableRow>
                <TableHead className="w-[15%] cursor-pointer" onClick={() => requestSort("username")}>
                  帳號 <ArrowUpDown className="inline h-3 w-3 ml-1" />
                </TableHead>
                <TableHead className="w-[15%]">姓名</TableHead>
                <TableHead className="w-[10%] text-center">權限</TableHead>
                <TableHead className="w-[45%]">聯絡資訊與地址</TableHead>
                <TableHead className="w-[15%] text-right px-6">操作</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {sortedAccounts.map((acc) => (
                <TableRow key={acc.id} className="hover:bg-zinc-50/50 dark:hover:bg-zinc-900/50 transition-colors">
                  <TableCell className="font-medium py-4">{acc.username}</TableCell>
                  <TableCell>{acc.name || <span className="text-zinc-400 italic">未填寫</span>}</TableCell>
                  <TableCell className="text-center">
                    <Badge variant={acc.role === "admin" ? "default" : "outline"} className={cn("text-[10px] px-2 py-0", acc.role === "admin" ? "bg-blue-600" : "text-zinc-500 border-zinc-300")}>
                      {acc.role.toUpperCase()}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <div className="flex flex-col gap-1">
                      <div className="flex items-center gap-2 text-sm text-zinc-700 dark:text-zinc-300">
                        <Phone className="h-3 w-3 opacity-60 shrink-0" />
                        <span>{acc.phone || "---"}</span>
                      </div>
                      <div className="flex items-center gap-2 text-xs text-zinc-500">
                        <MapPin className="h-3 w-3 shrink-0 opacity-60" />
                        <span className="truncate max-w-[350px]">{acc.address || "未提供地址"}</span>
                      </div>
                    </div>
                  </TableCell>
                  <TableCell className="text-right px-6">
                    <div className="flex justify-end gap-2">
                      <Button variant="outline" size="icon" className="h-8 w-8" onClick={() => {
                        setEditingAccount(acc)
                        setErrorMsg(null)
                        setForm({...acc, password: ""})
                        setIsDialogOpen(true)
                      }}>
                        <Pencil className="h-3.5 w-3.5" />
                      </Button>
                      <Button variant="outline" size="icon" className="h-8 w-8 text-red-500 hover:bg-red-50" onClick={() => {
                        setTargetId(acc.id)
                        setIsDeleteConfirmOpen(true)
                      }}>
                        <Trash2 className="h-3.5 w-3.5" />
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {/* 新增/編輯彈窗 (Dialog) */}
      <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
        <DialogContent className="sm:max-w-[420px]" onKeyDown={handleKeyDown}>
          <DialogHeader>
            <DialogTitle className="text-lg font-bold text-black! dark:text-white! opacity-100">{editingAccount ? "編輯資訊" : "新增帳號"}</DialogTitle>
          </DialogHeader>

          {errorMsg && (
            <div className="flex items-center gap-2 p-2.5 rounded-md bg-red-50 text-red-600 text-xs border border-red-100 animate-in fade-in zoom-in-95">
              <AlertCircle className="h-4 w-4 shrink-0" />
              <span>{errorMsg}</span>
            </div>
          )}

          <div className="grid gap-3.5 py-2">
            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-1">
                <p className="text-[11px] font-bold text-muted-foreground uppercase flex justify-between">
                  * 帳號
                </p>
                <Input 
                  value={form.username} 
                  onChange={e => {setErrorMsg(null); setForm({...form, username: e.target.value})}} 
                  disabled={!!editingAccount} 
                  placeholder="登入帳號"
                />
              </div>
              <div className="space-y-1">
                <p className="text-[11px] font-bold text-muted-foreground uppercase">權限</p>
                <select className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm" value={form.role} onChange={e => setForm({...form, role: e.target.value})}>
                  <option value="user">User</option>
                  <option value="admin">Admin</option>
                </select>
              </div>
            </div>

            <div className="space-y-1">
              <div className="flex justify-between items-end">
                <p className="text-[11px] font-bold text-muted-foreground uppercase flex gap-1">
                  * 密碼 
                </p>
              </div>
              <Input 
                type="password" 
                placeholder={editingAccount ? "不修改請留空" : "請設定密碼"} 
                value={form.password}
                onChange={e => {setErrorMsg(null); setForm({...form, password: e.target.value})}} 
                className={cn(errorMsg?.includes("密碼") && "border-red-500")}
              />
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-1">
                <p className="text-[11px] font-bold text-muted-foreground uppercase">真實姓名 (選填)</p>
                <Input value={form.name} onChange={e => setForm({...form, name: e.target.value})} />
              </div>
              <div className="space-y-1">
                <p className="text-[11px] font-bold text-muted-foreground uppercase">電話</p>
                <Input value={form.phone} onChange={e => setForm({...form, phone: e.target.value})} />
              </div>
            </div>
            
            <div className="space-y-1">
              <p className="text-[11px] font-bold text-muted-foreground uppercase">通訊地址</p>
              <Input value={form.address} onChange={e => setForm({...form, address: e.target.value})} />
            </div>
          </div>

          <DialogFooter className="pt-2">
            <Button variant="ghost" onClick={() => setIsDialogOpen(false)}>取消</Button>
            <Button onClick={handleSubmit} disabled={loading} className="bg-blue-600">儲存資料</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* 刪除確認彈窗 (Delete Confirmation) */}
      <Dialog open={isDeleteConfirmOpen} onOpenChange={setIsDeleteConfirmOpen}>
        <DialogContent className="sm:max-w-[320px]">
          <DialogHeader className="flex flex-col items-center gap-2 pt-4">
            <div className="h-12 w-12 bg-red-100 rounded-full flex items-center justify-center text-red-600">
              <AlertCircle className="h-6 w-6" />
            </div>
            <DialogTitle className="text-base font-bold">確認刪除帳號？</DialogTitle>
          </DialogHeader>
          <p className="text-center text-xs text-muted-foreground px-2">這將永久移除使用者的系統權限。</p>
          <DialogFooter className="sm:justify-center gap-2 mt-4">
            <Button variant="ghost" className="flex-1" onClick={() => setIsDeleteConfirmOpen(false)}>取消</Button>
            <Button variant="destructive" className="flex-1 bg-red-600" onClick={confirmDelete} disabled={loading}>確定刪除</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

    </div>
  )
}