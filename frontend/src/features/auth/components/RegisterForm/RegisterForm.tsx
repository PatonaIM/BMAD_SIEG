import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import {
  Box,
  Button,
  TextField,
  Typography,
  Alert,
  LinearProgress,
} from '@mui/material';
import { useRegister } from '../../hooks/useAuth';
import type { RegisterData } from '../../types/auth.types';

const registerSchema = z.object({
  email: z.string().email('Invalid email format'),
  full_name: z.string().min(2, 'Full name must be at least 2 characters'),
  password: z
    .string()
    .min(8, 'Password must be at least 8 characters')
    .regex(
      /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/,
      'Password must contain uppercase, lowercase, and number',
    ),
});

export const RegisterForm = () => {
  const {
    register,
    handleSubmit,
    formState: { errors },
    watch,
  } = useForm<RegisterData>({
    resolver: zodResolver(registerSchema),
  });

  const registerMutation = useRegister();
  const password = watch('password', '');

  const onSubmit = (data: RegisterData) => {
    registerMutation.mutate(data);
  };

  // Password strength indicator
  const getPasswordStrength = (pass: string) => {
    if (!pass) return { value: 0, label: '', color: 'error' };
    if (pass.length < 8) return { value: 25, label: 'Weak', color: 'error' };
    if (!/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/.test(pass)) {
      return { value: 50, label: 'Fair', color: 'warning' };
    }
    if (pass.length >= 12) {
      return { value: 100, label: 'Strong', color: 'success' };
    }
    return { value: 75, label: 'Good', color: 'info' };
  };

  const passwordStrength = getPasswordStrength(password);

  return (
    <Box
      component="form"
      onSubmit={handleSubmit(onSubmit)}
      sx={{ width: '100%', maxWidth: 400 }}
    >
      <Typography variant="h4" component="h1" gutterBottom>
        Create Account
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        Register to start your interview
      </Typography>

      {registerMutation.isError && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {registerMutation.error instanceof Error
            ? registerMutation.error.message
            : 'Registration failed. Please try again.'}
        </Alert>
      )}

      <TextField
        {...register('email')}
        label="Email"
        type="email"
        fullWidth
        margin="normal"
        error={!!errors.email}
        helperText={errors.email?.message}
        disabled={registerMutation.isPending}
      />

      <TextField
        {...register('full_name')}
        label="Full Name"
        fullWidth
        margin="normal"
        error={!!errors.full_name}
        helperText={errors.full_name?.message}
        disabled={registerMutation.isPending}
      />

      <TextField
        {...register('password')}
        label="Password"
        type="password"
        fullWidth
        margin="normal"
        error={!!errors.password}
        helperText={errors.password?.message}
        disabled={registerMutation.isPending}
      />

      {password && (
        <Box sx={{ mt: 1, mb: 2 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
            <Typography variant="caption" color="text.secondary">
              Password Strength
            </Typography>
            <Typography variant="caption" color={`${passwordStrength.color}.main`}>
              {passwordStrength.label}
            </Typography>
          </Box>
          <LinearProgress
            variant="determinate"
            value={passwordStrength.value}
            color={
              passwordStrength.color as 'error' | 'warning' | 'info' | 'success'
            }
          />
        </Box>
      )}

      <Button
        type="submit"
        variant="contained"
        fullWidth
        size="large"
        disabled={registerMutation.isPending}
        sx={{ mt: 2 }}
      >
        {registerMutation.isPending ? 'Creating Account...' : 'Create Account'}
      </Button>

      <Typography variant="body2" color="text.secondary" sx={{ mt: 2, textAlign: 'center' }}>
        Already have an account?{' '}
        <Typography
          component="a"
          href="/login"
          sx={{ color: 'primary.main', textDecoration: 'none', fontWeight: 500 }}
        >
          Sign In
        </Typography>
      </Typography>
    </Box>
  );
};
