/**
 * Mapbox visualization component for power plants
 */

import mapboxgl from 'mapbox-gl';
import { PowerPlant, EnergyType, FilterOptions, MapViewState } from '../types/powerPlant';
import { getEnergyTypeColor, calculateMarkerSize } from '../styles/colors';

export class PowerPlantMap {
  private map: mapboxgl.Map;
  private container: HTMLElement;
  private data: PowerPlant[] = [];
  private filteredData: PowerPlant[] = [];
  private markers: mapboxgl.Marker[] = [];
  private popups: mapboxgl.Popup[] = [];
  private filters: FilterOptions;
  private maxCapacity: number = 0;

  constructor(
    container: HTMLElement | string,
    accessToken: string,
    initialView: MapViewState = {
      longitude: -98.5,
      latitude: 39.8,
      zoom: 4
    }
  ) {
    // Set Mapbox access token
    mapboxgl.accessToken = accessToken;

    // Get container element
    this.container = typeof container === 'string' 
      ? document.getElementById(container)! 
      : container;

    // Initialize filters
    this.filters = {
      energyTypes: Object.values(EnergyType),
      minCapacity: undefined,
      maxCapacity: undefined,
      minYear: 2020,
      maxYear: undefined,
      states: [],
      renewableOnly: false
    };

    // Initialize map
    this.map = new mapboxgl.Map({
      container: this.container,
      style: 'mapbox://styles/mapbox/light-v11',
      center: [initialView.longitude, initialView.latitude],
      zoom: initialView.zoom,
      pitch: initialView.pitch || 0,
      bearing: initialView.bearing || 0
    });

    // Add navigation controls
    this.map.addControl(new mapboxgl.NavigationControl(), 'top-right');

    // Add fullscreen control
    this.map.addControl(new mapboxgl.FullscreenControl(), 'top-right');

    // Wait for map to load
    this.map.on('load', () => {
      this.onMapLoad();
    });
  }

  private onMapLoad(): void {
    // Map is ready, can add data now
    console.log('Map loaded successfully');
  }

  /**
   * Load power plant data
   */
  public async loadData(data: PowerPlant[]): Promise<void> {
    this.data = data;
    this.calculateMaxCapacity();
    this.applyFilters();
    this.renderMarkers();
  }

  /**
   * Calculate maximum capacity for marker sizing
   */
  private calculateMaxCapacity(): void {
    this.maxCapacity = Math.max(
      ...this.data.map(plant => plant.total_mw || 0)
    );
  }

  /**
   * Apply current filters to data
   */
  private applyFilters(): void {
    this.filteredData = this.data.filter(plant => {
      // Energy type filter
      if (!this.filters.energyTypes.includes(plant.primary_energy_type)) {
        return false;
      }

      // Capacity filters
      const capacity = plant.total_mw || 0;
      if (this.filters.minCapacity !== undefined && capacity < this.filters.minCapacity) {
        return false;
      }
      if (this.filters.maxCapacity !== undefined && capacity > this.filters.maxCapacity) {
        return false;
      }

      // Year filters
      if (plant.data_period) {
        const year = Math.floor(plant.data_period / 100);
        if (this.filters.minYear !== undefined && year < this.filters.minYear) {
          return false;
        }
        if (this.filters.maxYear !== undefined && year > this.filters.maxYear) {
          return false;
        }
      }

      // State filter
      if (this.filters.states.length > 0 && !this.filters.states.includes(plant.state)) {
        return false;
      }

      // Renewable only filter
      if (this.filters.renewableOnly && !plant.is_renewable) {
        return false;
      }

      return true;
    });

    console.log(`Filtered ${this.filteredData.length} plants from ${this.data.length} total`);
  }

  /**
   * Render markers on the map
   */
  private renderMarkers(): void {
    // Clear existing markers
    this.clearMarkers();

    // Create markers for filtered data
    this.filteredData.forEach(plant => {
      const marker = this.createMarker(plant);
      this.markers.push(marker);
    });
  }

  /**
   * Create a marker for a power plant
   */
  private createMarker(plant: PowerPlant): mapboxgl.Marker {
    const capacity = plant.total_mw || 0;
    const color = getEnergyTypeColor(plant.primary_energy_type);
    const size = calculateMarkerSize(capacity, this.maxCapacity);

    // Create marker element
    const el = document.createElement('div');
    el.className = 'power-plant-marker';
    el.style.width = `${size}px`;
    el.style.height = `${size}px`;
    el.style.backgroundColor = color;
    el.style.border = '2px solid white';
    el.style.borderRadius = '50%';
    el.style.cursor = 'pointer';
    el.style.boxShadow = '0 2px 4px rgba(0,0,0,0.2)';
    el.style.transition = 'box-shadow 0.2s ease';
    el.style.transformOrigin = 'center center';

    // Add hover effects using box-shadow instead of transform to avoid mouse issues
    el.addEventListener('mouseenter', () => {
      el.style.boxShadow = '0 0 0 3px rgba(255,255,255,0.8), 0 4px 8px rgba(0,0,0,0.3)';
      el.style.zIndex = '1000';
    });

    el.addEventListener('mouseleave', () => {
      el.style.boxShadow = '0 2px 4px rgba(0,0,0,0.2)';
      el.style.zIndex = 'auto';
    });

    // Create popup
    const popup = new mapboxgl.Popup({
      offset: 25,
      closeButton: true,
      closeOnClick: false
    }).setHTML(this.createPopupContent(plant));

    // Create marker
    const marker = new mapboxgl.Marker(el)
      .setLngLat([plant.longitude, plant.latitude])
      .setPopup(popup)
      .addTo(this.map);

    return marker;
  }

  /**
   * Create popup content for a power plant
   */
  private createPopupContent(plant: PowerPlant): string {
    const capacity = plant.total_mw || 0;
    const renewableCapacity = plant.renewable_capacity_mw || 0;
    
    return `
      <div class="power-plant-popup">
        <h3 style="margin: 0 0 8px 0; color: var(--color-text-primary);">
          ${plant.plant_name}
        </h3>
        
        <div style="margin-bottom: 8px;">
          <strong>Energy Type:</strong> 
          <span style="color: ${getEnergyTypeColor(plant.primary_energy_type)};">
            ${plant.primary_energy_type}
          </span>
        </div>
        
        <div style="margin-bottom: 8px;">
          <strong>Total Capacity:</strong> ${capacity.toFixed(1)} MW
        </div>
        
        ${renewableCapacity > 0 ? `
          <div style="margin-bottom: 8px;">
            <strong>Renewable Capacity:</strong> ${renewableCapacity.toFixed(1)} MW
          </div>
        ` : ''}
        
        <div style="margin-bottom: 8px;">
          <strong>Utility:</strong> ${plant.utility_name}
        </div>
        
        <div style="margin-bottom: 8px;">
          <strong>Location:</strong> ${plant.city}, ${plant.state}
        </div>
        
        ${plant.data_period ? `
          <div style="margin-bottom: 8px;">
            <strong>Data Period:</strong> ${Math.floor(plant.data_period / 100)}
          </div>
        ` : ''}
        
        ${plant.tech_desc ? `
          <div style="margin-bottom: 8px;">
            <strong>Technology:</strong> ${plant.tech_desc}
          </div>
        ` : ''}
      </div>
    `;
  }

  /**
   * Clear all markers from the map
   */
  private clearMarkers(): void {
    this.markers.forEach(marker => marker.remove());
    this.markers = [];
    
    this.popups.forEach(popup => popup.remove());
    this.popups = [];
  }

  /**
   * Update filters and re-render
   */
  public updateFilters(newFilters: Partial<FilterOptions>): void {
    this.filters = { ...this.filters, ...newFilters };
    this.applyFilters();
    this.renderMarkers();
  }

  /**
   * Get current filters
   */
  public getFilters(): FilterOptions {
    return { ...this.filters };
  }

  /**
   * Get filtered data
   */
  public getFilteredData(): PowerPlant[] {
    return [...this.filteredData];
  }

  /**
   * Fit map to show all filtered markers
   */
  public fitToData(): void {
    if (this.filteredData.length === 0) return;

    const bounds = new mapboxgl.LngLatBounds();
    
    this.filteredData.forEach(plant => {
      bounds.extend([plant.longitude, plant.latitude]);
    });

    this.map.fitBounds(bounds, {
      padding: 50,
      maxZoom: 10
    });
  }

  /**
   * Fly to a specific location
   */
  public flyTo(longitude: number, latitude: number, zoom: number = 8): void {
    this.map.flyTo({
      center: [longitude, latitude],
      zoom: zoom,
      duration: 1500
    });
  }

  /**
   * Get map instance for advanced usage
   */
  public getMap(): mapboxgl.Map {
    return this.map;
  }

  /**
   * Resize map (call when container size changes)
   */
  public resize(): void {
    this.map.resize();
  }

  /**
   * Destroy map and clean up
   */
  public destroy(): void {
    this.clearMarkers();
    this.map.remove();
  }

  /**
   * Export current view as image
   */
  public exportImage(): string {
    return this.map.getCanvas().toDataURL();
  }

  /**
   * Get statistics for current filtered data
   */
  public getStatistics(): {
    totalPlants: number;
    totalCapacity: number;
    renewableCapacity: number;
    energyTypeBreakdown: Record<string, number>;
    stateBreakdown: Record<string, number>;
  } {
    const stats = {
      totalPlants: this.filteredData.length,
      totalCapacity: 0,
      renewableCapacity: 0,
      energyTypeBreakdown: {} as Record<string, number>,
      stateBreakdown: {} as Record<string, number>
    };

    this.filteredData.forEach(plant => {
      // Capacity totals
      stats.totalCapacity += plant.total_mw || 0;
      stats.renewableCapacity += plant.renewable_capacity_mw || 0;

      // Energy type breakdown
      const energyType = plant.primary_energy_type;
      stats.energyTypeBreakdown[energyType] = (stats.energyTypeBreakdown[energyType] || 0) + 1;

      // State breakdown
      const state = plant.state;
      stats.stateBreakdown[state] = (stats.stateBreakdown[state] || 0) + 1;
    });

    return stats;
  }
}
