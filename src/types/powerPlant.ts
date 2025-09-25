/**
 * TypeScript types for power plant data - mirrors Python data models
 */

export enum EnergyType {
  COAL = 'Coal',
  NATURAL_GAS = 'Natural Gas',
  NUCLEAR = 'Nuclear',
  HYDRO = 'Hydroelectric',
  HYDRO_PUMPED = 'Hydro Pumped Storage',
  SOLAR = 'Solar',
  WIND = 'Wind',
  GEOTHERMAL = 'Geothermal',
  BIOMASS = 'Biomass',
  BATTERY = 'Battery Storage',
  OTHER = 'Other',
  CRUDE_OIL = 'Crude Oil',
}

export enum SectorType {
  ELECTRIC_UTILITY = 'Electric Utility',
  IPP_NON_CHP = 'IPP Non-CHP',
  IPP_CHP = 'IPP CHP',
  COMBINED_HEAT_POWER = 'Combined Heat and Power',
}

export interface PowerPlantLocation {
  latitude: number;
  longitude: number;
  city: string;
  county: string;
  state: string;
  zip_code?: number;
  street_address?: string;
}

export interface PowerPlantCapacity {
  total_mw?: number;
  install_mw?: number;
  coal_mw?: number;
  natural_gas_mw?: number;
  nuclear_mw?: number;
  hydro_mw?: number;
  hydro_pumped_mw?: number;
  solar_mw?: number;
  wind_mw?: number;
  geothermal_mw?: number;
  biomass_mw?: number;
  battery_mw?: number;
  crude_oil_mw?: number;
  other_mw?: number;
  renewable_capacity_mw?: number;
}

export interface PowerPlant {
  object_id: number;
  plant_code: number;
  plant_name: string;
  utility_name: string;
  utility_id: number;
  sector_name: string;
  primary_source: string;
  primary_energy_type: EnergyType;
  is_renewable: boolean;
  
  // Location
  latitude: number;
  longitude: number;
  city: string;
  county: string;
  state: string;
  zip_code?: number;
  street_address?: string;
  
  // Capacity
  total_mw?: number;
  install_mw?: number;
  coal_mw?: number;
  natural_gas_mw?: number;
  nuclear_mw?: number;
  hydro_mw?: number;
  hydro_pumped_mw?: number;
  solar_mw?: number;
  wind_mw?: number;
  geothermal_mw?: number;
  biomass_mw?: number;
  battery_mw?: number;
  crude_oil_mw?: number;
  other_mw?: number;
  renewable_capacity_mw?: number;
  
  // Additional fields
  tech_desc?: string;
  source_desc?: string;
  data_period?: number;
  source?: string;
}

export interface FilterOptions {
  energyTypes: EnergyType[];
  minCapacity?: number;
  maxCapacity?: number;
  minYear?: number;
  maxYear?: number;
  states: string[];
  renewableOnly: boolean;
}

export interface MapViewState {
  longitude: number;
  latitude: number;
  zoom: number;
  pitch?: number;
  bearing?: number;
}

export interface MarkerStyle {
  color: string;
  size: number;
  opacity: number;
}

export interface LegendItem {
  energyType: EnergyType;
  color: string;
  count: number;
  totalCapacity: number;
}
