"use client"

import { useState } from "react"
import { FileText, MoreVertical, Download, Trash2, CheckCircle2, Eye } from "lucide-react"
import { ResumeResponse } from "@/lib/api/resumes"
import { useActivateResume, useDeleteResume, useDownloadResume } from "@/hooks/use-resumes"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog"
import { ResumeAnalysisModal } from "./resume-analysis-modal"

interface ResumeCardProps {
  resume: ResumeResponse
}

export function ResumeCard({ resume }: ResumeCardProps) {
  const [showDeleteDialog, setShowDeleteDialog] = useState(false)
  const [showAnalysisModal, setShowAnalysisModal] = useState(false)

  const { mutate: activateResume, isPending: isActivating } = useActivateResume()
  const { mutate: deleteResume, isPending: isDeleting } = useDeleteResume()
  const { mutate: downloadResume, isPending: isDownloading } = useDownloadResume()

  const handleActivate = () => {
    if (!resume.is_active) {
      activateResume(resume.id)
    }
  }

  const handleDelete = () => {
    deleteResume(resume.id, {
      onSuccess: () => setShowDeleteDialog(false)
    })
  }

  const handleDownload = () => {
    downloadResume(resume.id)
  }

  const handleViewAnalysis = () => {
    setShowAnalysisModal(true)
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    })
  }

  const formatFileSize = (bytes: number) => {
    return (bytes / 1024 / 1024).toFixed(2) + ' MB'
  }

  return (
    <>
      <div className="flex items-center justify-between p-4 border rounded-lg hover:bg-muted/50 transition-colors">
        <div className="flex items-center gap-3 flex-1 min-w-0">
          {/* File Icon */}
          <div className="rounded-lg bg-primary/10 p-2 shrink-0">
            <FileText className="h-5 w-5 text-primary" />
          </div>

          {/* File Info */}
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-1">
              <p className="text-sm font-medium truncate">{resume.file_name}</p>
              {resume.is_active && (
                <Badge variant="default" className="shrink-0">
                  Active
                </Badge>
              )}
            </div>
            <div className="flex items-center gap-3 text-xs text-muted-foreground">
              <span>{formatFileSize(resume.file_size)}</span>
              <span>•</span>
              <span>Uploaded {formatDate(resume.uploaded_at)}</span>
            </div>
          </div>
        </div>

        {/* Actions */}
        <div className="flex items-center gap-2 shrink-0">
          <Button
            onClick={handleViewAnalysis}
            size="sm"
            variant="outline"
          >
            <Eye className="h-4 w-4 mr-1" />
            View Analysis
          </Button>

          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                <MoreVertical className="h-4 w-4" />
                <span className="sr-only">Open menu</span>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              {!resume.is_active && (
                <>
                  <DropdownMenuItem
                    onClick={handleActivate}
                    disabled={isActivating}
                  >
                    <CheckCircle2 className="h-4 w-4 mr-2" />
                    Set as Active
                  </DropdownMenuItem>
                  <DropdownMenuSeparator />
                </>
              )}
              <DropdownMenuItem
                onClick={handleDownload}
                disabled={isDownloading}
              >
                <Download className="h-4 w-4 mr-2" />
                Download
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem
                onClick={() => setShowDeleteDialog(true)}
                className="text-destructive focus:text-destructive"
                disabled={isDeleting}
              >
                <Trash2 className="h-4 w-4 mr-2" />
                Delete
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={showDeleteDialog} onOpenChange={setShowDeleteDialog}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete Resume</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete <strong>{resume.file_name}</strong>?
              This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleDelete}
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
            >
              Delete
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

      {/* Analysis Modal */}
      {showAnalysisModal && (
        <ResumeAnalysisModal
          resumeId={resume.id}
          open={showAnalysisModal}
          onOpenChange={setShowAnalysisModal}
        />
      )}
    </>
  )
}
