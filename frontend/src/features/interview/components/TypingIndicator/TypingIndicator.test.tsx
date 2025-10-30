import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { ThemeProvider } from '@mui/material/styles';
import { teamifiedTheme } from '../../../../theme/theme';
import TypingIndicator from './TypingIndicator';

const renderWithTheme = (component: React.ReactElement) =>
  render(<ThemeProvider theme={teamifiedTheme}>{component}</ThemeProvider>);

describe('TypingIndicator', () => {
  it('renders when isVisible is true', () => {
    const { container } = renderWithTheme(<TypingIndicator isVisible={true} />);
    
    // Check for the typing bubble container
    expect(container.querySelector('[class*="MuiBox"]')).toBeInTheDocument();
  });

  it('does not render when isVisible is false', () => {
    const { container } = renderWithTheme(<TypingIndicator isVisible={false} />);
    
    // Component should not render anything
    expect(container.firstChild).toBeNull();
  });

  it('renders by default when no isVisible prop provided', () => {
    const { container } = renderWithTheme(<TypingIndicator />);
    
    expect(container.querySelector('[class*="MuiBox"]')).toBeInTheDocument();
  });

  it('includes accessible text for screen readers', () => {
    renderWithTheme(<TypingIndicator isVisible={true} />);
    
    expect(screen.getByText('AI is thinking...')).toBeInTheDocument();
  });

  it('renders AI avatar icon', () => {
    const { container } = renderWithTheme(<TypingIndicator isVisible={true} />);
    
    // Check for avatar icon by data-testid
    expect(container.querySelector('[data-testid="SmartToyIcon"]')).toBeInTheDocument();
  });

  it('renders three animated dots', () => {
    const { container } = renderWithTheme(<TypingIndicator isVisible={true} />);
    
    // Check for styled dots (span elements with the Dot class from styled components)
    const allSpans = container.querySelectorAll('span');
    // Should have at least 3 dot spans plus the screen reader text span
    expect(allSpans.length).toBeGreaterThanOrEqual(4);
  });
});
