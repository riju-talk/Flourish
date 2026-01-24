import { useState, useRef, useEffect } from "react";
import { useMutation } from "@tanstack/react-query";
import { Navbar } from "@/components/Navbar";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Leaf, Send, Bot, User, Sparkles, Paperclip, FileText } from "lucide-react";
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
    <div className="min-h-screen bg-background flex flex-col">
      <Navbar />

      <main className="flex-1 container mx-auto max-w-4xl p-4 md:p-8 flex flex-col gap-6">
        <header className="flex items-center justify-between">
          <h1 className="text-3xl font-bold text-primary flex items-center gap-2">
            PlantMind AI <Sparkles className="h-5 w-5 text-yellow-500 leaf-pulse" />
          </h1>
          <div className="text-sm font-medium px-3 py-1 bg-primary/10 rounded-full text-primary">
            Powered by Ollama
          </div>
        </header>

        {/* Chat Area */}
        <section className="flex-1 glass-card rounded-3xl overflow-hidden flex flex-col animate-in fade-in zoom-in duration-500">
          <ScrollArea className="flex-1 p-6" ref={scrollRef}>
            <div className="space-y-6 pb-4">
              {messages.map((msg, i) => (
                <div key={i} className={`flex gap-4 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}>
                  <div className={`w-10 h-10 rounded-2xl flex items-center justify-center shrink-0 ${msg.role === 'assistant' ? 'vibrant-gradient text-white' : 'bg-secondary'
                    }`}>
                    {msg.role === 'assistant' ? <Bot size={20} /> : <User size={20} />}
                  </div>

                  <div className="flex flex-col gap-3 max-w-[80%]">
                    <div className={`p-4 rounded-3xl text-sm leading-relaxed ${msg.role === 'assistant'
                      ? 'bg-white/50 border border-white/20'
                      : 'vibrant-gradient text-white'
                      }`}>
                      <ReactMarkdown className="markdown-content">{msg.content}</ReactMarkdown>
                    </div>

                    {/* Follow-up Suggestions */}
                    {msg.suggestions && msg.role === 'assistant' && (
                      <div className="flex flex-wrap gap-2 animate-in fade-in slide-in-from-bottom duration-700">
                        {msg.suggestions.map((suggestion, j) => (
                          <button
                            key={j}
                            onClick={() => { setInput(suggestion); }}
                            className="text-xs px-3 py-1.5 rounded-full border border-primary/20 bg-white/30 hover:bg-primary/10 transition-colors"
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
                <div className="flex gap-4 animate-pulse">
                  <div className="w-10 h-10 rounded-2xl vibrant-gradient opacity-50 flex items-center justify-center">
                    <Bot size={20} className="text-white" />
                  </div>
                  <div className="p-4 rounded-3xl bg-secondary/50 w-32 h-10"></div>
                </div>
              )}
            </div>
          </ScrollArea>

          {/* Input Area */}
          <div className="p-4 bg-white/30 border-t border-white/20">
            <div className="relative">
              <Input
                placeholder="Ask Ollama about your plants..."
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                className="rounded-2xl pr-12 h-14 bg-white/50 border-white/30 focus:ring-primary"
              />
              <Button
                size="icon"
                onClick={handleSend}
                disabled={chatMutation.isPending}
                className="absolute right-2 top-2 h-10 w-10 rounded-xl bg-primary hover:vibrant-gradient text-white"
              >
                <Send size={18} />
              </Button>
            </div>
          </div>
        </section>
      </main>
    </div>
  );
};

export default Chat;
