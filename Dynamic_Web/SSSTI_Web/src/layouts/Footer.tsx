export default function Footer() {
  return (
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
  )
}