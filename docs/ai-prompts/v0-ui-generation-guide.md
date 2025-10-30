# v0 UI Generation Guide - Teamified Candidates Portal

## 📋 Overview

This document contains carefully crafted prompts for generating the Teamified Candidates Portal UI using Vercel v0. The prompts follow a structured framework to ensure high-quality, consistent, and production-ready code generation.

**Strategy:** Hybrid Approach
1. **Phase 1:** Generate foundational design system components
2. **Phase 2:** Generate Pre-Interview System Check screen using those components

---

## 📝 How to Use This Guide

**IMPORTANT - Read Before Copying to v0:**

1. **Expand the prompt section** below (Phase 1 or Phase 2)
2. **Copy ONLY the text inside the code fence** (between the triple backticks \`\`\`)
   - ✅ **START copying from:** `# TEAMIFIED DESIGN SYSTEM...`
   - ✅ **STOP copying at:** `...Include a brief README...` (end of prompt text)
   - ❌ **DO NOT copy:** The outer triple backticks (\`\`\`)
   - ❌ **DO NOT copy:** The `<details>` or `</details>` HTML tags
3. **Paste into v0.dev** (https://v0.vercel.app) chat interface
4. **Review and iterate** with v0 as needed

**Visual Guide:**
```
<details>                          ← Don't copy this
<summary>...</summary>             ← Don't copy this
```                                ← Don't copy this outer fence
# TEAMIFIED DESIGN SYSTEM...      ← START copying here
...
[All the prompt content]
...
Include a brief README...         ← STOP copying here
```                                ← Don't copy this outer fence
</details>                         ← Don't copy this
```

**Note:** The prompts are quite comprehensive (~500+ lines each). v0 handles this well, but if you encounter token limits, you can ask v0 to focus on specific components first.

---

## 🎯 Phase 1: Design System Foundation

### Purpose
Generate reusable, accessible, and professionally styled components that will serve as the foundation for all screens in the Teamified platform.

### Components to Generate
- MUI Theme Configuration
- Button Component (Primary, Secondary, Danger, Ghost variants)
- Card Component (Default, Interactive, Selected variants)
- Status Badge Component (Success, Warning, Error, Info)
- Input Field Component (Text, Textarea, Password)
- Progress Indicator Component (Linear, Circular, Stepper)

---

<details>
<summary><strong>📋 Click to expand: Phase 1 Prompt (Copy the text inside to v0)</strong></summary>

```
⬇️ COPY EVERYTHING BELOW THIS LINE (excluding this line) ⬇️

# TEAMIFIED DESIGN SYSTEM - CORE COMPONENTS

## PROJECT CONTEXT

You are building a design system for **Teamified Candidates Portal**, an AI-driven technical interview platform. This is a professional HR/recruitment tool built with **React 18+ and TypeScript**, using **Material-UI 3 Expressive Design** as the foundation with custom Teamified refinements.

**Tech Stack:**
- React 18+ with TypeScript
- Material-UI v3 (MUI)
- Styling: MUI's `sx` prop + theme customization
- Font: "Plus Jakarta Sans" (primary), "Inter" (fallback)
- Icons: Material-UI Icons (outlined style, 2px stroke)

**Design Philosophy:**
- Bold simplicity with professional polish
- Accessibility-first (WCAG 2.1 AA compliance)
- Expressive design with generous spacing and subtle shadows
- Modern HR dashboard aesthetic

---

## STEP-BY-STEP INSTRUCTIONS

### 1. CREATE THE MUI THEME CONFIGURATION

Create a file `theme.ts` that defines the Teamified custom theme:

1. Extend the default MUI theme with custom color palette
2. Configure typography with Plus Jakarta Sans font family
3. Define component style overrides for buttons, cards, and inputs
4. Set up spacing scale based on 8px baseline
5. Configure shadow/elevation values
6. Set border radius defaults

**Required Color Palette:**
```typescript
palette: {
  primary: {
    main: '#A16AE8',      // Brand Purple
    light: '#E8E5F5',     // Light Purple
    dark: '#7B3FD6',      // Dark Purple
    contrastText: '#FFFFFF'
  },
  success: {
    main: '#1DD1A1',      // Success Teal
    light: '#D4F5EE',     // Success Light
    contrastText: '#FFFFFF'
  },
  warning: {
    main: '#FFA502',      // Warning Orange
    contrastText: '#FFFFFF'
  },
  error: {
    main: '#EF4444',      // Error Red
    contrastText: '#FFFFFF'
  },
  info: {
    main: '#3B82F6',      // Info Blue
    contrastText: '#FFFFFF'
  },
  grey: {
    900: '#2C3E50',       // Dark Gray (text)
    700: '#7F8C8D',       // Medium Gray (secondary text)
    300: '#E0E4E8',       // Border Gray
    100: '#F5F6F7',       // Light Gray (backgrounds)
    50: '#FAFBFC'         // Background
  },
  background: {
    default: '#FAFBFC',
    paper: '#FFFFFF'
  }
}
```

**Typography Configuration:**
- Font family: `"Plus Jakarta Sans", "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif`
- Font weights: 400 (regular), 500 (medium), 600 (semibold), 700 (bold)
- Type scale with sizes: 56px (h1), 44px (h2), 36px (h3), 30px (h4), 24px (h5), 20px (h6), 16px (body1), 14px (body2), 12px (caption)

**Spacing:** Use 8px baseline (theme.spacing(1) = 8px)

**Shadows:**
```typescript
shadows: {
  cardDefault: '0 2px 8px rgba(0, 0, 0, 0.04)',
  cardHover: '0 4px 16px rgba(0, 0, 0, 0.08)',
  level1: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
  level2: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
  level3: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
  dialog: '0 25px 50px -12px rgba(0, 0, 0, 0.25)'
}
```

**Border Radius:**
- Small (badges): 16px
- Medium (buttons/inputs): 8px
- Large (cards): 12px
- XL (modals): 16-20px

---

### 2. CREATE BUTTON COMPONENT

Create `components/Button.tsx` with the following specifications:

**Variants Required:**
- `primary` - Purple background (#A16AE8), white text, used for main actions
- `secondary` - Transparent with 1px border (#E0E4E8), dark gray text (#2C3E50)
- `danger` - Red background (#EF4444), white text, for destructive actions
- `ghost` - Transparent, no border, medium gray text, for tertiary actions

**States to Implement:**
- Default
- Hover (darken primary by 10%, light gray background for secondary)
- Active (scale down to 0.95x with reduced shadow)
- Disabled (70% opacity, cursor not-allowed)
- Loading (show circular progress spinner, dim to 70% opacity)

**Specifications:**
- Height: 44px (standard), 36px (compact)
- Padding: 12px horizontal, 24px vertical
- Border radius: 8px
- Font: 14px, medium weight (500)
- Minimum touch target: 44x44px
- Support for left/right icons
- Hover animation: 150ms ease-out
- Active animation: 150ms cubic-bezier(0.4, 0.0, 0.2, 1)

**Props Interface:**
```typescript
interface ButtonProps {
  variant?: 'primary' | 'secondary' | 'danger' | 'ghost';
  size?: 'standard' | 'compact';
  disabled?: boolean;
  loading?: boolean;
  startIcon?: React.ReactNode;
  endIcon?: React.ReactNode;
  fullWidth?: boolean;
  onClick?: () => void;
  children: React.ReactNode;
}
```

---

### 3. CREATE CARD COMPONENT

Create `components/Card.tsx` with the following specifications:

**Variants Required:**
- `default` - Standard card with subtle shadow
- `interactive` - Clickable/hoverable with elevation change
- `selected` - 2px purple border indicating selection

**Specifications:**
- Background: White (#FFFFFF)
- Border: 1px solid #E0E4E8
- Border radius: 12px
- Padding: 24px
- Default shadow: `0 2px 8px rgba(0, 0, 0, 0.04)`
- Hover shadow (interactive only): `0 4px 16px rgba(0, 0, 0, 0.08)`
- Selected state: 2px solid #A16AE8 border
- Hover animation: 250ms cubic-bezier(0.4, 0.0, 0.2, 1)

**Props Interface:**
```typescript
interface CardProps {
  variant?: 'default' | 'interactive' | 'selected';
  onClick?: () => void;
  children: React.ReactNode;
  className?: string;
}
```

---

### 4. CREATE STATUS BADGE COMPONENT

Create `components/StatusBadge.tsx` with the following specifications:

**Variants Required:**
- `success` - Teal background (#1DD1A1), white text
- `warning` - Orange background (#FFA502), white text
- `error` - Red background (#EF4444), white text
- `info` - Light teal background (#D4F5EE), teal text (#1DD1A1)

**Specifications:**
- Height: 24px
- Padding: 4px horizontal, 12px vertical
- Border radius: 16px (full pill shape)
- Font: 12px, medium weight (500)
- Include optional left icon
- Text transform: capitalize

**Props Interface:**
```typescript
interface StatusBadgeProps {
  variant: 'success' | 'warning' | 'error' | 'info';
  icon?: React.ReactNode;
  children: React.ReactNode;
}
```

---

### 5. CREATE INPUT FIELD COMPONENT

Create `components/Input.tsx` with the following specifications:

**Variants Required:**
- `text` - Standard text input
- `textarea` - Multi-line text area
- `password` - Password input with show/hide toggle

**Specifications:**
- Height: 44px (text input only)
- Border: 1px solid #E0E4E8
- Border radius: 8px
- Padding: 12px horizontal, 16px vertical
- Font: 14px, regular weight (400)
- Placeholder color: Medium gray (#7F8C8D)
- Focus state: 2px solid purple border (#A16AE8)
- Error state: 2px solid red border (#EF4444) + error message below
- Label: 14px, medium weight, positioned above input
- Help text: 12px, medium gray, positioned below input
- Error message: 12px, red (#EF4444), with error icon

**Props Interface:**
```typescript
interface InputProps {
  variant?: 'text' | 'textarea' | 'password';
  label: string;
  placeholder?: string;
  value: string;
  onChange: (value: string) => void;
  error?: string;
  helpText?: string;
  disabled?: boolean;
  required?: boolean;
  rows?: number; // for textarea
}
```

---

### 6. CREATE PROGRESS INDICATOR COMPONENT

Create `components/ProgressIndicator.tsx` with the following specifications:

**Variants Required:**
- `linear` - Horizontal progress bar with percentage
- `circular` - Circular spinner for indeterminate loading
- `stepper` - Step indicator with checkmarks (e.g., "Step 2 of 4")

**Linear Progress Specifications:**
- Height: 8px
- Background: Light gray (#E0E4E8)
- Fill: Purple (#A16AE8)
- Border radius: 4px
- Show percentage label (14px, medium, purple)
- Smooth fill animation: 400ms ease-out

**Circular Progress Specifications:**
- Size: 40px (standard), 24px (small)
- Color: Purple (#A16AE8)
- Thickness: 3px

**Stepper Specifications:**
- Display horizontal step indicators
- Completed steps: Teal checkmark (#1DD1A1) in circle
- Current step: Purple circle (#A16AE8)
- Upcoming steps: Gray circle (#E0E4E8)
- Connect steps with lines

**Props Interface:**
```typescript
interface ProgressIndicatorProps {
  variant: 'linear' | 'circular' | 'stepper';
  value?: number; // 0-100 for linear
  steps?: number; // for stepper
  currentStep?: number; // for stepper
  size?: 'small' | 'standard'; // for circular
}
```

---

## CODE EXAMPLES & CONSTRAINTS

**MUI Theme Usage:**
```typescript
// Use MUI's sx prop for styling
<Box sx={{
  backgroundColor: 'primary.main',
  padding: 3, // 24px (3 * 8px)
  borderRadius: '12px',
  boxShadow: (theme) => theme.shadows.cardDefault
}}>
```

**Animation Example:**
```typescript
// Button hover animation
sx={{
  transition: 'all 150ms cubic-bezier(0.4, 0.0, 0.2, 1)',
  '&:hover': {
    backgroundColor: 'primary.dark',
    boxShadow: (theme) => theme.shadows.cardHover
  },
  '&:active': {
    transform: 'scale(0.95)'
  }
}}
```

**Accessibility Requirements:**
- All interactive elements must have minimum 44x44px touch target
- Proper ARIA labels on all components
- Focus indicators with 2px outline
- Color contrast ratio minimum 4.5:1 for text
- Keyboard navigation support (Tab, Enter, Space)

---

## STRICT SCOPE

**YOU SHOULD:**
- Create only the 6 components listed above: Theme, Button, Card, StatusBadge, Input, ProgressIndicator
- Use TypeScript with proper interfaces
- Use MUI's component library and styling system
- Include proper accessibility attributes (aria-labels, roles)
- Add hover and focus states to all interactive components
- Follow the exact color palette, typography, and spacing provided

**YOU SHOULD NOT:**
- Create any page layouts or screens
- Add routing or navigation
- Include state management libraries
- Create API integration code
- Add form validation logic (just display error states)
- Use CSS-in-JS libraries other than MUI's sx prop
- Create components not listed in the requirements

---

## DELIVERABLES

Provide the following files:
1. `theme.ts` - Complete MUI theme configuration
2. `components/Button.tsx` - Button component with all variants
3. `components/Card.tsx` - Card component with variants
4. `components/StatusBadge.tsx` - Status badge component
5. `components/Input.tsx` - Input field component with variants
6. `components/ProgressIndicator.tsx` - Progress indicator with variants
7. `components/index.ts` - Export barrel file for all components

Include a brief README explaining how to use each component with code examples.

⬆️ COPY EVERYTHING ABOVE THIS LINE (excluding this line) ⬆️
```

</details>


---

## 🎯 Phase 2: Pre-Interview System Check Screen

### Purpose
Generate a fully functional, production-ready Pre-Interview System Check page that validates candidate audio setup before interviews. This screen uses the design system components from Phase 1.

### Key Features
- Microphone permission handling
- Real-time audio visualization
- Audio recording and playback
- Connection testing
- Error handling with troubleshooting
- Responsive design
- Accessibility compliant

---

<details>
<summary><strong>📋 Click to expand: Phase 2 Prompt (Copy the text inside to v0)</strong></summary>

```
⬇️ COPY EVERYTHING BELOW THIS LINE (excluding this line) ⬇️

# TEAMIFIED - PRE-INTERVIEW SYSTEM CHECK SCREEN

## PROJECT CONTEXT

You are building the **Pre-Interview System Check** screen for Teamified Candidates Portal, an AI-driven technical interview platform. This critical screen validates a candidate's audio setup BEFORE they begin their interview to prevent mid-interview technical failures.

**Tech Stack:**
- React 18+ with TypeScript
- Material-UI v3 (MUI) with custom Teamified theme
- Use the design system components from the previous prompt (Button, Card, StatusBadge, ProgressIndicator, Input)
- Font: "Plus Jakarta Sans"
- Icons: Material-UI Icons (outlined style)

**User Context:**
- User: Technical candidate (anxious about AI interview)
- Goal: Ensure microphone and audio work properly
- Emotional state: Nervous but tech-savvy
- Critical UX: Must be reassuring, not intimidating

---

## STEP-BY-STEP INSTRUCTIONS

### 1. CREATE PAGE LAYOUT STRUCTURE

Create `pages/PreInterviewCheck.tsx` with the following layout:

1. Center the content vertically and horizontally on the page
2. Page background: Light gray (#FAFBFC)
3. Main content container: White card, max-width 600px, 24px padding
4. Header section with Teamified logo (placeholder) and page title
5. Progress checklist section (vertical layout)
6. Footer section with support contact and "Need Help?" link

**Layout Specifications:**
- Page margins: 24px on mobile, 48px on desktop
- Content max-width: 600px
- Vertical spacing between sections: 32px
- Use responsive design (mobile-first approach)

---

### 2. CREATE HEADER SECTION

Implement the header with:

1. Teamified logo placeholder (use a purple circle with "T" initial)
2. Page title: "System Check" (H4, 30px, semibold)
3. Subtitle: "This will only take a minute. We want to make sure everything works perfectly." (Body1, 16px, regular, medium gray)
4. Spacing: 16px between logo and title, 8px between title and subtitle

---

### 3. CREATE PROGRESS CHECKLIST COMPONENT

Build a vertical checklist showing 3 steps:

**Steps:**
1. "Microphone Permission" - Request browser microphone access
2. "Audio Test" - Record 3+ seconds of audio and play back
3. "Connection Test" - Verify network connectivity

**Visual Design for Each Step:**
- Card-style container for each step (white background, 1px border, 12px radius, 16px padding)
- Left side: Circle indicator (32px diameter)
  - Pending: Gray circle with number
  - In Progress: Purple circle with animated spinner
  - Completed: Teal circle with white checkmark icon
  - Failed: Red circle with white X icon
- Right side: Step content
  - Title: Body1, semibold
  - Description: Body2, medium gray
  - Status message: Caption, 12px
- Spacing between steps: 16px

**Step States:**
- `pending` - Not started, gray circle with step number
- `inProgress` - Currently active, purple animated spinner
- `completed` - Passed, teal checkmark
- `failed` - Error occurred, red X with expandable error details

---

### 4. IMPLEMENT MICROPHONE PERMISSION STEP

**When step becomes active:**

1. Show "Requesting permission..." status message
2. Use browser's `navigator.mediaDevices.getUserMedia({ audio: true })` API
3. On success:
   - Mark step as completed
   - Show "Permission granted ✓" message in teal
   - Automatically proceed to next step after 500ms
4. On denial:
   - Mark step as failed
   - Show error message: "Microphone access denied"
   - Display expandable troubleshooting accordion below step
   - Show "Retry" button

**Troubleshooting Accordion Content:**
```
How to enable microphone access:
- Chrome: Click the camera icon in address bar
- Safari: Go to Preferences > Websites > Microphone
- Firefox: Click the shield icon in address bar
```

---

### 5. IMPLEMENT AUDIO TEST STEP

**When step becomes active:**

1. Show waveform visualizer component (60px height, full width)
2. Display "Speak now..." prompt (Body1, medium gray)
3. Show real-time audio waveform animation as user speaks
4. Display countdown: "Recording... 3s remaining"
5. After 3 seconds of audio detected:
   - Stop recording
   - Show "Listen to yourself" button (secondary variant)
   - Play back the recorded audio when button clicked
   - Show "Did it sound clear?" with Yes/No buttons
6. On "Yes":
   - Mark step as completed
   - Show "Audio quality confirmed ✓" in teal
   - Automatically proceed to next step after 500ms
7. On "No":
   - Show "Try again" option
   - Display troubleshooting tips for common audio issues

**Waveform Visualizer Specifications:**
- Display 20-30 vertical bars (4px width, 4px spacing)
- Bars animate based on audio amplitude (green color #1DD1A1)
- Smooth animation: 100ms linear transitions
- Minimum bar height: 8px, maximum: 60px
- Background: Very light gray (#F5F6F7)
- Border radius: 8px

---

### 6. IMPLEMENT CONNECTION TEST STEP

**When step becomes active:**

1. Show "Testing connection..." with circular progress spinner
2. Simulate API connectivity check (ping endpoint or WebSocket connection)
3. Display latency result: "Connection speed: X ms"
4. On success:
   - Mark step as completed
   - Show "Connection verified ✓" in teal
5. On failure:
   - Mark step as failed
   - Show error message: "Connection unstable"
   - Display troubleshooting tips
   - Show "Retry" button

**Success criteria:** Latency < 200ms = Good, 200-500ms = Fair, >500ms = Poor

---

### 7. CREATE FOOTER CTA SECTION

**When all steps completed:**

1. Show large primary button: "Begin Interview" (full width on mobile, auto width on desktop)
2. Button should only be enabled when all 3 steps are completed
3. Display estimated interview duration: "Estimated time: 20-30 minutes" (Caption, medium gray)
4. Show "Skip Check" link (only appears after 3 failed retry attempts)

**Before completion:**
- Button is disabled with text "Complete system check first"
- Show progress message: "X of 3 checks completed"

---

### 8. ADD SUPPORT SECTION

In the footer, add:

1. "Need help?" text with support icon
2. "Contact Support" link (ghost button variant)
3. Alternative: "Email us at support@teamified.com"

---

## CODE EXAMPLES & CONSTRAINTS

**Using Design System Components:**
```typescript
import { Button, Card, StatusBadge, ProgressIndicator } from '@/components';

// Button usage
<Button variant="primary" fullWidth onClick={handleBeginInterview}>
  Begin Interview
</Button>

// Card usage
<Card variant="interactive">
  <Typography>Step content</Typography>
</Card>

// Status badge
<StatusBadge variant="success" icon={<CheckCircleIcon />}>
  Completed
</StatusBadge>
```

**Audio API Example:**
```typescript
// Request microphone permission
const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

// Create audio visualizer
const audioContext = new AudioContext();
const analyser = audioContext.createAnalyser();
const source = audioContext.createMediaStreamSource(stream);
source.connect(analyser);

// Get frequency data for visualization
const dataArray = new Uint8Array(analyser.frequencyBinCount);
analyser.getByteFrequencyData(dataArray);
```

**Step State Management:**
```typescript
type StepStatus = 'pending' | 'inProgress' | 'completed' | 'failed';

interface Step {
  id: string;
  title: string;
  description: string;
  status: StepStatus;
  errorMessage?: string;
}
```

**Accessibility Requirements:**
- All interactive elements keyboard accessible (Tab navigation)
- ARIA live regions for status updates
- Clear focus indicators on all buttons
- Screen reader announcements for step completion
- Alt text for all icons
- Proper heading hierarchy (H1 > H2 > H3)

**Animation Specifications:**
- Step completion: 500ms fade-in for checkmark with scale animation
- Card expansion (troubleshooting): 250ms ease-out
- Waveform bars: 100ms linear height transitions
- Button enable transition: 250ms ease-in

---

## STRICT SCOPE

**YOU SHOULD:**
- Create only the Pre-Interview System Check page
- Use the design system components (Button, Card, StatusBadge, ProgressIndicator)
- Implement real browser microphone API integration
- Add proper error handling for all audio/permission scenarios
- Include responsive design for mobile, tablet, desktop
- Add loading states and animations
- Include accessibility attributes (ARIA labels, keyboard navigation)
- Use TypeScript with proper interfaces

**YOU SHOULD NOT:**
- Create navigation or routing logic
- Build actual interview functionality
- Add authentication/login logic
- Create API integration for interview scheduling
- Build database persistence
- Add analytics tracking
- Create other pages or components not specified

---

## MOCK DATA

Use this mock data for testing:

```typescript
// Simulated latency test result
const mockLatency = Math.random() * 300 + 50; // 50-350ms

// Simulated audio permission responses
const mockPermissionGranted = true; // Change to false to test denial flow

// Step initial state
const initialSteps: Step[] = [
  {
    id: 'mic-permission',
    title: 'Microphone Permission',
    description: 'Allow browser access to your microphone',
    status: 'pending'
  },
  {
    id: 'audio-test',
    title: 'Audio Test',
    description: 'Record and play back a short audio sample',
    status: 'pending'
  },
  {
    id: 'connection-test',
    title: 'Connection Test',
    description: 'Verify your internet connection',
    status: 'pending'
  }
];
```

---

## RESPONSIVE BREAKPOINTS

**Mobile (320-767px):**
- Single column layout
- Full-width buttons
- Simplified waveform (15 bars instead of 30)
- Stacked step indicators

**Tablet (768-1023px):**
- Centered content, max-width 600px
- Standard button widths
- Full waveform

**Desktop (1024px+):**
- Centered content, max-width 600px
- Additional padding around container
- Hover states enabled

---

## DELIVERABLES

Provide:
1. `pages/PreInterviewCheck.tsx` - Main page component
2. `components/WaveformVisualizer.tsx` - Audio waveform component
3. `components/SystemCheckStep.tsx` - Individual step component
4. `hooks/useAudioRecording.ts` - Custom hook for audio recording logic
5. `hooks/useMicrophonePermission.ts` - Custom hook for permission handling
6. Brief README with usage instructions and testing guidance

---

## EXPECTED USER EXPERIENCE FLOW

1. Page loads → All steps show as "pending"
2. Microphone permission step auto-starts → Shows "Requesting permission..."
3. Browser permission dialog appears → User clicks "Allow"
4. Step 1 completes with checkmark → Auto-advances to step 2 after 500ms
5. Audio test begins → Waveform shows live audio visualization
6. User speaks for 3+ seconds → Recording completes, playback button appears
7. User clicks playback → Hears their recorded audio
8. User clicks "Yes, it sounds clear" → Step 2 completes with checkmark
9. Connection test auto-starts → Shows spinner + "Testing..."
10. Connection verified → Step 3 completes with checkmark
11. "Begin Interview" button becomes enabled and highlighted
12. User clicks button → Proceeds to interview (show console.log for now)

This flow should feel smooth, reassuring, and professional. Minimize anxiety through clear feedback and encouraging copy.

⬆️ COPY EVERYTHING ABOVE THIS LINE (excluding this line) ⬆️
```

</details>


---

## 🚀 Complete Workflow: From Prompt to Production

### 📂 File Placement Strategy

**IMPORTANT:** v0-generated code serves as **design reference**, not production code.

**Reference Location (v0 Output):**
```
docs/style-guide/design-system-reference/
├── components/
│   ├── teamified/          # Design system components
│   │   ├── Button.tsx
│   │   ├── Card.tsx
│   │   └── ...
│   └── ui/                 # shadcn/ui components
├── app/
│   ├── page.tsx            # Component showcase
│   └── pre-interview-check/ # Reference screens
├── hooks/
├── lib/
│   └── theme.ts
└── REFERENCE.md
```

**Production Location (Developer Implementation):**
```
src/
├── components/
│   └── ui/                 # Production components
│       ├── Button.tsx      # Adapted from reference
│       ├── Card.tsx
│       └── ...
├── lib/
│   ├── theme.ts            # MUI theme config
│   └── api.ts              # API integration
├── hooks/
└── pages/
```

**Workflow:**
1. **PM/Designer:** References `docs/style-guide/design-system-reference/` in user stories
2. **Developer:** Reviews reference, implements in `src/` with production features
3. **No direct imports** from reference to production code

---

### Step 1: Generate Phase 1 Components (Design System)

1. **Go to v0.dev** (https://v0.vercel.app)
2. **Paste the entire Phase 1 prompt** into v0's chat interface
3. **Review the generated code:**
   - Check theme configuration matches specifications
   - Verify all component variants are present
   - Test interactive states (hover, focus, disabled)
   - Validate accessibility features
4. **Iterate if needed:**
   - Ask v0 to adjust specific aspects: "Make the button hover effect slightly slower"
   - Request fixes for any missing features: "Add the compact size variant to the Button"
5. **Export the code:**
   - Click "Code" tab in v0 interface
   - Copy all generated files
   - Save as **reference documentation** (not production code):
     ```
     docs/
       style-guide/
         design-system-reference/
           components/
             teamified/
               Button.tsx
               Card.tsx
               StatusBadge.tsx
               Input.tsx
               ProgressIndicator.tsx
               index.ts
           lib/
             theme.ts
           REFERENCE.md
     ```

### Step 2: Test Design System Components

1. **Create a component showcase page** (optional but recommended):
   ```tsx
   // pages/design-system-showcase.tsx
   import { Button, Card, StatusBadge, Input, ProgressIndicator } from '@/components';

   export default function DesignSystemShowcase() {
     return (
       <div style={{ padding: '48px' }}>
         <h1>Teamified Design System</h1>
         
         {/* Button showcase */}
         <section>
           <h2>Buttons</h2>
           <Button variant="primary">Primary Button</Button>
           <Button variant="secondary">Secondary Button</Button>
           <Button variant="danger">Danger Button</Button>
           <Button variant="ghost">Ghost Button</Button>
         </section>

         {/* Card showcase */}
         <section>
           <h2>Cards</h2>
           <Card variant="default">Default Card</Card>
           <Card variant="interactive">Interactive Card</Card>
         </section>

         {/* Status badges */}
         <section>
           <h2>Status Badges</h2>
           <StatusBadge variant="success">Success</StatusBadge>
           <StatusBadge variant="warning">Warning</StatusBadge>
           <StatusBadge variant="error">Error</StatusBadge>
           <StatusBadge variant="info">Info</StatusBadge>
         </section>

         {/* Progress indicators */}
         <section>
           <h2>Progress Indicators</h2>
           <ProgressIndicator variant="linear" value={65} />
           <ProgressIndicator variant="circular" />
           <ProgressIndicator variant="stepper" steps={3} currentStep={2} />
         </section>
       </div>
     );
   }
   ```

2. **Manual testing checklist:**
   - [ ] All variants render correctly
   - [ ] Hover states work
   - [ ] Focus states visible (Tab navigation)
   - [ ] Disabled states prevent interaction
   - [ ] Loading states display spinner
   - [ ] Responsive at mobile, tablet, desktop
   - [ ] Color contrast meets WCAG AA
   - [ ] Screen reader announces properly

3. **Fix any issues:**
   - Go back to v0 with specific feedback
   - Manually adjust generated code if minor
   - Document any deviations from spec

### Step 3: Generate Phase 2 Screen (Pre-Interview Check)

1. **Return to v0.dev**
2. **Start a NEW chat session** (important for clean context)
3. **Paste Phase 2 prompt**
4. **v0 will generate the screen** using your design system components
5. **Review generated code:**
   - Check all 3 steps (mic permission, audio test, connection)
   - Verify waveform visualizer implementation
   - Test error handling flows
   - Validate responsive layout
6. **Test microphone integration:**
   - Browser must request permission
   - Audio recording works
   - Playback functions correctly
   - Waveform animates with audio
7. **Iterate on specific features:**
   - "Add more bars to the waveform visualizer"
   - "Make the troubleshooting accordion expand smoother"
   - "Add a subtle pulse animation to the active step"

### Step 4: Integration & Refinement

**Important:** The reference code in `docs/style-guide/design-system-reference/` should NOT be directly imported into production. Instead, developers should:

1. **Reference, don't copy blindly:**
   ```
   Reference:
     docs/style-guide/design-system-reference/components/teamified/Button.tsx
   
   Production Implementation:
     src/components/ui/Button.tsx (adapted with backend integration)
   ```

2. **Add production requirements:**
   ```typescript
   // Production implementation adds:
   - API integration and error handling
   - Analytics tracking
   - State management (Redux/Zustand)
   - Unit tests and integration tests
   - Proper TypeScript types
   - Documentation and Storybook stories
   ```

3. **Maintain design specifications:**
   - Use exact colors, typography, spacing from reference
   - Keep animation timings consistent
   - Preserve accessibility attributes
   - Follow responsive breakpoints

4. **Example production workflow:**
   ```typescript
   // Reference: docs/style-guide/design-system-reference/components/teamified/Button.tsx
   // Production: src/components/ui/Button.tsx
   
   import { trackEvent } from '@/lib/analytics';
   import { useAuth } from '@/hooks/useAuth';
   
   export function Button({ variant, onClick, children, ...props }: ButtonProps) {
     const { user } = useAuth();
     
     const handleClick = () => {
       // Add analytics
       trackEvent('button_click', { variant, userId: user?.id });
       
       // Original onClick logic
       onClick?.();
     };
     
     // Keep exact styling from reference
     return (
       <button 
         className={buttonVariants({ variant })}
         onClick={handleClick}
         {...props}
       >
         {children}
       </button>
     );
   }
   ```

### Step 5: Testing & Quality Assurance

**Functional Testing:**
- [ ] Microphone permission request works
- [ ] Audio recording captures 3+ seconds
- [ ] Playback plays recorded audio
- [ ] Connection test measures latency
- [ ] All steps complete successfully in order
- [ ] Error states trigger appropriately
- [ ] Retry functionality works
- [ ] Skip check appears after 3 failures
- [ ] Begin Interview button enables correctly

**Cross-Browser Testing:**
- [ ] Chrome (latest)
- [ ] Safari (latest)
- [ ] Firefox (latest)
- [ ] Edge (latest)

**Device Testing:**
- [ ] iPhone (Safari)
- [ ] Android (Chrome)
- [ ] iPad (Safari)
- [ ] Desktop (all browsers)

**Accessibility Testing:**
- [ ] Screen reader announces steps correctly
- [ ] Keyboard navigation works (Tab, Enter, Space)
- [ ] Focus indicators visible
- [ ] Color contrast passes WCAG AA
- [ ] ARIA labels present
- [ ] Live regions announce status changes

**Performance Testing:**
- [ ] Page loads under 3 seconds
- [ ] Animations run at 60fps
- [ ] No memory leaks from audio streams
- [ ] Waveform visualizer doesn't block UI

### Step 6: Documentation

**Create component documentation:**
```markdown
# Pre-Interview System Check

## Purpose
Validates candidate audio setup before interview begins.

## Usage
```tsx
import PreInterviewCheck from '@/pages/pre-interview-check';

<PreInterviewCheck 
  onComplete={() => router.push('/interview/session')}
  onSkip={() => router.push('/interview/session?skipCheck=true')}
/>
```

## Browser Support
- Chrome 90+
- Safari 14+
- Firefox 88+
- Edge 90+

## Permissions Required
- Microphone access
- Network connectivity

## Error Handling
All errors are logged to Sentry and displayed to user with actionable guidance.
```

### Step 7: Deployment Checklist

**Before deploying to production:**
- [ ] All tests pass
- [ ] Code reviewed by team
- [ ] Accessibility audit complete
- [ ] Performance benchmarks met
- [ ] Error tracking configured
- [ ] Analytics events added
- [ ] Documentation complete
- [ ] Staging environment tested
- [ ] Security review complete
- [ ] Browser compatibility verified

---

## 🔄 Iteration & Maintenance

### When to Iterate with v0

**Go back to v0 when you need:**
- New component variants
- Different screen layouts
- Additional features
- Responsive refinements
- Animation adjustments
- Accessibility improvements

**Example iteration prompts:**
```
"Add a 'loading' variant to the Card component with a skeleton loader animation"

"Create a toast notification component that slides in from top-right"

"Make the Pre-Interview Check screen work in landscape mode on mobile"

"Add a dark mode variant to the entire design system"
```

### Maintaining Consistency

**As you add more screens:**
1. Always reference your design system components
2. Follow the same color palette, typography, spacing
3. Use consistent animation timings
4. Maintain accessibility standards
5. Test across same device/browser matrix

**Create a design system checklist for new features:**
- [ ] Uses existing components where possible
- [ ] Follows Teamified color palette
- [ ] Implements 8px spacing scale
- [ ] Matches animation timing standards
- [ ] Meets WCAG 2.1 AA accessibility
- [ ] Responsive on all breakpoints
- [ ] Uses Plus Jakarta Sans typography

---

## 📊 Success Metrics

**After implementing these screens, measure:**

**Design System Adoption:**
- % of new components using design system
- Time to build new screens (should decrease)
- Code duplication (should decrease)
- Design consistency score (should increase)

**Pre-Interview Check Effectiveness:**
- % candidates completing system check
- Average time to complete (target: <2 minutes)
- % technical issues caught before interview
- % candidates skipping check (should be low)
- Browser/device-specific failure rates

**User Experience:**
- Candidate anxiety reduction (survey)
- Interview start success rate
- Technical support requests (should decrease)
- Net Promoter Score (should increase)

---

## 🆘 Troubleshooting Common Issues

### v0 Generated Code Issues

**Problem:** Components don't match exact specifications
**Solution:** Be more explicit in prompt, provide exact pixel values, reference specific MUI patterns

**Problem:** TypeScript errors in generated code
**Solution:** Ask v0 to "fix TypeScript errors" or manually add proper type definitions

**Problem:** Accessibility attributes missing
**Solution:** Explicitly request ARIA labels, keyboard navigation, screen reader support in prompt

### Integration Issues

**Problem:** Design system components conflict with existing styles
**Solution:** Use CSS modules or MUI's `sx` prop to scope styles, ensure theme provider wraps app

**Problem:** Microphone API doesn't work on mobile
**Solution:** Ensure HTTPS in production, request permissions on user gesture, add iOS-specific handling

**Problem:** Performance issues with waveform visualizer
**Solution:** Throttle animation frames, use `requestAnimationFrame`, reduce bar count on mobile

---

## 📚 Additional Resources

- **MUI Documentation:** https://mui.com/material-ui/getting-started/
- **Web Audio API:** https://developer.mozilla.org/en-US/docs/Web/API/Web_Audio_API
- **WCAG Guidelines:** https://www.w3.org/WAI/WCAG21/quickref/
- **v0 Documentation:** https://v0.dev/docs
- **TypeScript Handbook:** https://www.typescriptlang.org/docs/

---

## ✅ Next Steps After This Guide

1. **Generate Phase 3 screens:**
   - Live Interview Session
   - Candidate Results Dashboard
   - Recruiter Candidate Detail View

2. **Enhance design system:**
   - Add data visualization components
   - Create audio player component
   - Build notification/alert system

3. **Implement authentication:**
   - Login/signup screens
   - Password reset flow
   - Role-based access control

4. **Build recruiter portal:**
   - Candidate pipeline
   - Interview scheduler
   - Reports & analytics

5. **Add admin features:**
   - User management
   - System configuration
   - Audit logs

---

**Document Version:** 1.0  
**Last Updated:** October 28, 2025  
**Author:** Sally (UX Expert)  
**Status:** Ready for v0 Generation
