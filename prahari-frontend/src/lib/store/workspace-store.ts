import { create } from 'zustand'

interface WorkspaceState {
  activeCaseId: string | null;
  isAiSidebarOpen: boolean;
  
  setCaseId: (id: string | null) => void;
  toggleAiSidebar: () => void;
  openAiSidebar: () => void;
  closeAiSidebar: () => void;
}

export const useWorkspaceStore = create<WorkspaceState>((set) => ({
  activeCaseId: null,
  isAiSidebarOpen: true,
  
  setCaseId: (id) => set({ activeCaseId: id }),
  toggleAiSidebar: () => set((state) => ({ isAiSidebarOpen: !state.isAiSidebarOpen })),
  openAiSidebar: () => set({ isAiSidebarOpen: true }),
  closeAiSidebar: () => set({ isAiSidebarOpen: false }),
}))
