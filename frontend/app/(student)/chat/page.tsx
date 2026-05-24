"use client";

import { useState, useRef, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Badge } from "@/components/ui/badge";
import {
  Send,
  Plus,
  MessageSquare,
  Quote,
} from "lucide-react";
import Link from "next/link";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  citations?: { type: "question" | "article"; id: string; label: string }[];
}

const mockSessions = [
  { id: "1", title: "民法侵权责任", updatedAt: "10分钟前" },
  { id: "2", title: "刑法故意杀人罪构成", updatedAt: "1小时前" },
  { id: "3", title: "行政法基本原则", updatedAt: "昨天" },
];

const mockMessages: Record<string, Message[]> = {
  "1": [
    {
      id: "m1",
      role: "assistant",
      content:
        "你好！我是你的 AI 法考助手，可以帮你用苏格拉底式问答法理解法律概念。当前会话科目：**民法**。有什么问题吗？",
    },
    {
      id: "m2",
      role: "user",
      content: "请解释一下善意取得的构成要件",
    },
    {
      id: "m3",
      role: "assistant",
      content:
        "好的，让我们从基础开始思考。\n\n**问题1**：假设 A 把手机借给 B 使用，B 却把手机卖给了不知情的 C。请问 C 能否取得手机所有权？\n\n提示：这涉及到《民法典》第 311 条关于善意取得的规定。",
      citations: [
        { type: "article", id: "311", label: "民法典 第311条" },
        { type: "question", id: "Q123", label: "题 #Q123" },
      ],
    },
    {
      id: "m4",
      role: "user",
      content: "C 如果是善意的，应该可以取得所有权吧？",
    },
    {
      id: "m5",
      role: "assistant",
      content:
        "接近正确答案了！\n\n善意取得需要同时满足三个条件：\n1. **受让人善意**（不知道或无重大过失不知道处分人无权处分）\n2. **合理价格转让**（不是赠与或明显低价）\n3. **完成交付**（动产已交付 / 不动产已登记）\n\n你提到了善意这个条件，还有其他两个哦。能说说看分别是什么吗？😊",
    },
  ],
};

export default function ChatPage() {
  const [activeSession, setActiveSession] = useState("1");
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<Message[]>(mockMessages["1"] || []);
  const [streaming, setStreaming] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || streaming) return;
    const userMsg: Message = {
      id: Date.now().toString(),
      role: "user",
      content: input,
    };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setStreaming(true);

    // Mock streaming response
    const mockResponse =
      "这是一个模拟的 AI 回复。在正式实现中，这里会通过 SSE 流式输出 LLM 的回复内容，并支持实时渲染 Markdown 和 KaTeX 公式。\n\n> 引用的法条和题目会自动渲染成可点击的 chip。";
    const assistantMsg: Message = {
      id: (Date.now() + 1).toString(),
      role: "assistant",
      content: mockResponse,
      citations: [
        { type: "article", id: "311", label: "民法典 第311条" },
      ],
    };
    setTimeout(() => {
      setMessages((prev) => [...prev, assistantMsg]);
      setStreaming(false);
    }, 1000);
  };

  return (
    <div className="flex h-[calc(100vh-7rem)] gap-4">
      {/* Sidebar - session list */}
      <Card className="w-64 shrink-0 p-2">
        <Button className="w-full mb-2 gap-2" size="sm">
          <Plus className="h-4 w-4" />
          新建会话
        </Button>
        <ScrollArea className="h-[calc(100%-3rem)]">
          <div className="space-y-1">
            {mockSessions.map((s) => (
              <button
                key={s.id}
                onClick={() => {
                  setActiveSession(s.id);
                  setMessages(mockMessages[s.id] || []);
                }}
                className={`w-full text-left p-2 rounded-md text-sm flex items-center gap-2 ${
                  activeSession === s.id
                    ? "bg-primary/10 text-primary"
                    : "hover:bg-muted"
                }`}
              >
                <MessageSquare className="h-4 w-4 shrink-0" />
                <div className="truncate flex-1">
                  <div className="truncate">{s.title}</div>
                  <div className="text-xs text-muted-foreground">
                    {s.updatedAt}
                  </div>
                </div>
              </button>
            ))}
          </div>
        </ScrollArea>
      </Card>

      {/* Main chat pane */}
      <Card className="flex-1 flex flex-col">
        <ScrollArea ref={scrollRef} className="flex-1 p-4">
          <div className="space-y-4">
            {messages.map((msg) => (
              <div
                key={msg.id}
                className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
              >
                <div
                  className={`max-w-[80%] rounded-lg p-3 ${
                    msg.role === "user"
                      ? "bg-primary text-primary-foreground"
                      : "bg-muted"
                  }`}
                >
                  <div className="text-sm whitespace-pre-wrap">
                    {msg.content}
                  </div>
                  {msg.citations && msg.citations.length > 0 && (
                    <div className="flex flex-wrap gap-1 mt-2">
                      {msg.citations.map((c) => (
                        <Link
                          key={c.id}
                          href={
                            c.type === "article"
                              ? `/legal-articles/${c.id}`
                              : `/questions/${c.id}`
                          }
                        >
                          <Badge
                            variant="outline"
                            className="cursor-pointer hover:bg-primary/10"
                          >
                            <Quote className="h-3 w-3 mr-1" />
                            {c.label}
                          </Badge>
                        </Link>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ))}
            {streaming && (
              <div className="flex justify-start">
                <div className="bg-muted rounded-lg p-3">
                  <span className="animate-pulse">思考中...</span>
                </div>
              </div>
            )}
          </div>
        </ScrollArea>

        {/* Input area */}
        <div className="border-t p-4">
          <div className="flex gap-2">
            <Input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="输入你的问题，或使用 /quote 引用题目/法条..."
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  handleSend();
                }
              }}
              disabled={streaming}
            />
            <Button onClick={handleSend} disabled={streaming || !input.trim()}>
              <Send className="h-4 w-4" />
            </Button>
          </div>
          <p className="text-xs text-muted-foreground mt-1">
            支持 slash 命令：/quote Q123 引用题目 /article 第1062条 引用法条
          </p>
        </div>
      </Card>
    </div>
  );
}