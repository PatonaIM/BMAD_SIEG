"use client"

import { ResumeResponse } from "@/lib/api/resumes"
import { ResumeCard } from "./resume-card"

interface ResumeListProps {
  resumes: ResumeResponse[]
}

export function ResumeList({ resumes }: ResumeListProps) {
  if (!resumes || resumes.length === 0) {
    return (
      <div className="text-center py-8 text-muted-foreground">
        <p>No resumes uploaded yet</p>
      </div>
    )
  }

  // Sort by upload date (newest first)
  const sortedResumes = [...resumes].sort((a, b) => 
    new Date(b.uploaded_at).getTime() - new Date(a.uploaded_at).getTime()
  )

  return (
    <div className="space-y-3">
      {sortedResumes.map((resume) => (
        <ResumeCard key={resume.id} resume={resume} />
      ))}
    </div>
  )
}
