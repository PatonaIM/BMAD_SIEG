"use client"

import { useState } from "react"
import { zodResolver } from "@hookform/resolvers/zod"
import { useForm } from "react-hook-form"
import * as z from "zod"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Pencil } from "lucide-react"
import { useUpdateBasicInfo } from "@/hooks/use-profile-mutations"
import { UpdateBasicInfoRequestSchema } from "@/lib/schemas/profile.schema"

interface EditBasicInfoDialogProps {
  currentName: string
  currentPhone?: string
  currentExperience?: number
}

export function EditBasicInfoDialog({ currentName, currentPhone, currentExperience }: EditBasicInfoDialogProps) {
  const [open, setOpen] = useState(false)
  const { mutate: updateBasicInfo, isPending } = useUpdateBasicInfo()

  const form = useForm<z.infer<typeof UpdateBasicInfoRequestSchema>>({
    resolver: zodResolver(UpdateBasicInfoRequestSchema),
    defaultValues: {
      full_name: currentName,
      phone: currentPhone || "",
      experience_years: currentExperience ?? undefined,
    },
  })

  function onSubmit(values: z.infer<typeof UpdateBasicInfoRequestSchema>) {
    // Only send fields that are not empty/undefined
    const payload: { full_name?: string; phone?: string; experience_years?: number } = {}
    
    if (values.full_name && values.full_name.trim()) {
      payload.full_name = values.full_name.trim()
    }
    
    if (values.phone && values.phone.trim()) {
      payload.phone = values.phone.trim()
    }

    if (values.experience_years !== undefined && values.experience_years !== null) {
      payload.experience_years = values.experience_years
    }

    updateBasicInfo(payload, {
      onSuccess: () => {
        setOpen(false)
        form.reset(values) // Update form defaults to new values
      },
    })
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
          <Pencil className="h-4 w-4" />
          <span className="sr-only">Edit basic information</span>
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Edit Basic Information</DialogTitle>
          <DialogDescription>
            Update your name, phone number, and experience. Click save when you're done.
          </DialogDescription>
        </DialogHeader>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            <FormField
              control={form.control}
              name="full_name"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Full Name</FormLabel>
                  <FormControl>
                    <Input placeholder="John Doe" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="phone"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Phone Number</FormLabel>
                  <FormControl>
                    <Input placeholder="+1234567890" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="experience_years"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Years of Experience</FormLabel>
                  <FormControl>
                    <Input 
                      type="number" 
                      min={0} 
                      max={50} 
                      placeholder="5" 
                      {...field}
                      value={field.value ?? ""}
                      onChange={(e) => field.onChange(e.target.value ? parseInt(e.target.value) : undefined)}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <DialogFooter>
              <Button
                type="button"
                variant="outline"
                onClick={() => setOpen(false)}
                disabled={isPending}
              >
                Cancel
              </Button>
              <Button type="submit" disabled={isPending}>
                {isPending ? "Saving..." : "Save Changes"}
              </Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  )
}
