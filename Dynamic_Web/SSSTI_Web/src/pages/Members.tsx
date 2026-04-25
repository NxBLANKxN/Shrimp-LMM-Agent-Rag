import { useState, useEffect } from "react"
import { Card, CardHeader, CardTitle } from "@/components/ui/card"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog"
import { UserPlus, Camera, AlignLeft, Loader2, Pencil, Trash2, AlertCircle } from "lucide-react"

type Member = {
  id: number; name: string; role: string; image_url: string; bio?: string
}

export default function Members() {
  const [members, setMembers] = useState<Member[]>([])
  const [userRole, setUserRole] = useState<string | null>(null)
  
  const [isDialogOpen, setIsDialogOpen] = useState(false)
  const [isDeleteConfirmOpen, setIsDeleteConfirmOpen] = useState(false)
  const [editingMember, setEditingMember] = useState<Member | null>(null)
  const [targetId, setTargetId] = useState<number | null>(null)
  
  const [loading, setLoading] = useState(false)
  const [form, setForm] = useState({ name: "", role: "", bio: "" })
  const [file, setFile] = useState<File | null>(null)
  const [preview, setPreview] = useState<string | null>(null)

  useEffect(() => {
    const savedRole = localStorage.getItem("role")
    setUserRole(savedRole)
    fetchMembers()
  }, [])

  const fetchMembers = () => {
    fetch("http://127.0.0.1:8000/members")
      .then(res => res.json())
      .then(data => setMembers(data))
      .catch(err => console.error("API Error:", err))
  }

  // 開啟編輯視窗
  const handleEditClick = (member: Member) => {
    setEditingMember(member)
    setForm({ name: member.name, role: member.role, bio: member.bio || "" })
    setPreview(member.image_url)
    setIsDialogOpen(true)
  }

  // 提交 (新增或修改)
  const handleSubmit = async () => {
    if (!form.name || !form.role) return
    setLoading(true)
    
    const formData = new FormData()
    formData.append("name", form.name)
    formData.append("role", form.role)
    formData.append("bio", form.bio)
    if (file) formData.append("file", file)

    try {
      const url = editingMember 
        ? `http://127.0.0.1:8000/members/${editingMember.id}` 
        : "http://127.0.0.1:8000/members"
      
      const method = editingMember ? "PUT" : "POST"

      const res = await fetch(url, { method, body: formData })
      if (res.ok) {
        setIsDialogOpen(false)
        resetForm()
        fetchMembers()
      }
    } finally { setLoading(false) }
  }

  // 刪除邏輯
  const handleDelete = async () => {
    if (!targetId) return
    setLoading(true)
    try {
      const res = await fetch(`http://127.0.0.1:8000/members/${targetId}`, { method: "DELETE" })
      if (res.ok) {
        setIsDeleteConfirmOpen(false)
        fetchMembers()
      }
    } finally { 
      setLoading(false)
      setTargetId(null)
    }
  }

  const resetForm = () => {
    setEditingMember(null)
    setForm({ name: "", role: "", bio: "" })
    setFile(null)
    setPreview(null)
  }

  return (
    <div className="p-6 max-w-4xl mx-auto animate-in fade-in duration-500">
      
      <div className="relative mb-12 flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-3xl font-bold tracking-tight">團隊成員</h2>
          <p className="text-muted-foreground mt-2">系統開發與資料庫維護人員</p>
        </div>

        {userRole === "admin" && (
          <div className="absolute right-0 bottom-1">
            <Button onClick={() => { resetForm(); setIsDialogOpen(true); }} className="bg-indigo-600 hover:bg-indigo-700 shadow-sm" size="sm">
              <UserPlus className="h-4 w-4 mr-2" /> 新增成員
            </Button>
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
        {members.map((m) => (
          <Card key={m.id} className="relative overflow-hidden hover:border-indigo-400/50 transition-all hover:shadow-md group">
            <CardHeader className="flex flex-row items-center gap-5 p-4 text-left ">
              <Avatar className="w-32 h-32 border-2 border-background shadow-sm">
                <AvatarImage src={m.image_url} alt={m.name} className="object-cover" />
                <AvatarFallback className="bg-indigo-100 text-indigo-700 font-bold">{m.name.slice(-2)}</AvatarFallback>
              </Avatar>
              <div className="flex flex-col flex-1">
                <CardTitle className="text-2xl">{m.name}</CardTitle>
                <p className="text-lg text-indigo-600 font-bold uppercase tracking-widest mt-0.5">{m.role}</p>
                {m.bio && <p className="text-lg text-muted-foreground whitespace-pre-line mt-1.5">{m.bio}</p>}
              </div>

              {/* 管理員功能按鈕 */}
              {userRole === "admin" && (
                <div className="absolute top-2 right-2 flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                  <Button variant="ghost" size="icon" className="h-7 w-7 text-zinc-500 hover:text-indigo-600" onClick={() => handleEditClick(m)}>
                    <Pencil className="h-3.5 w-3.5" />
                  </Button>
                  <Button variant="ghost" size="icon" className="h-7 w-7 text-zinc-500 hover:text-red-600" onClick={() => { setTargetId(m.id); setIsDeleteConfirmOpen(true); }}>
                    <Trash2 className="h-3.5 w-3.5" />
                  </Button>
                </div>
              )}
            </CardHeader>
          </Card>
        ))}
      </div>

      {/* 新增/修改彈窗 */}
      <Dialog open={isDialogOpen} onOpenChange={(open) => { if(!open) resetForm(); setIsDialogOpen(open); }}>
        <DialogContent className="sm:max-w-[400px]">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              {editingMember ? <Pencil className="h-5 w-5 text-indigo-600" /> : <UserPlus className="h-5 w-5 text-indigo-600" />}
              {editingMember ? "編輯成員資訊" : "配置新成員"}
            </DialogTitle>
          </DialogHeader>
          <div className="flex flex-col items-center gap-5 py-4 text-left">
            <div className="relative group cursor-pointer">
              <div className="h-24 w-24 rounded-full border-2 border-dashed border-zinc-200 flex items-center justify-center overflow-hidden bg-zinc-50">
                {preview ? <img src={preview} className="h-full w-full object-cover" /> : <Camera className="h-8 w-8 text-zinc-300" />}
              </div>
              <input type="file" accept="image/*" className="absolute inset-0 opacity-0 cursor-pointer" onChange={(e) => {
                const f = e.target.files?.[0]; if (f) { setFile(f); setPreview(URL.createObjectURL(f)); }
              }} />
            </div>
            <div className="w-full space-y-3">
              <div className="space-y-1"><p className="text-[12px] font-bold text-muted-foreground uppercase">成員姓名</p><Input value={form.name} onChange={e=>setForm({...form, name:e.target.value})} /></div>
              <div className="space-y-1"><p className="text-[12px] font-bold text-muted-foreground uppercase">職位</p><Input value={form.role} onChange={e=>setForm({...form, role:e.target.value})} /></div>
              <div className="space-y-1">
                <p className="text-[11px] font-bold text-muted-foreground uppercase flex items-center gap-1"><AlignLeft className="h-3 w-3" /> 個人簡介</p>
                <Textarea className="h-20 resize-none" value={form.bio} onChange={e=>setForm({...form, bio:e.target.value})} />
              </div>
            </div>
          </div>
          <DialogFooter>
            <Button variant="ghost" onClick={() => setIsDialogOpen(false)}>取消</Button>
            <Button onClick={handleSubmit} disabled={loading} className="bg-indigo-600">
              {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              {editingMember ? "儲存修改" : "確認新增"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* 刪除確認彈窗 */}
      <Dialog open={isDeleteConfirmOpen} onOpenChange={setIsDeleteConfirmOpen}>
        <DialogContent className="sm:max-w-[320px]">
          <DialogHeader className="flex flex-col items-center gap-2">
            <div className="h-10 w-10 bg-red-100 rounded-full flex items-center justify-center text-red-600">
              <AlertCircle className="h-6 w-6" />
            </div>
            <DialogTitle>確認刪除？</DialogTitle>
          </DialogHeader>
          <p className="text-center text-sm text-muted-foreground">此操作無法撤銷，成員資料將永久移除。</p>
          <DialogFooter className="sm:justify-center gap-2">
            <Button variant="ghost" onClick={() => setIsDeleteConfirmOpen(false)} className="flex-1">取消</Button>
            <Button variant="destructive" onClick={handleDelete} disabled={loading} className="flex-1 bg-red-600 hover:bg-red-700">
              {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : "確定刪除"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}