import { Box, Container, CircularProgress, Typography } from '@mui/material';
import { useParams } from 'react-router-dom';
import { useEffect } from 'react';
import { useInterviewStore } from '../features/interview/store/interviewStore';
import { useSendMessage } from '../features/interview/hooks/useSendMessage';
import { useInterviewMessages } from '../features/interview/hooks/useInterview';
import InterviewProgress from '../features/interview/components/InterviewProgress';
import InterviewChat from '../features/interview/components/InterviewChat';
import ChatInput from '../features/interview/components/ChatInput';
import TypingIndicator from '../features/interview/components/TypingIndicator';

/**
 * Interview Page - Text Chat Interface
 * Main page for conducting AI-powered candidate interviews
 */
export default function InterviewPage() {
  const { sessionId } = useParams<{ sessionId: string }>();
  
  const {
    messages,
    isAiTyping,
    currentQuestion,
    totalQuestions,
    setSessionId,
    setStatus,
  } = useInterviewStore();

  const { mutate: sendMessage, isPending } = useSendMessage({
    sessionId: sessionId || '',
  });

  // Fetch interview messages on mount
  const { isLoading, isError, error } = useInterviewMessages(sessionId);

  // Initialize session ID in store (only once when sessionId changes)
  useEffect(() => {
    if (sessionId) {
      setSessionId(sessionId);
      setStatus('in_progress');
    }
  }, [sessionId, setSessionId, setStatus]);

  const handleSendMessage = (messageText: string) => {
    sendMessage(messageText);
  };

  if (!sessionId) {
    return (
      <Container maxWidth="lg">
        <Box
          sx={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            minHeight: '100vh',
            gap: 2,
          }}
          role="alert"
          aria-live="assertive"
        >
          <Box sx={{ textAlign: 'center' }}>
            <Box
              component="h1"
              sx={{ fontSize: '1.5rem', fontWeight: 600, color: 'error.main', mb: 1 }}
            >
              Invalid Interview Session
            </Box>
            <Box component="p" sx={{ color: 'text.secondary' }}>
              No session ID provided. Please return to the interview start page.
            </Box>
          </Box>
        </Box>
      </Container>
    );
  }

  // Show loading state while fetching messages
  if (isLoading) {
    return (
      <Container maxWidth="lg">
        <Box
          sx={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            minHeight: '100vh',
            gap: 2,
          }}
        >
          <CircularProgress />
          <Typography>Loading interview...</Typography>
        </Box>
      </Container>
    );
  }

  // Show error state if fetch failed
  if (isError) {
    return (
      <Container maxWidth="lg">
        <Box
          sx={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            minHeight: '100vh',
            gap: 2,
          }}
        >
          <Typography color="error" variant="h6">
            Failed to load interview
          </Typography>
          <Typography color="text.secondary">
            {error?.message || 'Unknown error occurred'}
          </Typography>
        </Box>
      </Container>
    );
  }

  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        height: '100vh',
        bgcolor: 'grey.100',
      }}
      role="main"
      aria-label="Interview chat interface"
    >
      {/* Progress indicator at top */}
      {totalQuestions > 0 && (
        <Box role="status" aria-live="polite">
          <InterviewProgress current={currentQuestion} total={totalQuestions} />
        </Box>
      )}

      {/* Chat messages */}
      <Box 
        sx={{ flex: 1, overflow: 'hidden' }}
        role="region"
        aria-label="Chat messages"
      >
        <InterviewChat messages={messages} isTyping={isAiTyping} />
        
        {/* Typing indicator */}
        {isAiTyping && (
          <Box sx={{ px: 2 }} role="status" aria-live="polite" aria-label="AI is typing">
            <TypingIndicator isVisible={isAiTyping} />
          </Box>
        )}
      </Box>

      {/* Chat input at bottom */}
      <Box role="region" aria-label="Message input">
        <ChatInput
          onSubmit={handleSendMessage}
          disabled={isPending || isAiTyping}
          placeholder="Type your response..."
        />
      </Box>
    </Box>
  );
}
