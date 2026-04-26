import React, { useState, useRef, useEffect } from "react";
import { Send, Loader2, Paperclip, X, Cpu } from "lucide-react";
import { ScrollArea } from "@/components/ui/scroll-area";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

interface Message {
    role: "user" | "ai";
    content: string;
}

export default function ChatPage() {
    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState("");
    const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
    const [isLoading, setIsLoading] = useState(false);

    const scrollRef = useRef<HTMLDivElement>(null);
    const fileInputRef = useRef<HTMLInputElement>(null);

    // ----------------------------------------------------------------------
    // 自動換行與空行處理器 (Markdown Formatter)
    // ----------------------------------------------------------------------
    const formatMarkdown = (text: string) => {
        if (!text) return "";

        return text
            // 1. 處理系統訊息，確保它獨立一塊，並與前後文有足夠空隙
            .replace(/(> ⚙️)/g, '\n\n$1')

            // 2. 針對檔案清單的間距優化：如果行末是 (影片) 或 (圖片)，強制補換行
            .replace(/(\(影片\)|\(圖片\))\s*/g, '$1\n')

            // 3. 處理路徑字串後的擠壓問題，確保括號路徑後有換行
            .replace(/(\/opt\/[^\s\)]+)\)/g, '$1)\n')

            // 4. 確保 Markdown 標題前有空行
            .replace(/^(#+)\s/gm, '\n\n$1 ')

            // 5. 防止過度堆疊換行（最多保留兩個）
            .replace(/\n{3,}/g, '\n\n')
            .trimStart();
    };
    useEffect(() => {
        const scrollContainer = scrollRef.current?.querySelector('[data-radix-scroll-area-viewport]');
        if (scrollContainer) {
            scrollContainer.scrollTo({
                top: scrollContainer.scrollHeight,
                behavior: "smooth"
            });
        }
    }, [messages, isLoading]);

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files) {
            setSelectedFiles((prev) => [...prev, ...Array.from(e.target.files!)]);
        }
    };

    const removeFile = (index: number) => {
        setSelectedFiles((prev) => prev.filter((_, i) => i !== index));
    };

    const handleSend = async () => {
        if (!input.trim() && selectedFiles.length === 0) return;

        const currentInput = input;
        const currentFiles = [...selectedFiles];

        setMessages((prev) => [...prev, { role: "user", content: currentInput }, { role: "ai", content: "" }]);
        setInput("");
        setSelectedFiles([]);
        setIsLoading(true);

        const formData = new FormData();
        formData.append("text", currentInput);
        formData.append("thread_id", "shrimp_session_research");
        currentFiles.forEach((file) => formData.append("files", file));

        try {
            const response = await fetch("http://127.0.0.1:8001/chat", { method: "POST", body: formData });
            if (!response.body) return;
            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let aiContent = "";

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;
                const chunk = decoder.decode(value, { stream: true });
                const lines = chunk.split("\n");
                for (const line of lines) {
                    if (line.startsWith("data: ") && line !== "data: [DONE]") {
                        try {
                            const data = JSON.parse(line.replace("data: ", ""));
                            const delta = data.choices[0].delta.content;
                            if (delta) {
                                aiContent += delta;
                                setMessages((prev) => {
                                    const updated = [...prev];
                                    if (updated.length > 0) {
                                        // 這裡應用格式化邏輯
                                        updated[updated.length - 1].content = formatMarkdown(aiContent);
                                    }
                                    return updated;
                                });
                            }
                        } catch (e) { }
                    }
                }
            }
        } catch (error) {
            console.error("Agent Error:", error);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="w-full h-screen flex flex-col bg-zinc-950 text-zinc-100 font-sans antialiased overflow-hidden relative">

            {/* 背景裝飾 */}
            <div className="absolute top-[-5%] left-[-10%] w-[600px] h-[600px] bg-blue-600/5 rounded-full blur-[140px] pointer-events-none" />
            <div className="absolute bottom-[-5%] right-[-10%] w-[600px] h-[600px] bg-indigo-600/5 rounded-full blur-[140px] pointer-events-none" />

            {/* Header */}
            <header className="w-full px-8 py-5 border-b border-white/[0.06] flex justify-between items-center bg-zinc-950/40 backdrop-blur-md flex-shrink-0 z-20">
                <div className="flex items-center gap-3 text-left">
                    <div className="p-2.5 bg-white/[0.03] rounded-2xl border border-white/[0.08]">
                        <Cpu size={20} className="text-blue-400" />
                    </div>
                    <div>
                        <p className="text-[12px] font-bold tracking-[0.3em] uppercase text-zinc-200">Shrimp_Agent</p>
                        <p className="text-[10px] text-zinc-600 font-mono tracking-widest">ANALYSIS_NODE_0354</p>
                    </div>
                </div>
                <div className="px-3 py-1.5 bg-blue-500/5 border border-blue-500/20 rounded-full">
                    <p className="text-[10px] text-blue-400 font-bold uppercase tracking-widest animate-pulse">Live</p>
                </div>
            </header>

            {/* 訊息流區域 */}
            <div className="flex-1 w-full min-h-0 flex flex-col items-center overflow-hidden">
                <ScrollArea className="w-full h-full min-h-0" ref={scrollRef}>
                    <div className="max-w-3xl mx-auto px-6 py-12 space-y-14">

                        {messages.length === 0 && (
                            <div className="py-40 text-center opacity-20">
                                <p className="text-sm tracking-[0.8em] uppercase font-light">Waiting_for_Sequence</p>
                            </div>
                        )}

                        {messages.map((msg, index) => (
                            <div
                                key={index}
                                className={`flex w-full ${msg.role === "user" ? "justify-end" : "justify-start"} animate-in fade-in duration-500`}
                            >
                                <div className={`min-w-[240px] ${msg.role === "user" ? "max-w-[70%]" : "max-w-[90%]"}`}>
                                    <p className={`text-[10px] font-bold tracking-[0.25em] uppercase mb-3 text-left ${msg.role === "user" ? "text-zinc-500" : "text-blue-500/70"
                                        }`}>
                                        {msg.role === "user" ? "Researcher" : "Agent_Analysis"}
                                    </p>

                                    <div className={`p-6 rounded-[24px] border transition-all duration-500 text-left ${msg.role === "user"
                                            ? "bg-white/[0.03] border-white/[0.12] text-zinc-100 rounded-tr-none shadow-md"
                                            : "bg-blue-600/[0.04] border-blue-400/[0.2] text-blue-50 rounded-tl-none shadow-md"
                                        }`}>
                                        <article className="prose prose-invert prose-zinc max-w-none text-left
                      prose-p:leading-relaxed 
                      prose-h1:text-2xl prose-h1:font-bold prose-h1:mb-6
                      prose-h2:text-xl prose-h2:font-semibold prose-h2:mb-4
                      prose-li:my-1
                      prose-pre:bg-black/50 prose-pre:rounded-xl">
                                            <ReactMarkdown remarkPlugins={[remarkGfm]}>
                                                {msg.content || (isLoading && msg.role === 'ai' ? '...' : '')}
                                            </ReactMarkdown>
                                            {msg.role === "ai" && isLoading && !msg.content && (
                                                <Loader2 size={14} className="animate-spin text-blue-400 opacity-40 mt-2" />
                                            )}
                                        </article>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </ScrollArea>
            </div>

            {/* 底部輸入區域 */}
            <footer className="w-full px-8 pb-8 pt-4 flex-shrink-0 z-20">

                {selectedFiles.length > 0 && (
                    <div className="max-w-5xl mx-auto flex flex-wrap gap-2 mb-4 px-3 text-left">
                        {selectedFiles.map((file, i) => (
                            <div key={i} className="flex items-center gap-2 px-3 py-2 bg-white/[0.04] border border-white/[0.1] rounded-full text-[11px] text-zinc-400">
                                <span className="truncate max-w-[140px]">{file.name}</span>
                                <X size={14} className="cursor-pointer hover:text-red-400 transition-colors" onClick={() => removeFile(i)} />
                            </div>
                        ))}
                    </div>
                )}

                <div className="max-w-5xl mx-auto bg-white/[0.02] border border-white/[0.08] rounded-[32px] p-2.5 transition-all duration-500 focus-within:border-white/[0.15] focus-within:bg-white/[0.04] focus-within:shadow-[0_8px_40px_-12px_rgba(0,0,0,0.5)]">
                    <div className="flex items-end gap-3">
                        <button
                            onClick={() => fileInputRef.current?.click()}
                            className="p-3.5 text-zinc-600 hover:text-zinc-200 transition-colors mb-0.5 rounded-full hover:bg-white/[0.04]"
                        >
                            <Paperclip size={22} strokeWidth={1.5} />
                            <input type="file" multiple hidden ref={fileInputRef} onChange={handleFileChange} />
                        </button>

                        <textarea
                            className="flex-1 bg-transparent border-none focus:ring-0 text-white py-3.5 px-1 resize-none max-h-36 placeholder-zinc-800 text-[15px] leading-relaxed text-left"
                            placeholder="在此輸入指令..."
                            rows={1}
                            value={input}
                            onChange={(e) => {
                                setInput(e.target.value);
                                e.target.style.height = "auto";
                                e.target.style.height = `${e.target.scrollHeight}px`;
                            }}
                            onKeyDown={(e) => {
                                if (e.key === "Enter" && !e.shiftKey && !e.nativeEvent.isComposing) {
                                    e.preventDefault();
                                    handleSend();
                                }
                            }}
                        />

                        <button
                            onClick={handleSend}
                            disabled={isLoading || (!input.trim() && selectedFiles.length === 0)}
                            className={`p-3.5 rounded-full mb-0.5 flex-shrink-0 transition-all duration-300 ${input.trim() || selectedFiles.length > 0
                                    ? "bg-blue-600/10 text-blue-400 hover:bg-blue-600/20 shadow-[0_0_20px_rgba(59,130,246,0.15)] active:scale-90"
                                    : "bg-transparent text-zinc-800"
                                }`}
                        >
                            <Send size={20} strokeWidth={2} />
                        </button>
                    </div>
                </div>
                <p className="mt-6 text-[9px] text-center text-zinc-800 tracking-[0.6em] uppercase font-bold opacity-40">
                    Providence Research Lab
                </p>
            </footer>
        </div>
    );
}