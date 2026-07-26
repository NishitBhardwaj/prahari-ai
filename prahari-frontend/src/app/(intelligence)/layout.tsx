import { PageShell } from "@/components/layout/PageShell"

export default function IntelligenceLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return <PageShell>{children}</PageShell>
}
