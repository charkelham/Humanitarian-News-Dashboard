'use client'

import { useState, useRef, useEffect } from 'react'

interface Message {
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
}

interface ArticleChatProps {
  isOpen: boolean
  onClose: () => void
  contextCountry?: string
}

const SUGGESTED_QUESTIONS = [
  "What is the current humanitarian situation in Sudan?",
  "Latest displacement figures for Syria",
  "Food security crisis in the Horn of Africa",
  "What are the major disease outbreaks right now?",
  "Tell me about humanitarian access in Gaza",
]

export default function ArticleChat({ isOpen, onClose, contextCountry }: ArticleChatProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'assistant',
      content: "Hi! I can help you understand articles, analyze trends, and answer questions about humanitarian crises. What would you like to know?",
      timestamp: new Date(),
    }
  ])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim() || isLoading) return

    const userMessage: Message = {
      role: 'user',
      content: input.trim(),
      timestamp: new Date(),
    }

    setMessages(prev => [...prev, userMessage])
    setInput('')
    setIsLoading(true)

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          question: userMessage.content,
          k: 5,
          filters: contextCountry && contextCountry !== 'all' ? {
            countries: [contextCountry]
          } : undefined
        }),
      })

      if (!response.ok) {
        throw new Error('Failed to get response')
      }

      const data = await response.json()

      // Format response with citations if available
      let responseText = data.answer
      if (data.citations && data.citations.length > 0) {
        responseText += '\n\n**Sources:**\n'
        data.citations.forEach((citation: any, index: number) => {
          responseText += `${index + 1}. [${citation.title}](${citation.url}) - ${citation.source}\n`
        })
      }

      const assistantMessage: Message = {
        role: 'assistant',
        content: responseText,
        timestamp: new Date(),
      }

      setMessages(prev => [...prev, assistantMessage])
    } catch (error) {
      console.error('Chat error:', error)
      const errorMessage: Message = {
        role: 'assistant',
        content: "I'm sorry, I encountered an error. Please try again.",
        timestamp: new Date(),
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const handleSuggestedQuestion = (question: string) => {
    setInput(question)
    // We can't directly call handleSubmit here because it takes an event, 
    // but we can trigger it or just use the same logic. 
    // Simplified: set input and let user send, or create a direct send function.
    // For now, let's make it auto-send.
    const fakeEvent = { preventDefault: () => { } } as React.FormEvent
    setInput(question)
    // Using setTimeout to ensure state is updated before submit logic (basic React state tip)
    setTimeout(() => {
      const form = document.getElementById('chat-form') as HTMLFormElement
      if (form) form.requestSubmit()
    }, 0)
  }

  if (!isOpen) return null

  return (
    <div className="fixed bottom-20 right-6 w-96 max-h-[calc(100vh-140px)] h-[600px] bg-white rounded-lg shadow-2xl border border-gray-200 flex flex-col z-50">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-blue-700 text-white px-4 py-3 rounded-t-lg flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
          <span className="font-semibold">Humanitarian News Assistant</span>
        </div>
        <button
          onClick={onClose}
          className="text-white/80 hover:text-white transition-colors"
          aria-label="Close chat"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message, index) => (
          <div
            key={index}
            className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[80%] rounded-lg px-4 py-2 ${message.role === 'user'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 text-gray-900'
                }`}
            >
              <div className="text-sm whitespace-pre-wrap">
                {message.content.split('\n').map((line, i) => {
                  // Check if line contains a markdown link
                  const linkRegex = /\[([^\]]+)\]\(([^)]+)\)/g
                  const parts = []
                  let lastIndex = 0
                  let match

                  while ((match = linkRegex.exec(line)) !== null) {
                    // Add text before the link
                    if (match.index > lastIndex) {
                      parts.push(line.substring(lastIndex, match.index))
                    }
                    // Add the link
                    parts.push(
                      <a
                        key={`link-${i}-${match.index}`}
                        href={match[2]}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="underline hover:text-blue-600"
                      >
                        {match[1]}
                      </a>
                    )
                    lastIndex = match.index + match[0].length
                  }

                  // Add remaining text
                  if (lastIndex < line.length) {
                    parts.push(line.substring(lastIndex))
                  }

                  return (
                    <div key={i}>
                      {parts.length > 0 ? parts : line}
                    </div>
                  )
                })}
              </div>
              <p className={`text-xs mt-1 ${message.role === 'user' ? 'text-blue-100' : 'text-gray-500'
                }`}>
                {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </p>
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-gray-100 rounded-lg px-4 py-2">
              <div className="flex space-x-2">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
              </div>
            </div>
          </div>
        )}

        {/* Suggested Follow-up Questions */}
        {!isLoading && messages.length > 0 && messages[messages.length - 1].role === 'assistant' && (
          <div className="space-y-2 pt-2 border-t border-gray-100">
            <p className="text-[10px] text-gray-400 mb-1 font-medium uppercase tracking-wider">Suggested Follow-ups:</p>
            <div className="flex flex-wrap gap-2">
              {SUGGESTED_QUESTIONS.map((q, i) => (
                <button
                  key={i}
                  onClick={() => handleSuggestedQuestion(q)}
                  className="text-xs bg-white border border-blue-100 text-blue-600 px-3 py-1.5 rounded-full hover:bg-blue-50 hover:border-blue-200 transition-all text-left shadow-sm"
                >
                  {q}
                </button>
              ))}
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <form id="chat-form" onSubmit={handleSubmit} className="p-4 border-t border-gray-200">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about articles or humanitarian topics..."
            className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={isLoading || !input.trim()}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
            </svg>
          </button>
        </div>
      </form>
    </div>
  )
}
