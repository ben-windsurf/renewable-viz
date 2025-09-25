/**
 * Main application entry point
 */

import { PowerPlantMap } from './components/PowerPlantMap';
import { FilterControls } from './components/FilterControls';
import { PowerPlant, FilterOptions } from './types/powerPlant';

class PowerPlantApp {
  private map: PowerPlantMap | null = null;
  private filterControls: FilterControls | null = null;
  private data: PowerPlant[] = [];
  private loadingOverlay: HTMLElement | null = null;
  private errorContainer: HTMLElement | null = null;
  private statsPanel: HTMLElement | null = null;

  constructor() {
    this.loadingOverlay = document.getElementById('loading-overlay');
    this.errorContainer = document.getElementById('error-container');
    this.statsPanel = document.getElementById('stats-content');
    
    this.init();
  }

  private async init(): Promise<void> {
    try {
      // Get Mapbox token from environment
      const mapboxToken = this.getMapboxToken();
      
      if (!mapboxToken) {
        throw new Error('Mapbox access token not found. Please check your .env file.');
      }

      // Initialize map
      this.map = new PowerPlantMap('map', mapboxToken, {
        longitude: -98.5,
        latitude: 39.8,
        zoom: 4
      });

      // Initialize filter controls
      this.filterControls = new FilterControls({
        container: 'filter-controls',
        onFilterChange: (filters) => this.handleFilterChange(filters),
        initialFilters: {
          minYear: 2024,
          renewableOnly: false
        }
      });

      // Load data
      await this.loadData();

      // Bind map controls
      this.bindMapControls();

      // Hide loading overlay
      this.hideLoading();

    } catch (error) {
      console.error('Application initialization failed:', error);
      this.showError(error instanceof Error ? error.message : 'Unknown error occurred');
      this.hideLoading();
    }
  }

  /**
   * Get Mapbox token from various sources
   */
  private getMapboxToken(): string {
    // Try to get from environment variable (if using Vite)
    if (import.meta.env?.VITE_MAPBOX_ACCESS_TOKEN) {
      return import.meta.env.VITE_MAPBOX_ACCESS_TOKEN;
    }

    // Try to get from global variable (fallback)
    if ((window as any).MAPBOX_ACCESS_TOKEN) {
      return (window as any).MAPBOX_ACCESS_TOKEN;
    }

    // Return the token from .env file (you'll need to replace this with actual token)
    return 'pk.eyJ1IjoiYmVubGVocmJ1cmdlcndpbmRzdXJmIiwiYSI6ImNtZW5ocGJ5bDEzODkybHB0dnQ2NGVtY3gifQ.te8qH4yvI2-VKuguoFAaZA';
  }

  /**
   * Load power plant data
   */
  private async loadData(): Promise<void> {
    try {
      // Try to load from exported JSON first
      console.log('Loading power plant data...');
      this.data = await this.loadFromJSON();
      console.log(`Loaded ${this.data.length} power plants`);
      
      if (this.data.length === 0) {
        // If no JSON data, try sample data
        console.log('No exported data found, loading sample data...');
        this.data = await this.loadSampleData();
        console.log(`Loaded ${this.data.length} sample plants`);
      }

      // Debug: Check sample data
      console.log('Sample plants:', this.data.slice(0, 3).map(p => ({
        name: p.plant_name,
        lat: p.latitude,
        lng: p.longitude,
        period: p.data_period,
        year: p.data_period ? Math.floor(p.data_period / 100) : null,
        energyType: p.primary_energy_type
      })));

      // Load data into map
      if (this.map && this.data.length > 0) {
        await this.map.loadData(this.data);
        this.updateStatistics();
        
        if (this.data.length <= 10) {
          this.showError('Using sample data. Run "python3 scripts/export_data.py" for full dataset.');
        }
      } else {
        throw new Error('Failed to load data. Please run "python3 scripts/export_data.py" to generate data files.');
      }

    } catch (error) {
      console.error('Data loading failed:', error);
      this.showError(`Failed to load data: ${error instanceof Error ? error.message : String(error)}`);
    }
  }

  /**
   * Load data from exported JSON files
   */
  private async loadFromJSON(): Promise<PowerPlant[]> {
    const urls = [
      '/data/power_plants_mixed.json',
      '/data/power_plants_comprehensive.json',
      '/data/sample_plants.json'
    ];

    for (const url of urls) {
      try {
        const response = await fetch(url);
        if (response.ok) {
          const data = await response.json();
          console.log(`Loaded ${data.length} plants from ${url}`);
          return data;
        }
      } catch (error) {
        console.warn(`Failed to load from ${url}:`, error);
      }
    }

    return [];
  }

  /**
   * Load sample data for demonstration
   */
  private async loadSampleData(): Promise<PowerPlant[]> {
    // Create some sample data for demonstration
    const sampleData: PowerPlant[] = [
      {
        object_id: 1,
        plant_code: 1001,
        plant_name: 'Sample Solar Farm',
        utility_name: 'Green Energy Corp',
        utility_id: 1001,
        sector_name: 'IPP Non-CHP',
        primary_source: 'solar',
        primary_energy_type: 'Solar' as any,
        is_renewable: true,
        latitude: 36.7783,
        longitude: -119.4179,
        city: 'Fresno',
        county: 'Fresno',
        state: 'California',
        total_mw: 150,
        solar_mw: 150,
        renewable_capacity_mw: 150,
        data_period: 202401
      },
      {
        object_id: 2,
        plant_code: 1002,
        plant_name: 'Sample Wind Farm',
        utility_name: 'Wind Power LLC',
        utility_id: 1002,
        sector_name: 'IPP Non-CHP',
        primary_source: 'wind',
        primary_energy_type: 'Wind' as any,
        is_renewable: true,
        latitude: 39.7391,
        longitude: -104.9847,
        city: 'Denver',
        county: 'Denver',
        state: 'Colorado',
        total_mw: 200,
        wind_mw: 200,
        renewable_capacity_mw: 200,
        data_period: 202401
      },
      {
        object_id: 3,
        plant_code: 1003,
        plant_name: 'Sample Natural Gas Plant',
        utility_name: 'Power Utilities Inc',
        utility_id: 1003,
        sector_name: 'Electric Utility',
        primary_source: 'natural gas',
        primary_energy_type: 'Natural Gas' as any,
        is_renewable: false,
        latitude: 29.7604,
        longitude: -95.3698,
        city: 'Houston',
        county: 'Harris',
        state: 'Texas',
        total_mw: 500,
        natural_gas_mw: 500,
        renewable_capacity_mw: 0,
        data_period: 202401
      }
    ];

    return sampleData;
  }

  /**
   * Handle filter changes
   */
  private handleFilterChange(filters: Partial<FilterOptions>): void {
    if (this.map) {
      this.map.updateFilters(filters);
      this.updateStatistics();
    }
  }

  /**
   * Update statistics display
   */
  private updateStatistics(): void {
    if (!this.map || !this.statsPanel) return;

    const stats = this.map.getStatistics();
    
    const html = `
      <div class="stat-item">
        <span class="stat-label">Total Plants:</span>
        <span class="stat-value">${stats.totalPlants.toLocaleString()}</span>
      </div>
      <div class="stat-item">
        <span class="stat-label">Total Capacity:</span>
        <span class="stat-value">${stats.totalCapacity.toFixed(0)} MW</span>
      </div>
      <div class="stat-item">
        <span class="stat-label">Renewable:</span>
        <span class="stat-value">${stats.renewableCapacity.toFixed(0)} MW</span>
      </div>
      <div class="stat-item">
        <span class="stat-label">Renewable %:</span>
        <span class="stat-value">${((stats.renewableCapacity / stats.totalCapacity) * 100 || 0).toFixed(1)}%</span>
      </div>
    `;

    this.statsPanel.innerHTML = html;
  }

  /**
   * Bind map control events
   */
  private bindMapControls(): void {
    const fitToDataBtn = document.getElementById('fit-to-data');
    const exportImageBtn = document.getElementById('export-image');

    fitToDataBtn?.addEventListener('click', () => {
      if (this.map) {
        this.map.fitToData();
      }
    });

    exportImageBtn?.addEventListener('click', () => {
      if (this.map) {
        const imageData = this.map.exportImage();
        this.downloadImage(imageData, 'power-plants-map.png');
      }
    });
  }

  /**
   * Download image
   */
  private downloadImage(dataUrl: string, filename: string): void {
    const link = document.createElement('a');
    link.download = filename;
    link.href = dataUrl;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }

  /**
   * Show error message
   */
  private showError(message: string): void {
    if (this.errorContainer) {
      this.errorContainer.innerHTML = `
        <div class="error-message">
          <strong>Error:</strong> ${message}
        </div>
      `;
    }
  }

  /**
   * Hide loading overlay
   */
  private hideLoading(): void {
    if (this.loadingOverlay) {
      this.loadingOverlay.style.display = 'none';
    }
  }

  /**
   * Show loading overlay
   */
  private showLoading(): void {
    if (this.loadingOverlay) {
      this.loadingOverlay.style.display = 'flex';
    }
  }
}

// Initialize application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  new PowerPlantApp();
});

// Handle window resize
window.addEventListener('resize', () => {
  // Resize map if it exists
  const app = (window as any).powerPlantApp;
  if (app && app.map) {
    app.map.resize();
  }
});
