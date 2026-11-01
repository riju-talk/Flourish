import { useMemo, useState } from "react";
import { MessageSquare, MoreHorizontal, Pencil, Plus, Trash2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent,
  AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { groupSessionsByDate } from "@/lib/chatSessions";
import type { ChatSessionSummary } from "@/integrations/api";

interface Props {
  sessions: ChatSessionSummary[];
  loading: boolean;
  activeId?: string;
  onSelect: (id: string) => void;
  onNew: () => void;
  onRename: (id: string, title: string) => void;
  onDelete: (id: string) => void;
}

export function ChatSidebar({ sessions, loading, activeId, onSelect, onNew, onRename, onDelete }: Props) {
  const [editingId, setEditingId] = useState<string | null>(null);
  const [draft, setDraft] = useState("");
  const [pendingDelete, setPendingDelete] = useState<ChatSessionSummary | null>(null);
  const groups = useMemo(() => groupSessionsByDate(sessions), [sessions]);

  const startRename = (s: ChatSessionSummary) => {
    setEditingId(s.id);
    setDraft(s.title);
  };

  const commitRename = () => {
    const title = draft.trim();
    const current = sessions.find((s) => s.id === editingId);
    if (editingId && title && current && title !== current.title) onRename(editingId, title);
    setEditingId(null);
  };

  return (
    <div className="flex h-full flex-col">
      <div className="p-3">
        <Button onClick={onNew} variant="outline" className="w-full justify-start gap-2">
          <Plus className="h-4 w-4" /> New chat
        </Button>
      </div>

      <ScrollArea className="flex-1 min-h-0 px-2">
        <nav aria-label="Chat history" className="pb-4">
          {loading && (
            <div className="space-y-2 p-1">
              {[1, 2, 3, 4].map((i) => <Skeleton key={i} className="h-9 w-full rounded-lg" />)}
            </div>
          )}

          {!loading && sessions.length === 0 && (
            <p className="px-3 py-8 text-center text-sm text-muted-foreground">
              No conversations yet. Ask PlantMind something to get started.
            </p>
          )}

          {groups.map((group) => (
            <div key={group.label} className="mb-3">
              <p className="px-3 pb-1 pt-2 text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">
                {group.label}
              </p>
              <ul>
                {group.sessions.map((s) => {
                  const active = s.id === activeId;
                  return (
                    <li key={s.id} className="group relative">
                      {editingId === s.id ? (
                        <Input
                          autoFocus
                          value={draft}
                          maxLength={80}
                          onChange={(e) => setDraft(e.target.value)}
                          onBlur={commitRename}
                          onKeyDown={(e) => {
                            if (e.key === "Enter") commitRename();
                            if (e.key === "Escape") setEditingId(null);
                          }}
                          aria-label="Rename chat"
                          className="h-9"
                        />
                      ) : (
                        <>
                          <button
                            onClick={() => onSelect(s.id)}
                            aria-current={active ? "page" : undefined}
                            className={`flex w-full items-center gap-2 rounded-lg px-3 py-2 pr-9 text-left text-sm transition-colors ${
                              active ? "bg-secondary text-foreground font-medium" : "text-muted-foreground hover:bg-secondary/60 hover:text-foreground"
                            }`}
                          >
                            <MessageSquare className="h-4 w-4 shrink-0" />
                            <span className="truncate">{s.title}</span>
                          </button>
                          <DropdownMenu>
                            <DropdownMenuTrigger asChild>
                              <button
                                aria-label={`Options for ${s.title}`}
                                className={`absolute right-1 top-1/2 -translate-y-1/2 rounded-md p-1.5 text-muted-foreground hover:bg-background hover:text-foreground focus:opacity-100 ${
                                  active ? "opacity-100" : "opacity-0 group-hover:opacity-100"
                                }`}
                              >
                                <MoreHorizontal className="h-4 w-4" />
                              </button>
                            </DropdownMenuTrigger>
                            <DropdownMenuContent align="end">
                              <DropdownMenuItem onSelect={() => startRename(s)}>
                                <Pencil className="mr-2 h-4 w-4" /> Rename
                              </DropdownMenuItem>
                              <DropdownMenuItem onSelect={() => setPendingDelete(s)} className="text-destructive focus:text-destructive">
                                <Trash2 className="mr-2 h-4 w-4" /> Delete
                              </DropdownMenuItem>
                            </DropdownMenuContent>
                          </DropdownMenu>
                        </>
                      )}
                    </li>
                  );
                })}
              </ul>
            </div>
          ))}
        </nav>
      </ScrollArea>

      <AlertDialog open={!!pendingDelete} onOpenChange={(open) => !open && setPendingDelete(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete this chat?</AlertDialogTitle>
            <AlertDialogDescription>
              “{pendingDelete?.title}” and all of its messages will be permanently deleted.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={() => {
                if (pendingDelete) onDelete(pendingDelete.id);
                setPendingDelete(null);
              }}
            >
              Delete
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}

export default ChatSidebar;
