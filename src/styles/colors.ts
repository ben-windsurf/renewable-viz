/**
 * Color palette for renewable energy visualization dashboard (MST-75)
 * Strictly enforced color scheme
 */

import { EnergyType } from '../types/powerPlant';

// Primary color palette
export const COLORS = {
  // Core palette
  PRIMARY: '#4a98d2',      // Blue - map accents, highlights, primary UI
  SECONDARY: '#92c362',    // Green - renewable energy layers, data viz
  TERTIARY: '#292929',     // Dark gray - backgrounds, typography
  
  // Extended palette for energy types
  ENERGY_TYPES: {
    [EnergyType.SOLAR]: '#92c362',        // Secondary green
    [EnergyType.WIND]: '#4a98d2',         // Primary blue
    [EnergyType.HYDRO]: '#6bb6ff',        // Light blue
    [EnergyType.HYDRO_PUMPED]: '#5aa3e6', // Medium blue
    [EnergyType.GEOTHERMAL]: '#ff8c42',   // Orange
    [EnergyType.NUCLEAR]: '#e74c3c',      // Red
    [EnergyType.NATURAL_GAS]: '#f39c12',  // Orange-yellow
    [EnergyType.COAL]: '#34495e',         // Dark blue-gray
    [EnergyType.BIOMASS]: '#27ae60',      // Forest green
    [EnergyType.BATTERY]: '#9b59b6',      // Purple
    [EnergyType.CRUDE_OIL]: '#8b4513',    // Brown
    [EnergyType.OTHER]: '#95a5a6',        // Gray
  } as const,
  
  // UI colors
  BACKGROUND: '#ffffff',
  SURFACE: '#f8f9fa',
  BORDER: '#e9ecef',
  TEXT_PRIMARY: '#292929',
  TEXT_SECONDARY: '#6c757d',
  TEXT_MUTED: '#adb5bd',
  
  // State colors
  SUCCESS: '#28a745',
  WARNING: '#ffc107',
  ERROR: '#dc3545',
  INFO: '#17a2b8',
  
  // Map colors
  MAP_BACKGROUND: '#f8f9fa',
  MAP_WATER: '#a8d8ea',
  MAP_LAND: '#ffffff',
  MAP_BORDER: '#dee2e6',
} as const;

// Color variants and utilities
export const createColorVariants = (baseColor: string) => ({
  base: baseColor,
  light: `${baseColor}20`, // 20% opacity
  medium: `${baseColor}60`, // 60% opacity
  dark: `${baseColor}cc`,   // 80% opacity
});

// Renewable energy color mapping
export const RENEWABLE_COLORS = {
  [EnergyType.SOLAR]: COLORS.ENERGY_TYPES[EnergyType.SOLAR],
  [EnergyType.WIND]: COLORS.ENERGY_TYPES[EnergyType.WIND],
  [EnergyType.HYDRO]: COLORS.ENERGY_TYPES[EnergyType.HYDRO],
  [EnergyType.HYDRO_PUMPED]: COLORS.ENERGY_TYPES[EnergyType.HYDRO_PUMPED],
  [EnergyType.GEOTHERMAL]: COLORS.ENERGY_TYPES[EnergyType.GEOTHERMAL],
  [EnergyType.BIOMASS]: COLORS.ENERGY_TYPES[EnergyType.BIOMASS],
} as const;

// Non-renewable energy color mapping
export const NON_RENEWABLE_COLORS = {
  [EnergyType.COAL]: COLORS.ENERGY_TYPES[EnergyType.COAL],
  [EnergyType.NATURAL_GAS]: COLORS.ENERGY_TYPES[EnergyType.NATURAL_GAS],
  [EnergyType.NUCLEAR]: COLORS.ENERGY_TYPES[EnergyType.NUCLEAR],
  [EnergyType.CRUDE_OIL]: COLORS.ENERGY_TYPES[EnergyType.CRUDE_OIL],
  [EnergyType.OTHER]: COLORS.ENERGY_TYPES[EnergyType.OTHER],
} as const;

// Utility functions
export const getEnergyTypeColor = (energyType: EnergyType): string => {
  return COLORS.ENERGY_TYPES[energyType] || COLORS.ENERGY_TYPES[EnergyType.OTHER];
};

export const isRenewableEnergyType = (energyType: EnergyType): boolean => {
  return energyType in RENEWABLE_COLORS;
};

export const hexToRgba = (hex: string, alpha: number): string => {
  const r = parseInt(hex.slice(1, 3), 16);
  const g = parseInt(hex.slice(3, 5), 16);
  const b = parseInt(hex.slice(5, 7), 16);
  return `rgba(${r}, ${g}, ${b}, ${alpha})`;
};

// Capacity-based color intensity
export const getCapacityColorIntensity = (capacity: number, maxCapacity: number): number => {
  if (maxCapacity === 0) return 0.3;
  const intensity = Math.min(capacity / maxCapacity, 1);
  return Math.max(intensity * 0.8 + 0.2, 0.3); // Ensure minimum visibility
};

// Marker size calculation
export const calculateMarkerSize = (capacity: number, maxCapacity: number): number => {
  if (maxCapacity === 0) return 8;
  const normalized = Math.min(capacity / maxCapacity, 1);
  return Math.max(normalized * 30 + 8, 8); // Size range: 8-38px
};
