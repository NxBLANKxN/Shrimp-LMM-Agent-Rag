import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import type { ApiSpec } from "@/data/api-docs"

export function ApiCard({ api }: { api: ApiSpec }) {
  return (
    <Card className="overflow-hidden border-none shadow-md ring-1 ring-zinc-200 dark:ring-zinc-800 transition-all hover:ring-blue-400">
      {/* API Header */}
      <div className="bg-zinc-50 dark:bg-zinc-900 px-4 py-3 flex flex-wrap items-center gap-3 border-b">
        <Badge className={`${api.method === 'POST' ? 'bg-blue-600' : 'bg-green-600'} font-mono px-3 py-1`}>
          {api.method}
        </Badge>
        <div className="flex items-center font-mono text-sm font-bold">
          <span className="text-blue-500">http://127.0.0.1:8000</span>
          <span className="text-blue-500">{api.endpoint}</span>
        </div>
      </div>

      {/* API Body */}
      <CardContent className="p-0">
        <div className="grid grid-cols-1 lg:grid-cols-2">
          {/* 左側描述 */}
          <div className="p-6 border-b lg:border-b-0 lg:border-r space-y-4 text-left">
            <div>
              <h3 className="text-base font-bold mb-1">{api.title}</h3>
              <p className="text-sm text-muted-foreground leading-relaxed">{api.desc}</p>
            </div>
            <div className="space-y-2">
              <p className="text-xs font-bold uppercase text-zinc-400">Response Format</p>
              <div className="bg-muted p-3 rounded text-xs font-mono">
                {JSON.stringify(api.response)}
              </div>
            </div>
          </div>

            {/* 右側範例 */}
            <div className="p-0 bg-zinc-950 flex flex-col items-start justify-start"> 
							<div className="w-full px-4 py-2 border-b border-zinc-800 text-[10px] text-zinc-500 font-bold uppercase text-left">
									Request Payload (JSON)
							</div>
							<pre className="w-full p-6 text-sm text-zinc-300 font-mono overflow-x-auto text-left whitespace-pre">
									{JSON.stringify(api.requestBody, null, 2)}
							</pre>
            </div>
        </div>
      </CardContent>
    </Card>
  )
}