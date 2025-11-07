"use client"

import { useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { TagInput } from "@/components/ui/tag-input"
import Link from "next/link"
import { Save, ArrowLeft, AlertCircle, Loader2 } from "lucide-react"
import { useProfile } from "@/hooks/use-profile"
import { useUpdateSkills } from "@/hooks/use-profile-mutations"
import { useProfileStore } from "@/stores/profile-store"
import { COMMON_SKILLS } from "@/lib/constants/profile"

export default function SkillsPage() {
  const { data: profile, isLoading, isError, error } = useProfile()
  const { mutate: updateSkills, isPending } = useUpdateSkills()
  const { 
    selectedSkills, 
    initializeSkills, 
    formDirty,
    setFormDirty 
  } = useProfileStore()

  // Initialize skills from profile
  useEffect(() => {
    if (profile?.skills) {
      initializeSkills(profile.skills)
    }
  }, [profile?.skills, initializeSkills])

  const handleSkillsChange = (skills: string[]) => {
    initializeSkills(skills)
    setFormDirty(true)
  }

  const handleSave = () => {
    updateSkills(selectedSkills, {
      onSuccess: () => {
        setFormDirty(false)
      }
    })
  }

  if (isLoading) {
    return (
      <div className="w-full max-w-4xl mx-auto space-y-6">
        <Skeleton className="h-10 w-64" />
        <Skeleton className="h-96 w-full" />
      </div>
    )
  }

  if (isError || !profile) {
    return (
      <div className="w-full max-w-4xl mx-auto space-y-6">
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            {error?.message || "Failed to load profile. Please try again."}
          </AlertDescription>
        </Alert>
      </div>
    )
  }

  return (
    <div className="w-full max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <Button variant="ghost" size="sm" asChild className="mb-2">
            <Link href="/profile">
              <ArrowLeft className="mr-2 h-4 w-4" />
              Back to Profile
            </Link>
          </Button>
          <h1 className="text-3xl font-bold mb-2">Manage Skills</h1>
          <p className="text-muted-foreground">
            Add or remove skills to improve your job matches
          </p>
        </div>
        <Button 
          onClick={handleSave} 
          disabled={!formDirty || isPending}
          className="min-w-24"
        >
          {isPending ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Saving...
            </>
          ) : (
            <>
              <Save className="mr-2 h-4 w-4" />
              Save Changes
            </>
          )}
        </Button>
      </div>

      {/* Add Skills */}
      <Card>
        <CardHeader>
          <CardTitle>Manage Skills</CardTitle>
          <CardDescription>
            Add skills with autocomplete suggestions. Type and press Enter or comma to add.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <TagInput
            value={selectedSkills}
            onChange={handleSkillsChange}
            placeholder="Type a skill (e.g., React, Python, AWS)..."
            maxTags={50}
            suggestions={COMMON_SKILLS}
          />
          <p className="text-xs text-muted-foreground">
            Press Enter or comma to add. Max 50 skills. Start typing to see suggestions.
          </p>
          {selectedSkills.length > 50 && (
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>
                Maximum 50 skills allowed. Please remove some skills before saving.
              </AlertDescription>
            </Alert>
          )}
        </CardContent>
      </Card>

      {/* Tips */}
      <Card>
        <CardHeader>
          <CardTitle>Tips for Better Matches</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2 text-sm text-muted-foreground">
          <p>• Add 4+ skills to maximize your profile completeness score (20%)</p>
          <p>• Include both technical skills (React, Python) and soft skills (Leadership, Communication)</p>
          <p>• Skills from your resume will be automatically added (coming soon)</p>
          <p>• The system will normalize skills (lowercase, deduplicate) automatically</p>
        </CardContent>
      </Card>
    </div>
  )
}
