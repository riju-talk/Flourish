import React, { useState, useCallback } from 'react'
import { useAuth } from '@/hooks/useAuth'
import { useMutation } from '@tanstack/react-query'
import ReactMarkdown from 'react-markdown'
import { chatWithAI, analyzeImage } from '@/integrations/api'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Loader2, Send, Camera, Brain, Sparkles } from 'lucide-react'

interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
  image_url?: string
}

const QUICK_QUESTIONS = [
  'How are my plants doing today?',
  'What should I focus on this week?',
  'Help me identify this plant issue',
  'Create a care schedule for my new plant',
  'Why are my plant leaves turning yellow?',
  'What fertilizer should I use?',
] as const

const AIAssistant: React.FC = () => {
  const { user } = useAuth()
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      role: 'assistant',
      content: '🧠 Hello! I\'m PlantMind, your AI plant care agent. I can help you with plant health analysis, care schedules, problem diagnosis, and much more. How can I assist you today?',
      timestamp: new Date()
    }
  ])
  const [inputMessage, setInputMessage] = useState('')
  const [selectedImage, setSelectedImage] = useState<string | null>(null)

  // Chat mutation
  const chatMutation = useMutation({
    mutationFn: (newMessages: ChatMessage[]) => chatWithAI(newMessages),
    onSuccess: (data) => {
      const aiMessage: ChatMessage = {
        role: 'assistant',
        content: data.response,
        timestamp: new Date()
      }
      setMessages(prev => [...prev, aiMessage])
    },
    onError: () => {
      const errorMessage: ChatMessage = {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date()
      }
      setMessages(prev => [...prev, errorMessage])
    }
  })

  // Image analysis mutation
  const imageMutation = useMutation({
    mutationFn: (imageData: string) => analyzeImage(imageData),
    onSuccess: (data) => {
      const analysisMessage: ChatMessage = {
        role: 'assistant',
        content: `🔍 **Image Analysis Results:**\n\n**Health Assessment:** ${data.health_assessment}\n\n**Recommendations:**\n${data.recommendations.map((rec: string) => `• ${rec}`).join('\n')}\n\n**Confidence:** ${(data.confidence * 100).toFixed(0)}%`,
        timestamp: new Date()
      }
      setMessages(prev => [...prev, analysisMessage])
    }
  })

  const handleSend = useCallback(() => {
    if (!inputMessage.trim() && !selectedImage) return

    const userMessage: ChatMessage = {
      role: 'user',
      content: inputMessage.trim() || 'Please analyze this image',
      timestamp: new Date(),
      image_url: selectedImage || undefined
    }

    setMessages(prev => [...prev, userMessage])

    if (selectedImage) {
      imageMutation.mutate(selectedImage)
      setSelectedImage(null)
    } else {
      const allMessages = [...messages, userMessage]
      chatMutation.mutate(allMessages)
    }

    setInputMessage('')
  }, [inputMessage, selectedImage, messages, chatMutation, imageMutation])

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent<HTMLInputElement>) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault()
        handleSend()
      }
    },
    [handleSend]
  )

  const handleQuick = useCallback((question: string) => {
    setInputMessage(question)
    setTimeout(() => {
      const userMessage: ChatMessage = {
        role: 'user',
        content: question,
        timestamp: new Date()
      }
      setMessages(prev => [...prev, userMessage])
      chatMutation.mutate([...messages, userMessage])
    }, 50)
  }, [messages, chatMutation])

  const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      const reader = new FileReader()
      reader.onload = (event) => {
        setSelectedImage(event.target?.result as string)
      }
      reader.readAsDataURL(file)
    }
  }

  const isLoading = chatMutation.isPending || imageMutation.isPending

  return (
    <Card className="max-w-4xl mx-auto mt-8 bg-white/80 backdrop-blur-sm border-emerald-200">
      <CardHeader className="bg-gradient-to-r from-emerald-500 to-teal-500 text-white rounded-t-lg">
        <CardTitle className="flex items-center space-x-2">
          <Brain className="w-6 h-6" />
          <span>PlantMind AI Assistant</span>
          <Sparkles className="w-5 h-5 text-emerald-200" />
        </CardTitle>
        <p className="text-emerald-100">Proactive plant care with advanced AI analysis</p>
      </CardHeader>
      <CardContent className="p-0">
        {/* Chat window */}
        <div className="h-96 overflow-y-auto p-6 space-y-4 bg-gradient-to-b from-emerald-50/30 to-teal-50/30">
          {messages.map((msg, index) => (
            <div
              key={index}
              className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[80%] px-4 py-3 rounded-lg ${
                  msg.role === 'user'
                    ? 'bg-gradient-to-r from-emerald-500 to-teal-500 text-white'
                    : 'bg-white border border-emerald-200 shadow-sm'
                }`}
              >
                {msg.image_url && (
                  <img 
                    src={msg.image_url} 
                    alt="Uploaded plant" 
                    className="max-w-full h-32 object-cover rounded mb-2"
                  />
                )}
                <ReactMarkdown className="prose prose-sm max-w-none">
                  {msg.content}
                </ReactMarkdown>
                <div className={`text-xs mt-2 ${
                  msg.role === 'user' ? 'text-emerald-100' : 'text-gray-500'
                }`}>
                  {msg.timestamp.toLocaleTimeString()}
                </div>
              </div>
            </div>
          ))}

          {/* Loading indicator */}
          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-white border border-emerald-200 px-4 py-3 rounded-lg flex items-center space-x-2 shadow-sm">
                <Loader2 className="h-4 w-4 animate-spin text-emerald-500" />
                <span className="text-sm text-gray-500">PlantMind is thinking...</span>
              </div>
            </div>
          )}
        </div>

        {/* Image preview */}
        {selectedImage && (
          <div className="px-6 py-2 bg-emerald-50 border-t border-emerald-200">
            <div className="flex items-center space-x-2">
              <img src={selectedImage} alt="Selected" className="w-12 h-12 object-cover rounded" />
              <span className="text-sm text-emerald-700">Image ready for analysis</span>
              <Button 
                size="sm" 
                variant="ghost" 
                onClick={() => setSelectedImage(null)}
                className="text-emerald-600 hover:text-emerald-700"
              >
                Remove
              </Button>
            </div>
          </div>
        )}

        {/* Input area */}
        <div className="p-6 border-t border-emerald-200 bg-white">
          <div className="flex gap-2 mb-4">
            <Input
              placeholder="Ask PlantMind anything about your plants..."
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyDown={handleKeyDown}
              className="flex-1 border-emerald-200 focus:border-emerald-400"
              disabled={isLoading}
            />
            <input
              type="file"
              accept="image/*"
              onChange={handleImageUpload}
              className="hidden"
              id="image-upload"
            />
            <Button
              variant="outline"
              size="icon"
              onClick={() => document.getElementById('image-upload')?.click()}
              disabled={isLoading}
              className="border-emerald-200 hover:bg-emerald-50"
            >
              <Camera className="h-4 w-4" />
            </Button>
            <Button
              onClick={handleSend}
              disabled={(!inputMessage.trim() && !selectedImage) || isLoading}
              size="icon"
              className="bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-600 hover:to-teal-600"
            >
              {isLoading ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Send className="h-4 w-4" />
              )}
            </Button>
          </div>

          {/* Quick Questions */}
          <div className="flex flex-wrap gap-2">
            {QUICK_QUESTIONS.map((question, index) => (
              <Button
                key={index}
                variant="outline"
                size="sm"
                onClick={() => handleQuick(question)}
                disabled={isLoading}
                className="text-xs border-emerald-200 hover:bg-emerald-50 hover:border-emerald-300"
              >
                {question}
              </Button>
            ))}
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

export default AIAssistant