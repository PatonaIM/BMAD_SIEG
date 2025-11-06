<!-- Updated: 2025-11-05 - Added Epic 03 job_postings and applications tables documentation -->

# Database Schema

## PostgreSQL DDL (Data Definition Language)

```sql
-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Candidates table
CREATE TABLE candidates (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    phone VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'deleted'))
);

CREATE INDEX idx_candidates_email ON candidates(email);
CREATE INDEX idx_candidates_status ON candidates(status);

-- Resumes table
CREATE TABLE resumes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    candidate_id UUID NOT NULL REFERENCES candidates(id) ON DELETE CASCADE,
    file_url TEXT NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    file_size INTEGER NOT NULL,
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    parsed_at TIMESTAMP WITH TIME ZONE,
    parsing_status VARCHAR(20) NOT NULL DEFAULT 'pending' CHECK (parsing_status IN ('pending', 'processing', 'completed', 'failed')),
    parsed_data JSONB
);

CREATE INDEX idx_resumes_candidate_id ON resumes(candidate_id);
CREATE INDEX idx_resumes_parsing_status ON resumes(parsing_status);
CREATE INDEX idx_resumes_parsed_data ON resumes USING GIN (parsed_data);  -- For JSONB queries

-- ResumeFeedback table
CREATE TABLE resume_feedback (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    resume_id UUID UNIQUE NOT NULL REFERENCES resumes(id) ON DELETE CASCADE,
    feedback_content TEXT NOT NULL,
    identified_gaps JSONB,
    recommended_resources JSONB,
    status VARCHAR(20) NOT NULL DEFAULT 'draft' CHECK (status IN ('draft', 'pending_approval', 'approved', 'sent')),
    generated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    approved_at TIMESTAMP WITH TIME ZONE,
    approved_by UUID REFERENCES recruiters(id),
    sent_at TIMESTAMP WITH TIME ZONE,
    auto_send_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_resume_feedback_resume_id ON resume_feedback(resume_id);
CREATE INDEX idx_resume_feedback_status ON resume_feedback(status);
CREATE INDEX idx_resume_feedback_auto_send ON resume_feedback(auto_send_at) WHERE status = 'pending_approval';

-- Interviews table
CREATE TABLE interviews (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    candidate_id UUID NOT NULL REFERENCES candidates(id) ON DELETE CASCADE,
    resume_id UUID REFERENCES resumes(id),
    role_type VARCHAR(50) NOT NULL CHECK (role_type IN ('react', 'python', 'javascript', 'fullstack')),
    status VARCHAR(20) NOT NULL DEFAULT 'scheduled' CHECK (status IN ('scheduled', 'in_progress', 'completed', 'abandoned')),
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    duration_seconds INTEGER,
    ai_model_used VARCHAR(50),
    total_tokens_used INTEGER DEFAULT 0,
    cost_usd DECIMAL(10, 4) DEFAULT 0.0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_interviews_candidate_id ON interviews(candidate_id);
CREATE INDEX idx_interviews_status ON interviews(status);
CREATE INDEX idx_interviews_created_at ON interviews(created_at);

-- InterviewSessions table
CREATE TABLE interview_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    interview_id UUID UNIQUE NOT NULL REFERENCES interviews(id) ON DELETE CASCADE,
    conversation_memory JSONB,
    current_difficulty_level VARCHAR(20) DEFAULT 'warmup' CHECK (current_difficulty_level IN ('warmup', 'standard', 'advanced')),
    questions_asked_count INTEGER DEFAULT 0,
    skill_boundaries_identified JSONB,
    progression_state JSONB,
    last_activity_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_interview_sessions_interview_id ON interview_sessions(interview_id);
CREATE INDEX idx_interview_sessions_last_activity ON interview_sessions(last_activity_at);

-- InterviewMessages table
CREATE TABLE interview_messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    interview_id UUID NOT NULL REFERENCES interviews(id) ON DELETE CASCADE,
    session_id UUID NOT NULL REFERENCES interview_sessions(id) ON DELETE CASCADE,
    sequence_number INTEGER NOT NULL,
    message_type VARCHAR(20) NOT NULL CHECK (message_type IN ('ai_question', 'candidate_response')),
    content_text TEXT NOT NULL,
    content_audio_url TEXT,
    audio_duration_seconds INTEGER,
    audio_metadata JSONB,
    response_time_seconds INTEGER,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_interview_messages_interview_id ON interview_messages(interview_id);
CREATE INDEX idx_interview_messages_session_id ON interview_messages(session_id);
CREATE INDEX idx_interview_messages_sequence ON interview_messages(interview_id, sequence_number);

-- AssessmentResults table
CREATE TABLE assessment_results (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    interview_id UUID UNIQUE NOT NULL REFERENCES interviews(id) ON DELETE CASCADE,
    overall_score DECIMAL(5, 2) NOT NULL CHECK (overall_score >= 0 AND overall_score <= 100),
    skill_scores JSONB NOT NULL,
    skill_boundary_map JSONB,
    strengths JSONB,
    weaknesses JSONB,
    integrity_score DECIMAL(5, 2) CHECK (integrity_score >= 0 AND integrity_score <= 100),
    integrity_flags JSONB,
    ai_reasoning JSONB,
    recommended_actions JSONB,
    generated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_assessment_results_interview_id ON assessment_results(interview_id);
CREATE INDEX idx_assessment_results_overall_score ON assessment_results(overall_score);

-- Recruiters table
CREATE TABLE recruiters (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'recruiter' CHECK (role IN ('recruiter', 'admin', 'viewer')),
    organization_id UUID,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_login_at TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE INDEX idx_recruiters_email ON recruiters(email);
CREATE INDEX idx_recruiters_organization_id ON recruiters(organization_id);

-- Job Postings table (Epic 03)
CREATE TYPE role_category AS ENUM ('engineering', 'quality_assurance', 'data', 'devops', 'design', 'product', 'sales', 'support', 'operations', 'management', 'other');
CREATE TYPE employment_type AS ENUM ('permanent', 'contract', 'part_time');
CREATE TYPE work_setup AS ENUM ('remote', 'hybrid', 'onsite');
CREATE TYPE job_posting_status AS ENUM ('active', 'paused', 'closed');

CREATE TABLE job_postings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(255) NOT NULL,  -- e.g., "Senior React Developer"
    company VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    role_category role_category NOT NULL,  -- Job function/department
    tech_stack VARCHAR(100),  -- Primary technology (e.g., 'React', 'Python', 'TypeScript')
    employment_type employment_type NOT NULL,
    work_setup work_setup NOT NULL,
    location VARCHAR(255) NOT NULL,
    salary_min NUMERIC(10, 2),
    salary_max NUMERIC(10, 2),
    salary_currency VARCHAR(3) NOT NULL DEFAULT 'AUD',
    required_skills JSONB,  -- Array of required skills
    experience_level VARCHAR(50) NOT NULL,  -- e.g., "Junior", "Mid-level", "Senior"
    status job_posting_status NOT NULL DEFAULT 'active',
    is_cancelled BOOLEAN NOT NULL DEFAULT FALSE,
    cancellation_reason TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for job_postings
CREATE INDEX idx_job_postings_role_category ON job_postings(role_category);
CREATE INDEX idx_job_postings_tech_stack ON job_postings(tech_stack) WHERE tech_stack IS NOT NULL;
CREATE INDEX idx_job_postings_status ON job_postings(status) WHERE status = 'active';
CREATE INDEX idx_job_postings_employment_type ON job_postings(employment_type);
CREATE INDEX idx_job_postings_created_at ON job_postings(created_at);

-- Applications table (Epic 03)
CREATE TYPE application_status AS ENUM ('applied', 'interview_scheduled', 'interview_completed', 'under_review', 'rejected', 'offered', 'accepted', 'withdrawn');

CREATE TABLE applications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    candidate_id UUID NOT NULL REFERENCES candidates(id) ON DELETE CASCADE,
    job_posting_id UUID NOT NULL REFERENCES job_postings(id) ON DELETE CASCADE,
    interview_id UUID REFERENCES interviews(id) ON DELETE SET NULL,
    status application_status NOT NULL DEFAULT 'applied',
    applied_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_applications_candidate_job UNIQUE (candidate_id, job_posting_id)  -- Prevents duplicate applications
);

-- Indexes for applications
CREATE INDEX idx_applications_candidate_id ON applications(candidate_id);
CREATE INDEX idx_applications_job_posting_id ON applications(job_posting_id);
CREATE INDEX idx_applications_interview_id ON applications(interview_id);
CREATE INDEX idx_applications_status ON applications(status);
CREATE INDEX idx_applications_applied_at ON applications(applied_at);

-- IntegrationWebhooks table (Epic 5 - Future)
CREATE TABLE integration_webhooks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID,
    webhook_url TEXT NOT NULL,
    webhook_secret VARCHAR(255) NOT NULL,
    event_types JSONB NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    last_triggered_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_integration_webhooks_organization_id ON integration_webhooks(organization_id);

-- Trigger for updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
   NEW.updated_at = CURRENT_TIMESTAMP;
   RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_candidates_updated_at
BEFORE UPDATE ON candidates
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();
```

---

## Alembic Migration Strategy

**Initial Migration (v1):**
```bash
# Generate migration
alembic revision --autogenerate -m "Initial schema with all tables"

# Apply migration
alembic upgrade head
```

**Future Migrations (Example):**
```bash
# Add new column
alembic revision -m "Add interview_type to interviews"
alembic upgrade head

# Rollback
alembic downgrade -1
```

**Migration File Structure:**
```
backend/
└── alembic/
    ├── versions/
    │   ├── 001_initial_schema.py
    │   ├── 002_add_interview_types.py
    │   └── ...
    ├── env.py
    └── script.py.mako
```

---

## Database Seeding (Development)

```python
# backend/scripts/seed_dev_data.py

async def seed_development_data():
    """Seed database with test data for development"""
    
    # Create test candidate
    candidate = Candidate(
        email="test@example.com",
        full_name="Test Candidate",
        password_hash=hash_password("TestPass123!"),
        status="active"
    )
    
    # Create test recruiter
    recruiter = Recruiter(
        email="recruiter@teamified.com",
        full_name="Test Recruiter",
        password_hash=hash_password("RecruiterPass123!"),
        role="admin"
    )
    
    # Add sample interview with messages
    # ...
```

---

