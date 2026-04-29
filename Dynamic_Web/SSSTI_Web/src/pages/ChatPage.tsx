import { useState, useRef, useEffect } from "react";
import { Send, Loader2, Paperclip, X, User, Bot, Activity } from "lucide-react";
import { ScrollArea } from "@/components/ui/scroll-area";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

interface Msg {
    role: "user" | "ai";
    content: string;
}

export default function ChatPage() {
    const [messages, setMessages] = useState<Msg[]>([]);
    const [input, setInput] = useState("");
    const [files, setFiles] = useState<File[]>([]);
    const [loading, setLoading] = useState(false);

    const [processMsg, setProcessMsg] = useState<string | null>(null);
    const [displayMsg, setDisplayMsg] = useState<string | null>(null);

    const buffer = useRef("");
    const scrollRef = useRef<HTMLDivElement | null>(null);
    const textareaRef = useRef<HTMLTextAreaElement>(null);
    const lastUpdate = useRef<number>(0);

    // 平滑顯示狀態邏輯
    useEffect(() => {
        if (!processMsg) {
            setDisplayMsg(null);
            return;
        }
        const now = Date.now();
        const minDisplayTime = 500;

        const update = () => {
            setDisplayMsg(processMsg);
            lastUpdate.current = Date.now();
        };

        if (now - lastUpdate.current > minDisplayTime) {
            update();
        } else {
            const delay = minDisplayTime - (now - lastUpdate.current);
            const timer = setTimeout(update, delay);
            return () => clearTimeout(timer);
        }
    }, [processMsg]);

    // 自動捲動邏輯
    useEffect(() => {
        if (scrollRef.current) {
            const viewport = scrollRef.current.querySelector('[data-radix-scroll-area-viewport]');
            if (viewport) {
                viewport.scrollTo({ top: viewport.scrollHeight, behavior: "smooth" });
            }
        }
    }, [messages, displayMsg]);

    const handleInput = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
        setInput(e.target.value);
        if (textareaRef.current) {
            textareaRef.current.style.height = "auto";
            textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 160)}px`;
        }
    };

    const send = async () => {
        if ((!input.trim() && files.length === 0) || loading) return;

        const text = input;
        const currentFiles = [...files];

        setInput("");
        setFiles([]);
        if (textareaRef.current) textareaRef.current.style.height = "auto";

        setLoading(true);
        setProcessMsg("連線中...");
        buffer.current = "";

        setMessages((prev) => [
            ...prev,
            { role: "user", content: text },
            { role: "ai", content: "" },
        ]);

        try {
            const form = new FormData();
            form.append("text", text);
            form.append("thread_id", "default");
            currentFiles.forEach((f) => form.append("files", f));

            const res = await fetch("http://127.0.0.1:8001/chat", {
                method: "POST",
                body: form,
            });

            if (!res.body) throw new Error("Stream error");

            const reader = res.body.getReader();
            const decoder = new TextDecoder();
            let rawData = "";

            while (true) {
                const { value, done } = await reader.read();
                if (done) break;

                rawData += decoder.decode(value, { stream: true });
                let parts = rawData.split(/(?=message:|data:)/g);

                if (parts.length > 0) {
                    const lastPart = parts[parts.length - 1];
                    try {
                        const cleanTest = lastPart.replace(/^(data:|message:)\s*/i, "").trim();
                        if (cleanTest !== "[DONE]") JSON.parse(cleanTest);
                        rawData = "";
                    } catch (e) {
                        rawData = parts.pop() || "";
                    }
                }

                for (const part of parts) {
                    const cleanJson = part.replace(/^(data:|message:)\s*/i, "").trim();
                    if (!cleanJson || cleanJson === "[DONE]") {
                        if (cleanJson === "[DONE]") {
                            setLoading(false);
                            setProcessMsg(null);
                        }
                        continue;
                    }

                    try {
                        const parsed = JSON.parse(cleanJson);
                        if (parsed.status) setProcessMsg(parsed.status);

                        const content = parsed.choices?.[0]?.delta?.content || "";
                        if (content) {
                            buffer.current += content;
                            setMessages((prev) => {
                                const updated = [...prev];
                                const lastIdx = updated.length - 1;
                                if (lastIdx >= 0 && updated[lastIdx].role === "ai") {
                                    updated[lastIdx] = { ...updated[lastIdx], content: buffer.current };
                                }
                                return updated;
                            });
                        }
                    } catch (e) { }
                }
            }
        } catch (err) {
            setProcessMsg("連線錯誤");
            setLoading(false);
        }
    };

    return (
        <div className="flex flex-col h-dvh w-full max-w-5xl mx-auto overflow-hidden bg-transparent">
            {/* 訊息顯示區域 */}
            <div className="flex-1 min-h-0 relative">
                <ScrollArea className="h-full w-full px-4" ref={scrollRef}>
                    <div className="flex flex-col gap-6 py-8">
                        {messages.length === 0 && (
                            <div className="flex flex-col items-center justify-center py-20 text-center animate-in fade-in duration-700">
                                <p className="text-2xl font-black text-zinc-300 dark:text-zinc-700 uppercase tracking-[0.2em]">Shrimp AI</p>
                                <p className="text-zinc-500 text-xs mt-2 font-medium italic tracking-wide">Intelligent Aquaculture Expert System</p>
                            </div>
                        )}

                        {messages.map((m, i) => (
                            <div
                                key={i}
                                className={`flex gap-3 w-full ${m.role === "user" ? "flex-row-reverse" : "flex-row"} animate-in fade-in slide-in-from-bottom-2 duration-300`}
                            >
                                {/* 頭像 */}
                                <div className={`w-9 h-9 rounded-xl flex items-center justify-center shrink-0 border shadow-sm ${m.role === "user"
                                    ? "bg-white dark:bg-zinc-800 border-zinc-200 dark:border-zinc-700"
                                    : "bg-blue-600 border-blue-500 text-white"
                                    }`}>
                                    {m.role === "user" ? <User size={16} className="text-zinc-500" /> : <Bot size={16} />}
                                </div>

                                {/* 訊息氣泡容器：加入 min-w-0 是為了解決表格撐破版面的核心 */}
                                <div className={`flex flex-col max-w-[85%] min-w-0 ${m.role === "user" ? "items-end" : "items-start"}`}>
                                    <div className={`w-full overflow-hidden relative px-4 py-2.5 rounded-2xl shadow-sm transition-colors ${m.role === "user"
                                        ? "bg-blue-600 text-white rounded-tr-none"
                                        : "bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 text-zinc-900 dark:text-zinc-100 rounded-tl-none"
                                        }`}>

                                        <article className={`
                                            max-w-none break-words text-left
                                            prose prose-sm md:prose-base
                                            ${m.role === "user" ? "prose-invert" : "dark:prose-invert"}
                                            
                                            /* 表格與代碼容器優化：確保內部可以捲動 */
                                            prose-table:w-full prose-table:overflow-x-auto
                                            prose-p:leading-relaxed
                                            prose-pre:bg-zinc-950 prose-pre:border prose-pre:border-zinc-800
                                            prose-code:text-blue-500 prose-code:before:content-[''] prose-code:after:content-['']
                                        `}>
                                            <ReactMarkdown remarkPlugins={[remarkGfm]}>
                                                {m.content}
                                            </ReactMarkdown>
                                        </article>

                                        {/* 生成中動畫 */}
                                        {loading && i === messages.length - 1 && !m.content && (
                                            <div className="flex gap-1.5 py-3 items-center">
                                                <div className="w-1.5 h-1.5 bg-blue-400 rounded-full animate-bounce [animation-delay:-0.3s]" />
                                                <div className="w-1.5 h-1.5 bg-blue-400 rounded-full animate-bounce [animation-delay:-0.15s]" />
                                                <div className="w-1.5 h-1.5 bg-blue-400 rounded-full animate-bounce" />
                                            </div>
                                        )}
                                    </div>
                                </div>
                            </div>
                        ))}

                        {/* 平滑化的 Agent 狀態顯示 */}
                        {displayMsg && (
                            <div className="flex items-center gap-3 px-12 animate-in fade-in slide-in-from-left-2 duration-500">
                                <div className="flex items-center bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-full px-4 py-1.5 gap-2.5 shadow-sm max-w-[95%]">
                                    <Activity size={12} className="text-blue-500 shrink-0" />
                                    <p className="text-[11px] font-mono font-medium text-zinc-500 dark:text-zinc-400 truncate">
                                        {displayMsg}
                                    </p>
                                    <Loader2 size={10} className="animate-spin text-zinc-300 shrink-0" />
                                </div>
                            </div>
                        )}
                    </div>
                </ScrollArea>
            </div>

            {/* 下方固定輸入區 */}
            <div className="shrink-0 p-4 pt-2 border-t border-zinc-100 dark:border-zinc-800 bg-white/80 dark:bg-zinc-950/80 backdrop-blur-md">
                <div className="max-w-4xl mx-auto relative bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-2xl shadow-xl transition-shadow focus-within:shadow-blue-500/5">

                    {files.length > 0 && (
                        <div className="flex flex-wrap gap-2 p-3 border-b border-zinc-50 dark:border-zinc-800">
                            {files.map((file, idx) => (
                                <div key={idx} className="flex items-center gap-1.5 bg-zinc-100 dark:bg-zinc-800 px-2.5 py-1 rounded-lg text-[11px] border border-zinc-200 dark:border-zinc-700 shadow-sm transition-all hover:bg-zinc-200">
                                    <span className="truncate max-w-[150px] font-medium">{file.name}</span>
                                    <X size={14} className="cursor-pointer hover:text-red-500 transition-colors" onClick={() => setFiles(prev => prev.filter((_, i) => i !== idx))} />
                                </div>
                            ))}
                        </div>
                    )}

                    <div className="flex items-end gap-1 p-2">
                        <label className="p-3 text-zinc-400 hover:text-blue-500 cursor-pointer transition-colors shrink-0">
                            <Paperclip size={20} />
                            <input type="file" multiple className="hidden" onChange={(e) => e.target.files && setFiles(prev => [...prev, ...Array.from(e.target.files!)])} />
                        </label>

                        <textarea
                            ref={textareaRef}
                            rows={1}
                            value={input}
                            onChange={handleInput}
                            onKeyDown={(e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); send(); } }}
                            placeholder="Message Shrimp AI..."
                            className="flex-1 bg-transparent border-none focus:ring-0 resize-none py-3 text-[15px] max-h-40 min-h-[44px] placeholder-zinc-400"
                        />

                        <button
                            onClick={send}
                            disabled={loading || (!input.trim() && files.length === 0)}
                            className="p-2.5 bg-blue-600 text-white rounded-xl hover:bg-blue-700 disabled:bg-zinc-100 dark:disabled:bg-zinc-800 disabled:text-zinc-400 transition-all shrink-0 m-1"
                        >
                            {loading ? <Loader2 size={18} className="animate-spin" /> : <Send size={18} />}
                        </button>
                    </div>
                </div>
                <p className="text-[10px] text-center text-zinc-400 py-2 uppercase tracking-[0.2em] opacity-50 font-bold">
                    Terminal System v2.0
                </p>
            </div>
        </div>
    );
}