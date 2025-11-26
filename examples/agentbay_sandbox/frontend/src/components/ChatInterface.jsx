import React, { useState, useRef, useEffect } from 'react'
import MessageList from './MessageList'
import InputBox from './InputBox'
import './ChatInterface.css'

function ChatInterface({ onToolCall, onSandboxResource }) {
  const [messages, setMessages] = useState([])
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef(null)
  const eventSourceRef = useRef(null)
  const cleanupEventSource = () => {
    const current = eventSourceRef.current
    if (current) {
      if (current._sandboxResourceHandler) {
        current.removeEventListener(
          'sandbox_resource',
          current._sandboxResourceHandler
        )
      }
      current.close()
      eventSourceRef.current = null
    }
  }

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  // Cleanup EventSource on unmount
  useEffect(() => {
    return () => {
      cleanupEventSource()
    }
  }, [])

  const handleSendMessage = async (message) => {
    if (!message.trim()) return

    // Close previous EventSource if exists
    cleanupEventSource()

    // Add user message
    const userMessage = {
      id: Date.now(),
      role: 'user',
      content: message,
      timestamp: new Date(),
    }
    setMessages((prev) => [...prev, userMessage])
    setIsLoading(true)

    try {
      // Use SSE (Server-Sent Events) for streaming
      const encodedMessage = encodeURIComponent(message)
      const eventSource = new EventSource(
        `/api/chat/stream?message=${encodedMessage}`
      )
      const handleResourceEvent = (event) => {
        if (!onSandboxResource) {
          return
        }
        try {
          const payload = JSON.parse(event.data)
          onSandboxResource(payload)
        } catch (err) {
          console.error('Failed to parse sandbox resource event:', err)
        }
      }
      eventSource.addEventListener('sandbox_resource', handleResourceEvent)
      eventSource._sandboxResourceHandler = handleResourceEvent
      eventSourceRef.current = eventSource

      const assistantMessageId = Date.now() + 1
      let assistantMessage = {
        id: assistantMessageId,
        role: 'assistant',
        content: '',
        timestamp: new Date(),
      }
      setMessages((prev) => [...prev, assistantMessage])

      eventSource.onmessage = (event) => {
        const data = event.data

        if (data === '[DONE]') {
          cleanupEventSource()
          setIsLoading(false)
          if (onToolCall) {
            onToolCall()
          }
        } else if (data.startsWith('Error:')) {
          cleanupEventSource()
          setIsLoading(false)
          setMessages((prev) => {
            // 创建新数组和新对象，确保 React 检测到变化
            const updated = prev.map((msg) => {
              if (msg.id === assistantMessageId && msg.role === 'assistant') {
                return {
                  ...msg,
                  content: msg.content + `\n\n${data}`,
                }
              }
              return msg
            })
            return updated
          })
        } else if (data) {
          // Append chunk to assistant message
          // 使用函数式更新，确保每次都是新的对象引用
          setMessages((prev) => {
            // 创建新数组，最后一个消息创建新对象
            const updated = prev.map((msg) => {
              if (msg.id === assistantMessageId && msg.role === 'assistant') {
                return {
                  ...msg,
                  content: msg.content + data,
                }
              }
              return msg
            })
            return updated
          })
        }
      }

      eventSource.onerror = (error) => {
        console.error('SSE error:', error)
        // Only close if connection is actually closed
        if (eventSource.readyState === EventSource.CLOSED) {
          cleanupEventSource()
          setIsLoading(false)
          setMessages((prev) => {
            // 创建新数组和新对象，确保 React 检测到变化
            const updated = prev.map((msg) => {
              if (msg.id === assistantMessageId && msg.role === 'assistant') {
                const errorMsg = !msg.content
                  ? 'Error: Connection failed'
                  : msg.content + '\n\nError: Connection failed'
                return {
                  ...msg,
                  content: errorMsg,
                }
              }
              return msg
            })
            return updated
          })
        }
      }
    } catch (error) {
      console.error('Error sending message:', error)
      setIsLoading(false)
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now() + 2,
          role: 'assistant',
          content: `Error: ${error.message}`,
          timestamp: new Date(),
        },
      ])
    }
  }

  return (
    <div className="chat-interface">
      <div className="chat-header">
        <h2>Chat</h2>
      </div>
      <MessageList messages={messages} isLoading={isLoading} />
      <InputBox onSendMessage={handleSendMessage} disabled={isLoading} />
    </div>
  )
}

export default ChatInterface
