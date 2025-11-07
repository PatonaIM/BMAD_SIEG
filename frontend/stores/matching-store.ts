/**
 * Matching UI State Store
 * 
 * Zustand store for managing job matching UI state that doesn't need
 * to be persisted (expanded explanations, filters).
 * 
 * @example
 * ```tsx
 * const { expandedExplanations, toggleExplanation } = useMatchingStore();
 * 
 * const isExpanded = expandedExplanations.has(jobId);
 * 
 * <Button onClick={() => toggleExplanation(jobId)}>
 *   {isExpanded ? 'Hide' : 'Show'} Explanation
 * </Button>
 * ```
 */

import { create } from 'zustand';
import type { MatchingFilters } from '@/types/matching';

interface MatchingState {
  // Set of job IDs with expanded explanations
  expandedExplanations: Set<string>;
  
  // Filter state for job matches
  filterState: MatchingFilters;
  
  // Current page for pagination
  currentPage: number;
  
  // Actions
  toggleExplanation: (jobId: string) => void;
  setFilterState: (filters: MatchingFilters) => void;
  resetFilters: () => void;
  setCurrentPage: (page: number) => void;
  isExplanationExpanded: (jobId: string) => boolean;
}

const initialFilterState: MatchingFilters = {
  location: undefined,
  work_setup: undefined,
  employment_type: undefined,
  salary_min: undefined,
  salary_max: undefined,
};

export const useMatchingStore = create<MatchingState>((set, get) => ({
  expandedExplanations: new Set<string>(),
  filterState: initialFilterState,
  currentPage: 1,
  
  toggleExplanation: (jobId: string) =>
    set((state) => {
      const newExpanded = new Set(state.expandedExplanations);
      if (newExpanded.has(jobId)) {
        newExpanded.delete(jobId);
      } else {
        newExpanded.add(jobId);
      }
      return { expandedExplanations: newExpanded };
    }),
  
  setFilterState: (filters: MatchingFilters) =>
    set({ filterState: filters, currentPage: 1 }), // Reset to page 1 on filter change
  
  resetFilters: () =>
    set({ filterState: initialFilterState, currentPage: 1 }),
  
  setCurrentPage: (page: number) =>
    set({ currentPage: page }),
  
  isExplanationExpanded: (jobId: string) =>
    get().expandedExplanations.has(jobId),
}));
