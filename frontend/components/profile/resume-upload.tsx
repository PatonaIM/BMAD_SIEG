"use client"

import { useCallback, useState } from "react"
import { Upload, FileText, X, Loader2 } from "lucide-react"
import { useUploadResume } from "@/hooks/use-resumes"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"

type UploadProgress = 'idle' | 'uploading' | 'analyzing' | 'complete'

const MAX_FILE_SIZE = 5 * 1024 * 1024 // 5MB

export function ResumeUpload() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [isDragOver, setIsDragOver] = useState(false)
  const [fileError, setFileError] = useState<string | null>(null)
  const [uploadProgress, setUploadProgress] = useState<UploadProgress>('idle')

  const { mutate: uploadResume } = useUploadResume()

  /**
   * Validate file before upload
   */
  const validateFile = useCallback((file: File): string | null => {
    // Check file type
    if (file.type !== 'application/pdf') {
      return 'Only PDF files are allowed'
    }

    // Check file size
    if (file.size > MAX_FILE_SIZE) {
      return 'File must be under 5MB'
    }

    return null
  }, [])

  /**
   * Handle file selection
   */
  const handleFileSelect = useCallback((file: File) => {
    const error = validateFile(file)
    
    if (error) {
      setFileError(error)
      setSelectedFile(null)
      return
    }

    setFileError(null)
    setSelectedFile(file)
  }, [validateFile])

  /**
   * Handle drag over event
   */
  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragOver(true)
  }, [])

  /**
   * Handle drag leave event
   */
  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragOver(false)
  }, [])

  /**
   * Handle drop event
   */
  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragOver(false)

    const files = Array.from(e.dataTransfer.files)
    if (files.length > 0) {
      handleFileSelect(files[0])
    }
  }, [handleFileSelect])

  /**
   * Handle file input change
   */
  const handleFileInputChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files
    if (files && files.length > 0) {
      handleFileSelect(files[0])
    }
  }, [handleFileSelect])

  /**
   * Handle upload submission
   */
  const handleUpload = useCallback(() => {
    if (!selectedFile) return

    setUploadProgress('uploading')

    uploadResume(selectedFile, {
      onSuccess: () => {
        setUploadProgress('analyzing')
        
        // Simulate analysis phase (backend processes in background)
        setTimeout(() => {
          setUploadProgress('complete')
          
          // Reset after 2 seconds
          setTimeout(() => {
            setSelectedFile(null)
            setUploadProgress('idle')
          }, 2000)
        }, 1000)
      },
      onError: () => {
        setUploadProgress('idle')
      }
    })
  }, [selectedFile, uploadResume])

  /**
   * Clear selected file
   */
  const handleClear = useCallback(() => {
    setSelectedFile(null)
    setFileError(null)
    setUploadProgress('idle')
  }, [])

  const showDropZone = !selectedFile && uploadProgress === 'idle'
  const showFilePreview = selectedFile && uploadProgress === 'idle'
  const showProgressIndicator = uploadProgress !== 'idle'

  return (
    <div className="space-y-4">
      {/* Drag & Drop Zone */}
      {showDropZone && (
        <div
          className={cn(
            "relative border-2 border-dashed rounded-lg p-8 text-center transition-colors",
            isDragOver 
              ? "border-primary bg-primary/5" 
              : "border-muted-foreground/25 hover:border-muted-foreground/50"
          )}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
        >
          <input
            type="file"
            id="resume-upload"
            accept="application/pdf"
            onChange={handleFileInputChange}
            className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
          />
          
          <div className="flex flex-col items-center gap-3">
            <div className="rounded-full bg-primary/10 p-3">
              <Upload className="h-6 w-6 text-primary" />
            </div>
            
            <div>
              <p className="text-sm font-medium">
                Drag and drop your resume here, or{" "}
                <label htmlFor="resume-upload" className="text-primary cursor-pointer hover:underline">
                  browse
                </label>
              </p>
              <p className="text-xs text-muted-foreground mt-1">
                PDF only, max 5MB
              </p>
            </div>
          </div>
        </div>
      )}

      {/* File Preview */}
      {showFilePreview && (
        <div className="flex items-center justify-between p-4 border rounded-lg">
          <div className="flex items-center gap-3">
            <div className="rounded-lg bg-primary/10 p-2">
              <FileText className="h-5 w-5 text-primary" />
            </div>
            <div>
              <p className="text-sm font-medium">{selectedFile.name}</p>
              <p className="text-xs text-muted-foreground">
                {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
              </p>
            </div>
          </div>
          
          <div className="flex items-center gap-2">
            <Button onClick={handleUpload} size="sm">
              Upload
            </Button>
            <Button 
              onClick={handleClear} 
              size="sm" 
              variant="ghost"
              className="h-8 w-8 p-0"
            >
              <X className="h-4 w-4" />
            </Button>
          </div>
        </div>
      )}

      {/* Upload Progress Indicator */}
      {showProgressIndicator && (
        <div className="flex items-center gap-3 p-4 border rounded-lg bg-muted/50">
          <Loader2 className="h-5 w-5 animate-spin text-primary" />
          <div>
            <p className="text-sm font-medium">
              {uploadProgress === 'uploading' && 'Uploading resume...'}
              {uploadProgress === 'analyzing' && 'AI analysis in progress...'}
              {uploadProgress === 'complete' && 'Complete! ✓'}
            </p>
            <p className="text-xs text-muted-foreground">
              {uploadProgress === 'uploading' && 'Please wait while we upload your file'}
              {uploadProgress === 'analyzing' && 'Analyzing your resume for feedback'}
              {uploadProgress === 'complete' && 'Your resume has been uploaded successfully'}
            </p>
          </div>
        </div>
      )}

      {/* Error Display */}
      {fileError && (
        <div className="p-3 bg-destructive/10 border border-destructive/20 rounded-lg">
          <p className="text-sm text-destructive">{fileError}</p>
        </div>
      )}
    </div>
  )
}
