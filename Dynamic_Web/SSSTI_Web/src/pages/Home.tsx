import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { 
  ArrowRight, 
  LayoutDashboard, 
  ScanSearch, 
  Waves, 
  LineChart, 
  ShieldCheck,
  Users
} from "lucide-react"

export default function Home() {
  return (
    <div className="space-y-16 pb-20">
      
      {/* 英雄區塊 (Hero Section) */}
      <section className="flex flex-col items-center justify-center pt-12 text-center space-y-6">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/10 text-blue-500 text-xs font-bold">
          <Waves className="h-3 w-3" />
          <span>AI 智慧養殖技術革新</span>
        </div>
        
        <p className="text-4xl md:text-6xl font-extrabold tracking-tight max-w-3xl">
          智慧 <span className="text-blue-500">蝦隻辨識</span> 系統
        </p>
        
        <p className="text-lg text-muted-foreground max-w-xl">
          利用深度學習技術即時分析蝦隻健康狀態、體長與分布， <br />
          讓養殖管理從「經驗判斷」轉化為「數據驅動」。
        </p>

        <div className="flex flex-col sm:flex-row gap-4 pt-4">
          <Button 
            size="lg" 
            className="h-14 px-8 text-lg font-bold gap-2"
            onClick={() => (window.location.href = "/systempreview")}
          >
            <LayoutDashboard className="h-5 w-5" />
            進入管特色預覽
          </Button>
          <Button 
            size="lg" 
            variant="outline" 
            className="h-14 px-8 text-lg font-bold"
            onClick={() => (window.location.href = "/members  ")}
          >
            <Users className="h-5 w-5" />
            查看成員展示
          </Button>
        </div>
      </section>

      {/* 核心技術展示區塊 (Feature Grid) */}
      <section className="grid grid-cols-1 md:grid-cols-3 gap-8 px-4 max-w-6xl mx-auto">
        <Card className="border-none shadow-md bg-zinc-50/50 dark:bg-zinc-900/50 justify-center">
          <CardContent className="text-left">
            <div className="p-3 bg-blue-500/10 rounded-2xl w-fit mb-4">
              <ScanSearch className="h-6 w-6 text-blue-500" />
            </div>
            <h3 className="text-xl font-bold mb-2">精準影像辨識</h3>
            <p className="text-muted-foreground text-sm leading-relaxed">
              透過高畫質水下鏡頭與 AI 模型，自動偵測蝦隻個體，辨識準確率高達 95% 以上。
            </p>
          </CardContent>
        </Card>

        <Card className="border-none shadow-md bg-zinc-50/50 dark:bg-zinc-900/50 justify-center">
          <CardContent className="text-left">
            <div className="p-3 bg-indigo-500/10 rounded-2xl w-fit mb-4">
              <LineChart className="h-6 w-6 text-indigo-500" />
            </div>
            <h3 className="text-xl font-bold mb-2">生長曲線追蹤</h3>
            <p className="text-muted-foreground text-sm leading-relaxed">
              紀錄每日平均體長與增重數據，視覺化呈現生長動態，精確掌握收成時機。
            </p>
          </CardContent>
        </Card>

        <Card className="border-none shadow-md bg-zinc-50/50 dark:bg-zinc-900/50 justify-center">
          <CardContent className=" text-left">
            <div className="p-3 bg-green-500/10 rounded-2xl w-fit mb-4">
              <ShieldCheck className="h-6 w-6 text-green-500" />
            </div>
            <h3 className="text-xl font-bold mb-2">異常預警系統</h3>
            <p className="text-muted-foreground text-sm leading-relaxed">
              監控異常游動或群聚行為，第一時間發送警報至行動裝置，降低養殖風險。
            </p>
          </CardContent>
        </Card>
      </section>

      {/* 關於我們 / 技術區塊 */}
      <section className="max-w-5xl mx-auto px-6 py-12 bg-zinc-50 dark:bg-zinc-900 rounded-3xl flex flex-col md:flex-row items-center gap-12 border border-none shadow-xl relative overflow-hidden">
        {/* 背景裝飾水紋 */}
        <Waves className="absolute -bottom-10 -left-10 h-40 w-40 text-blue-500/5 -rotate-12 pointer-events-none" />
        
        <div className="flex-1 space-y-4 text-left z-10">
          <p className="text-3xl font-bold">為什麼選擇我們的技術？</p>
          <p className="text-muted-foreground leading-loose">
            我們的「智慧蝦隻辨識系統」不僅是資料的收集，更是深度的場域洞察。我們結合了水質監測與電腦視覺，為養殖戶提供一站式的管理方案。
          </p>
          <ul className="space-y-3 pt-2">
            {[
              "支援多種蝦種辨識（如白蝦、泰國蝦）",
              "高精確度 AI 模型，適應複雜水質環境",
              "結合低成本攝影設備，即時的數據處理與傳輸 "
            ].map((text, i) => (
              <li key={i} className="flex items-center gap-3 text-sm font-medium">
                <div className="h-2 w-2 rounded-full bg-blue-500" />
                {text}
              </li>
            ))}
          </ul>
        </div>
        
        {/* 圖片展示區塊 */}
        <div className="flex-1 w-full h-80 bg-background rounded-2xl flex items-center justify-center border p-2 shadow-inner group overflow-hidden">
          <img 
            src="/shrimp.png" 
            alt="智慧蝦隻辨識系統示意圖"
            className="w-full h-full object-cover rounded-xl transition-transform duration-500 group-hover:scale-105" 
          />
        </div>
      </section>
    </div>
  )
}