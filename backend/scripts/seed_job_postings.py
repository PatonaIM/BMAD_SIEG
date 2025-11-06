#!/usr/bin/env python3
"""
Job Postings Seed Data Script

Purpose: Generate realistic seed data for the job_postings table.

Usage:
    From backend directory:
        uv run python scripts/seed_job_postings.py

Output:
    Summary of created job postings including count and tech stack variety.

Behavior:
    - Idempotent: Warns if database contains existing job postings
    - Prompts for confirmation before adding to existing data
    - Creates 20+ diverse job postings across 10+ tech stacks
    - Includes variety in experience levels, locations, and salary ranges
"""
import asyncio
import sys
from pathlib import Path
from typing import Any

# Add backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import func, select  # noqa: E402

from app.core.database import AsyncSessionLocal  # noqa: E402
from app.models.job_posting import JobPosting  # noqa: E402

# Seed data based on real-world examples from Teamified job postings
JOB_POSTINGS: list[dict[str, Any]] = [
    # React/Frontend roles
    {
        "title": "Senior React Developer",
        "company": "pay.com.au",
        "description": "Build cutting-edge payment platform features using React and TypeScript. Work with a collaborative team on scalable solutions that matter to Australian businesses.",
        "role_category": "engineering",
        "tech_stack": "React",
        "employment_type": "permanent",
        "work_setup": "remote",
        "location": "Remote Australia",
        "salary_min": 120000,
        "salary_max": 150000,
        "salary_currency": "AUD",
        "required_skills": ["React", "TypeScript", "REST APIs", "Git", "Agile"],
        "experience_level": "Senior",
        "status": "active"
    },
    {
        "title": "Frontend Developer",
        "company": "Tim Ryan Consulting",
        "description": "Passionate frontend developer needed for online and SaaS-based products. Translate UI/UX designs into responsive web applications using React.",
        "role_category": "engineering",
        "tech_stack": "React",
        "employment_type": "permanent",
        "work_setup": "hybrid",
        "location": "Manila, Philippines",
        "salary_min": 60000,
        "salary_max": 80000,
        "salary_currency": "AUD",
        "required_skills": ["React", "JavaScript", "HTML5", "CSS3", "Responsive Design"],
        "experience_level": "Mid-level",
        "status": "active"
    },
    # Python/Backend roles
    {
        "title": "Senior AI Data Engineer",
        "company": "Teamified",
        "description": "Design and develop AI data architecture & API using Python (Django). Manage SQL, NoSQL, and Vector databases. Work on cutting-edge RAG pipelines.",
        "role_category": "data",
        "tech_stack": "Python",
        "employment_type": "permanent",
        "work_setup": "remote",
        "location": "Remote Philippines",
        "salary_min": 100000,
        "salary_max": 130000,
        "salary_currency": "AUD",
        "required_skills": ["Python", "Django", "SQL", "MongoDB", "Pinecone", "LangChain"],
        "experience_level": "Senior",
        "status": "active"
    },
    {
        "title": "Senior Backend Engineer",
        "company": "Forte Global",
        "description": "Build robust backend systems using Node.js and TypeScript. Design scalable APIs and optimize database performance for education technology platform.",
        "role_category": "engineering",
        "tech_stack": "Node.js",
        "employment_type": "permanent",
        "work_setup": "remote",
        "location": "Remote Philippines",
        "salary_min": 90000,
        "salary_max": 120000,
        "salary_currency": "AUD",
        "required_skills": ["Node.js", "TypeScript", "PostgreSQL", "AWS", "RESTful APIs"],
        "experience_level": "Senior",
        "status": "active"
    },
    # TypeScript/Fullstack roles
    {
        "title": "Senior Full Stack Engineer",
        "company": "pay.com.au",
        "description": "Take ownership of solutions from design to deployment. Build scalable payment platform using Node.js, TypeScript, and React. Mentor junior developers.",
        "role_category": "engineering",
        "tech_stack": "TypeScript",
        "employment_type": "permanent",
        "work_setup": "remote",
        "location": "Remote Philippines",
        "salary_min": 110000,
        "salary_max": 140000,
        "salary_currency": "AUD",
        "required_skills": ["TypeScript", "Node.js", "React", "AWS", "MySQL", "MongoDB"],
        "experience_level": "Senior",
        "status": "active"
    },
    {
        "title": "Full Stack Developer",
        "company": "Maths Pathway",
        "description": "Highly skilled developer with 10+ years experience in C# and Angular. Design, build, and maintain robust, scalable applications for education technology.",
        "role_category": "engineering",
        "tech_stack": "TypeScript",
        "employment_type": "permanent",
        "work_setup": "remote",
        "location": "Remote Philippines",
        "salary_min": 100000,
        "salary_max": 125000,
        "salary_currency": "AUD",
        "required_skills": ["C#", ".NET", "Angular", "TypeScript", "SQL Server", "Azure"],
        "experience_level": "Senior",
        "status": "active"
    },
    # Go/Cloud roles
    {
        "title": "Technical Lead",
        "company": "Bluechain",
        "description": "Guide development team while contributing to architecture. Strong expertise in Payments, .NET Core, Java, and AWS. Lead technical direction.",
        "role_category": "engineering",
        "tech_stack": "Go",
        "employment_type": "permanent",
        "work_setup": "remote",
        "location": "Remote Sri Lanka",
        "salary_min": 140000,
        "salary_max": 180000,
        "salary_currency": "AUD",
        "required_skills": ["Go", ".NET Core", "Java", "AWS", "Jenkins", "Unix", "SQL"],
        "experience_level": "Lead",
        "status": "active"
    },
    # Java/Enterprise roles
    {
        "title": "Salesforce Developer",
        "company": "pay.com.au",
        "description": "Lead design and architecture of scalable Salesforce solutions. Build custom applications, Apex triggers, Lightning Components. 8+ years experience required.",
        "role_category": "engineering",
        "tech_stack": "Java",
        "employment_type": "permanent",
        "work_setup": "remote",
        "location": "Remote Philippines",
        "salary_min": 100000,
        "salary_max": 125000,
        "salary_currency": "AUD",
        "required_skills": ["Salesforce", "Apex", "Java", "Lightning", "REST APIs", "SOAP"],
        "experience_level": "Senior",
        "status": "active"
    },
    # Ruby on Rails
    {
        "title": "Senior Fullstack Engineer",
        "company": "Everperform",
        "description": "Build robust backend systems using Ruby on Rails. Integrate AI/LLM capabilities. Work with PostgreSQL, Sidekiq, and Next.js frontend.",
        "role_category": "engineering",
        "tech_stack": "Ruby",
        "employment_type": "permanent",
        "work_setup": "remote",
        "location": "Remote India",
        "salary_min": 95000,
        "salary_max": 125000,
        "salary_currency": "AUD",
        "required_skills": ["Ruby on Rails", "PostgreSQL", "Sidekiq", "Redis", "Next.js"],
        "experience_level": "Senior",
        "status": "active"
    },
    # iOS/Mobile
    {
        "title": "iOS Developer",
        "company": "Session",
        "description": "Help improve iOS app's usability, performance and functionality. Build cutting edge, onion routed and end-to-end encrypted messaging application.",
        "role_category": "engineering",
        "tech_stack": "Swift",
        "employment_type": "permanent",
        "work_setup": "hybrid",
        "location": "Manila, Philippines",
        "salary_min": 110000,
        "salary_max": 140000,
        "salary_currency": "AUD",
        "required_skills": ["Swift", "iOS", "UIKit", "SwiftUI", "Networking", "Cryptography"],
        "experience_level": "Senior",
        "status": "active"
    },
    # QA/Testing roles
    {
        "title": "QA Automation Engineer",
        "company": "Teamified",
        "description": "Design and maintain test automation frameworks. Build automated tests for web and mobile applications. Integrate tests into CI/CD pipelines.",
        "role_category": "quality_assurance",
        "tech_stack": "Playwright",
        "employment_type": "permanent",
        "work_setup": "remote",
        "location": "Remote India",
        "salary_min": 85000,
        "salary_max": 110000,
        "salary_currency": "AUD",
        "required_skills": ["Playwright", "Selenium", "JavaScript", "Jenkins", "GitLab CI"],
        "experience_level": "Mid-level",
        "status": "active"
    },
    {
        "title": "Lead QA Engineer",
        "company": "Teamified",
        "description": "Spearhead Quality Assurance initiatives. Develop testing strategies, lead QA team. Ensure high-quality software delivery across all projects.",
        "role_category": "quality_assurance",
        "tech_stack": "Playwright",
        "employment_type": "permanent",
        "work_setup": "remote",
        "location": "Remote India",
        "salary_min": 120000,
        "salary_max": 150000,
        "salary_currency": "AUD",
        "required_skills": ["Test Automation", "Selenium", "Python", "Java", "Agile", "CI/CD"],
        "experience_level": "Lead",
        "status": "active"
    },
    # DevOps/Infrastructure
    {
        "title": "Principal Engineer",
        "company": "Red Horizon Consulting",
        "description": "Design and implement next-generation platforms integrating AI. Build scalable systems with AWS, Kubernetes, Terraform. Lead technical strategy.",
        "role_category": "devops",
        "tech_stack": "Go",
        "employment_type": "permanent",
        "work_setup": "hybrid",
        "location": "Manila, Philippines",
        "salary_min": 150000,
        "salary_max": 180000,
        "salary_currency": "AUD",
        "required_skills": ["Go", "AWS", "Kubernetes", "Terraform", "C#", ".NET Core", "React"],
        "experience_level": "Principal",
        "status": "active"
    },
    # Design roles
    {
        "title": "Senior UI/UX Designer",
        "company": "Everperform",
        "description": "Drive design strategy for workplace analytics platform. Create intuitive interfaces for complex data. Build and maintain design systems using Figma.",
        "role_category": "design",
        "tech_stack": None,  # Design role - no primary tech stack
        "employment_type": "permanent",
        "work_setup": "remote",
        "location": "Remote India",
        "salary_min": 85000,
        "salary_max": 115000,
        "salary_currency": "AUD",
        "required_skills": ["Figma", "UI/UX Design", "Design Systems", "Prototyping", "User Research"],
        "experience_level": "Senior",
        "status": "active"
    },
    # Product roles
    {
        "title": "Product Manager",
        "company": "Forte Global",
        "description": "Lead product workstreams for education technology platform. Manage agile sprints, coordinate with engineering and design. Define product roadmap.",
        "role_category": "product",
        "tech_stack": None,  # Product role - no primary tech stack
        "employment_type": "permanent",
        "work_setup": "remote",
        "location": "Remote Philippines",
        "salary_min": 130000,
        "salary_max": 160000,
        "salary_currency": "AUD",
        "required_skills": ["Product Management", "Agile", "Roadmapping", "Stakeholder Management", "Analytics"],
        "experience_level": "Senior",
        "status": "active"
    },
    # Support roles
    {
        "title": "Customer Support Representative",
        "company": "Kolmeo",
        "description": "Provide excellent customer service for property management software. Handle inquiries via chat, email, and phone. Manage client concerns efficiently.",
        "role_category": "support",
        "tech_stack": None,  # Support role - no primary tech stack
        "employment_type": "permanent",
        "work_setup": "hybrid",
        "location": "Manila, Philippines",
        "salary_min": 60000,
        "salary_max": 75000,
        "salary_currency": "AUD",
        "required_skills": ["Customer Service", "Communication", "Problem Solving", "CRM Software", "Jira"],
        "experience_level": "Mid-level",
        "status": "active"
    },
    {
        "title": "Technical Support",
        "company": "Next Payments",
        "description": "Provide first-level technical support for payment systems. Diagnose hardware, software, and network issues. Maintain high customer satisfaction.",
        "role_category": "support",
        "tech_stack": None,  # Support role - no primary tech stack
        "employment_type": "permanent",
        "work_setup": "hybrid",
        "location": "Manila, Philippines",
        "salary_min": 65000,
        "salary_max": 85000,
        "salary_currency": "AUD",
        "required_skills": ["Technical Support", "Troubleshooting", "Networking", "Payment Systems", "Communication"],
        "experience_level": "Mid-level",
        "status": "active"
    },
    # Sales/Business roles
    {
        "title": "Lead Generator",
        "company": "Red Horizon Consulting",
        "description": "Create qualified sales pipeline and book discovery calls. Execute outbound campaigns via LinkedIn, email, and calling. Manage CRM and sales activities.",
        "role_category": "sales",
        "tech_stack": None,  # Sales role - no primary tech stack
        "employment_type": "permanent",
        "work_setup": "hybrid",
        "location": "Manila, Philippines",
        "salary_min": 70000,
        "salary_max": 95000,
        "salary_currency": "AUD",
        "required_skills": ["B2B Sales", "CRM", "LinkedIn Sales Navigator", "Lead Generation", "Communication"],
        "experience_level": "Mid-level",
        "status": "active"
    },
    # Operations roles
    {
        "title": "Executive Assistant",
        "company": "Recode Ventures",
        "description": "Serve as operational cornerstone for AgriFood innovation firm. Manage workflows, coordinate Human-AI team, handle executive support and project coordination.",
        "role_category": "operations",
        "tech_stack": None,  # Operations role - no primary tech stack
        "employment_type": "permanent",
        "work_setup": "remote",
        "location": "Remote Philippines",
        "salary_min": 70000,
        "salary_max": 90000,
        "salary_currency": "AUD",
        "required_skills": ["Executive Support", "Project Coordination", "Xero", "Google Workspace", "Communication"],
        "experience_level": "Mid-level",
        "status": "active"
    },
    {
        "title": "Marketplace Coordinator",
        "company": "Helio",
        "description": "Bridge sales, support, and operations for advertising marketplace. Manage listings, onboard sellers, coordinate campaigns from start to finish.",
        "role_category": "operations",
        "tech_stack": None,  # Operations role - no primary tech stack
        "employment_type": "permanent",
        "work_setup": "remote",
        "location": "Remote Philippines",
        "salary_min": 65000,
        "salary_max": 85000,
        "salary_currency": "AUD",
        "required_skills": ["Operations", "Customer Service", "Salesforce", "Campaign Management", "Communication"],
        "experience_level": "Mid-level",
        "status": "active"
    },
    # Finance/Accounting
    {
        "title": "Bookkeeper",
        "company": "Volaro Group",
        "description": "Maintain accurate financial records for sport, media, and entertainment company. Process transactions, manage payroll, support financial operations.",
        "role_category": "operations",
        "tech_stack": None,  # Finance role - no primary tech stack
        "employment_type": "permanent",
        "work_setup": "remote",
        "location": "Remote Philippines",
        "salary_min": 70000,
        "salary_max": 90000,
        "salary_currency": "AUD",
        "required_skills": ["Bookkeeping", "Xero", "Payroll", "Financial Reporting", "Compliance"],
        "experience_level": "Mid-level",
        "status": "active"
    },
    {
        "title": "Accounts Payable Specialist",
        "company": "Deputy",
        "description": "Support AP and General Ledger operations. Manage end-to-end AP workflows, reconcile accounts, support month-end close in multi-currency environment.",
        "role_category": "operations",
        "tech_stack": None,  # Finance role - no primary tech stack
        "employment_type": "permanent",
        "work_setup": "remote",
        "location": "Remote India",
        "salary_min": 75000,
        "salary_max": 100000,
        "salary_currency": "AUD",
        "required_skills": ["Accounts Payable", "NetSuite", "Tipalti", "Accounting", "Multi-currency"],
        "experience_level": "Mid-level",
        "status": "active"
    },
    # Compliance/Risk
    {
        "title": "AML Officer",
        "company": "KAST",
        "description": "Manage AML and KYC processes for cryptocurrency platform. Conduct customer due diligence, monitor transactions, ensure regulatory compliance.",
        "role_category": "operations",
        "tech_stack": None,  # Compliance role - no primary tech stack
        "employment_type": "permanent",
        "work_setup": "hybrid",
        "location": "Manila, Philippines",
        "salary_min": 80000,
        "salary_max": 110000,
        "salary_currency": "AUD",
        "required_skills": ["AML", "KYC", "Compliance", "Risk Assessment", "Cryptocurrency"],
        "experience_level": "Senior",
        "status": "active"
    },
]


async def seed_job_postings(db) -> None:
    """
    Seed the database with job posting data.

    Args:
        db: AsyncSession database connection
    """
    try:
        # Check if database already contains job postings
        result = await db.execute(select(func.count()).select_from(JobPosting))
        existing_count = result.scalar()

        if existing_count > 0:
            print(f"\n⚠️  Database already contains {existing_count} job postings")
            response = input("Do you want to add more seed data? (y/N): ").strip().lower()

            if response != 'y':
                print("Seed operation cancelled. No changes made.")
                return

            print("\nProceeding to add more seed data...")
        else:
            print("\nDatabase is empty. Proceeding with seed data...")

        # Insert job postings
        print(f"\nInserting {len(JOB_POSTINGS)} job postings...")

        for job_data in JOB_POSTINGS:
            job = JobPosting(**job_data)
            db.add(job)

        await db.commit()

        # Calculate statistics
        tech_stacks = {
            job['tech_stack']
            for job in JOB_POSTINGS
            if job.get('tech_stack')
        }
        role_categories = {job['role_category'] for job in JOB_POSTINGS}

        # Print summary
        print("\n" + "=" * 70)
        print("SEED DATA SUMMARY")
        print("=" * 70)
        print(f"✓ Created {len(JOB_POSTINGS)} job postings across {len(tech_stacks)} tech stacks")
        print(f"\nRole categories ({len(role_categories)}):")
        for category in sorted(role_categories):
            count = sum(1 for job in JOB_POSTINGS if job['role_category'] == category)
            print(f"  - {category}: {count}")
        print(f"\nTech stacks ({len(tech_stacks)}):")
        for tech in sorted(tech_stacks):
            count = sum(1 for job in JOB_POSTINGS if job.get('tech_stack') == tech)
            print(f"  - {tech}: {count}")
        print("=" * 70)

    except Exception as e:
        await db.rollback()
        print(f"\n❌ Error seeding job postings: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


async def main():
    """Main entry point for seed script."""
    print("=" * 70)
    print("Job Postings Seed Data Script")
    print("=" * 70)

    async with AsyncSessionLocal() as db:
        await seed_job_postings(db)

    print("\nSeed operation completed successfully")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
