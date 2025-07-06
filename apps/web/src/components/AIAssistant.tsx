// components/AIAssistant.tsx
import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { askAI, getChatSessions, getChatMessages, sendChatMessage } from '@/integrations/api';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { MessageSquare, Camera, Sun } from 'lucide-react';

const AIAssistant: React.FC = () => {
  const queryClient = useQueryClient();
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [inputMessage, setInputMessage] = useState('');

  // ── Fetch or create a chat session ──
  const { data: sessions } = useQuery(['aiSessions'], getChatSessions);
  // (you can pick the first session or create a new one)

  // ── Fetch messages for current session ──
  const { data: messages = [], isLoading: messagesLoading } = useQuery(
    ['aiMessages', sessionId],
    () => getChatMessages(sessionId!),
    { enabled: !!sessionId }
  );

  // ── Mutation: send a new message ──
  const sendMutation = useMutation(sendChatMessage, {
    onSuccess: () => queryClient.invalidateQueries(['aiMessages', sessionId]),
  });

  const handleSend = () => {
    if (!inputMessage.trim() || !sessionId) return;
    sendMutation.mutate({
      session: sessionId,
      content: inputMessage,
      is_user: true,
    });
    setInputMessage('');
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <Card className="bg-white/60 backdrop-blur-sm border-green-200">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <MessageSquare className="w-5 h-5 text-green-600" />
            <span>AI Plant Care Assistant</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          {messagesLoading ? (
            <p>Loading chat…</p>
          ) : (
            <div className="h-96 overflow-y-auto space-y-4 p-4 bg-gray-50/50 rounded-lg">
              {messages.map((msg, i) => (
                <div key={i} className={`flex ${msg.is_user ? 'justify-end' : 'justify-start'}`}>
                  <div
                    className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                      msg.is_user ? 'bg-green-600 text-white' : 'bg-white border'
                    }`}
                  >
                    <p className="text-sm">{msg.content}</p>
                    <p className="text-xs mt-1 text-gray-500">
                      {new Date(msg.created_at).toLocaleTimeString()}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          )}

          <div className="flex space-x-2 mt-4">
            <Input
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              placeholder="Ask about your plants..."
              onKeyPress={(e) => e.key === 'Enter' && handleSend()}
              className="flex-1"
            />
            <Button onClick={handleSend} className="bg-green-600 hover:bg-green-700">
              Send
            </Button>
            <Button variant="outline">
              <Camera className="w-4 h-4" />
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card className="bg-white/60 backdrop-blur-sm border-green-200">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Sun className="w-5 h-5 text-yellow-600" />
            <span>Common Questions</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {[
              "Why are my plant leaves turning yellow?",
              "How often should I water my monstera?",
              "What's the best fertilizer for indoor plants?",
              "How to deal with plant pests naturally?",
            ].map((q, idx) => (
              <Button
                key={idx}
                variant="outline"
                className="text-left h-auto p-3 border-green-200 hover:bg-green-50"
                onClick={() => setInputMessage(q)}
              >
                {q}
              </Button>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default AIAssistant;
