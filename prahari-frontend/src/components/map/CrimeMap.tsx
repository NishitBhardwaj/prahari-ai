"use client"

import { useEffect, useRef, useState } from "react"
import * as maplibregl from "maplibre-gl"
import "maplibre-gl/dist/maplibre-gl.css"
import { useTheme } from "next-themes"

export function CrimeMap() {
  const mapContainer = useRef<HTMLDivElement>(null)
  const map = useRef<maplibregl.Map | null>(null)
  const { theme } = useTheme()
  const [loaded, setLoaded] = useState(false)

  useEffect(() => {
    if (map.current || !mapContainer.current) return

    const styleUrl = theme === 'dark' 
      ? 'https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json'
      : 'https://basemaps.cartocdn.com/gl/positron-gl-style/style.json'

    map.current = new maplibregl.Map({
      container: mapContainer.current,
      style: styleUrl,
      center: [76.5, 14.5], // Center of Karnataka
      zoom: 6,
      attributionControl: false
    })

    map.current.on('load', () => {
      setLoaded(true)
      
      // Mock data source for hotspots
      map.current?.addSource('hotspots', {
        type: 'geojson',
        data: {
          type: 'FeatureCollection',
          features: [
            { type: 'Feature', geometry: { type: 'Point', coordinates: [77.59, 12.97] }, properties: { intensity: 0.9, type: 'robbery' } }, // Bengaluru
            { type: 'Feature', geometry: { type: 'Point', coordinates: [76.65, 12.30] }, properties: { intensity: 0.6, type: 'theft' } }, // Mysuru
            { type: 'Feature', geometry: { type: 'Point', coordinates: [74.85, 12.87] }, properties: { intensity: 0.7, type: 'assault' } }, // Mangaluru
            { type: 'Feature', geometry: { type: 'Point', coordinates: [75.12, 15.36] }, properties: { intensity: 0.5, type: 'burglary' } }, // Hubballi
          ]
        }
      })

      // Add heatmap layer
      map.current?.addLayer({
        id: 'hotspots-heat',
        type: 'heatmap',
        source: 'hotspots',
        paint: {
          'heatmap-weight': ['get', 'intensity'],
          'heatmap-intensity': 1,
          'heatmap-color': [
            'interpolate',
            ['linear'],
            ['heatmap-density'],
            0, 'rgba(0,0,255,0)',
            0.2, 'rgba(65,105,225,0.5)',
            0.4, 'rgba(0,255,255,0.6)',
            0.6, 'rgba(0,255,0,0.7)',
            0.8, 'rgba(255,255,0,0.8)',
            1, 'rgba(255,0,0,0.9)'
          ],
          'heatmap-radius': 30,
          'heatmap-opacity': 0.8
        }
      })
    })

    return () => {
      map.current?.remove()
      map.current = null
    }
  }, [theme])

  return (
    <div className="relative h-full w-full rounded-xl overflow-hidden shadow-md border border-border">
      <div ref={mapContainer} className="h-full w-full" />
      
      {/* Overlay UI */}
      <div className="absolute top-4 left-4 z-10 bg-card/90 backdrop-blur-sm p-4 rounded-lg shadow-lg border border-border w-64">
        <h3 className="font-heading font-bold text-foreground">Karnataka Crime Map</h3>
        <p className="text-xs text-muted-foreground mt-1">Live Geospatial Hotspot Engine</p>
        
        <div className="mt-4 space-y-2">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-red-500"></div>
            <span className="text-sm font-medium">Robbery Clusters</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-amber-500"></div>
            <span className="text-sm font-medium">Vehicle Theft</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-blue-500"></div>
            <span className="text-sm font-medium">Cyber Fraud Nodes</span>
          </div>
        </div>
      </div>
    </div>
  )
}
