"use client"

export default function CasesPage() {
  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold tracking-tight font-heading text-primary dark:text-accent mb-4">
        Investigation Workspace
      </h1>
      <p className="text-muted-foreground mb-8">
        Manage active cases, register new FIRs, and explore evidence.
      </p>
      
      <div className="rounded-md border border-border bg-card shadow-sm p-8 text-center text-muted-foreground">
        <p>List of active cases would appear here in a data table.</p>
        <p className="text-sm mt-2">Example: CASE-001 (Armed Robbery) - Assigned to ACP South</p>
      </div>
    </div>
  )
}
