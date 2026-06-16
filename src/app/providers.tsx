import { QueryClientProvider } from "@tanstack/react-query";
import type { PropsWithChildren } from "react";
import { Toaster } from "sonner";

import { AuthProvider } from "@/app/auth-provider";
import { queryClient } from "@/lib/query-client";

export function Providers({ children }: PropsWithChildren) {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>{children}</AuthProvider>
      <Toaster richColors position="top-right" />
    </QueryClientProvider>
  );
}
