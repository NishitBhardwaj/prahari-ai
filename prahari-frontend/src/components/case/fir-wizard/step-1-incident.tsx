"use client"

import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import * as z from "zod"
import { useWizardStore } from "./wizard-store"
import { useCreateDraftCase } from "@/lib/api/queries"
import { Button } from "@/components/ui/button"
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Loader2 } from "lucide-react"

const formSchema = z.object({
  station_id: z.string().min(1, "Station is required"),
  station_name: z.string().min(1, "Station is required"),
  district_id: z.string().min(1, "District is required"),
  date_of_report: z.string().min(1, "Date is required"),
  year: z.number().int().min(2000)
})

export function Step1Incident() {
  const { setCaseId, nextStep, setSaveStatus, activeCaseId } = useWizardStore()
  const { mutateAsync: createDraft, isPending } = useCreateDraftCase()

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      station_id: "",
      station_name: "",
      district_id: "",
      date_of_report: new Date().toISOString().split('T')[0],
      year: new Date().getFullYear(),
    },
  })

  async function onSubmit(values: z.infer<typeof formSchema>) {
    if (activeCaseId) {
      // If we already have a draft, we'd do a PATCH here. For now just move to next step.
      nextStep()
      return
    }

    try {
      setSaveStatus("saving")
      const result = await createDraft(values)
      setCaseId(result.data.case_id)
      setSaveStatus("saved")
      nextStep()
    } catch (error) {
      setSaveStatus("error")
    }
  }

  return (
    <div className="max-w-2xl mx-auto py-6">
      <div className="mb-8">
        <h3 className="text-xl font-heading font-semibold">Incident & Jurisdiction</h3>
        <p className="text-muted-foreground text-sm mt-1">
          Record the primary details of the crime and establish jurisdiction.
        </p>
      </div>

      <Form {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
          <div className="grid grid-cols-2 gap-4">
            <FormField
              control={form.control}
              name="district_id"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>District</FormLabel>
                  <Select onValueChange={field.onChange} defaultValue={field.value}>
                    <FormControl>
                      <SelectTrigger>
                        <SelectValue placeholder="Select District" />
                      </SelectTrigger>
                    </FormControl>
                    <SelectContent>
                      <SelectItem value="DIST_BENGALURU">Bengaluru City</SelectItem>
                      <SelectItem value="DIST_MYSURU">Mysuru</SelectItem>
                      <SelectItem value="DIST_MANGALURU">Mangaluru</SelectItem>
                    </SelectContent>
                  </Select>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="station_id"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Police Station</FormLabel>
                  <Select onValueChange={(val) => {
                    field.onChange(val)
                    form.setValue("station_name", val === "PS_KORAMANGALA" ? "Koramangala Police Station" : "Other Station")
                  }} defaultValue={field.value}>
                    <FormControl>
                      <SelectTrigger>
                        <SelectValue placeholder="Select Station" />
                      </SelectTrigger>
                    </FormControl>
                    <SelectContent>
                      <SelectItem value="PS_KORAMANGALA">Koramangala PS</SelectItem>
                      <SelectItem value="PS_INDIRANAGAR">Indiranagar PS</SelectItem>
                    </SelectContent>
                  </Select>
                  <FormMessage />
                </FormItem>
              )}
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
             <FormField
              control={form.control}
              name="date_of_report"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Date of Report</FormLabel>
                  <FormControl>
                    <Input type="date" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
          </div>

          <div className="flex justify-end pt-4">
            <Button type="submit" disabled={isPending}>
              {isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              Save & Continue
            </Button>
          </div>
        </form>
      </Form>
    </div>
  )
}
