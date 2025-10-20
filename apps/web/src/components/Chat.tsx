import React, { useState, useRef, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Card } from '@/components/ui/card';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { Mic, MicOff, Image as ImageIcon, Send, Loader2 } from 'lucide-react';
import { chatWithAI, analyzeImage } from '@/integrations/api';
import { useAuth } from '@/hooks/useAuth';

interface Message {
  id: string;
  content: string;
  role: 'user' | 'assistant';
  timestamp: Date;
  image?: string;
}

interface ChatProps {
  plantId?: string;
}

export default function Chat({ plantId }: ChatProps) {
  const { user } = useAuth();
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const scrollAreaRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const recognitionRef = useRef<SpeechRecognition | null>(null);

  // Initialize speech recognition
  useEffect(() => {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.webkitSpeechRecognition || window.SpeechRecognition;
      recognitionRef.current = new SpeechRecognition();
      recognitionRef.current.continuous = false;
      recognitionRef.current.interimResults = false;
      recognitionRef.current.lang = 'en-US';

      recognitionRef.current.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        setInput(transcript);
      };

      recognitionRef.current.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        setIsRecording(false);
      };

      recognitionRef.current.onend = () => {
        setIsRecording(false);
      };
    }
  }, []);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (scrollAreaRef.current) {
      scrollAreaRef.current.scrollTop = scrollAreaRef.current.scrollHeight;
    }
  }, [messages]);

  const startRecording = () => {
    if (recognitionRef.current && !isRecording) {
      setIsRecording(true);
      recognitionRef.current.start();
    }
  };

  const stopRecording = () => {
    if (recognitionRef.current && isRecording) {
      recognitionRef.current.stop();
    }
  };

  const handleImageUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = async (e) => {
        const imageData = e.target?.result as string;
        setIsLoading(true);

        try {
          const analysis = await analyzeImage(imageData, plantId);

          const newMessage: Message = {
            id: Date.now().toString(),
            content: `I uploaded an image for analysis. ${analysis.health_assessment}`,
            role: 'assistant',
            timestamp: new Date(),
          };

          setMessages(prev => [...prev, newMessage]);
        } catch (error) {
          console.error('Image analysis error:', error);
          const errorMessage: Message = {
            id: Date.now().toString(),
            content: 'Sorry, I had trouble analyzing your image. Please try again.',
            role: 'assistant',
            timestamp: new Date(),
          };
          setMessages(prev => [...prev, errorMessage]);
        } finally {
          setIsLoading(false);
        }
      };
      reader.readAsDataURL(file);
    }
  };

  const sendMessage = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      content: input.trim(),
      role: 'user',
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      // Convert messages to API format
      const apiMessages = messages.concat(userMessage).map(msg => ({
        role: msg.role,
        content: msg.content,
      }));

      const response = await chatWithAI(apiMessages);

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: response.response,
        role: 'assistant',
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Chat error:', error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: 'Sorry, I\'m having trouble responding right now. Please try again.',
        role: 'assistant',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const generateSmartSuggestions = () => {
    const suggestions = [];
    const lastMessage = messages[messages.length - 1];

    if (!lastMessage || messages.length === 0) {
      return [
        "How do I identify my plant?",
        "What's the best soil for houseplants?",
        "Help me create a watering schedule",
        "Show me common plant problems"
      ];
    }

    const content = lastMessage.content.toLowerCase();

    // Context-based suggestions
    if (content.includes('water') || content.includes('watering')) {
      suggestions.push("How often should I water this plant?", "What's the best watering technique?");
    }

    if (content.includes('light') || content.includes('sun') || content.includes('sunlight')) {
      suggestions.push("What's the ideal lighting for this plant?", "Can this plant handle direct sunlight?");
    }

    if (content.includes('problem') || content.includes('issue') || content.includes('sick') || content.includes('dying')) {
      suggestions.push("Help me diagnose this plant problem", "Show me common plant diseases");
    }

    if (content.includes('identify') || content.includes('species') || content.includes('name')) {
      suggestions.push("Can you identify my plant from a photo?", "How do I find my plant's species?");
    }

    if (content.includes('soil') || content.includes('pot') || content.includes('repot')) {
      suggestions.push("What's the best soil type for this plant?", "When should I repot my plant?");
    }

    if (content.includes('fertilizer') || content.includes('feed') || content.includes('nutrients')) {
      suggestions.push("What fertilizer should I use?", "How often should I fertilize?");
    }

    // If no specific context matches, provide general helpful suggestions
    if (suggestions.length === 0) {
      suggestions.push(
        "Show me best soil type",
        "Detect disease from image",
        "Create a care schedule",
        "Check local weather conditions"
      );
    }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const smartSuggestions = generateSmartSuggestions();

  return (
    <div className="flex flex-col h-full max-w-4xl mx-auto">
      {/* Header */}
      <div className="p-4 border-b bg-gradient-to-r from-flourish-green to-flourish-dark text-white rounded-t-lg">
        <div className="flex items-center space-x-3">
          <Avatar className="h-10 w-10">
            <AvatarFallback className="bg-white/20 text-white">🌱</AvatarFallback>
          </Avatar>
          <div>
            <h2 className="text-lg font-semibold">Plant Care Assistant</h2>
            <p className="text-sm opacity-90">Ask me anything about your plants!</p>
          </div>
        </div>
      </div>

      {/* Messages */}
      <ScrollArea className="flex-1 p-4" ref={scrollAreaRef}>
        <div className="space-y-4">
          {messages.length === 0 && (
            <div className="text-center text-muted-foreground py-8">
              <div className="text-4xl mb-2">🌱</div>
              <p>Hi! I'm your plant care assistant. How can I help you today?</p>
            </div>
          )}

          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <Card className={`max-w-[80%] p-3 ${
                message.role === 'user'
                  ? 'bg-flourish-green text-white'
                  : 'bg-muted'
              }`}>
                <div className="flex items-start space-x-2">
                  {message.role === 'assistant' && (
                    <Avatar className="h-6 w-6 flex-shrink-0">
                      <AvatarFallback className="bg-flourish-green text-white text-xs">🤖</AvatarFallback>
                    </Avatar>
                  )}
                  <div className="flex-1">
                    <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                    <p className={`text-xs mt-1 ${
                      message.role === 'user' ? 'text-white/70' : 'text-muted-foreground'
                    }`}>
                      {message.timestamp.toLocaleTimeString()}
                    </p>
                  </div>
                  {message.role === 'user' && (
                    <Avatar className="h-6 w-6 flex-shrink-0">
                      <AvatarFallback className="bg-flourish-dark text-white text-xs">
                        {user?.displayName?.[0] || 'U'}
                      </AvatarFallback>
                    </Avatar>
                  )}
                </div>
              </Card>
            </div>
          ))}

          {isLoading && (
            <div className="flex justify-start">
              <Card className="max-w-[80%] p-3 bg-muted">
                <div className="flex items-center space-x-2">
                  <Avatar className="h-6 w-6">
                    <AvatarFallback className="bg-flourish-green text-white text-xs">🤖</AvatarFallback>
                  </Avatar>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  <span className="text-sm text-muted-foreground">Thinking...</span>
                </div>
              </Card>
            </div>
          )}
        </div>
      </ScrollArea>

      {/* Input Area */}
      <div className="p-4 border-t bg-background">
        <div className="flex items-end space-x-2">
          {/* Image Upload Button */}
          <Button
            variant="outline"
            size="icon"
            onClick={() => fileInputRef.current?.click()}
            className="flex-shrink-0"
          >
            <ImageIcon className="h-4 w-4" />
          </Button>

          {/* Voice Input Button */}
          <Button
            variant={isRecording ? "destructive" : "outline"}
            size="icon"
            onMouseDown={startRecording}
            onMouseUp={stopRecording}
            onMouseLeave={stopRecording}
            className="flex-shrink-0"
          >
            {isRecording ? <MicOff className="h-4 w-4" /> : <Mic className="h-4 w-4" />}
          </Button>

          {/* Text Input */}
          <div className="flex-1 relative">
            <Input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask me about plant care..."
              className="pr-12"
              disabled={isLoading}
            />
          </div>

          {/* Send Button */}
          <Button
            onClick={sendMessage}
            disabled={!input.trim() || isLoading}
            size="icon"
            className="flex-shrink-0"
          >
            {isLoading ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Send className="h-4 w-4" />
            )}
          </Button>
        </div>

        {/* Follow-up Suggestions */}
        {messages.length > 0 && (
          <div className="mt-3 flex flex-wrap gap-2">
            <span className="text-xs text-muted-foreground">Try asking:</span>
            {smartSuggestions.map((suggestion, index) => (
              <Button
                key={index}
                variant="ghost"
                size="sm"
                className="h-6 text-xs"
                onClick={() => setInput(suggestion)}
              >
                {suggestion}
              </Button>
            ))}
          </div>
        )}
      </div>

      {/* Hidden file input */}
      <input
        ref={fileInputRef}
        type="file"
        accept="image/*"
        onChange={handleImageUpload}
        className="hidden"
      />
    </div>
  );
}
