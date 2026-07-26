import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { apiClient } from "./client"

// ── Types ────────────────────────────────────────────────────────────────
export interface DraftCasePayload {
  station_id: string;
  station_name: string;
  district_id: string;
  date_of_report: string;
  year: number;
}

export interface VictimPayload {
  first_name: string;
  last_name?: string;
  gender?: string;
  age?: number;
  injury_type?: string;
}

// ── Case Draft Workflow ──────────────────────────────────────────────────

export const useCreateDraftCase = () => {
  return useMutation({
    mutationFn: async (payload: any) => {
      const response = await apiClient.post("/cases/draft", payload)
      return response.data
    },
  })
}

export const useUpdateCase = () => {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async ({ caseId, payload }: { caseId: string; payload: any }) => {
      const response = await apiClient.patch(`/cases/${caseId}`, payload)
      return response.data
    },
    onSuccess: (data, variables) => {
      queryClient.invalidateQueries({ queryKey: ["case", variables.caseId] })
    },
  })
}

export const useAddVictim = () => {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async ({ caseId, payload }: { caseId: string; payload: VictimPayload }) => {
      const response = await apiClient.post(`/cases/${caseId}/victims`, payload)
      return response.data
    },
    onSuccess: (data, variables) => {
      queryClient.invalidateQueries({ queryKey: ["case", variables.caseId, "timeline"] })
    },
  })
}

export const useAddAccused = () => {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async ({ caseId, payload }: { caseId: string; payload: any }) => {
      const response = await apiClient.post(`/cases/${caseId}/accused`, payload)
      return response.data
    },
    onSuccess: (data, variables) => {
      queryClient.invalidateQueries({ queryKey: ["case", variables.caseId, "timeline"] })
    },
  })
}

// ── Case Read ────────────────────────────────────────────────────────────

export const useCaseDetails = (caseId: string) => {
  return useQuery({
    queryKey: ["case", caseId],
    queryFn: async () => {
      const response = await apiClient.get(`/cases/${caseId}`)
      return response.data
    },
    enabled: !!caseId,
  })
}

export const useCaseTimeline = (caseId: string) => {
  return useQuery({
    queryKey: ["case", caseId, "timeline"],
    queryFn: async () => {
      const response = await apiClient.get(`/cases/${caseId}/timeline`)
      return response.data
    },
    enabled: !!caseId,
  })
}

export const useListCases = (params: any) => {
  return useQuery({
    queryKey: ["cases", params],
    queryFn: async () => {
      const response = await apiClient.get("/cases", { params })
      return response.data
    },
  })
}

// ── Task Management ────────────────────────────────────────────────────────

export const useCaseTasks = (caseId: string) => {
  return useQuery({
    queryKey: ["case", caseId, "tasks"],
    queryFn: async () => {
      const response = await apiClient.get(`/tasks/case/${caseId}`)
      return response.data
    },
    enabled: !!caseId,
  })
}

export const useUpdateTask = () => {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async ({ taskId, payload }: { taskId: string; payload: any }) => {
      const response = await apiClient.patch(`/tasks/${taskId}`, payload)
      return response.data
    },
    onSuccess: (_, variables) => {
      // Invalidate both tasks and timeline since status change generates an event
      queryClient.invalidateQueries({ queryKey: ["case"] }) 
    },
  })
}

// ── Evidence Management ───────────────────────────────────────────────────

export const useCaseEvidence = (caseId: string) => {
  return useQuery({
    queryKey: ["case", caseId, "evidence"],
    queryFn: async () => {
      const response = await apiClient.get(`/evidence/case/${caseId}`)
      return response.data
    },
    enabled: !!caseId,
  })
}
