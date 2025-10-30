import { Box, Avatar } from '@mui/material';
import { SmartToy as AIIcon } from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';
import { styled, keyframes } from '@mui/material/styles';

export interface TypingIndicatorProps {
  isVisible?: boolean;
}

// Keyframe animation for typing dots
const bounce = keyframes`
  0%, 60%, 100% {
    transform: translateY(0);
  }
  30% {
    transform: translateY(-8px);
  }
`;

const Dot = styled('span')(({ theme }) => ({
  width: 8,
  height: 8,
  borderRadius: '50%',
  backgroundColor: theme.palette.primary.main,
  display: 'inline-block',
  margin: '0 2px',
  animation: `${bounce} 1.4s infinite ease-in-out`,
  '&:nth-of-type(1)': {
    animationDelay: '0s',
  },
  '&:nth-of-type(2)': {
    animationDelay: '0.2s',
  },
  '&:nth-of-type(3)': {
    animationDelay: '0.4s',
  },
}));

/**
 * TypingIndicator Component
 * Shows animated dots to indicate AI is generating a response
 * - Left-aligned like AI messages
 * - Smooth enter/exit animations with Framer Motion
 */
export default function TypingIndicator({ isVisible = true }: TypingIndicatorProps) {
  if (!isVisible) return null;

  return (
    <AnimatePresence>
      {isVisible && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -10 }}
          transition={{ duration: 0.25 }}
        >
          <Box
            sx={{
              display: 'flex',
              alignItems: 'flex-start',
              gap: 1,
              mb: 2,
            }}
          >
            {/* AI Avatar */}
            <Avatar
              sx={{
                bgcolor: 'primary.main',
                width: 40,
                height: 40,
              }}
            >
              <AIIcon />
            </Avatar>

            {/* Typing bubble */}
            <Box
              sx={{
                bgcolor: 'primary.main',
                px: 2,
                py: 1.5,
                borderRadius: '8px',
                display: 'flex',
                alignItems: 'center',
                gap: 0.5,
                minWidth: 70,
              }}
            >
              <Dot />
              <Dot />
              <Dot />
              {/* Hidden text for screen readers */}
              <Box
                component="span"
                sx={{
                  position: 'absolute',
                  left: -10000,
                  width: 1,
                  height: 1,
                  overflow: 'hidden',
                }}
              >
                AI is thinking...
              </Box>
            </Box>
          </Box>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
