import { Box, TextField, Button, Typography, CircularProgress, useMediaQuery, useTheme } from '@mui/material';
import { Send as SendIcon } from '@mui/icons-material';
import { useState, useRef, useEffect } from 'react';
import type { KeyboardEvent } from 'react';

export interface ChatInputProps {
  onSubmit: (message: string) => void;
  disabled?: boolean;
  placeholder?: string;
}

const MAX_CHARACTERS = 2000;

/**
 * ChatInput Component
 * Multiline text input with character counter and submit button
 * - Enter key submits message
 * - Shift+Enter creates new line
 * - Responsive design for different screen sizes
 * - Full accessibility support
 */
export default function ChatInput({
  onSubmit,
  disabled = false,
  placeholder = 'Type your response...',
}: ChatInputProps) {
  const [message, setMessage] = useState('');
  const inputRef = useRef<HTMLInputElement>(null);
  const theme = useTheme();
  const isSmallScreen = useMediaQuery(theme.breakpoints.down('lg'));

  const charCount = message.length;
  const isOverLimit = charCount > MAX_CHARACTERS;
  const isEmpty = message.trim().length === 0;
  const isSubmitDisabled = disabled || isEmpty || isOverLimit;

  // Return focus to input after message sent
  useEffect(() => {
    if (!disabled && inputRef.current) {
      inputRef.current.focus();
    }
  }, [disabled]);

  const handleSubmit = () => {
    if (isSubmitDisabled) return;

    const trimmedMessage = message.trim();
    if (trimmedMessage) {
      onSubmit(trimmedMessage);
      setMessage('');
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLDivElement>) => {
    // Submit on Enter (without Shift)
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
    // Allow Shift+Enter for new line (default behavior)
  };

  return (
    <Box
      sx={{
        p: isSmallScreen ? 1.5 : 2,
        bgcolor: 'background.paper',
        borderTop: '1px solid',
        borderColor: 'grey.300',
        display: 'flex',
        gap: isSmallScreen ? 1 : 2,
        alignItems: 'flex-end',
      }}
      component="form"
      onSubmit={(e) => {
        e.preventDefault();
        handleSubmit();
      }}
    >
      <Box sx={{ flex: 1 }}>
        <TextField
          inputRef={inputRef}
          fullWidth
          multiline
          maxRows={5}
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          disabled={disabled}
          aria-label="Interview response input"
          aria-describedby="char-count-label keyboard-hint-label"
          inputProps={{
            'aria-required': 'true',
            'aria-invalid': isOverLimit,
          }}
          sx={{
            '& .MuiOutlinedInput-root': {
              bgcolor: disabled ? 'grey.100' : 'background.paper',
              fontSize: isSmallScreen ? '0.9rem' : '1rem',
              '&:focus-within': {
                outline: `2px solid ${theme.palette.primary.main}`,
                outlineOffset: '2px',
              },
            },
          }}
        />
        <Box
          sx={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            mt: 0.5,
            px: 1,
            flexDirection: isSmallScreen ? 'column' : 'row',
            gap: isSmallScreen ? 0.5 : 0,
          }}
        >
          <Typography
            id="char-count-label"
            variant="caption"
            color={isOverLimit ? 'error' : 'text.secondary'}
            sx={{
              fontSize: isSmallScreen ? '0.65rem' : '0.75rem',
            }}
            role="status"
            aria-live="polite"
          >
            {charCount}/{MAX_CHARACTERS} characters
          </Typography>
          {!isSmallScreen && (
            <Typography 
              id="keyboard-hint-label"
              variant="caption" 
              color="text.secondary"
              aria-label="Keyboard shortcuts"
            >
              Press Enter to send, Shift+Enter for new line
            </Typography>
          )}
        </Box>
      </Box>

      <Button
        type="submit"
        variant="contained"
        color="primary"
        onClick={handleSubmit}
        disabled={isSubmitDisabled}
        endIcon={
          disabled ? (
            <CircularProgress size={20} color="inherit" />
          ) : (
            <SendIcon />
          )
        }
        aria-label={disabled ? 'Sending message...' : 'Send message'}
        sx={{
          minWidth: isSmallScreen ? '90px' : '120px',
          height: '56px',
          fontSize: isSmallScreen ? '0.875rem' : '1rem',
          '&:focus-visible': {
            outline: `3px solid ${theme.palette.primary.main}`,
            outlineOffset: '2px',
          },
        }}
      >
        Send
      </Button>
    </Box>
  );
}
