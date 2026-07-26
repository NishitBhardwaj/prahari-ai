"use client"

import { useEffect } from "react"
import { WizardShell } from "@/components/case/fir-wizard/WizardShell"
import { useWizardStore } from "@/components/case/fir-wizard/wizard-store"
import { Step1Incident } from "@/components/case/fir-wizard/step-1-incident"
import { Step5Victims } from "@/components/case/fir-wizard/step-5-victims"

// Mock placeholders for other steps
const StepPlaceholder = ({ title }: { title: string }) => {
  const { nextStep, prevStep } = useWizardStore()
  return (
    <div className="max-w-2xl mx-auto py-6 flex flex-col h-[50vh]">
      <div className="flex-1 flex items-center justify-center border-2 border-dashed border-border rounded-xl">
        <h2 className="text-2xl font-heading text-muted-foreground">{title} (Coming Soon)</h2>
      </div>
      <div className="flex justify-between pt-8 mt-8 border-t border-border">
        <button className="px-4 py-2 border rounded-md" onClick={prevStep}>Back</button>
        <button className="px-4 py-2 bg-primary text-primary-foreground rounded-md" onClick={nextStep}>Next Step</button>
      </div>
    </div>
  )
}

export default function NewCasePage() {
  const { currentStep, reset } = useWizardStore()

  // Reset wizard state on mount
  useEffect(() => {
    reset()
  }, [reset])

  return (
    <div className="h-[calc(100vh-4rem)] p-6">
      <div className="max-w-7xl mx-auto h-full flex flex-col">
        <div className="mb-6">
          <h1 className="text-3xl font-heading font-bold text-foreground">Register FIR</h1>
          <p className="text-muted-foreground mt-1">Create a new First Information Report using the progressive draft system.</p>
        </div>
        
        <div className="flex-1 min-h-0 bg-background rounded-xl border shadow-sm p-4 overflow-hidden">
          <WizardShell>
            {currentStep === "init" && (
              <div className="flex flex-col items-center justify-center h-full gap-4">
                <h2 className="text-2xl font-heading">Start New Investigation</h2>
                <p className="text-muted-foreground">This wizard will guide you through creating a new case.</p>
                <button 
                  onClick={() => useWizardStore.getState().setStep("incident")}
                  className="px-6 py-2 bg-primary text-primary-foreground rounded-md mt-4"
                >
                  Start FIR Registration
                </button>
              </div>
            )}
            
            {currentStep === "incident" && <Step1Incident />}
            {currentStep === "location" && <StepPlaceholder title="Location Details" />}
            {currentStep === "complainant" && <StepPlaceholder title="Complainant Details" />}
            {currentStep === "victims" && <Step5Victims />}
            {currentStep === "accused" && <StepPlaceholder title="Accused Details" />}
            {currentStep === "witnesses" && <StepPlaceholder title="Witnesses" />}
            {currentStep === "vehicles" && <StepPlaceholder title="Vehicles Involved" />}
            {currentStep === "devices" && <StepPlaceholder title="Digital Devices" />}
            {currentStep === "evidence" && <StepPlaceholder title="Evidence Collection" />}
            {currentStep === "legal" && <StepPlaceholder title="Legal Sections" />}
            {currentStep === "officer" && <StepPlaceholder title="Officer Assignment" />}
            {currentStep === "media" && <StepPlaceholder title="Media Uploads" />}
            
            {currentStep === "review" && (
              <div className="max-w-2xl mx-auto py-6 flex flex-col">
                <div className="flex-1 flex flex-col items-center justify-center border-2 border-dashed border-border rounded-xl p-12 text-center">
                  <h2 className="text-2xl font-heading text-foreground mb-2">Review & Submit</h2>
                  <p className="text-muted-foreground mb-8">All sections have been drafted and saved to the backend.</p>
                  <button className="px-8 py-3 bg-primary text-primary-foreground font-semibold rounded-md shadow-md hover:bg-primary/90">
                    Submit Final FIR
                  </button>
                </div>
                <div className="flex justify-between pt-8 mt-8 border-t border-border">
                  <button className="px-4 py-2 border rounded-md" onClick={() => useWizardStore.getState().prevStep()}>Back</button>
                </div>
              </div>
            )}
          </WizardShell>
        </div>
      </div>
    </div>
  )
}
