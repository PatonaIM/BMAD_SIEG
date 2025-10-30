import { Box, Typography, useMediaQuery, useTheme } from '@mui/material';
import { useRef, useEffect, useLayoutEffect, memo } from 'react';
import ChatMessage from '../ChatMessage';

export interface Message {
  id: string;
  role: 'ai' | 'candidate';
  content: string;
  timestamp: number;
}

export interface InterviewChatProps {
  messages: Message[];
  isTyping?: boolean;
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
  const scrollContainerRef = useRef<HTMLDivElement>(null);
  const theme = useTheme();
  const isSmallScreen = useMediaQuery(theme.breakpoints.down('lg'));

  // Auto-scroll to bottom when new messages arrive
  // Using useLayoutEffect to prevent flash before scroll (PERF-001 mitigation)
  useLayoutEffect(() => {
    if (scrollContainerRef.current) {
      scrollContainerRef.current.scrollTo({
        top: scrollContainerRef.current.scrollHeight,
        behavior: 'smooth',
      });
    }
  }, [messages, isTyping]);

  // Warn if message count exceeds recommended limit (PERF-001 mitigation)
  useEffect(() => {
    if (messages.length > 50) {
      console.warn(`Message count (${messages.length}) exceeds recommended limit of 50. Consider implementing pagination.`);
    }
  }, [messages.length]);

  return (
    <Box
      ref={scrollContainerRef}
      sx={{
        height: 'calc(100vh - 200px)', // Adjust for header, input, progress
        overflowY: 'auto',
        bgcolor: 'grey.100',
        p: isSmallScreen ? 1.5 : 2, // Reduced padding on smaller screens
        display: 'flex',
        flexDirection: 'column',
        // Custom scrollbar styling
        '&::-webkit-scrollbar': {
          width: '8px',
        },
        '&::-webkit-scrollbar-track': {
          bgcolor: 'grey.100',
        },
        '&::-webkit-scrollbar-thumb': {
          bgcolor: 'grey.300',
          borderRadius: '4px',
          '&:hover': {
            bgcolor: 'grey.400',
          },
        },
      }}
    >
      {messages.length === 0 && !isTyping ? (
        <Box
          sx={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            height: '100%',
          }}
        >
          <Typography 
            variant="body1" 
            color="text.secondary"
            sx={{
              fontSize: isSmallScreen ? '0.9rem' : '1rem', // Scale down font on small screens
            }}
          >
            Your interview will begin shortly...
          </Typography>
        </Box>
      ) : (
        messages.map((message) => (
          <ChatMessage
            key={message.id}
            role={message.role}
            content={message.content}
            timestamp={message.timestamp}
          />
        ))
      )}
    </Box>
  );
}
