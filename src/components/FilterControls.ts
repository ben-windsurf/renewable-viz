/**
 * Filter controls for power plant visualization
 */

import { EnergyType, FilterOptions } from '../types/powerPlant';
import { getEnergyTypeColor, isRenewableEnergyType } from '../styles/colors';

export interface FilterControlsConfig {
  container: HTMLElement | string;
  onFilterChange: (filters: Partial<FilterOptions>) => void;
  initialFilters?: Partial<FilterOptions>;
}

export class FilterControls {
  private container: HTMLElement;
  private onFilterChange: (filters: Partial<FilterOptions>) => void;
  private currentFilters: FilterOptions;

  constructor(config: FilterControlsConfig) {
    this.container = typeof config.container === 'string' 
      ? document.getElementById(config.container)! 
      : config.container;
    
    this.onFilterChange = config.onFilterChange;
    
    // Initialize filters
    this.currentFilters = {
      energyTypes: Object.values(EnergyType),
      minCapacity: undefined,
      maxCapacity: undefined,
      minYear: 2020,
      maxYear: undefined,
      states: [],
      renewableOnly: false,
      ...config.initialFilters
    };

    this.render();
    this.bindEvents();
  }

  /**
   * Render the filter controls
   */
  private render(): void {
    this.container.innerHTML = `
      <div class="filter-controls">
        <div class="card">
          <div class="card-header">
            <h3 class="mb-0">Filters</h3>
          </div>
          
          <div class="card-body">
            <!-- Energy Type Filters -->
            <div class="form-group">
              <label class="form-label">Energy Types</label>
              <div class="energy-type-controls mb-2">
                <button type="button" class="btn btn-sm btn-outline" id="select-all-energy">
                  Select All
                </button>
                <button type="button" class="btn btn-sm btn-outline" id="select-renewable">
                  Renewable Only
                </button>
                <button type="button" class="btn btn-sm btn-outline" id="clear-energy">
                  Clear All
                </button>
              </div>
              <div class="energy-type-checkboxes">
                ${this.renderEnergyTypeCheckboxes()}
              </div>
            </div>

            <!-- Capacity Range -->
            <div class="form-group">
              <label class="form-label">Capacity Range (MW)</label>
              <div class="d-flex" style="gap: 8px;">
                <input 
                  type="number" 
                  class="form-control" 
                  id="min-capacity"
                  placeholder="Min MW"
                  min="0"
                  step="0.1"
                  value="${this.currentFilters.minCapacity || ''}"
                >
                <input 
                  type="number" 
                  class="form-control" 
                  id="max-capacity"
                  placeholder="Max MW"
                  min="0"
                  step="0.1"
                  value="${this.currentFilters.maxCapacity || ''}"
                >
              </div>
            </div>

            <!-- Year Range -->
            <div class="form-group">
              <label class="form-label">Data Period</label>
              <div class="d-flex" style="gap: 8px;">
                <input 
                  type="number" 
                  class="form-control" 
                  id="min-year"
                  placeholder="Min Year"
                  min="2020"
                  max="2030"
                  value="${this.currentFilters.minYear || ''}"
                >
                <input 
                  type="number" 
                  class="form-control" 
                  id="max-year"
                  placeholder="Max Year"
                  min="2020"
                  max="2030"
                  value="${this.currentFilters.maxYear || ''}"
                >
              </div>
            </div>

            <!-- State Filter -->
            <div class="form-group">
              <label class="form-label">States</label>
              <select class="form-control form-select" id="state-filter" multiple>
                <option value="">All States</option>
                ${this.renderStateOptions()}
              </select>
              <small class="text-muted">Hold Ctrl/Cmd to select multiple states</small>
            </div>

            <!-- Renewable Only Toggle -->
            <div class="form-group">
              <div class="form-check">
                <input 
                  type="checkbox" 
                  class="form-check-input" 
                  id="renewable-only"
                  ${this.currentFilters.renewableOnly ? 'checked' : ''}
                >
                <label class="form-check-label" for="renewable-only">
                  Show renewable energy plants only
                </label>
              </div>
            </div>

            <!-- Action Buttons -->
            <div class="form-group mb-0">
              <div class="d-flex" style="gap: 8px;">
                <button type="button" class="btn btn-primary" id="apply-filters">
                  Apply Filters
                </button>
                <button type="button" class="btn btn-outline" id="reset-filters">
                  Reset
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Filter Summary -->
        <div class="card mt-3">
          <div class="card-header">
            <h4 class="mb-0">Active Filters</h4>
          </div>
          <div class="card-body" id="filter-summary">
            ${this.renderFilterSummary()}
          </div>
        </div>
      </div>
    `;
  }

  /**
   * Render energy type checkboxes
   */
  private renderEnergyTypeCheckboxes(): string {
    return Object.values(EnergyType).map(energyType => {
      const isChecked = this.currentFilters.energyTypes.includes(energyType);
      const color = getEnergyTypeColor(energyType);
      const isRenewable = isRenewableEnergyType(energyType);
      
      return `
        <div class="form-check energy-type-check">
          <input 
            type="checkbox" 
            class="form-check-input energy-type-checkbox" 
            id="energy-${energyType.replace(/\s+/g, '-').toLowerCase()}"
            value="${energyType}"
            ${isChecked ? 'checked' : ''}
          >
          <label class="form-check-label" for="energy-${energyType.replace(/\s+/g, '-').toLowerCase()}">
            <span 
              class="energy-type-indicator" 
              style="background-color: ${color};"
            ></span>
            ${energyType}
            ${isRenewable ? '<span class="renewable-badge">R</span>' : ''}
          </label>
        </div>
      `;
    }).join('');
  }

  /**
   * Render state options
   */
  private renderStateOptions(): string {
    const states = [
      'Alabama', 'Alaska', 'Arizona', 'Arkansas', 'California', 'Colorado', 'Connecticut',
      'Delaware', 'Florida', 'Georgia', 'Hawaii', 'Idaho', 'Illinois', 'Indiana', 'Iowa',
      'Kansas', 'Kentucky', 'Louisiana', 'Maine', 'Maryland', 'Massachusetts', 'Michigan',
      'Minnesota', 'Mississippi', 'Missouri', 'Montana', 'Nebraska', 'Nevada', 'New Hampshire',
      'New Jersey', 'New Mexico', 'New York', 'North Carolina', 'North Dakota', 'Ohio',
      'Oklahoma', 'Oregon', 'Pennsylvania', 'Rhode Island', 'South Carolina', 'South Dakota',
      'Tennessee', 'Texas', 'Utah', 'Vermont', 'Virginia', 'Washington', 'West Virginia',
      'Wisconsin', 'Wyoming'
    ];

    return states.map(state => {
      const isSelected = this.currentFilters.states.includes(state);
      return `<option value="${state}" ${isSelected ? 'selected' : ''}>${state}</option>`;
    }).join('');
  }

  /**
   * Render filter summary
   */
  private renderFilterSummary(): string {
    const summary = [];

    // Energy types
    if (this.currentFilters.energyTypes.length < Object.values(EnergyType).length) {
      summary.push(`Energy Types: ${this.currentFilters.energyTypes.length} selected`);
    }

    // Capacity range
    if (this.currentFilters.minCapacity !== undefined || this.currentFilters.maxCapacity !== undefined) {
      const min = this.currentFilters.minCapacity || 0;
      const max = this.currentFilters.maxCapacity || '∞';
      summary.push(`Capacity: ${min} - ${max} MW`);
    }

    // Year range
    if (this.currentFilters.minYear !== undefined || this.currentFilters.maxYear !== undefined) {
      const min = this.currentFilters.minYear || 'Any';
      const max = this.currentFilters.maxYear || 'Latest';
      summary.push(`Years: ${min} - ${max}`);
    }

    // States
    if (this.currentFilters.states.length > 0) {
      summary.push(`States: ${this.currentFilters.states.length} selected`);
    }

    // Renewable only
    if (this.currentFilters.renewableOnly) {
      summary.push('Renewable energy only');
    }

    return summary.length > 0 
      ? `<ul class="mb-0">${summary.map(item => `<li>${item}</li>`).join('')}</ul>`
      : '<p class="text-muted mb-0">No active filters</p>';
  }

  /**
   * Bind event listeners
   */
  private bindEvents(): void {
    // Energy type controls
    const selectAllBtn = this.container.querySelector('#select-all-energy') as HTMLButtonElement;
    const selectRenewableBtn = this.container.querySelector('#select-renewable') as HTMLButtonElement;
    const clearEnergyBtn = this.container.querySelector('#clear-energy') as HTMLButtonElement;

    selectAllBtn?.addEventListener('click', () => {
      this.selectAllEnergyTypes();
    });

    selectRenewableBtn?.addEventListener('click', () => {
      this.selectRenewableEnergyTypes();
    });

    clearEnergyBtn?.addEventListener('click', () => {
      this.clearEnergyTypes();
    });

    // Individual energy type checkboxes
    const energyCheckboxes = this.container.querySelectorAll('.energy-type-checkbox') as NodeListOf<HTMLInputElement>;
    energyCheckboxes.forEach(checkbox => {
      checkbox.addEventListener('change', () => {
        this.updateEnergyTypeFilters();
      });
    });

    // Capacity inputs
    const minCapacityInput = this.container.querySelector('#min-capacity') as HTMLInputElement;
    const maxCapacityInput = this.container.querySelector('#max-capacity') as HTMLInputElement;

    minCapacityInput?.addEventListener('input', () => {
      this.updateCapacityFilters();
    });

    maxCapacityInput?.addEventListener('input', () => {
      this.updateCapacityFilters();
    });

    // Year inputs
    const minYearInput = this.container.querySelector('#min-year') as HTMLInputElement;
    const maxYearInput = this.container.querySelector('#max-year') as HTMLInputElement;

    minYearInput?.addEventListener('input', () => {
      this.updateYearFilters();
    });

    maxYearInput?.addEventListener('input', () => {
      this.updateYearFilters();
    });

    // State filter
    const stateSelect = this.container.querySelector('#state-filter') as HTMLSelectElement;
    stateSelect?.addEventListener('change', () => {
      this.updateStateFilters();
    });

    // Renewable only checkbox
    const renewableCheckbox = this.container.querySelector('#renewable-only') as HTMLInputElement;
    renewableCheckbox?.addEventListener('change', () => {
      this.updateRenewableFilter();
    });

    // Action buttons
    const applyBtn = this.container.querySelector('#apply-filters') as HTMLButtonElement;
    const resetBtn = this.container.querySelector('#reset-filters') as HTMLButtonElement;

    applyBtn?.addEventListener('click', () => {
      this.applyFilters();
    });

    resetBtn?.addEventListener('click', () => {
      this.resetFilters();
    });
  }

  /**
   * Select all energy types
   */
  private selectAllEnergyTypes(): void {
    const checkboxes = this.container.querySelectorAll('.energy-type-checkbox') as NodeListOf<HTMLInputElement>;
    checkboxes.forEach(checkbox => {
      checkbox.checked = true;
    });
    this.updateEnergyTypeFilters();
  }

  /**
   * Select only renewable energy types
   */
  private selectRenewableEnergyTypes(): void {
    const checkboxes = this.container.querySelectorAll('.energy-type-checkbox') as NodeListOf<HTMLInputElement>;
    checkboxes.forEach(checkbox => {
      const energyType = checkbox.value as EnergyType;
      checkbox.checked = isRenewableEnergyType(energyType);
    });
    this.updateEnergyTypeFilters();
  }

  /**
   * Clear all energy types
   */
  private clearEnergyTypes(): void {
    const checkboxes = this.container.querySelectorAll('.energy-type-checkbox') as NodeListOf<HTMLInputElement>;
    checkboxes.forEach(checkbox => {
      checkbox.checked = false;
    });
    this.updateEnergyTypeFilters();
  }

  /**
   * Update energy type filters
   */
  private updateEnergyTypeFilters(): void {
    const checkboxes = this.container.querySelectorAll('.energy-type-checkbox:checked') as NodeListOf<HTMLInputElement>;
    this.currentFilters.energyTypes = Array.from(checkboxes).map(cb => cb.value as EnergyType);
    this.updateFilterSummary();
  }

  /**
   * Update capacity filters
   */
  private updateCapacityFilters(): void {
    const minInput = this.container.querySelector('#min-capacity') as HTMLInputElement;
    const maxInput = this.container.querySelector('#max-capacity') as HTMLInputElement;

    this.currentFilters.minCapacity = minInput.value ? parseFloat(minInput.value) : undefined;
    this.currentFilters.maxCapacity = maxInput.value ? parseFloat(maxInput.value) : undefined;
    this.updateFilterSummary();
  }

  /**
   * Update year filters
   */
  private updateYearFilters(): void {
    const minInput = this.container.querySelector('#min-year') as HTMLInputElement;
    const maxInput = this.container.querySelector('#max-year') as HTMLInputElement;

    this.currentFilters.minYear = minInput.value ? parseInt(minInput.value) : undefined;
    this.currentFilters.maxYear = maxInput.value ? parseInt(maxInput.value) : undefined;
    this.updateFilterSummary();
  }

  /**
   * Update state filters
   */
  private updateStateFilters(): void {
    const select = this.container.querySelector('#state-filter') as HTMLSelectElement;
    const selectedOptions = Array.from(select.selectedOptions);
    this.currentFilters.states = selectedOptions.map(option => option.value).filter(value => value !== '');
    this.updateFilterSummary();
  }

  /**
   * Update renewable filter
   */
  private updateRenewableFilter(): void {
    const checkbox = this.container.querySelector('#renewable-only') as HTMLInputElement;
    this.currentFilters.renewableOnly = checkbox.checked;
    this.updateFilterSummary();
  }

  /**
   * Update filter summary display
   */
  private updateFilterSummary(): void {
    const summaryContainer = this.container.querySelector('#filter-summary');
    if (summaryContainer) {
      summaryContainer.innerHTML = this.renderFilterSummary();
    }
  }

  /**
   * Apply current filters
   */
  private applyFilters(): void {
    this.onFilterChange(this.currentFilters);
  }

  /**
   * Get current filters
   */
  public getFilters(): FilterOptions {
    return { ...this.currentFilters };
  }

  /**
   * Set filters programmatically
   */
  public setFilters(filters: Partial<FilterOptions>): void {
    this.currentFilters = { ...this.currentFilters, ...filters };
    this.render();
    this.bindEvents();
  }

  /**
   * Reset all filters to default
   */
  private resetFilters(): void {
    this.currentFilters = {
      energyTypes: Object.values(EnergyType),
      minCapacity: undefined,
      maxCapacity: undefined,
      minYear: 2020,
      maxYear: undefined,
      states: [],
      renewableOnly: false
    };

    this.render();
    this.bindEvents();
    this.onFilterChange(this.currentFilters);
  }
}
