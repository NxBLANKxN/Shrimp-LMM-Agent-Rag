import { useState } from "react"
import Header from "@/layouts/Header"
import Sidebar from "@/layouts/Sidebar"
import Footer from "@/layouts/Footer"

export default function MainLayout({ children }: { children: React.ReactNode }) {
  const [open, setOpen] = useState(false)

  return (
    <div className="h-screen flex flex-col overflow-hidden">

      <Header onMenuClick={() => setOpen(true)} />

      <div className="flex flex-1 relative min-h-0">


        {open && (
          <div
            className="fixed inset-0 bg-black/40 z-40"
            onClick={() => setOpen(false)}
          />
        )}


        <Sidebar open={open} onClose={() => setOpen(false)} />


        <main className="flex-1 bg-background flex flex-col min-h-0 overflow-hidden">
          {children}
        </main>

      </div>

      <Footer />
    </div>
  )
}