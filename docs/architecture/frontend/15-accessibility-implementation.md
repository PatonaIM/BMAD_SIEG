# 15. Accessibility Implementation

## 15.1 WCAG 2.1 AA Compliance

**Keyboard Navigation:**
\`\`\`typescript
// Example: Accessible button component
<Button
  onClick={handleClick}
  onKeyDown={(e) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      handleClick();
    }
  }}
  aria-label="Start interview"
  tabIndex={0}
>
  Start Interview
</Button>
\`\`\`

**Screen Reader Support:**
\`\`\`typescript
// Example: ARIA live regions for dynamic content
<div role="status" aria-live="polite" aria-atomic="true">
  {isRecording ? 'Recording in progress' : 'Recording stopped'}
</div>

// Interview progress announcement
<div role="alert" aria-live="assertive">
  {`Question ${currentQuestion} of ${totalQuestions}`}
</div>
\`\`\`

**Color Contrast:**
- Text: 4.5:1 minimum contrast ratio
- Large text (18pt+): 3:1 minimum
- UI components: 3:1 minimum
- Use color + icon/text (not color alone)

**Focus Management:**
\`\`\`typescript
// Example: Focus trap in modal
import { useRef, useEffect } from 'react';

export const Modal = ({ isOpen, children }) => {
  const modalRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (isOpen && modalRef.current) {
      const focusableElements = modalRef.current.querySelectorAll(
        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
      );
      
      const firstElement = focusableElements[0] as HTMLElement;
      const lastElement = focusableElements[focusableElements.length - 1] as HTMLElement;

      firstElement?.focus();

      const handleTab = (e: KeyboardEvent) => {
        if (e.key === 'Tab') {
          if (e.shiftKey && document.activeElement === firstElement) {
            e.preventDefault();
            lastElement?.focus();
          } else if (!e.shiftKey && document.activeElement === lastElement) {
            e.preventDefault();
            firstElement?.focus();
          }
        }
      };

      document.addEventListener('keydown', handleTab);
      return () => document.removeEventListener('keydown', handleTab);
    }
  }, [isOpen]);

  return <div ref={modalRef} role="dialog">{children}</div>;
};
\`\`\`

## 15.2 Speech-Specific Accessibility

**Visual Alternatives:**
- Always show text transcript alongside speech
- Provide text input as fallback
- Visual indicators for all audio states
- Closed captions for AI speech (optional)

**Audio Feedback:**
- Confirm microphone is working before interview
- Visual audio level indicators
- Clear error messages for audio failures
- Allow replay of AI questions

---
