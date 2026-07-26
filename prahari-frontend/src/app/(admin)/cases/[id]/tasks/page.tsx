"use client"

import { use } from "react"

import { useState } from "react"
import { useCaseTasks, useUpdateTask } from "@/lib/api/queries"
import { Loader2, Plus, Clock, CheckCircle2, Circle, AlertCircle } from "lucide-react"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"

const COLUMNS = [
  { id: "TODO", title: "To Do", icon: Circle },
  { id: "IN_PROGRESS", title: "In Progress", icon: Clock },
  { id: "COMPLETED", title: "Completed", icon: CheckCircle2 },
]

export default function TaskBoardPage({ params }: { params: Promise<{ id: string }> }) {
  const { data, isLoading } = useCaseTasks(use(params).id)
  const { mutate: updateTask, isPending: isUpdating } = useUpdateTask()
  
  const [updatingTaskId, setUpdatingTaskId] = useState<string | null>(null)

  if (isLoading) {
    return <div className="h-full flex items-center justify-center"><Loader2 className="h-8 w-8 animate-spin text-muted-foreground" /></div>
  }

  const tasks = data?.data || []

  const handleMove = (taskId: string, newStatus: string) => {
    setUpdatingTaskId(taskId)
    updateTask(
      { taskId, payload: { status: newStatus } },
      { onSettled: () => setUpdatingTaskId(null) }
    )
  }

  return (
    <div className="flex flex-col h-full bg-background">
      <div className="p-6 border-b border-border flex items-center justify-between bg-card">
        <div>
          <h2 className="text-2xl font-heading font-semibold">Investigation Board</h2>
          <p className="text-muted-foreground text-sm mt-1">Manage and track tasks for this case.</p>
        </div>
        
        <Button>
          <Plus className="mr-2 h-4 w-4" />
          Create Task
        </Button>
      </div>
      
      <div className="flex-1 overflow-x-auto p-6">
        <div className="flex h-full gap-6 min-w-max">
          {COLUMNS.map(col => {
            const colTasks = tasks.filter((t: any) => t.status === col.id)
            return (
              <div key={col.id} className="w-80 flex flex-col bg-muted/30 rounded-xl border border-border">
                <div className="p-4 border-b border-border flex items-center justify-between bg-card rounded-t-xl">
                  <div className="flex items-center gap-2 font-semibold">
                    <col.icon className="h-4 w-4 text-muted-foreground" />
                    {col.title}
                  </div>
                  <span className="bg-muted px-2 py-0.5 rounded-full text-xs font-mono">{colTasks.length}</span>
                </div>
                
                <div className="flex-1 overflow-y-auto p-3 space-y-3">
                  {colTasks.map((task: any) => (
                    <div key={task.task_id} className="bg-card border border-border rounded-lg p-4 shadow-sm hover:shadow-md transition-shadow">
                      <div className="flex justify-between items-start mb-2">
                        <span className={cn(
                          "text-[10px] font-bold uppercase px-2 py-0.5 rounded-sm",
                          task.priority === "HIGH" || task.priority === "URGENT" ? "bg-destructive/10 text-destructive" : "bg-primary/10 text-primary"
                        )}>
                          {task.priority}
                        </span>
                        {task.task_type && (
                          <span className="text-[10px] text-muted-foreground">{task.task_type.replace("_", " ")}</span>
                        )}
                      </div>
                      
                      <h4 className="font-semibold text-sm mb-1">{task.title}</h4>
                      {task.description && (
                        <p className="text-xs text-muted-foreground line-clamp-2 mb-3">{task.description}</p>
                      )}
                      
                      <div className="flex items-center justify-between mt-4 border-t border-border pt-3">
                        <div className="flex -space-x-2">
                          {/* Mock avatar */}
                          <div className="h-6 w-6 rounded-full bg-primary flex items-center justify-center text-[10px] text-primary-foreground border-2 border-card">
                            {task.assigned_to_id ? "IO" : "U"}
                          </div>
                        </div>
                        
                        <div className="flex gap-1">
                          {col.id !== "TODO" && (
                            <Button 
                              variant="ghost" 
                              size="sm" 
                              className="h-6 text-[10px] px-2"
                              onClick={() => handleMove(task.task_id, col.id === "COMPLETED" ? "IN_PROGRESS" : "TODO")}
                              disabled={updatingTaskId === task.task_id}
                            >
                              &larr;
                            </Button>
                          )}
                          {col.id !== "COMPLETED" && (
                            <Button 
                              variant="secondary" 
                              size="sm" 
                              className="h-6 text-[10px] px-2"
                              onClick={() => handleMove(task.task_id, col.id === "TODO" ? "IN_PROGRESS" : "COMPLETED")}
                              disabled={updatingTaskId === task.task_id}
                            >
                              {updatingTaskId === task.task_id ? <Loader2 className="h-3 w-3 animate-spin" /> : "Move &rarr;"}
                            </Button>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                  
                  {colTasks.length === 0 && (
                    <div className="h-24 border-2 border-dashed border-border rounded-lg flex items-center justify-center text-muted-foreground text-sm">
                      Drop tasks here
                    </div>
                  )}
                </div>
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}