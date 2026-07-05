import { QueryProvider } from '@/shared/providers';
import { AuthProvider } from '@/features/auth';
import { AppRouter } from '@/routes/AppRouter';
import { ErrorBoundary } from '@/shared/components/feedback/ErrorBoundary';

function App() {
  return (
    <ErrorBoundary>
      <QueryProvider>
        <AuthProvider>
          <AppRouter />
        </AuthProvider>
      </QueryProvider>
    </ErrorBoundary>
  );
}

export default App;
