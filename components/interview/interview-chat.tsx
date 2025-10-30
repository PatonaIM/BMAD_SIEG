"use client"

import { Box, Typography, useMediaQuery, useTheme } from "@mui/material"
import { useRef, useLayoutEffect } from "react"
import ChatMessage from "./chat-message"

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
 */
export default function InterviewChat({ messages, isTyping = false }: InterviewChatProps) {
  const scrollContainerRef = useRef<HTMLDivElement>(null)
  const theme = useTheme()
  const isSmallScreen = useMediaQuery(theme.breakpoints.down("lg"))

  // Auto-scroll to bottom when new messages arrive
  useLayoutEffect(() => {
    if (scrollContainerRef.current) {
      scrollContainerRef.current.scrollTo({
        top: scrollContainerRef.current.scrollHeight,
        behavior: "smooth",
      })
    }
  }, [messages, isTyping])

  return (
    <Box
      ref={scrollContainerRef}
      sx={{
        height: "calc(100vh - 200px)",
        overflowY: "auto",
        bgcolor: "grey.100",
        p: isSmallScreen ? 1.5 : 2,
        display: "flex",
        flexDirection: "column",
        "&::-webkit-scrollbar": {
          width: "8px",
        },
        "&::-webkit-scrollbar-track": {
          bgcolor: "grey.100",
        },
        "&::-webkit-scrollbar-thumb": {
          bgcolor: "grey.300",
          borderRadius: "4px",
          "&:hover": {
            bgcolor: "grey.400",
          },
        },
      }}
    >
      {messages.length === 0 && !isTyping ? (
        <Box
          sx={{
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            height: "100%",
          }}
        >
          <Typography
            variant="body1"
            color="text.secondary"
            sx={{
              fontSize: isSmallScreen ? "0.9rem" : "1rem",
            }}
          >
            Your interview will begin shortly...
          </Typography>
        </Box>
      ) : (
        messages.map((message) => (
          <ChatMessage key={message.id} role={message.role} content={message.content} timestamp={message.timestamp} />
        ))
      )}
    </Box>
  )
}
