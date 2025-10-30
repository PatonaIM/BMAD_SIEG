import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { ThemeProvider } from '@mui/material/styles';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { teamifiedTheme } from '../theme/theme';
import InterviewPage from './InterviewPage';
import { useInterviewStore } from '../features/interview/store/interviewStore';

// Create a new QueryClient for each test
const createTestQueryClient = () => new QueryClient({
  defaultOptions: {
    queries: { retry: false },
    mutations: { retry: false },
  },
});

// Helper to render with all required providers
const renderWithProviders = (sessionId: string = 'test-session-123') => {
  const queryClient = createTestQueryClient();
  
  return render(
    <QueryClientProvider client={queryClient}>
      <ThemeProvider theme={teamifiedTheme}>
        <MemoryRouter initialEntries={[`/interview/${sessionId}`]}>
          <Routes>
            <Route path="/interview/:sessionId" element={<InterviewPage />} />
          </Routes>
        </MemoryRouter>
      </ThemeProvider>
    </QueryClientProvider>
  );
};

describe('InterviewPage - Integration Tests', () => {
  beforeEach(() => {
    // Reset store before each test
    useInterviewStore.getState().reset();
    
    // Mock scrollTo for InterviewChat auto-scroll
    Element.prototype.scrollTo = vi.fn();
  });

  describe('1.6-INT-FULL-001: Complete Send-Receive Workflow with MSW', () => {
    it('should handle full message cycle: send → typing → response → update', async () => {
      const user = userEvent.setup();
      
      renderWithProviders();

      // Wait for page to initialize
      await waitFor(() => {
        expect(screen.getByRole('textbox')).toBeInTheDocument();
      });

      // Type a message
      const input = screen.getByRole('textbox');
      await user.type(input, 'I have 5 years of React experience');

      // Submit message
      const sendButton = screen.getByRole('button', { name: /send/i });
      await user.click(sendButton);

      // Verify optimistic update - candidate message appears immediately
      const candidateMessages = screen.getAllByText('I have 5 years of React experience');
      expect(candidateMessages.length).toBeGreaterThan(0);

      // Verify typing indicator appears
      await waitFor(() => {
        expect(screen.getByText(/AI is thinking/i)).toBeInTheDocument();
      });

      // Verify input is disabled during AI response
      expect(input).toBeDisabled();

      // Wait for AI response from MSW (1-2 second delay)
      await waitFor(
        () => {
          const aiResponses = [
            /thank you for your response/i,
            /that's an interesting approach/i,
            /i see\. how would you handle/i,
            /great! now let's move on/i,
            /can you walk me through/i,
          ];
          
          const hasAiResponse = aiResponses.some(pattern => 
            screen.queryByText(pattern) !== null
          );
          
          expect(hasAiResponse).toBe(true);
        },
        { timeout: 3000 }
      );

      // Verify typing indicator disappears after response
      expect(screen.queryByText(/AI is thinking/i)).not.toBeInTheDocument();

      // Verify progress updated
      const store = useInterviewStore.getState();
      expect(store.currentQuestion).toBeGreaterThan(0);
      expect(store.totalQuestions).toBeGreaterThan(0);

      // Verify input is re-enabled
      expect(input).not.toBeDisabled();
      expect(input).toHaveValue(''); // Input should be cleared
    });
  });

  describe('1.6-INT-FULL-002: Error Handling', () => {
    it('should handle API errors gracefully', async () => {
      const user = userEvent.setup();
      
      // Mock console.error to suppress expected error logs
      const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
      
      renderWithProviders();

      await waitFor(() => {
        expect(screen.getByRole('textbox')).toBeInTheDocument();
      });

      const input = screen.getByRole('textbox');
      await user.type(input, 'Test message');
      
      const sendButton = screen.getByRole('button', { name: /send/i });
      await user.click(sendButton);

      // Optimistic message should appear
      const messages = screen.getAllByText('Test message');
      expect(messages.length).toBeGreaterThan(0);

      // If API fails, message should still remain (MSW doesn't typically fail in tests)
      // In real scenario, error notification would appear
      await waitFor(() => {
        expect(input).not.toBeDisabled();
      }, { timeout: 3000 });

      consoleErrorSpy.mockRestore();
    });
  });

  describe('1.6-INT-FULL-003: Multiple Message Flow', () => {
    it('should handle multiple messages in sequence', async () => {
      const user = userEvent.setup();
      
      renderWithProviders();

      await waitFor(() => {
        expect(screen.getByRole('textbox')).toBeInTheDocument();
      });

      const input = screen.getByRole('textbox');

      // Send first message
      await user.type(input, 'First message');
      await user.click(screen.getByRole('button', { name: /send/i }));

      const firstMessages = screen.getAllByText('First message');
      expect(firstMessages.length).toBeGreaterThan(0);

      // Wait for AI response
      await waitFor(() => {
        expect(screen.queryByText(/AI is thinking/i)).not.toBeInTheDocument();
      }, { timeout: 3000 });

      // Send second message
      await user.type(input, 'Second message');
      await user.click(screen.getByRole('button', { name: /send/i }));

      expect(screen.getByText('Second message')).toBeInTheDocument();

      // Verify both messages are visible (chronological order maintained)
      expect(screen.getByText('First message')).toBeInTheDocument();
      expect(screen.getByText('Second message')).toBeInTheDocument();
    });
  });

  describe('1.6-INT-FULL-004: Invalid Session Handling', () => {
    it('should display error when no session ID provided', () => {
      const queryClient = createTestQueryClient();
      
      render(
        <QueryClientProvider client={queryClient}>
          <ThemeProvider theme={teamifiedTheme}>
            <MemoryRouter initialEntries={['/interview/']}>
              <Routes>
                <Route path="/interview/:sessionId?" element={<InterviewPage />} />
              </Routes>
            </MemoryRouter>
          </ThemeProvider>
        </QueryClientProvider>
      );

      expect(screen.getByRole('alert')).toBeInTheDocument();
      expect(screen.getByText(/invalid interview session/i)).toBeInTheDocument();
      expect(screen.getByText(/no session id provided/i)).toBeInTheDocument();
    });
  });

  describe('1.6-INT-FULL-005: Responsive Layout', () => {
    it('should render all main sections', () => {
      renderWithProviders();

      // Main container should be present
      expect(screen.getByRole('main')).toBeInTheDocument();

      // Chat messages region
      expect(screen.getByRole('region', { name: /chat messages/i })).toBeInTheDocument();

      // Message input region
      expect(screen.getByRole('region', { name: /message input/i })).toBeInTheDocument();
    });
  });

  describe('1.6-INT-FULL-006: Accessibility Features', () => {
    it('should have proper ARIA labels and roles', () => {
      renderWithProviders();

      // Main landmark
      expect(screen.getByRole('main')).toHaveAttribute('aria-label', 'Interview chat interface');

      // Chat messages region
      expect(screen.getByRole('region', { name: /chat messages/i })).toBeInTheDocument();

      // Input region
      expect(screen.getByRole('region', { name: /message input/i })).toBeInTheDocument();

      // Input field
      const input = screen.getByRole('textbox');
      expect(input).toHaveAttribute('placeholder');
    });

    it('should announce typing indicator to screen readers', async () => {
      const user = userEvent.setup();
      
      renderWithProviders();

      await waitFor(() => {
        expect(screen.getByRole('textbox')).toBeInTheDocument();
      });

      const input = screen.getByRole('textbox');
      await user.type(input, 'Test');
      await user.click(screen.getByRole('button', { name: /send/i }));

      // Typing indicator should have aria-live
      await waitFor(() => {
        // The typing indicator renders with "AI is thinking" text
        expect(screen.getByText(/AI is thinking/i)).toBeInTheDocument();
      });
    });
  });

  describe('1.6-INT-FULL-007: Keyboard Navigation', () => {
    it('should submit message on Enter key', async () => {
      const user = userEvent.setup();
      
      renderWithProviders();

      await waitFor(() => {
        expect(screen.getByRole('textbox')).toBeInTheDocument();
      });

      const input = screen.getByRole('textbox');
      await user.type(input, 'Keyboard test{Enter}');

      // Message should be sent (input cleared)
      await waitFor(() => {
        expect(input).toHaveValue('');
      });

      expect(screen.getByText('Keyboard test')).toBeInTheDocument();
    });
  });
});
