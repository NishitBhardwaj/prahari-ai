import { create } from 'zustand'

export type WizardStep = 
  | "init"
  | "incident"
  | "location"
  | "complainant"
  | "victims"
  | "accused"
  | "witnesses"
  | "vehicles"
  | "devices"
  | "evidence"
  | "legal"
  | "officer"
  | "media"
  | "review";

export const WIZARD_STEPS: WizardStep[] = [
  "init", "incident", "location", "complainant", "victims", "accused", 
  "witnesses", "vehicles", "devices", "evidence", "legal", "officer", "media", "review"
];

interface WizardState {
  currentStep: WizardStep;
  activeCaseId: string | null;
  saveStatus: "idle" | "saving" | "saved" | "error";
  lastSavedAt: Date | null;
  
  setStep: (step: WizardStep) => void;
  nextStep: () => void;
  prevStep: () => void;
  
  setCaseId: (id: string) => void;
  setSaveStatus: (status: "idle" | "saving" | "saved" | "error") => void;
  
  reset: () => void;
}

export const useWizardStore = create<WizardState>((set, get) => ({
  currentStep: "init",
  activeCaseId: null,
  saveStatus: "idle",
  lastSavedAt: null,
  
  setStep: (step) => set({ currentStep: step }),
  
  nextStep: () => {
    const current = get().currentStep;
    const idx = WIZARD_STEPS.indexOf(current);
    if (idx < WIZARD_STEPS.length - 1) {
      set({ currentStep: WIZARD_STEPS[idx + 1] });
    }
  },
  
  prevStep: () => {
    const current = get().currentStep;
    const idx = WIZARD_STEPS.indexOf(current);
    if (idx > 0) {
      set({ currentStep: WIZARD_STEPS[idx - 1] });
    }
  },
  
  setCaseId: (id) => set({ activeCaseId: id }),
  
  setSaveStatus: (status) => set({ 
    saveStatus: status,
    lastSavedAt: status === "saved" ? new Date() : get().lastSavedAt
  }),
  
  reset: () => set({
    currentStep: "init",
    activeCaseId: null,
    saveStatus: "idle",
    lastSavedAt: null
  })
}))
