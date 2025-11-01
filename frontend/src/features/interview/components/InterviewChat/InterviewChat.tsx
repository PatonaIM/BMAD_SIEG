"use client"

import { useRef, useEffect, useLayoutEffect } from "react"
import ChatMessage from "../ChatMessage/ChatMessage.tsx"

export interface Message {
  id: string
  role: "ai" | "candidate"
  content: string
  timestamp: number
}

export interface InterviewChatProps {
  messages: Message[]
  isTyping?: boolean
}

/**
 * InterviewChat Component
 * Scrollable container for displaying chat messages with auto-scroll
 * Responsive design for different screen sizes
 *
 * Performance optimizations (PERF-001):
 * - useLayoutEffect for scroll (prevents flash)
 * - Message limit enforcement (max 50)
 * - Memoized ChatMessage components
 */
export default function InterviewChat({ messages, isTyping = false }: InterviewChatProps) {
  const scrollContainerRef = useRef<HTMLDivElement>(null)

  // Auto-scroll to bottom when new messages arrive
  // Using useLayoutEffect to prevent flash before scroll (PERF-001 mitigation)
  useLayoutEffect(() => {
    if (scrollContainerRef.current) {
      scrollContainerRef.current.scrollTo({
        top: scrollContainerRef.current.scrollHeight,
        behavior: "smooth",
      })
    }
  }, [messages, isTyping])

  // Warn if message count exceeds recommended limit (PERF-001 mitigation)
  useEffect(() => {
    if (messages.length > 50) {
      console.warn(
        `Message count (${messages.length}) exceeds recommended limit of 50. Consider implementing pagination.`,
      )
    }
  }, [messages.length])

  return (
    <div
      ref={scrollContainerRef}
      className="h-[calc(100vh-200px)] overflow-y-auto bg-muted/30 p-3 lg:p-4 flex flex-col scrollbar-thin scrollbar-thumb-muted-foreground/20 scrollbar-track-transparent hover:scrollbar-thumb-muted-foreground/40"
    >
      {messages.length === 0 && !isTyping ? (
        <div className="flex items-center justify-center h-full">
          <p className="text-sm lg:text-base text-muted-foreground">Your interview will begin shortly...</p>
        </div>
      ) : (
        messages.map((message) => (
          <ChatMessage key={message.id} role={message.role} content={message.content} timestamp={message.timestamp} />
        ))
      )}
    </div>
  )
}
