import React, { useState, useRef, useEffect } from "react";
import { Send, Image as ImageIcon, Film, X, Loader2, Paperclip } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Badge } from "@/components/ui/badge";

interface Message {
  role: "user" | "ai";
  content: string;
  files?: string[];
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  
  const scrollRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    const scrollContainer = scrollRef.current?.querySelector('[data-radix-scroll-area-viewport]');
    if (scrollContainer) {
      scrollContainer.scrollTop = scrollContainer.scrollHeight;
    }
  }, [messages, isLoading]);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const filesArray = Array.from(e.target.files);
      setSelectedFiles((prev) => [...prev, ...filesArray]);
    }
  };

  const removeFile = (index: number) => {
    setSelectedFiles((prev) => prev.filter((_, i) => i !== index));
  };

  const handleSend = async () => {
    if (!input.trim() && selectedFiles.length === 0) return;

    const userMessage: Message = {
      role: "user",
      content: input,
      files: selectedFiles.map(file => URL.createObjectURL(file))
    };

    setMessages((prev) => [...prev, userMessage]);
    const currentInput = input;
    const currentFiles = [...selectedFiles];
    
    setInput("");
    setSelectedFiles([]);
    setIsLoading(true);

    const formData = new FormData();
    formData.append("text", currentInput);
    formData.append("thread_id", "shrimp_research_session"); 
    currentFiles.forEach((file) => {
      formData.append("files", file);
    });

    try {
      const response = await fetch("http://127.0.0.1:8000/chat", {
        method: "POST",
        body: formData,
      });
      const data = await response.json();
      setMessages((prev) => [...prev, { role: "ai", content: data.reply }]);
    } catch (error) {
      setMessages((prev) => [...prev, { role: "ai", content: "抱歉，系統連線發生錯誤 (Connection Error)。" }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-screen max-w-5xl mx-auto p-4 lg:p-6 bg-background">
      {/* Header */}
      <div className="flex items-center justify-between mb-4 border-b pb-4">
        <div>
          <p className="text-2xl text-left text-blue-500 font-bold tracking-tight">Shrimp-AI Researcher</p>
          <p className="text-muted-foreground text-sm flex items-center gap-2">
            <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
            自主式蝦類行為解析系統 (Autonomous Analysis System)
          </p>
        </div>
      </div>

      {/* Main Chat Area */}
      <Card className="flex-1 overflow-hidden flex flex-col shadow-lg border-muted">
        <ScrollArea className="flex-1 overflow-y-auto" ref={scrollRef}>
          <div className="p-4 space-y-6">
            {messages.length === 0 && (
              <div className="flex flex-col items-center justify-center h-[40vh] text-center space-y-4">
                <div className="p-4 bg-muted rounded-full">
                  <ImageIcon className="h-8 w-8 text-muted-foreground" />
                </div>
                <div className="space-y-1">
                  <p className="font-medium">尚未開始對話</p>
                  <p className="text-sm text-muted-foreground max-w-[250px]">
                    您可以上傳照片進行物種鑑定，或詢問養殖技術相關問題。
                  </p>
                </div>
              </div>
            )}
            
            {messages.map((msg, index) => (
              <div
                key={index}
                className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
              >
                <div
                  className={`relative group max-w-[85%] lg:max-w-[70%] rounded-2xl px-4 py-3 shadow-sm ${
                    msg.role === "user"
                      ? "bg-primary text-primary-foreground rounded-tr-none"
                      : "bg-muted text-foreground rounded-tl-none border border-border"
                  }`}
                >
                  <div className="text-sm leading-relaxed whitespace-pre-wrap font-sans">
                    {msg.content}
                  </div>
                  
                  {msg.files && msg.files.length > 0 && (
                    <div className="grid gap-2 mt-2">
                      {msg.files.map((url, i) => (
                        <div key={i} className="relative aspect-square overflow-hidden rounded-lg border bg-white shadow-inner">
                          <img src={url} alt="upload" className="w-full h-full object-cover" />
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ))}

            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-muted rounded-2xl rounded-tl-none px-4 py-3 flex items-center gap-3 border border-border">
                  <Loader2 className="h-4 w-4 animate-spin text-primary" />
                  <span className="text-sm font-medium animate-pulse">分析數據中 (Analyzing)...</span>
                </div>
              </div>
            )}
          </div>
        </ScrollArea>

        {/* Input Control Area */}
        <div className="p-4 border-t bg-card">
          <div className="flex flex-col gap-3">
            {/* File Previews */}
            {selectedFiles.length > 0 && (
              <div className="flex flex-wrap gap-2 animate-in slide-in-from-bottom-2">
                {selectedFiles.map((file, index) => (
                  <Badge key={index} variant="secondary" className="pl-2 pr-1 py-1 flex items-center gap-2 ring-1 ring-primary/10">
                    <span className="text-xs truncate max-w-[120px]">{file.name}</span>
                    <button 
                      onClick={() => removeFile(index)}
                      className="p-0.5 hover:bg-destructive hover:text-destructive-foreground rounded-full transition-colors"
                    >
                      <X className="h-3 w-3" />
                    </button>
                  </Badge>
                ))}
              </div>
            )}

            {/* Actions & Text Input */}
            <div className="flex items-center gap-2">
              <div className="flex items-center gap-1 border-r pr-2 mr-1">
                <input
                  type="file"
                  multiple
                  hidden
                  ref={fileInputRef}
                  onChange={handleFileChange}
                  accept="image/*,video/*"
                />
                <Button
                  variant="ghost"
                  size="icon"
                  className="rounded-full hover:bg-primary/10 hover:text-primary"
                  onClick={() => fileInputRef.current?.click()}
                  type="button"
                >
                  <Paperclip className="h-5 w-5" />
                </Button>
              </div>

              <Input
                className="flex-1 bg-muted/50 border-none focus-visible:ring-1 focus-visible:ring-primary h-11"
                placeholder="輸入關於蝦類養殖的問題或指令..."
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && !e.nativeEvent.isComposing && handleSend()}
              />
              
              <Button 
                onClick={handleSend} 
                disabled={isLoading || (!input.trim() && selectedFiles.length === 0)}
                className="rounded-full w-11 h-11 p-0 shadow-md"
              >
                {isLoading ? (
                  <Loader2 className="h-5 w-5 animate-spin" />
                ) : (
                  <Send className="h-5 w-5" />
                )}
              </Button>
            </div>
          </div>
        </div>
      </Card>
      
      <div className="mt-2 text-center text-[10px] text-muted-foreground uppercase tracking-widest">
        Providence University • Shrimp-LMM-Agent Project
      </div>
    </div>
  );
}