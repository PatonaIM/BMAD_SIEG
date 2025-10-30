# User Interface Design Goals

## Overall UX Vision

The platform delivers a professional, distraction-free interview experience that reduces candidate anxiety while maintaining assessment integrity. The candidate interface emphasizes clarity and conversational flow, mimicking natural chat interactions with progress indicators only - no scoring visible during the interview. For recruitment firms, the portal provides comprehensive candidate insights through data-rich dashboards with detailed AI reasoning, specific integrity red flags, and intuitive filtering and comparison tools.

The design prioritizes trust-building through transparency - candidates understand the assessment process and their progress, while recruiters gain confidence through detailed scoring breakdowns, AI decision reasoning, and specific integrity violation indicators.

## Key Interaction Paradigms

**Conversational Interview Flow**: Chat-like interface with typing indicators, smooth message transitions, and clear turn-taking between AI and candidate. Progressive disclosure of complexity keeps candidates engaged without overwhelming them.

**Progress-Only Feedback for Candidates**: Candidates see interview completion progress (e.g., "Question 8 of ~15-20") and encouraging affirmations, but no scores or competency indicators until interview completion. This maintains focus and reduces anxiety.

**Detailed AI Reasoning for Recruiters**: Real-time monitoring dashboard (future consideration) and post-interview reports show not just scores, but AI's reasoning - "Why did the AI rate this response as junior level?", "What patterns triggered integrity concerns?", "How did the AI determine skill boundaries?"

**Granular Integrity Indicators**: Instead of simple pass/fail, show specific red flags with severity levels: "Response timing anomaly - answered complex algorithm question in 15 seconds", "Pattern match - 85% similarity to common online solution", "Inconsistency detected - contradicts earlier stated experience with React hooks"

**Skill Boundary Visualization**: Interactive skill maps and competency charts use color-coding and radar graphs to quickly communicate proficiency levels across technical domains, with drill-down capability to see specific question/answer pairs that determined each rating.

**Batch Processing with Approval Workflow**: Resume upload provides clear status updates and estimated processing time. Automated feedback generation with recruiter approval option before sending - recruiter can review, edit, and approve or auto-send after X hours.

## Core Screens and Views

**Candidate Resume Upload Screen**: Simple drag-and-drop interface with format validation (PDF/DOCX), upload progress indicator, and confirmation message with expected processing timeline (within 24 hours).

**Candidate Interview Screen**: Full-screen interview interface with AI voice questions (with text transcript displayed), microphone controls (push-to-talk or voice-activated), real-time audio visualization showing candidate speaking, optional text input area for code examples, progress indicator showing approximate completion (e.g., "~60% complete"), and visual states (AI speaking, AI listening, candidate speaking). No scoring or competency indicators visible during interview.

**Candidate Results Screen**: Post-interview summary displaying overall competency score, skill boundary map visualization, strengths/areas for improvement breakdown, specific recommendations, and next steps. This is the first time candidates see any scoring information.

**Recruiter Dashboard**: Multi-candidate overview with sortable/filterable table showing key metrics (completion status, overall scores, integrity risk levels - color coded: green/yellow/red), quick actions (view details, export report, approve resume feedback), and search functionality.

**Recruiter Candidate Detail View**: Comprehensive single-candidate report including:
- **Interview Transcript**: Full conversation with AI questions and candidate responses
- **AI Scoring Reasoning**: For each major assessment area, show the AI's reasoning (e.g., "Rated React proficiency as 'Intermediate' because: demonstrated understanding of hooks and state management, but struggled with performance optimization concepts")
- **Detailed Integrity Analysis**: Specific red flags with severity and evidence:
  - Response timing anomalies with specific examples
  - Pattern matching results with similarity percentages
  - Inconsistency detection with contradicting statements highlighted
  - Behavioral indicators the AI detected
- **Skill Boundary Visualization**: Interactive charts showing proficiency across domains with drill-down to supporting evidence
- **Recommended Actions**: AI-generated suggestions for recruiter (e.g., "Schedule follow-up on React performance topics", "High integrity risk - recommend supervised technical assessment")

**Recruiter Resume Feedback Approval Screen**: Shows auto-generated feedback email with:
- Parsed skills summary
- Identified technical areas and gaps
- Specific improvement suggestions
- Call-to-action to schedule interview
- Recruiter options: "Send Now", "Edit & Send", "Auto-send in 4 hours if not reviewed"

**Resume Feedback Email**: Email template providing parsed skills summary, identified technical areas, specific suggestions for improvement, and call-to-action to schedule interview when ready.

## Accessibility

**WCAG AA Compliance**: Keyboard navigation support, proper ARIA labels, sufficient color contrast ratios (4.5:1 minimum for text), and screen reader compatibility for all interactive elements.

## Branding

**Professional Technical Aesthetic**: Clean, modern interface with emphasis on data visualization and information hierarchy. Color palette uses trust-building blues and greens with severity-coded integrity warnings (green=passed, yellow=minor concerns, red=significant red flags). Typography prioritizes readability with clear font hierarchy distinguishing AI questions, candidate responses, AI reasoning explanations, and system messages.

The design should feel more like a professional technical assessment tool than a casual chat app - balancing approachability with credibility. Emphasis on transparency and explainability of AI decisions.

## Target Device and Platforms

**Web Responsive (Desktop Primary, Tablet Secondary)**: Optimized for desktop browsers (Chrome, Firefox, Safari, Edge) with 1920x1080 and 1366x768 viewport support. Tablet support (iPad landscape) for recruiter review workflows. Mobile devices out of scope for MVP - interviews require focused desktop/laptop environment.
