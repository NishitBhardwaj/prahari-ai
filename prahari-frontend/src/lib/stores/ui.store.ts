import { create } from 'zustand'

interface UIState {
  sidebarOpen: boolean;
  toggleSidebar: () => void;
  setSidebarOpen: (open: boolean) => void;
  activePortal: 'admin' | 'intelligence';
  setActivePortal: (portal: 'admin' | 'intelligence') => void;
  assistantOpen: boolean;
  toggleAssistant: () => void;
  setAssistantOpen: (open: boolean) => void;
  presentationMode: boolean;
  togglePresentationMode: () => void;
  demoActive: boolean;
  setDemoActive: (active: boolean) => void;
  showDemoConclusion: boolean;
  setShowDemoConclusion: (show: boolean) => void;
}

export const useUIStore = create<UIState>((set) => ({
  sidebarOpen: true,
  toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
  setSidebarOpen: (open) => set({ sidebarOpen: open }),
  activePortal: 'admin',
  setActivePortal: (portal) => set({ activePortal: portal }),
  assistantOpen: false,
  toggleAssistant: () => set((state) => ({ assistantOpen: !state.assistantOpen })),
  setAssistantOpen: (open) => set({ assistantOpen: open }),
  presentationMode: false,
  togglePresentationMode: () => set((state) => ({ presentationMode: !state.presentationMode })),
  demoActive: false,
  setDemoActive: (active) => set({ demoActive: active }),
  showDemoConclusion: false,
  setShowDemoConclusion: (show) => set({ showDemoConclusion: show }),
}))
