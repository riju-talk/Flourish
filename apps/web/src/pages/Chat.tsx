import { useState, useRef, useEffect } from "react";
import { useMutation } from "@tanstack/react-query";
import { Navbar } from "@/components/Navbar";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Send, Bot, User, Sparkles, Paperclip } from "lucide-react";
import { chatWithAI, analyzeDocument } from "@/integrations/api";
import ReactMarkdown from "react-markdown";

interface Message {
  role: 'user' | 'assistant';
  content: string;
  suggestions?: string[];
}

const Chat = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'assistant',
      content: "Hello! I'm PlantMind, your personal botanical assistant. How can I help your garden thrive today?",
      suggestions: ["How do I care for my Monstera?", "Suggest low-light plants", "Identify a watering issue"]
    }
  ]);
  const [input, setInput] = useState("");
  const [analyzing, setAnalyzing] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const chatMutation = useMutation({
    mutationFn: chatWithAI,
    onSuccess: (data) => {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: data.response,
        suggestions: data.suggestions
      }]);
    }
  });

  const handleSend = () => {
    if (!input.trim() || chatMutation.isPending) return;

    const userMsg = { role: 'user' as const, content: input };
    setMessages(prev => [...prev, userMsg]);
    chatMutation.mutate([...messages, userMsg]);
    setInput("");
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setAnalyzing(true);
    try {
      const data = await analyzeDocument(file);
      setMessages(prev => [...prev,
      { role: 'user', content: `Analyzing care document: ${file.name}` },
      {
        role: 'assistant',
        content: `${data.analysis}\n\n**Recommendations:**\n${data.recommendations.map((r: string) => `- ${r}`).join('\n')}`,
        suggestions: ["Add this to my plant profile", "Tell me more about this species"]
      }
      ]);
    } catch (error) {
      setMessages(prev => [...prev, { role: 'assistant', content: "Sorry, I had trouble analyzing that document. Please try again." }]);
    } finally {
      setAnalyzing(false);
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  };

  return (
    <div className="min-h-screen bg-transparent flex flex-col pb-6">
      <Navbar />

      <main className="flex-1 container mx-auto max-w-5xl p-4 md:p-8 flex flex-col gap-6 h-[calc(100vh-100px)]">
        <header className="flex items-center justify-between animate-in slide-in-from-top-5 duration-500">
          <div className="glass-card px-6 py-3 rounded-full flex items-center gap-3">
            <div className="bg-primary/10 p-2 rounded-full">
              <Sparkles className="h-5 w-5 text-primary leaf-pulse" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-foreground">PlantMind AI</h1>
              <div className="flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span>
                <span className="text-xs text-muted-foreground font-medium">Online & Ready</span>
              </div>
            </div>
          </div>
        </header>

        {/* Chat Area */}
        <section className="flex-1 glass-card rounded-[2.5rem] overflow-hidden flex flex-col animate-in fade-in zoom-in duration-500 shadow-2xl relative">
          {/* Background Decor */}
          <div className="absolute inset-0 opacity-30 pointer-events-none bg-[radial-gradient(ellipse_at_top_right,_var(--tw-gradient-stops))] from-primary/20 via-transparent to-transparent"></div>

          <ScrollArea className="flex-1 p-6 md:p-10" ref={scrollRef}>
            <div className="space-y-8 pb-4">
              {messages.map((msg, i) => (
                <div key={i} className={`flex gap-5 ${msg.role === 'user' ? 'flex-row-reverse' : ''} animate-in slide-in-from-bottom-2 duration-300`}>
                  <div className={`w-12 h-12 rounded-full flex items-center justify-center shrink-0 shadow-md ${msg.role === 'assistant'
                      ? 'vibrant-gradient text-white ring-4 ring-white/20'
                      : 'bg-white text-muted-foreground ring-4 ring-black/5'
                    }`}>
                    {msg.role === 'assistant' ? <Bot size={24} /> : <User size={24} />}
                  </div>

                  <div className="flex flex-col gap-3 max-w-[85%] md:max-w-[75%]">
                    <div className={`p-6 rounded-[2rem] text-[15px] leading-relaxed shadow-sm ${msg.role === 'assistant'
                        ? 'bg-white/80 backdrop-blur-md border border-white/50 rounded-tl-none'
                        : 'vibrant-gradient text-white rounded-tr-none'
                      }`}>
                      <div className={`markdown-content ${msg.role === 'user' ? 'text-white' : 'text-foreground'}`}>
                        <ReactMarkdown
                          components={{
                            p: ({ children }) => <p className="mb-2 last:mb-0">{children}</p>,
                            ul: ({ children }) => <ul className="list-disc pl-4 mb-2">{children}</ul>,
                            strong: ({ children }) => <strong className="font-bold">{children}</strong>
                          }}
                        >
                          {msg.content}
                        </ReactMarkdown>
                      </div>
                    </div>

                    {/* Follow-up Suggestions */}
                    {msg.suggestions && msg.role === 'assistant' && (
                      <div className="flex flex-wrap gap-2 animate-in fade-in slide-in-from-bottom duration-700 ml-2">
                        {msg.suggestions.map((suggestion, j) => (
                          <button
                            key={j}
                            onClick={() => { setInput(suggestion); }}
                            className="text-xs px-4 py-2 rounded-full border border-primary/20 bg-white/40 hover:bg-primary hover:text-white transition-all duration-300 hover:scale-105"
                          >
                            {suggestion}
                          </button>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              ))}

              {chatMutation.isPending && (
                <div className="flex gap-5 animate-pulse">
                  <div className="w-12 h-12 rounded-full vibrant-gradient opacity-50 flex items-center justify-center">
                    <Bot size={24} className="text-white" />
                  </div>
                  <div className="p-6 rounded-[2rem] bg-white/40 w-48 h-20 flex items-center gap-1 rounded-tl-none">
                    <span className="w-2 h-2 bg-primary/60 rounded-full animate-bounce delay-0"></span>
                    <span className="w-2 h-2 bg-primary/60 rounded-full animate-bounce delay-150"></span>
                    <span className="w-2 h-2 bg-primary/60 rounded-full animate-bounce delay-300"></span>
                  </div>
                </div>
              )}
            </div>
          </ScrollArea>

          {/* Input Area */}
          <div className="p-6 bg-white/40 backdrop-blur-xl border-t border-white/20">
            <div className="relative flex gap-3 max-w-4xl mx-auto">
              <Button variant="outline" size="icon" className="h-14 w-14 rounded-2xl border-white/40 hover:bg-white/60 bg-white/20 shrink-0" onClick={() => fileInputRef.current?.click()}>
                <Paperclip size={20} className="text-muted-foreground" />
              </Button>
              <input
                type="file"
                ref={fileInputRef}
                className="hidden"
                accept=".pdf,.png,.jpg,.jpeg"
                onChange={handleFileUpload}
              />

              <Input
                placeholder="Ask PlantMind about your plants..."
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                className="rounded-2xl pr-4 h-14 bg-white/60 border-white/40 focus:ring-primary/50 text-base shadow-inner"
              />
              <Button
                size="icon"
                onClick={handleSend}
                disabled={chatMutation.isPending || !input.trim()}
                className={`absolute right-2 top-2 h-10 w-10 rounded-xl transition-all duration-300 ${input.trim() ? 'vibrant-gradient hover:scale-105' : 'bg-muted text-muted-foreground'}`}
              >
                <Send size={18} />
              </Button>
            </div>
            {analyzing && <p className="text-xs text-center mt-2 text-primary animate-pulse">Analyzing document...</p>}
          </div>
        </section>
      </main>
    </div>
  );
};

export default Chat;
