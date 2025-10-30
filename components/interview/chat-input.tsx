"use client"

import { useState, type KeyboardEvent } from "react"
import { Box, TextField, IconButton, CircularProgress } from "@mui/material"
import { Send as SendIcon } from "@mui/icons-material"

export interface ChatInputProps {
  onSendMessage: (message: string) => void
  disabled?: boolean
  isLoading?: boolean
}

/**
 * ChatInput Component
 * Multiline text input with send button
 * Supports Enter to send, Shift+Enter for new line
 */
export default function ChatInput({ onSendMessage, disabled = false, isLoading = false }: ChatInputProps) {
  const [message, setMessage] = useState("")

  const handleSend = () => {
    const trimmedMessage = message.trim()
    if (trimmedMessage && !disabled && !isLoading) {
      onSendMessage(trimmedMessage)
      setMessage("")
    }
  }

  const handleKeyDown = (e: KeyboardEvent<HTMLDivElement>) => {
    // Send on Enter (without Shift)
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <Box
      sx={{
        position: "sticky",
        bottom: 0,
        bgcolor: "background.paper",
        p: 2,
        borderTop: "1px solid",
        borderColor: "grey.300",
        display: "flex",
        gap: 1,
        alignItems: "flex-end",
      }}
    >
      <TextField
        fullWidth
        multiline
        maxRows={4}
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Type your answer here..."
        disabled={disabled || isLoading}
        variant="outlined"
        sx={{
          "& .MuiOutlinedInput-root": {
            bgcolor: "background.default",
          },
        }}
      />
      <IconButton
        color="primary"
        onClick={handleSend}
        disabled={!message.trim() || disabled || isLoading}
        sx={{
          bgcolor: "primary.main",
          color: "white",
          "&:hover": {
            bgcolor: "primary.dark",
          },
          "&.Mui-disabled": {
            bgcolor: "grey.300",
            color: "grey.500",
          },
        }}
      >
        {isLoading ? <CircularProgress size={24} color="inherit" /> : <SendIcon />}
      </IconButton>
    </Box>
  )
}
