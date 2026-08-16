import { useState, useRef, useEffect } from "react";
import { useMutation } from "@tanstack/react-query";
import { Navbar } from "@/components/Navbar";
import { Footer } from "@/components/Footer";
import { Seo } from "@/components/Seo";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Send, Bot, User, Sparkles } from "lucide-react";
import { chatWithAI } from "@/integrations/api";
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

  return (
    <div className="min-h-screen bg-transparent flex flex-col">
      <Seo title="PlantMind Chat" description="Chat with PlantMind, your AI plant care assistant, for personalized care advice." />
      <Navbar />

      <main className="flex-1 min-h-0 container mx-auto max-w-5xl p-4 md:p-8 flex flex-col gap-6">
        <header className="flex items-center justify-between animate-in fade-in slide-in-from-top-3 duration-1000 ease-out">
          <div className="glass-card px-6 py-3 rounded-full flex items-center gap-3">
            <div className="bg-primary/10 p-2 rounded-full">
              <Sparkles className="h-5 w-5 text-primary leaf-pulse" />
            </div>
            <div>
              <h1 className="font-serif text-xl font-semibold text-foreground">PlantMind AI</h1>
              <div className="flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span>
                <span className="text-xs text-muted-foreground font-medium">Online & Ready</span>
              </div>
            </div>
          </div>
        </header>

        {/* Chat Area */}
        <section className="flex-1 min-h-0 glass-card rounded-[2.5rem] overflow-hidden flex flex-col animate-in fade-in duration-1000 ease-out shadow-2xl relative">
          {/* Background Decor */}
          <div className="absolute inset-0 opacity-30 pointer-events-none bg-[radial-gradient(ellipse_at_top_right,_var(--tw-gradient-stops))] from-primary/20 via-transparent to-transparent"></div>

          <ScrollArea className="flex-1 min-h-0 p-6 md:p-10" ref={scrollRef}>
            <div className="space-y-8 pb-4">
              {messages.map((msg, i) => (
                <div key={i} className={`flex gap-5 ${msg.role === 'user' ? 'flex-row-reverse' : ''} animate-in fade-in slide-in-from-bottom-2 duration-700 ease-out`}>
                  <div className={`w-12 h-12 rounded-full flex items-center justify-center shrink-0 shadow-sm ${msg.role === 'assistant'
                      ? 'bg-primary text-primary-foreground'
                      : 'bg-card border border-border text-muted-foreground'
                    }`}>
                    {msg.role === 'assistant' ? <Bot size={24} /> : <User size={24} />}
                  </div>

                  <div className="flex flex-col gap-3 max-w-[85%] md:max-w-[75%]">
                    <div className={`p-6 rounded-[2rem] text-[15px] leading-relaxed shadow-sm ${msg.role === 'assistant'
                        ? 'bg-card border border-border rounded-tl-none'
                        : 'bg-primary text-primary-foreground rounded-tr-none'
                      }`}>
                      <div className={`markdown-content ${msg.role === 'user' ? 'text-primary-foreground' : 'text-foreground'}`}>
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
                      <div className="flex flex-wrap gap-2 animate-in fade-in slide-in-from-bottom duration-1000 ease-out ml-2">
                        {msg.suggestions.map((suggestion, j) => (
                          <button
                            key={j}
                            onClick={() => { setInput(suggestion); }}
                            className="text-xs px-4 py-2 rounded-full border border-primary/20 bg-secondary/60 hover:bg-primary hover:text-primary-foreground transition-all duration-500 ease-out hover:scale-[1.03]"
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
                  <div className="w-12 h-12 rounded-full bg-primary/50 flex items-center justify-center">
                    <Bot size={24} className="text-primary-foreground" />
                  </div>
                  <div className="p-6 rounded-[2rem] bg-secondary/50 w-48 h-20 flex items-center gap-1 rounded-tl-none">
                    <span className="w-2 h-2 bg-primary/60 rounded-full animate-bounce delay-0"></span>
                    <span className="w-2 h-2 bg-primary/60 rounded-full animate-bounce delay-150"></span>
                    <span className="w-2 h-2 bg-primary/60 rounded-full animate-bounce delay-300"></span>
                  </div>
                </div>
              )}
            </div>
          </ScrollArea>

          {/* Input Area */}
          <div className="p-6 bg-card border-t border-border">
            <div className="relative flex gap-3 max-w-4xl mx-auto">
              <Input
                placeholder="Ask PlantMind about your plants..."
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                className="rounded-2xl pr-4 h-14 bg-background border-border focus-visible:ring-primary/50 text-base"
              />
              <Button
                size="icon"
                onClick={handleSend}
                disabled={chatMutation.isPending || !input.trim()}
                className={`absolute right-2 top-2 h-10 w-10 rounded-xl transition-all duration-500 ease-out ${input.trim() ? 'bg-primary text-primary-foreground hover:scale-[1.03]' : 'bg-muted text-muted-foreground'}`}
              >
                <Send size={18} />
              </Button>
            </div>
          </div>
        </section>
      </main>

      <Footer />
    </div>
  );
};

export default Chat;
