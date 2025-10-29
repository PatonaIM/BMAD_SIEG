import { Box, Container, Paper } from '@mui/material';
import { RegisterForm } from '../features/auth/components/RegisterForm/RegisterForm';

const RegisterPage = () => {
  return (
    <Container maxWidth="sm">
      <Box
        sx={{
          minHeight: '100vh',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
        <Paper
          elevation={3}
          sx={{
            p: 4,
            width: '100%',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
          }}
        >
          <RegisterForm />
        </Paper>
      </Box>
    </Container>
  );
};

export default RegisterPage;
