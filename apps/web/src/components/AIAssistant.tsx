// components/AIAssistant.tsx
import React, { useState, useCallback } from 'react'
import { useAuth } from '@/hooks/useAuth'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import ReactMarkdown from 'react-markdown'
import { fetchChatMessages, sendChatMessage } from '@/integrations/api'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Loader2, Send } from 'lucide-react'

interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  created_at: string
}

interface ChatResponse {
  response: string
  suggestions?: string[]
}

const QUICK_QUESTIONS = [
  'Why are my plant leaves turning yellow?',
  'How often should I water my monstera?',
  "What's the best fertilizer for indoor plants?",
  'How to deal with plant pests naturally?',
  'When should I repot my ficus?',
  'How much humidity does a fern need?',
] as const

const generateGuestEmail = (): string =>
  `guest-${Math.random().toString(36).substring(2, 15)}@example.com`

const AIAssistant: React.FC = () => {
  const { user } = useAuth()
  const queryClient = useQueryClient()
  const email = user?.email || generateGuestEmail()

  const [inputMessage, setInputMessage] = useState('')
  const [pendingUserMsg, setPendingUserMsg] = useState<ChatMessage | null>(null)
  const [assistantReply, setAssistantReply] = useState<string>('')
  const [followUps, setFollowUps] = useState<string[]>([])

  // 1️⃣ Load conversation
  const {
    data: messages = [],
    isLoading: loadingMessages,
    error: loadError,
    refetch: reloadMessages,
  } = useQuery<ChatMessage[], Error>({
    queryKey: ['chatMessages', email],
    queryFn: () => fetchChatMessages(email),
    enabled: !!email,
  })

  // 2️⃣ Send new message
  const sendMutation = useMutation<ChatResponse, Error, string>({
    mutationFn: (msg) => sendChatMessage(email, msg),
    onMutate: (msg) => {
      // optimistic user bubble
      setPendingUserMsg({
        id: `temp-${Date.now()}`,
        role: 'user',
        content: msg,
        created_at: new Date().toISOString(),
      })
      setAssistantReply('')
      setFollowUps([])
    },
    onSuccess: (data) => {
      setInputMessage('')
      setAssistantReply(data.response)
      setFollowUps(data.suggestions || [])
      // refresh persisted history
      queryClient.invalidateQueries({ queryKey: ['chatMessages', email] })
    },
    onError: () => {
      setAssistantReply('Sorry, something went wrong.')
    },
  })

  // 3️⃣ Handlers
  const handleSend = useCallback(() => {
    if (!inputMessage.trim() || sendMutation.isLoading) return
    sendMutation.mutate(inputMessage.trim())
  }, [inputMessage, sendMutation])

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault()
        handleSend()
      }
    },
    [handleSend]
  )

  const handleQuick = useCallback((q: string) => {
    setInputMessage(q)
    setTimeout(() => sendMutation.mutate(q), 50)
  }, [sendMutation])

  // 4️⃣ Render
  if (loadError) {
    return (
      <Card className="max-w-3xl mx-auto mt-8">
        <CardHeader>
          <CardTitle>Error loading chat</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-red-500">Unable to load messages.</p>
          <Button onClick={() => reloadMessages()}>Retry</Button>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className="max-w-3xl mx-auto mt-8">
      <CardHeader>
        <CardTitle>AI Plant Care Assistant</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Chat window */}
        <div className="h-96 overflow-y-auto p-4 space-y-4 bg-gray-50 rounded-lg">
          {loadingMessages ? (
            <div className="flex justify-center items-center h-full">
              <Loader2 className="h-8 w-8 animate-spin text-gray-400" />
            </div>
          ) : (
            <>
              {/* persisted history */}
              {messages.map((msg) => (
                <div
                  key={msg.id}
                  className={`flex ${
                    msg.role === 'user' ? 'justify-end' : 'justify-start'
                  }`}
                >
                  <div
                    className={`max-w-[80%] px-4 py-2 rounded-lg ${
                      msg.role === 'user'
                        ? 'bg-green-600 text-white'
                        : 'bg-white border border-gray-200'
                    }`}
                  >
                    <ReactMarkdown>{msg.content}</ReactMarkdown>
                  </div>
                </div>
              ))}

              {/* optimistic user */}
              {pendingUserMsg && (
                <div className="flex justify-end">
                  <div className="max-w-[80%] px-4 py-2 rounded-lg bg-green-600 text-white">
                    <ReactMarkdown>{pendingUserMsg.content}</ReactMarkdown>
                  </div>
                </div>
              )}

              {/* thinking */}
              {sendMutation.isLoading && (
                <div className="flex justify-start">
                  <div className="bg-white border border-gray-200 px-4 py-2 rounded-lg flex items-center space-x-2">
                    <Loader2 className="h-4 w-4 animate-spin" />
                    <span className="text-sm text-gray-500">Thinking…</span>
                  </div>
                </div>
              )}

              {/* assistant reply */}
              {assistantReply && !sendMutation.isLoading && (
                <div className="flex justify-start">
                  <div className="max-w-[80%] px-4 py-2 rounded-lg bg-white border border-gray-200">
                    <ReactMarkdown>{assistantReply}</ReactMarkdown>
                  </div>
                </div>
              )}

              {/* follow‑ups */}
              {followUps.length > 0 && (
                <div className="flex flex-wrap gap-2 mt-2">
                  {followUps.map((q, i) => (
                    <Button
                      key={`follow-${i}`}
                      variant="outline"
                      size="sm"
                      onClick={() => handleQuick(q)}
                    >
                      {q}
                    </Button>
                  ))}
                </div>
              )}
            </>
          )}
        </div>

        {/* Input + send */}
        <div className="flex gap-2">
          <Input
            as="textarea"
            placeholder="Ask me anything about plant care…"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyDown={handleKeyDown}
            className="flex-1 min-h-[40px] resize-none"
            rows={1}
            disabled={sendMutation.isLoading}
          />
          <Button
            onClick={handleSend}
            disabled={!inputMessage.trim() || sendMutation.isLoading}
            size="icon"
            type="button"
          >
            {sendMutation.isLoading ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Send className="h-4 w-4" />
            )}
          </Button>
        </div>

        {/* Quick Questions */}
        <div className="flex flex-wrap gap-2 px-2">
          {QUICK_QUESTIONS.map((q, i) => (
            <Button
              key={`quick-${i}`}
              variant="outline"
              size="sm"
              onClick={() => handleQuick(q)}
              disabled={sendMutation.isLoading}
            >
              {q}
            </Button>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}

export default AIAssistant
