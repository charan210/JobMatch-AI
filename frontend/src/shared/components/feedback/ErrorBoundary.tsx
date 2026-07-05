import { Component, type ReactNode } from "react";
import { ErrorState } from "./ErrorState";

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch() {
    // Intentionally omitted logging per constraints
  }

  public render() {
    if (this.state.hasError) {
      return (
        <div className="flex min-h-screen items-center justify-center bg-[hsl(var(--background))] p-4">
          <ErrorState 
            title="Application Error" 
            description={this.state.error?.message || "An unexpected rendering error occurred."} 
            onRetry={() => window.location.reload()} 
          />
        </div>
      );
    }

    return this.props.children;
  }
}
