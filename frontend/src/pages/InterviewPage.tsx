import { Box, Container } from '@mui/material';
import { useParams } from 'react-router-dom';
import { useEffect } from 'react';
import { useInterviewStore } from '../features/interview/store/interviewStore';
import { useSendMessage } from '../features/interview/hooks/useSendMessage';
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

  // Initialize session on mount
  useEffect(() => {
    if (sessionId) {
      setSessionId(sessionId);
      setStatus('in_progress');
      
      // TODO: In Story 1.7, fetch initial interview state from API
      // For now, we'll start with an initial AI greeting
      // This would normally come from the backend
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
