"use client"

import { useWizardStore, WIZARD_STEPS } from "./wizard-store"
import { cn } from "@/lib/utils"
import { Check, Loader2, Save } from "lucide-react"

export function WizardShell({ children }: { children: React.ReactNode }) {
  const { currentStep, activeCaseId, saveStatus, lastSavedAt } = useWizardStore()
  
  const currentIndex = WIZARD_STEPS.indexOf(currentStep)
  
  return (
    <div className="flex flex-col lg:flex-row h-full gap-6">
      {/* Left Sidebar - Steps */}
      <div className="w-full lg:w-64 flex-shrink-0 space-y-1 bg-card border border-border p-4 rounded-xl h-fit">
        <h3 className="font-heading font-semibold text-lg mb-4 px-2">FIR Registration</h3>
        
        {WIZARD_STEPS.map((step, idx) => {
          const isActive = step === currentStep
          const isPast = idx < currentIndex
          
          return (
            <div 
              key={step}
              className={cn(
                "flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium transition-colors",
                isActive ? "bg-primary/10 text-primary dark:bg-accent/20 dark:text-accent" : 
                isPast ? "text-foreground" : "text-muted-foreground opacity-60"
              )}
            >
              <div className={cn(
                "flex items-center justify-center h-6 w-6 rounded-full border text-xs",
                isActive ? "border-primary text-primary dark:border-accent dark:text-accent" : 
                isPast ? "bg-primary text-primary-foreground border-primary dark:bg-accent dark:text-accent-foreground dark:border-accent" : "border-muted-foreground"
              )}>
                {isPast ? <Check className="h-3 w-3" /> : (idx + 1)}
              </div>
              <span className="capitalize">{step.replace("-", " ")}</span>
            </div>
          )
        })}
      </div>
      
      {/* Center - Content */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Header bar with save status */}
        <div className="flex items-center justify-between mb-6 bg-card border border-border p-4 rounded-xl">
          <div>
            <h2 className="text-xl font-heading font-semibold capitalize">{currentStep.replace("-", " ")} Details</h2>
            {activeCaseId && <p className="text-sm text-muted-foreground font-mono mt-1">Draft ID: {activeCaseId}</p>}
          </div>
          
          <div className="flex items-center gap-2 text-sm">
            {saveStatus === "saving" && (
              <span className="flex items-center gap-2 text-warning"><Loader2 className="h-4 w-4 animate-spin" /> Saving...</span>
            )}
            {saveStatus === "saved" && lastSavedAt && (
              <span className="flex items-center gap-2 text-success"><Check className="h-4 w-4" /> Saved at {lastSavedAt.toLocaleTimeString()}</span>
            )}
            {saveStatus === "error" && (
              <span className="flex items-center gap-2 text-destructive">Failed to save draft</span>
            )}
            {saveStatus === "idle" && activeCaseId && (
              <span className="flex items-center gap-2 text-muted-foreground"><Save className="h-4 w-4" /> All changes saved</span>
            )}
          </div>
        </div>
        
        {/* Step Content */}
        <div className="flex-1 overflow-y-auto">
          {children}
        </div>
      </div>
    </div>
  )
}
