"use client"

import CytoscapeComponent from 'react-cytoscapejs'
import { useTheme } from 'next-themes'
import { useEffect, useState } from 'react'

export function NetworkVisualizer() {
  const { theme } = useTheme()
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  const elements = [
    { data: { id: 'gang-1', label: 'Bawariya Gang', type: 'gang' } },
    { data: { id: 'person-1', label: 'Rajesh K.', type: 'suspect' } },
    { data: { id: 'person-2', label: 'Suresh M.', type: 'suspect' } },
    { data: { id: 'case-1', label: 'CASE-001 (Robbery)', type: 'case' } },
    { data: { id: 'case-2', label: 'CASE-104 (Assault)', type: 'case' } },
    { data: { id: 'evidence-1', label: 'Gun (EV-99)', type: 'evidence' } },
    
    { data: { source: 'gang-1', target: 'person-1', label: 'MEMBER' } },
    { data: { source: 'gang-1', target: 'person-2', label: 'MEMBER' } },
    { data: { source: 'person-1', target: 'case-1', label: 'SUSPECT_IN' } },
    { data: { source: 'person-2', target: 'case-1', label: 'SUSPECT_IN' } },
    { data: { source: 'person-1', target: 'case-2', label: 'ARRESTED_FOR' } },
    { data: { source: 'case-1', target: 'evidence-1', label: 'HAS_EVIDENCE' } },
  ]

  const style = [
    {
      selector: 'node',
      style: {
        'label': 'data(label)',
        'text-valign': 'bottom',
        'text-halign': 'center',
        'color': theme === 'dark' ? '#fff' : '#000',
        'font-size': '12px',
        'background-color': '#94a3b8'
      }
    },
    {
      selector: 'node[type="gang"]',
      style: { 'background-color': '#ef4444', 'width': 40, 'height': 40 }
    },
    {
      selector: 'node[type="suspect"]',
      style: { 'background-color': '#f59e0b' }
    },
    {
      selector: 'node[type="case"]',
      style: { 'background-color': '#3b82f6', 'shape': 'rectangle', 'width': 30, 'height': 30 }
    },
    {
      selector: 'node[type="evidence"]',
      style: { 'background-color': '#10b981', 'shape': 'triangle' }
    },
    {
      selector: 'edge',
      style: {
        'width': 2,
        'line-color': theme === 'dark' ? '#475569' : '#cbd5e1',
        'target-arrow-color': theme === 'dark' ? '#475569' : '#cbd5e1',
        'target-arrow-shape': 'triangle',
        'curve-style': 'bezier',
        'label': 'data(label)',
        'font-size': '10px',
        'color': theme === 'dark' ? '#94a3b8' : '#64748b',
        'text-rotation': 'autorotate',
        'text-margin-y': -10
      }
    }
  ]

  if (!mounted) return null

  return (
    <div className="h-full w-full bg-card rounded-lg border border-border shadow-md">
      <CytoscapeComponent
        elements={elements}
        style={{ width: '100%', height: '100%' }}
        stylesheet={style as any}
        layout={{ name: 'cose', padding: 30, nodeRepulsion: 400000 }}
      />
    </div>
  )
}
