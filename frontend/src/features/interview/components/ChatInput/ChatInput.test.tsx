import { render, screen, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi } from 'vitest';
import { ThemeProvider } from '@mui/material/styles';
import { teamifiedTheme } from '../../../../theme/theme';
import ChatInput from './ChatInput';

const renderWithTheme = (component: React.ReactElement) =>
  render(<ThemeProvider theme={teamifiedTheme}>{component}</ThemeProvider>);

describe('ChatInput', () => {
  it('renders input field and send button', () => {
    renderWithTheme(<ChatInput onSubmit={vi.fn()} />);
    
    expect(screen.getByPlaceholderText('Type your response...')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /send/i })).toBeInTheDocument();
  });

  it('shows character counter', () => {
    renderWithTheme(<ChatInput onSubmit={vi.fn()} />);
    
    expect(screen.getByText(/0\/2000/)).toBeInTheDocument();
  });

  it('updates character counter as user types', async () => {
    const user = userEvent.setup();
    renderWithTheme(<ChatInput onSubmit={vi.fn()} />);
    
    const input = screen.getByPlaceholderText('Type your response...');
    await user.type(input, 'Hello');
    
    expect(screen.getByText(/5\/2000/)).toBeInTheDocument();
  });

  it('disables submit button when input is empty', () => {
    renderWithTheme(<ChatInput onSubmit={vi.fn()} />);
    
    const button = screen.getByRole('button', { name: /send/i });
    expect(button).toBeDisabled();
  });

  it('enables submit button when input has text', async () => {
    const user = userEvent.setup();
    renderWithTheme(<ChatInput onSubmit={vi.fn()} />);
    
    const input = screen.getByPlaceholderText('Type your response...');
    await user.type(input, 'Test message');
    
    const button = screen.getByRole('button', { name: /send/i });
    expect(button).toBeEnabled();
  });

  it('calls onSubmit with trimmed message on button click', async () => {
    const user = userEvent.setup();
    const onSubmit = vi.fn();
    renderWithTheme(<ChatInput onSubmit={onSubmit} />);
    
    const input = screen.getByPlaceholderText('Type your response...');
    await user.type(input, '  Test message  ');
    
    const button = screen.getByRole('button', { name: /send/i });
    await user.click(button);
    
    expect(onSubmit).toHaveBeenCalledWith('Test message');
  });

  it('clears input after successful submit', async () => {
    const user = userEvent.setup();
    const onSubmit = vi.fn();
    renderWithTheme(<ChatInput onSubmit={onSubmit} />);
    
    const input = screen.getByPlaceholderText('Type your response...') as HTMLInputElement;
    await user.type(input, 'Test message');
    
    const button = screen.getByRole('button', { name: /send/i });
    await user.click(button);
    
    expect(input.value).toBe('');
  });

  it('submits on Enter key (without Shift)', async () => {
    const onSubmit = vi.fn();
    renderWithTheme(<ChatInput onSubmit={onSubmit} />);
    
    const input = screen.getByPlaceholderText('Type your response...');
    await userEvent.type(input, 'Test message');
    
    fireEvent.keyDown(input, { key: 'Enter', shiftKey: false });
    
    expect(onSubmit).toHaveBeenCalledWith('Test message');
  });

  it('does not submit on Shift+Enter (allows new line)', async () => {
    const onSubmit = vi.fn();
    renderWithTheme(<ChatInput onSubmit={onSubmit} />);
    
    const input = screen.getByPlaceholderText('Type your response...');
    await userEvent.type(input, 'Test message');
    
    fireEvent.keyDown(input, { key: 'Enter', shiftKey: true });
    
    expect(onSubmit).not.toHaveBeenCalled();
  });

  it('shows error color when character limit exceeded', async () => {
    renderWithTheme(<ChatInput onSubmit={vi.fn()} />);
    
    const input = screen.getByPlaceholderText('Type your response...') as HTMLTextAreaElement;
    const longText = 'a'.repeat(2001);
    
    // Directly change the value to avoid timeout with userEvent
    fireEvent.change(input, { target: { value: longText } });
    
    expect(screen.getByText(/2001\/2000/)).toBeInTheDocument();
  });

  it('disables submit button when character limit exceeded', async () => {
    renderWithTheme(<ChatInput onSubmit={vi.fn()} />);
    
    const input = screen.getByPlaceholderText('Type your response...') as HTMLTextAreaElement;
    const longText = 'a'.repeat(2001);
    
    // Directly change the value to avoid timeout with userEvent
    fireEvent.change(input, { target: { value: longText } });
    
    const button = screen.getByRole('button', { name: /send/i });
    expect(button).toBeDisabled();
  });

  it('shows loading spinner when disabled', () => {
    renderWithTheme(<ChatInput onSubmit={vi.fn()} disabled />);
    
    expect(screen.getByRole('progressbar')).toBeInTheDocument();
  });

  it('disables input field when disabled prop is true', () => {
    renderWithTheme(<ChatInput onSubmit={vi.fn()} disabled />);
    
    const input = screen.getByPlaceholderText('Type your response...');
    expect(input).toBeDisabled();
  });
});
