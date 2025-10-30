import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { ThemeProvider } from '@mui/material/styles';
import { teamifiedTheme } from '../../../../theme/theme';
import ChatMessage from './ChatMessage';

const renderWithTheme = (component: React.ReactElement) =>
  render(<ThemeProvider theme={teamifiedTheme}>{component}</ThemeProvider>);

describe('ChatMessage', () => {
  const mockTimestamp = new Date('2025-10-30T14:30:00').getTime();

  it('renders AI message with correct styling', () => {
    renderWithTheme(
      <ChatMessage
        role="ai"
        content="Hello, let's start the interview!"
        timestamp={mockTimestamp}
      />
    );

    expect(screen.getByText("Hello, let's start the interview!")).toBeInTheDocument();
    expect(screen.getByText(/2:30 PM/i)).toBeInTheDocument();
  });

  it('renders candidate message with correct styling', () => {
    renderWithTheme(
      <ChatMessage
        role="candidate"
        content="I'm ready to begin!"
        timestamp={mockTimestamp}
      />
    );

    expect(screen.getByText("I'm ready to begin!")).toBeInTheDocument();
    expect(screen.getByText(/2:30 PM/i)).toBeInTheDocument();
  });

  it('shows avatar icon for AI messages only', () => {
    const { container, rerender } = renderWithTheme(
      <ChatMessage
        role="ai"
        content="AI message"
        timestamp={mockTimestamp}
      />
    );

    // AI message should have an avatar with icon
    expect(container.querySelector('[data-testid="SmartToyIcon"]')).toBeInTheDocument();

    // Candidate message should not have an avatar
    rerender(
      <ThemeProvider theme={teamifiedTheme}>
        <ChatMessage
          role="candidate"
          content="Candidate message"
          timestamp={mockTimestamp}
        />
      </ThemeProvider>
    );

    expect(container.querySelector('[data-testid="SmartToyIcon"]')).not.toBeInTheDocument();
  });

  it('formats timestamp correctly', () => {
    const morningTime = new Date('2025-10-30T09:15:00').getTime();
    renderWithTheme(
      <ChatMessage
        role="ai"
        content="Morning message"
        timestamp={morningTime}
      />
    );

    expect(screen.getByText(/9:15 AM/i)).toBeInTheDocument();
  });

  it('handles long content with word wrapping', () => {
    const longContent = 'This is a very long message that should wrap properly within the message bubble without breaking the layout or causing overflow issues in the chat interface.';
    
    renderWithTheme(
      <ChatMessage
        role="candidate"
        content={longContent}
        timestamp={mockTimestamp}
      />
    );

    expect(screen.getByText(longContent)).toBeInTheDocument();
  });

  describe('XSS Protection (SEC-002)', () => {
    it('should escape HTML script tags in message content', () => {
      const xssPayload = '<script>alert("XSS")</script>Hello';
      
      const { container } = renderWithTheme(
        <ChatMessage
          role="ai"
          content={xssPayload}
          timestamp={mockTimestamp}
        />
      );

      // React should escape the script tag - it should appear as text, not execute
      expect(screen.getByText(/<script>alert\("XSS"\)<\/script>Hello/)).toBeInTheDocument();
      
      // Verify no actual script tags are in the DOM
      expect(container.querySelector('script')).not.toBeInTheDocument();
    });

    it('should escape HTML entities in message content', () => {
      const htmlEntities = 'Test <b>bold</b> and <i>italic</i> tags';
      
      const { container } = renderWithTheme(
        <ChatMessage
          role="candidate"
          content={htmlEntities}
          timestamp={mockTimestamp}
        />
      );

      // React should render HTML as text, not as actual HTML
      expect(screen.getByText(/Test <b>bold<\/b> and <i>italic<\/i> tags/)).toBeInTheDocument();
      
      // Verify no bold or italic tags actually rendered
      expect(container.querySelector('b')).not.toBeInTheDocument();
      expect(container.querySelector('i')).not.toBeInTheDocument();
    });

    it('should handle special characters safely', () => {
      const specialChars = 'Test & < > " \' characters';
      
      renderWithTheme(
        <ChatMessage
          role="ai"
          content={specialChars}
          timestamp={mockTimestamp}
        />
      );

      // All special characters should be rendered as text
      expect(screen.getByText(/Test & < > " ' characters/)).toBeInTheDocument();
    });

    it('should not execute onclick or onerror attributes', () => {
      const maliciousContent = '<img src="x" onerror="alert(\'XSS\')">';
      
      const { container } = renderWithTheme(
        <ChatMessage
          role="candidate"
          content={maliciousContent}
          timestamp={mockTimestamp}
        />
      );

      // Content should be text, not actual img tag
      expect(screen.getByText(/<img src="x" onerror="alert\('XSS'\)">/)).toBeInTheDocument();
      
      // Verify no img tag in DOM
      expect(container.querySelector('img:not([src*="data:image"])')).not.toBeInTheDocument();
    });
  });
});
