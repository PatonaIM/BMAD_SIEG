import { useMutation } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { authService } from '../services/authService';
import { useAuthStore } from '../store/authStore';
import type { RegisterData, LoginData } from '../types/auth.types';

export const useRegister = () => {
  const navigate = useNavigate();
  const setAuth = useAuthStore((state) => state.setAuth);

  return useMutation({
    mutationFn: (data: RegisterData) => authService.registerCandidate(data),
    onSuccess: (response) => {
      const user = {
        id: response.candidate_id,
        email: response.email,
        full_name: '', // Will be populated from candidate profile if needed
      };
      setAuth(user, response.token);
      navigate('/interview/start');
    },
  });
};

export const useLogin = () => {
  const navigate = useNavigate();
  const setAuth = useAuthStore((state) => state.setAuth);

  return useMutation({
    mutationFn: (data: LoginData) => authService.loginCandidate(data),
    onSuccess: (response) => {
      const user = {
        id: response.candidate_id,
        email: response.email,
        full_name: '', // Will be populated from candidate profile if needed
      };
      setAuth(user, response.token);
      navigate('/interview/start');
    },
  });
};

export const useLogout = () => {
  const navigate = useNavigate();
  const clearAuth = useAuthStore((state) => state.clearAuth);

  return () => {
    clearAuth();
    navigate('/login');
  };
};
