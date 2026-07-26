import { redirect } from "next/navigation"

export default async function CaseWorkspaceRoot({ params }: { params: Promise<{ id: string }> }) {
  redirect(`/cases/${(await params).id}/timeline`)
}
