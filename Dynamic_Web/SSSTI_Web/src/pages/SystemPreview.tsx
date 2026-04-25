import { useState, useEffect } from "react"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { 
  ScanSearch, 
  Info,
  ExternalLink
} from "lucide-react"

export default function SystemPreview() {
  // 將你的 YouTube 網址中的 watch?v=ID 改成 embed/ID
  // 例如: https://www.youtube.com/watch?v=dQw4w9WgXcQ 
  // 變成: https://www.youtube.com/embed/dQw4w9WgXcQ
  const videoId = "qc-uJ37FXqs"; // 👈 請替換這裡，例如 "dQw4w9WgXcQ"
  const embedUrl = `https://www.youtube.com/embed/${videoId}?autoplay=0&rel=0`;

  return (
    <div className="container mx-auto py-8 space-y-6">
      {/* 頂部標題 */}
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 border-b pb-6">
        <div>
          <p className="text-3xl font-black tracking-tighter text-zinc-900 dark:text-zinc-50 flex items-center gap-3">
            <ScanSearch className="w-8 h-8 text-blue-600" />
            YOLOv8 <span className="text-blue-600">Shrimp Analytics</span>
          </p>
          <p className="text-muted-foreground mt-1">智慧養殖監測系統展示 — 核心算法演示</p>
        </div>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-4 gap-6">
        {/* --- 左側：主影片展示區 (使用 iframe) --- */}
        <Card className="xl:col-span-3 overflow-hidden border-2 border-zinc-200 dark:border-zinc-800 shadow-xl bg-black">
          <div className="relative aspect-video bg-zinc-900">
            <iframe
              className="absolute inset-0 w-full h-full"
              src={embedUrl}
              title="YouTube video player"
              frameBorder="0"
              allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
              allowFullScreen
            ></iframe>
          </div>
        </Card>

        {/* --- 右側：專案說明欄 --- */}
        <div className="space-y-4">
          <Card className="bg-zinc-50 dark:bg-zinc-900 border-none shadow-sm">
            <CardHeader className="p-4 border-b">
              <CardTitle className="text-sm flex items-center gap-2">
                <Info className="w-4 h-4 text-blue-600" /> 辨識功能說明
              </CardTitle>
            </CardHeader>
            <CardContent className="p-4">
              <ul className="space-y-4 text-sm text-zinc-600 dark:text-zinc-400">
                <li className="flex gap-3">
                  <div className="mt-1 w-1.5 h-1.5 rounded-full bg-blue-500 shrink-0" />
                  <p className="text-left">
                    <strong className="text-zinc-900 dark:text-zinc-100">即時蝦隻計數：</strong>
                    展示 YOLOv8 模型在動態水面下的偵測實力，能高效識別並統計活體蝦隻總數。
                  </p>
                </li>

                <li className="flex gap-3">
                  <div className="mt-1 w-1.5 h-1.5 rounded-full bg-blue-500 shrink-0" />
                  <p className="text-left">
                    <strong className="text-zinc-900 dark:text-zinc-100">視覺化邊界框 (Bounding Box)：</strong>
                    影片中的<span className="text-yellow-600 font-bold">黃色方框</span>為模型推理生成的目標區域，同步顯示辨識標籤及其信心水準。
                  </p>
                </li>

                <li className="flex gap-3">
                  <div className="mt-1 w-1.5 h-1.5 rounded-full bg-blue-500 shrink-0" />
                  <p className="text-left">
                    <strong className="text-zinc-900 dark:text-zinc-100">軌跡追蹤技術：</strong>
                    影片中的<span className="text-yellow-600 font-bold">黃色圓心</span>為系統運算得出的質心點，用於精準追蹤蝦隻的移動路徑與分佈趨勢。
                  </p>
                </li>

                <li className="flex gap-3 ">
                  <div className="mt-1 w-1.5 h-1.5 rounded-full bg-blue-500 shrink-0" />
                  <p className="text-left">
                    <strong className="text-zinc-900 dark:text-zinc-100">唯一 ID 標註：</strong>
                    系統為每個偵測目標分配獨立編號，實現長效跟蹤並有效避免重複計數。
                  </p>
                </li>
              </ul>
            </CardContent>
          </Card>

          <a 
            href={`https://www.youtube.com/watch?v=${videoId}`} 
            target="_blank" 
            rel="noreferrer"
            className="flex items-center justify-center gap-2 text-xs text-zinc-500 hover:text-blue-600 transition-colors py-2 border border-dashed rounded-lg"
          >
            <ExternalLink className="w-3 h-3" /> 在 YouTube 上查看原始影片
          </a>
        </div>
      </div>
    </div>
  )
}