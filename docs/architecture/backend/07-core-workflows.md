# Core Workflows

## Workflow 1: Candidate Completes AI Interview (Speech-Based)

**Trigger:** Candidate clicks "Start Interview" button

**Actors:** Candidate, Frontend, Backend, OpenAI API, Database

\`\`\`mermaid
sequenceDiagram
    participant C as Candidate
    participant FE as Frontend
    participant API as API Gateway
    participant Auth as Auth Service
    participant IE as Interview Engine
    participant Speech as Speech Service
    participant OpenAI as OpenAI API
    participant DB as Database

    C->>FE: Click "Start Interview"
    FE->>API: POST /api/v1/interviews {candidate_id, resume_id, role_type}
    API->>Auth: Verify JWT
    Auth-->>API: Authorized
    
    API->>IE: start_interview()
    IE->>DB: CREATE Interview record (status='in_progress')
    IE->>DB: CREATE InterviewSession record
    IE->>OpenAI: Generate first question (GPT-4o-mini)
    OpenAI-->>IE: "Tell me about your React experience..."
    
    IE->>Speech: synthesize_speech(question_text)
    Speech->>OpenAI: TTS API call
    OpenAI-->>Speech: Audio file (MP3)
    Speech->>DB: Store audio URL
    
    IE->>DB: INSERT InterviewMessage (type='ai_question')
    IE-->>API: {audio_url, text, session_id}
    API-->>FE: Interview started successfully
    FE->>C: Play audio question
    
    Note over C,FE: Candidate speaks answer
    
    C->>FE: Audio recorded (WebM/Opus)
    FE->>API: POST /api/v1/interviews/{id}/messages {audio_data}
    API->>Auth: Verify JWT
    Auth-->>API: Authorized
    
    API->>Speech: transcribe_audio(audio_data)
    Speech->>OpenAI: Whisper API call
    OpenAI-->>Speech: Transcription + confidence
    Speech->>DB: Store audio URL + metadata
    
    API->>IE: process_candidate_response(interview_id, text)
    IE->>DB: INSERT InterviewMessage (type='candidate_response')
    IE->>DB: UPDATE InterviewSession (skill_boundaries, progression_state)
    
    IE->>OpenAI: Generate next question based on response
    OpenAI-->>IE: Next contextual question
    
    IE->>Speech: synthesize_speech(next_question)
    Speech->>OpenAI: TTS API call
    OpenAI-->>Speech: Audio file
    
    IE->>DB: INSERT InterviewMessage (type='ai_question')
    IE-->>API: {audio_url, text, next_question}
    API-->>FE: Next question ready
    FE->>C: Play next audio question
    
    Note over C,FE: Loop continues for 12-20 questions
    
    C->>FE: Click "Submit Interview"
    FE->>API: POST /api/v1/interviews/{id}/complete
    API->>IE: complete_interview(interview_id)
    IE->>DB: UPDATE Interview (status='completed', completed_at=NOW)
    
    IE->>IE: Trigger async assessment scoring
    Note over IE: BackgroundTask starts
    
    IE-->>API: Interview completed
    API-->>FE: Success, redirecting to results page
    FE->>C: Show "Processing assessment..." screen
    
    Note over IE,DB: Background assessment generation
    IE->>DB: Load all InterviewMessages
    IE->>OpenAI: Analyze conversation for scoring
    OpenAI-->>IE: Skill scores + reasoning
    IE->>OpenAI: Analyze integrity flags
    OpenAI-->>IE: Integrity analysis
    IE->>DB: INSERT AssessmentResult
    
    Note over C: Candidate can view results when ready
\`\`\`

**Key Steps:**
1. Interview creation with resume context
2. First AI question generation and TTS synthesis
3. Repeated question-answer loop (12-20 exchanges)
4. Real-time transcription via Whisper
5. Progressive difficulty adjustment based on responses
6. Interview completion trigger
7. Async assessment scoring generation

**Error Handling:**
- **OpenAI Rate Limit:** Queue request, show "Generating question..." spinner
- **Whisper Transcription Failure:** Allow candidate to re-record answer
- **TTS Failure:** Display text question as fallback
- **Network Interruption:** Session state persisted, resume from last question

---

## Workflow 2: Resume Upload to Feedback Generation

**Trigger:** Candidate uploads resume file

**Actors:** Candidate, Frontend, Backend, OpenAI API, Recruiter

\`\`\`mermaid
sequenceDiagram
    participant C as Candidate
    participant FE as Frontend
    participant API as API Gateway
    participant Resume as Resume Parser Service
    participant Storage as Supabase Storage
    participant OpenAI as OpenAI API
    participant DB as Database
    participant Email as Email Service
    participant R as Recruiter

    C->>FE: Upload resume file (PDF/DOCX)
    FE->>API: POST /api/v1/resumes {file, candidate_id}
    API->>Resume: upload_resume(file, candidate_id)
    
    Resume->>Storage: Upload file to 'resumes' bucket
    Storage-->>Resume: {file_url}
    
    Resume->>DB: INSERT Resume (status='pending', file_url)
    Resume-->>API: {resume_id, status='pending'}
    API-->>FE: Upload successful
    FE->>C: Show "Processing resume..." message
    
    Note over Resume: Background task triggered
    
    Resume->>Resume: parse_resume_async(resume_id)
    Resume->>DB: UPDATE Resume (status='processing')
    
    Resume->>Storage: Download file from Supabase
    Storage-->>Resume: File bytes
    
    Resume->>Resume: Extract text (PyPDF2/python-docx)
    Resume->>OpenAI: Parse resume for skills (GPT-4o-mini)
    OpenAI-->>Resume: Structured data (skills, experience, etc.)
    
    Resume->>DB: UPDATE Resume (parsed_data, status='completed', parsed_at=NOW)
    
    Resume->>OpenAI: Generate feedback email (GPT-4o-mini)
    OpenAI-->>Resume: Feedback content + improvement suggestions
    
    Resume->>DB: INSERT ResumeFeedback (status='pending_approval', auto_send_at=+4 hours)
    
    Note over R: Recruiter dashboard shows pending feedback
    
    alt Recruiter approves within 4 hours
        R->>FE: Review feedback, click "Approve & Send"
        FE->>API: POST /api/v1/resumes/{id}/feedback/approve {recruiter_id}
        API->>Resume: approve_feedback(feedback_id, recruiter_id)
        Resume->>DB: UPDATE ResumeFeedback (status='approved', approved_at=NOW, approved_by)
        Resume->>Email: send_email(candidate_email, feedback_content)
        Email-->>Resume: Email sent
        Resume->>DB: UPDATE ResumeFeedback (status='sent', sent_at=NOW)
        Resume-->>API: Feedback sent
        API-->>FE: Success
        FE->>R: Show confirmation
    else Auto-send after 4 hours (no manual action)
        Note over Resume: Scheduled task runs every 5 minutes
        Resume->>DB: SELECT ResumeFeedback WHERE status='pending_approval' AND auto_send_at <= NOW
        Resume->>Email: send_email(candidate_email, feedback_content)
        Email-->>Resume: Email sent
        Resume->>DB: UPDATE ResumeFeedback (status='sent', sent_at=NOW)
    end
    
    Note over C: Candidate receives feedback email
\`\`\`

**Key Steps:**
1. File upload to Supabase Storage
2. Resume record created with `pending` status
3. Background task extracts text from PDF/DOCX
4. GPT-4o-mini parses skills and experience
5. GPT-4o-mini generates feedback email
6. Recruiter approval workflow (4-hour window)
7. Auto-send if not manually reviewed

**SLA:** 24 hours from upload to feedback delivery (NFR15)

**Error Handling:**
- **File Format Invalid:** Return 400 with "Only PDF/DOCX supported"
- **AI Parsing Failure:** Retry 3 times, then mark as `failed` and alert recruiter
- **Email Delivery Failure:** Retry with exponential backoff, log failure after 5 attempts

---

## Workflow 3: Interview Scoring and Assessment Generation

**Trigger:** Interview marked as `completed`

**Actors:** Background Task, Interview Engine, OpenAI API, Database

\`\`\`mermaid
sequenceDiagram
    participant BG as Background Task
    participant IE as Interview Engine
    participant Scoring as Assessment Scoring Service
    participant DB as Database
    participant OpenAI as OpenAI API

    Note over BG: Triggered when interview status='completed'
    
    BG->>Scoring: generate_assessment(interview_id)
    Scoring->>DB: Load Interview record
    Scoring->>DB: Load all InterviewMessages (questions + answers)
    Scoring->>DB: Load InterviewSession (skill_boundaries, progression_state)
    
    Note over Scoring: Multi-pass analysis begins
    
    Scoring->>Scoring: PASS 1 - Technical Scoring
    Scoring->>OpenAI: Analyze responses for technical competency (GPT-4o-mini)
    OpenAI-->>Scoring: {react_fundamentals: 85, hooks: 72, performance: 45}
    
    Scoring->>Scoring: PASS 2 - Integrity Analysis
    Scoring->>OpenAI: Detect timing anomalies, inconsistencies (GPT-4o-mini)
    OpenAI-->>Scoring: [{type: "fast_response", severity: "medium", evidence: "..."}]
    
    Scoring->>Scoring: PASS 3 - AI Reasoning Generation
    Scoring->>OpenAI: Generate explanations for scores (GPT-4o-mini)
    OpenAI-->>Scoring: "Strong understanding of hooks but lacks optimization experience..."
    
    Scoring->>Scoring: PASS 4 - Recommendations
    Scoring->>OpenAI: Generate recruiter action items (GPT-4o-mini)
    OpenAI-->>Scoring: ["Schedule technical deep-dive", "Test optimization knowledge in coding task"]
    
    Scoring->>Scoring: Aggregate results
    Scoring->>DB: INSERT AssessmentResult (all scoring data)
    
    Scoring->>DB: UPDATE Interview (status='completed', cost_usd calculated)
    
    Scoring-->>BG: Assessment complete
    
    Note over DB: Recruiter can now view results in portal
\`\`\`

**Key Steps:**
1. Load interview conversation history
2. **Pass 1:** Technical skill scoring with evidence
3. **Pass 2:** Integrity flag detection
4. **Pass 3:** AI reasoning generation
5. **Pass 4:** Recruiter recommendations
6. Store comprehensive `AssessmentResult`

**Processing Time:** Target <30 seconds for standard interview (NFR6)

**Error Handling:**
- **OpenAI Timeout:** Retry with truncated conversation history
- **Scoring Failure:** Mark assessment as `failed`, alert admin, allow manual retry
- **Partial Success:** Store partial results, flag incomplete sections

---

## Workflow 4: Session Recovery (Interrupted Interview)

**Trigger:** Candidate network drops mid-interview

**Actors:** Candidate, Frontend, Backend

\`\`\`mermaid
sequenceDiagram
    participant C as Candidate
    participant FE as Frontend
    participant API as API Gateway
    participant IE as Interview Engine
    participant DB as Database

    Note over C,FE: Network interruption during question 7
    
    C->>FE: Browser reconnects
    FE->>FE: Check localStorage for active_interview_id
    FE->>API: GET /api/v1/interviews/{id}/status
    API->>DB: Load Interview record
    
    alt Interview status = 'in_progress'
        API->>DB: Load InterviewSession
        API->>DB: Load last 5 InterviewMessages
        API-->>FE: {status: 'in_progress', last_message, session_state}
        FE->>C: Show "Resume Interview" button
        
        C->>FE: Click "Resume Interview"
        FE->>API: GET /api/v1/interviews/{id}/messages/latest
        API->>DB: Get latest AI question
        API-->>FE: {audio_url, text}
        FE->>C: Replay last question
        
        Note over C: Interview continues from last question
    else Interview status = 'completed'
        API-->>FE: {status: 'completed', redirect_to: '/results/{id}'}
        FE->>C: Redirect to results page
    else Interview status = 'abandoned' (>30 min inactive)
        API-->>FE: {status: 'abandoned', can_restart: true}
        FE->>C: Show "Interview expired, start new interview"
    end
\`\`\`

**Key Features:**
- Session state persisted after every message
- Frontend stores `active_interview_id` in localStorage
- Backend tracks `last_activity_at` for abandonment detection
- 30-minute inactivity threshold for auto-abandonment

---

## Workflow 5: Candidate Registration & First Login

**Trigger:** Candidate clicks "Sign Up" from landing page

\`\`\`mermaid
sequenceDiagram
    participant C as Candidate
    participant FE as Frontend
    participant API as API Gateway
    participant Auth as Auth Service
    participant DB as Database

    C->>FE: Enter email, password, full name
    FE->>API: POST /api/v1/auth/register {email, password, full_name}
    API->>Auth: register_candidate()
    
    Auth->>DB: Check if email exists
    
    alt Email already exists
        DB-->>Auth: Email found
        Auth-->>API: Error 409 Conflict
        API-->>FE: "Email already registered"
        FE->>C: Show error, suggest login
    else Email available
        DB-->>Auth: Email available
        Auth->>Auth: Hash password (bcrypt, cost=12)
        Auth->>DB: INSERT Candidate (email, password_hash, full_name, status='active')
        DB-->>Auth: Candidate created
        
        Auth->>Auth: Generate JWT token (expires in 24h)
        Auth-->>API: {token, candidate_id, email}
        API-->>FE: Registration successful + JWT
        
        FE->>FE: Store JWT in localStorage
        FE->>C: Redirect to dashboard
        
        C->>FE: See "Upload Resume" and "Start Interview" options
    end
\`\`\`

**Validation Rules:**
- Email: Valid email format, unique
- Password: Min 8 characters, 1 uppercase, 1 number, 1 special char
- Full name: Min 2 characters

**Security:**
- Passwords hashed with bcrypt (cost factor 12)
- JWT signed with secret key (256-bit)
- HTTPS-only token transmission

---
