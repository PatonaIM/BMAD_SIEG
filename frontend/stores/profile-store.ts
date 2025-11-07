/**
 * Profile UI State Store
 * 
 * Zustand store for managing profile-related UI state that doesn't need
 * to be persisted (selected skills, filters, form dirty state).
 * 
 * @example
 * ```tsx
 * const { selectedSkills, addSkill, removeSkill } = useProfileStore();
 * 
 * <Badge onClick={() => removeSkill(skill)}>
 *   {skill} <X />
 * </Badge>
 * ```
 */

import { create } from 'zustand';

interface ProfileState {
  // Selected skills during editing (before save)
  selectedSkills: string[];
  
  // Search query for skill autocomplete
  skillsSearchQuery: string;
  
  // Filter state for skills view
  skillsFilter: 'all' | 'manual' | 'resume';
  
  // Track if form has unsaved changes
  formDirty: boolean;
  
  // Actions
  addSkill: (skill: string) => void;
  removeSkill: (skill: string) => void;
  setSkillsSearchQuery: (query: string) => void;
  setSkillsFilter: (filter: 'all' | 'manual' | 'resume') => void;
  setFormDirty: (dirty: boolean) => void;
  resetForm: () => void;
  initializeSkills: (skills: string[]) => void;
}

export const useProfileStore = create<ProfileState>((set) => ({
  selectedSkills: [],
  skillsSearchQuery: '',
  skillsFilter: 'all',
  formDirty: false,
  
  addSkill: (skill: string) => 
    set((state) => ({
      selectedSkills: [...state.selectedSkills, skill],
      formDirty: true,
    })),
  
  removeSkill: (skill: string) =>
    set((state) => ({
      selectedSkills: state.selectedSkills.filter((s) => s !== skill),
      formDirty: true,
    })),
  
  setSkillsSearchQuery: (query: string) =>
    set({ skillsSearchQuery: query }),
  
  setSkillsFilter: (filter: 'all' | 'manual' | 'resume') =>
    set({ skillsFilter: filter }),
  
  setFormDirty: (dirty: boolean) =>
    set({ formDirty: dirty }),
  
  resetForm: () =>
    set({
      selectedSkills: [],
      skillsSearchQuery: '',
      skillsFilter: 'all',
      formDirty: false,
    }),
  
  initializeSkills: (skills: string[]) =>
    set({
      selectedSkills: skills,
      formDirty: false,
    }),
}));
