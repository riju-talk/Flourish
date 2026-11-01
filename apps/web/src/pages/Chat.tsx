import { useEffect, useRef, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import ReactMarkdown from "react-markdown";
import { Bot, Loader2, PanelLeft, Send, Sparkles, User } from "lucide-react";
import { Navbar } from "@/components/Navbar";
import { Seo } from "@/components/Seo";
import { ChatSidebar } from "@/components/ChatSidebar";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Sheet, SheetContent, SheetTitle } from "@/components/ui/sheet";
import { useToast } from "@/hooks/use-toast";
import { rateLimitMessage } from "@/lib/apiError";
import {
  createChatSession, deleteChatSession, getChatSession, listChatSessions,
  renameChatSession, sendSessionMessage,
  type ChatSessionDetail, type ChatSessionSummary, type SessionMessage,
} from "@/integrations/api";

const STARTERS = [
  "How do I care for my Monstera?",
  "Suggest low-light plants for my room",
  "Why are my plant's leaves turning yellow?",
  "Which of my plants need water this week?",
];

const SESSIONS_KEY = ["chat-sessions"] as const;
const sessionKey = (id: string) => ["chat-session", id] as const;

/** A message that exists only on the client (optimistic user turn or a failure notice). */
type LocalMessage = Pick<SessionMessage, "role" | "content"> & { id: string; suggestions?: string[]; failed?: boolean };

const Chat = () => {
  const { sessionId } = useParams<{ sessionId?: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { toast } = useToast();

  const [input, setInput] = useState("");
  const [local, setLocal] = useState<LocalMessage[]>([]);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  const sessionsQuery = useQuery({ queryKey: SESSIONS_KEY, queryFn: listChatSessions });
  const detailQuery = useQuery({
    queryKey: sessionKey(sessionId ?? ""),
    queryFn: () => getChatSession(sessionId!),
    enabled: !!sessionId,
    retry: false,
    // The send mutation writes the new turn straight into this cache; don't refetch it
    // the instant we navigate to the session.
    staleTime: 30_000,
  });

  // A session that no longer exists (deleted elsewhere, bad link) falls back to a new chat.
  useEffect(() => {
    if (detailQuery.isError && sessionId) {
      toast({ title: "That chat couldn't be found", variant: "destructive" });
      navigate("/chat", { replace: true });
    }
  }, [detailQuery.isError, sessionId, navigate, toast]);

  // Local-only messages belong to the conversation being viewed.
  useEffect(() => setLocal([]), [sessionId]);

  const saved: SessionMessage[] = detailQuery.data?.messages ?? [];
  const sending = useRef(false);

  const send = useMutation({
    mutationFn: async ({ text, id }: { text: string; id?: string }) => {
      const sid = id ?? (await createChatSession()).id;
      return { sid, result: await sendSessionMessage(sid, text), created: !id };
    },
    onSuccess: ({ sid, result, created }, { text }) => {
      if (result.error) {
        // Nothing was saved server-side; show the notice and give the text back to retry.
        setLocal((prev) => [...prev, { id: `err-${Date.now()}`, role: "assistant", content: result.assistant_message.content, failed: true }]);
        setInput(text);
        // Don't leave an empty "New chat" behind for a first message that never landed.
        if (created) deleteChatSession(sid).catch(() => undefined);
        return;
      }
      queryClient.setQueryData<ChatSessionDetail>(sessionKey(sid), (old) => ({
        ...result.session,
        messages: [...(old?.messages ?? []), ...(result.user_message ? [result.user_message] : []), result.assistant_message],
      }));
      queryClient.setQueryData<ChatSessionSummary[]>(SESSIONS_KEY, (old = []) => [
        result.session,
        ...old.filter((s) => s.id !== sid),
      ]);
      setLocal([]);
      if (created) navigate(`/chat/${sid}`, { replace: true });
    },
    onError: (e, { text }) => {
      setInput(text);
      setLocal((prev) => prev.filter((m) => m.role !== "user" || m.id.startsWith("err")));
      const limited = rateLimitMessage(e);
      toast({
        title: limited ? "Slow down a little" : "Message failed to send",
        description: limited ?? "Check your connection and try again.",
        variant: "destructive",
      });
    },
    onSettled: () => { sending.current = false; },
  });

  const rename = useMutation({
    mutationFn: ({ id, title }: { id: string; title: string }) => renameChatSession(id, title),
    onSuccess: (s) => {
      queryClient.setQueryData<ChatSessionSummary[]>(SESSIONS_KEY, (old = []) => old.map((x) => (x.id === s.id ? { ...x, title: s.title } : x)));
      queryClient.setQueryData<ChatSessionDetail>(sessionKey(s.id), (old) => (old ? { ...old, title: s.title } : old));
    },
    onError: () => toast({ title: "Couldn't rename chat", variant: "destructive" }),
  });

  const remove = useMutation({
    mutationFn: (id: string) => deleteChatSession(id),
    onSuccess: (_d, id) => {
      queryClient.setQueryData<ChatSessionSummary[]>(SESSIONS_KEY, (old = []) => old.filter((s) => s.id !== id));
      queryClient.removeQueries({ queryKey: sessionKey(id) });
      if (id === sessionId) navigate("/chat");
    },
    onError: () => toast({ title: "Couldn't delete chat", variant: "destructive" }),
  });

  const submit = (text = input) => {
    const content = text.trim();
    if (!content || sending.current) return;
    sending.current = true;
    setLocal((prev) => [...prev.filter((m) => !m.failed), { id: `local-${Date.now()}`, role: "user", content }]);
    setInput("");
    send.mutate({ text: content, id: sessionId });
  };

  const messages: (SessionMessage | LocalMessage)[] = [...saved, ...local];
  const lastIdx = messages.length - 1;

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages.length, send.isPending]);

  const goTo = (id: string) => { navigate(`/chat/${id}`); setSidebarOpen(false); };
  const newChat = () => { navigate("/chat"); setInput(""); setSidebarOpen(false); };

  const sidebar = (
    <ChatSidebar
      sessions={sessionsQuery.data ?? []}
      loading={sessionsQuery.isLoading}
      activeId={sessionId}
      onSelect={goTo}
      onNew={newChat}
      onRename={(id, title) => rename.mutate({ id, title })}
      onDelete={(id) => remove.mutate(id)}
    />
  );

  const title = detailQuery.data?.title;
  const showWelcome = !sessionId && messages.length === 0;

  return (
    <div className="flex h-[100dvh] flex-col bg-background">
      <Seo title="PlantMind Chat" description="Chat with PlantMind, your AI plant care assistant, for personalized care advice." />
      <Navbar />

      <div className="flex flex-1 min-h-0">
        <aside className="hidden w-72 shrink-0 border-r border-border bg-card/40 md:block">{sidebar}</aside>

        <Sheet open={sidebarOpen} onOpenChange={setSidebarOpen}>
          <SheetContent side="left" className="w-80 p-0">
            <SheetTitle className="sr-only">Chat history</SheetTitle>
            {sidebar}
          </SheetContent>
        </Sheet>

        <main className="flex min-w-0 flex-1 flex-col">
          <div className="flex items-center gap-2 border-b border-border px-4 py-2.5">
            <Button variant="ghost" size="icon" className="md:hidden" onClick={() => setSidebarOpen(true)} aria-label="Open chat history">
              <PanelLeft className="h-5 w-5" />
            </Button>
            <Sparkles className="h-4 w-4 text-primary" />
            <h1 className="truncate text-sm font-semibold">{title || "PlantMind"}</h1>
          </div>

          <div className="flex-1 min-h-0 overflow-y-auto">
            <div className="mx-auto max-w-3xl px-4 py-6">
              {detailQuery.isLoading && sessionId && (
                <div className="flex justify-center py-20 text-muted-foreground"><Loader2 className="h-5 w-5 animate-spin" /></div>
              )}

              {showWelcome && (
                <div className="py-12 text-center">
                  <div className="mx-auto mb-5 flex h-14 w-14 items-center justify-center rounded-2xl bg-primary/10">
                    <Bot className="h-7 w-7 text-primary" />
                  </div>
                  <h2 className="font-serif text-3xl font-semibold">How can I help your garden today?</h2>
                  <p className="mx-auto mt-2 max-w-md text-sm text-muted-foreground">
                    I know your plants, your care history and the local weather. Ask me anything.
                  </p>
                  <div className="mx-auto mt-8 grid max-w-xl gap-2 sm:grid-cols-2">
                    {STARTERS.map((s) => (
                      <button
                        key={s}
                        onClick={() => submit(s)}
                        className="rounded-xl border border-border bg-card px-4 py-3 text-left text-sm transition-colors hover:bg-secondary"
                      >
                        {s}
                      </button>
                    ))}
                  </div>
                </div>
              )}

              <div className="space-y-6">
                {messages.map((m, i) => {
                  const isUser = m.role === "user";
                  const failed = "failed" in m && m.failed;
                  return (
                    <div key={m.id} className={`flex gap-3 ${isUser ? "flex-row-reverse" : ""}`}>
                      <div className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-full ${isUser ? "border border-border bg-card text-muted-foreground" : "bg-primary text-primary-foreground"}`}>
                        {isUser ? <User size={16} /> : <Bot size={16} />}
                      </div>
                      <div className={`flex max-w-[85%] flex-col gap-2 ${isUser ? "items-end" : ""}`}>
                        <div
                          className={`rounded-2xl px-4 py-3 text-[15px] leading-relaxed ${
                            isUser ? "bg-primary text-primary-foreground" : failed ? "border border-destructive/40 bg-destructive/5" : "border border-border bg-card"
                          }`}
                        >
                          <div className="markdown-content">
                            <ReactMarkdown
                              components={{
                                p: ({ children }) => <p className="mb-2 last:mb-0">{children}</p>,
                                ul: ({ children }) => <ul className="mb-2 list-disc pl-5">{children}</ul>,
                                ol: ({ children }) => <ol className="mb-2 list-decimal pl-5">{children}</ol>,
                                strong: ({ children }) => <strong className="font-semibold">{children}</strong>,
                              }}
                            >
                              {m.content}
                            </ReactMarkdown>
                          </div>
                        </div>
                        {!isUser && !failed && i === lastIdx && !send.isPending && !!m.suggestions?.length && (
                          <div className="flex flex-wrap gap-2">
                            {m.suggestions.map((s) => (
                              <button
                                key={s}
                                onClick={() => submit(s)}
                                className="rounded-full border border-primary/20 bg-secondary/60 px-3 py-1.5 text-xs transition-colors hover:bg-primary hover:text-primary-foreground"
                              >
                                {s}
                              </button>
                            ))}
                          </div>
                        )}
                      </div>
                    </div>
                  );
                })}

                {send.isPending && (
                  <div className="flex gap-3" aria-live="polite" aria-label="PlantMind is thinking">
                    <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary text-primary-foreground"><Bot size={16} /></div>
                    <div className="flex items-center gap-1 rounded-2xl border border-border bg-card px-4 py-4">
                      <span className="h-2 w-2 animate-bounce rounded-full bg-primary/60" />
                      <span className="h-2 w-2 animate-bounce rounded-full bg-primary/60 [animation-delay:150ms]" />
                      <span className="h-2 w-2 animate-bounce rounded-full bg-primary/60 [animation-delay:300ms]" />
                    </div>
                  </div>
                )}
              </div>
              <div ref={bottomRef} />
            </div>
          </div>

          <div className="border-t border-border bg-card/60 p-4">
            <form
              onSubmit={(e) => { e.preventDefault(); submit(); }}
              className="relative mx-auto flex max-w-3xl items-end gap-2"
            >
              <Textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" && !e.shiftKey) {
                    e.preventDefault();
                    submit();
                  }
                }}
                rows={1}
                maxLength={4000}
                placeholder="Message PlantMind…"
                aria-label="Message PlantMind"
                className="max-h-40 min-h-[48px] resize-none rounded-2xl bg-background py-3 pr-14"
              />
              <Button
                type="submit"
                size="icon"
                disabled={send.isPending || !input.trim()}
                aria-label="Send message"
                className="absolute bottom-1.5 right-1.5 h-9 w-9 rounded-xl"
              >
                {send.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
              </Button>
            </form>
            <p className="mt-2 text-center text-[11px] text-muted-foreground">
              PlantMind can make mistakes. Check pet-safety and treatment advice before acting on it.
            </p>
          </div>
        </main>
      </div>
    </div>
  );
};

export default Chat;
