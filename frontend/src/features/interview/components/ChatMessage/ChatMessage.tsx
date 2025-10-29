import { Box, Typography, Avatar, useMediaQuery, useTheme } from '@mui/material';
import { SmartToy as AIIcon } from '@mui/icons-material';
import { memo } from 'react';

export interface ChatMessageProps {
  role: 'ai' | 'candidate';
  content: string;
  timestamp: number;
}

/**
 * ChatMessage Component
 * Displays a single message bubble in the interview chat
 * - AI messages: Left-aligned, brand purple background, white text
 * - Candidate messages: Right-aligned, light grey background, dark text
 * - Responsive design for different screen sizes
 * - Full accessibility support
 * - Memoized for performance optimization (PERF-001)
 */
const ChatMessage = memo(function ChatMessage({ role, content, timestamp }: ChatMessageProps) {
  const isAI = role === 'ai';
  const theme = useTheme();
  const isSmallScreen = useMediaQuery(theme.breakpoints.down('lg'));
  
  // Format timestamp as HH:mm AM/PM
  const formatTime = (ts: number) => {
    const date = new Date(ts);
    return date.toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      hour12: true,
    });
  };

  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: isAI ? 'row' : 'row-reverse',
        alignItems: 'flex-start',
        gap: 1,
        mb: 2,
      }}
      role="article"
      aria-label={`${isAI ? 'AI interviewer' : 'Your'} message at ${formatTime(timestamp)}`}
    >
      {/* Avatar - only show for AI messages */}
      {isAI && (
        <Avatar
          sx={{
            bgcolor: 'primary.main',
            width: isSmallScreen ? 36 : 40,
            height: isSmallScreen ? 36 : 40,
          }}
          aria-label="AI interviewer avatar"
        >
          <AIIcon sx={{ fontSize: isSmallScreen ? 18 : 20 }} />
        </Avatar>
      )}

      {/* Message bubble */}
      <Box
        sx={{
          maxWidth: isSmallScreen ? '80%' : '70%',
          display: 'flex',
          flexDirection: 'column',
          gap: 0.5,
        }}
      >
        <Box
          sx={{
            bgcolor: isAI ? 'primary.main' : 'grey.200',
            color: isAI ? 'primary.contrastText' : 'text.primary',
            px: isSmallScreen ? 1.5 : 2,
            py: isSmallScreen ? 1 : 1.5,
            borderRadius: '8px',
            wordBreak: 'break-word',
          }}
        >
          <Typography 
            variant="body1"
            sx={{
              fontSize: isSmallScreen ? '0.9rem' : '1rem',
            }}
            component="p"
          >
            {content}
          </Typography>
        </Box>

        {/* Timestamp */}
        <Typography
          variant="caption"
          color="text.secondary"
          sx={{
            alignSelf: isAI ? 'flex-start' : 'flex-end',
            px: 1,
            fontSize: isSmallScreen ? '0.65rem' : '0.75rem',
          }}
          component="time"
          dateTime={new Date(timestamp).toISOString()}
        >
          {formatTime(timestamp)}
        </Typography>
      </Box>
    </Box>
  );
});

export default ChatMessage;
