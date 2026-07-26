"use client"

import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import * as z from "zod"
import { useWizardStore } from "./wizard-store"
import { useAddVictim } from "@/lib/api/queries"
import { Button } from "@/components/ui/button"
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Loader2, Plus } from "lucide-react"

const formSchema = z.object({
  first_name: z.string().min(1, "First name is required"),
  last_name: z.string().optional(),
  gender: z.string().optional(),
  age: z.number().min(0).max(120).optional(),
  injury_type: z.string().optional()
})

export function Step5Victims() {
  const { nextStep, prevStep, setSaveStatus, activeCaseId } = useWizardStore()
  const { mutateAsync: addVictim, isPending } = useAddVictim()

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      first_name: "",
      last_name: "",
      gender: "",
    },
  })

  async function handleAdd(values: z.infer<typeof formSchema>) {
    if (!activeCaseId) return
    
    try {
      setSaveStatus("saving")
      await addVictim({ caseId: activeCaseId, payload: values })
      setSaveStatus("saved")
      form.reset()
    } catch (error) {
      setSaveStatus("error")
    }
  }

  return (
    <div className="max-w-2xl mx-auto py-6">
      <div className="mb-8">
        <h3 className="text-xl font-heading font-semibold">Victims Details</h3>
        <p className="text-muted-foreground text-sm mt-1">
          Add victims involved in the incident. You can add multiple victims.
        </p>
      </div>

      <Form {...form}>
        <div className="space-y-6 bg-muted/30 p-6 rounded-lg border border-border">
          <div className="grid grid-cols-2 gap-4">
            <FormField
              control={form.control}
              name="first_name"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>First Name</FormLabel>
                  <FormControl><Input placeholder="John" {...field} /></FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="last_name"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Last Name</FormLabel>
                  <FormControl><Input placeholder="Doe" {...field} /></FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="gender"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Gender</FormLabel>
                  <Select onValueChange={field.onChange} value={field.value}>
                    <FormControl><SelectTrigger><SelectValue placeholder="Select" /></SelectTrigger></FormControl>
                    <SelectContent>
                      <SelectItem value="MALE">Male</SelectItem>
                      <SelectItem value="FEMALE">Female</SelectItem>
                      <SelectItem value="OTHER">Other</SelectItem>
                    </SelectContent>
                  </Select>
                  <FormMessage />
                </FormItem>
              )}
            />
             <FormField
              control={form.control}
              name="age"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Age</FormLabel>
                  <FormControl><Input type="number" {...field} onChange={e => field.onChange(parseInt(e.target.value))} /></FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
          </div>

          <div className="flex justify-end">
            <Button type="button" variant="outline" onClick={form.handleSubmit(handleAdd)} disabled={isPending}>
              {isPending ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Plus className="mr-2 h-4 w-4" />}
              Add Victim
            </Button>
          </div>
        </div>
      </Form>

      <div className="flex justify-between pt-8 mt-8 border-t border-border">
        <Button variant="ghost" onClick={prevStep}>Back</Button>
        <Button onClick={nextStep}>Next Step</Button>
      </div>
    </div>
  )
}
