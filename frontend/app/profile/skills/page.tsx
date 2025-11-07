"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import { Skeleton } from "@/components/ui/skeleton"
import { Alert, AlertDescription } from "@/components/ui/alert"
import Link from "next/link"
import { X, Plus, Save, ArrowLeft, AlertCircle, Loader2 } from "lucide-react"
import { useProfile } from "@/hooks/use-profile"
import { useUpdateSkills } from "@/hooks/use-profile-mutations"
import { useProfileStore } from "@/stores/profile-store"

export default function SkillsPage() {
  const { data: profile, isLoading, isError, error } = useProfile()
  const { mutate: updateSkills, isPending } = useUpdateSkills()
  const { 
    selectedSkills, 
    addSkill, 
    removeSkill, 
    initializeSkills, 
    formDirty,
    setFormDirty 
  } = useProfileStore()
  
  const [newSkillInput, setNewSkillInput] = useState("")

  // Initialize skills from profile
  useEffect(() => {
    if (profile?.skills) {
      initializeSkills(profile.skills)
    }
  }, [profile?.skills, initializeSkills])

  const handleAddSkill = () => {
    const skill = newSkillInput.trim()
    if (skill && !selectedSkills.includes(skill)) {
      addSkill(skill)
      setNewSkillInput("")
    }
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
          <CardTitle>Add Skills</CardTitle>
          <CardDescription>
            Enter skills one at a time. Backend will normalize and deduplicate.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex gap-2">
            <Input
              placeholder="Type a skill (e.g., React, Python, AWS)"
              value={newSkillInput}
              onChange={(e) => setNewSkillInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter') {
                  e.preventDefault()
                  handleAddSkill()
                }
              }}
              maxLength={100}
            />
            <Button 
              onClick={handleAddSkill} 
              disabled={!newSkillInput.trim()}
              variant="outline"
            >
              <Plus className="h-4 w-4" />
            </Button>
          </div>
          <p className="text-xs text-muted-foreground">
            Press Enter or click + to add. Max 50 skills, 100 characters each.
          </p>
        </CardContent>
      </Card>

      {/* Current Skills */}
      <Card>
        <CardHeader>
          <CardTitle>Your Skills ({selectedSkills.length})</CardTitle>
          <CardDescription>
            Click X to remove a skill. Changes are saved when you click "Save Changes".
          </CardDescription>
        </CardHeader>
        <CardContent>
          {selectedSkills.length > 0 ? (
            <div className="flex flex-wrap gap-2">
              {selectedSkills.map((skill) => (
                <Badge 
                  key={skill} 
                  variant="secondary"
                  className="text-sm px-3 py-1.5 cursor-pointer hover:bg-secondary/80"
                >
                  {skill}
                  <button
                    onClick={() => removeSkill(skill)}
                    className="ml-2 hover:text-destructive"
                    aria-label={`Remove ${skill}`}
                  >
                    <X className="h-3 w-3" />
                  </button>
                </Badge>
              ))}
            </div>
          ) : (
            <p className="text-sm text-muted-foreground">
              No skills added yet. Start by typing a skill above.
            </p>
          )}
          {selectedSkills.length > 50 && (
            <Alert variant="destructive" className="mt-4">
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
