"use client"

import * as React from 'react';
import Map, { NavigationControl, FullscreenControl, ScaleControl, MapRef } from 'react-map-gl/maplibre';
import 'maplibre-gl/dist/maplibre-gl.css';
import { useTheme } from 'next-themes';

interface MapShellProps {
  children?: React.ReactNode;
  initialViewState?: {
    longitude: number;
    latitude: number;
    zoom: number;
    pitch?: number;
    bearing?: number;
  };
  className?: string;
  onMapLoad?: (map: any) => void;
}

export function MapShell({ 
  children, 
  initialViewState = {
    longitude: 76.6214, // Center of Karnataka (approx)
    latitude: 14.8871,
    zoom: 6,
    pitch: 45,
    bearing: 0
  },
  className = "",
  onMapLoad
}: MapShellProps) {
  const { resolvedTheme } = useTheme();
  const mapRef = React.useRef<any>(null);
  const [mounted, setMounted] = React.useState(false);

  React.useEffect(() => {
    setMounted(true);
  }, []);

  const mapStyle = resolvedTheme === 'dark' 
    ? "https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json"
    : "https://basemaps.cartocdn.com/gl/positron-gl-style/style.json";

  if (!mounted) {
    return <div className={`w-full h-full bg-secondary/50 animate-pulse rounded-lg flex items-center justify-center text-muted-foreground ${className}`}>Initializing Map...</div>
  }

  return (
    <div className={`relative w-full h-full overflow-hidden rounded-lg ${className}`}>
      <Map
        ref={mapRef}
        initialViewState={initialViewState}
        mapStyle={mapStyle}
        onLoad={(e) => onMapLoad?.(e.target as any)}
        attributionControl={false}
      >
        <NavigationControl position="top-right" />
        <FullscreenControl position="top-right" />
        <ScaleControl position="bottom-right" />
        
        {/* Render Deck.gl layers or custom maplibre markers here */}
        {children}
      </Map>
    </div>
  );
}
