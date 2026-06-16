import type { PropsWithChildren } from "react";
import { createContext, useContext, useEffect, useMemo, useState } from "react";

import type { Session } from "@supabase/supabase-js";

import { supabase } from "@/lib/supabase";
import { useAppStore } from "@/store/app-store";

interface AuthContextValue {
  session: Session | null;
  isLoading: boolean;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: PropsWithChildren) {
  const setAuthSession = useAppStore((state) => state.setAuthSession);
  const [session, setSession] = useState<Session | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let active = true;

    supabase.auth
      .getSession()
      .then(({ data }) => {
        if (!active) return;
        setSession(data.session);
        setAuthSession({
          accessToken: data.session?.access_token ?? null,
          authUserId: data.session?.user.id ?? null,
        });
        setIsLoading(false);
      })
      .catch(() => {
        if (!active) return;
        setSession(null);
        setAuthSession({ accessToken: null, authUserId: null });
        setIsLoading(false);
      });

    const { data: subscription } = supabase.auth.onAuthStateChange((_event, nextSession) => {
      setSession(nextSession);
      setAuthSession({
        accessToken: nextSession?.access_token ?? null,
        authUserId: nextSession?.user.id ?? null,
      });
    });

    return () => {
      active = false;
      subscription.subscription.unsubscribe();
    };
  }, [setAuthSession]);

  const value = useMemo<AuthContextValue>(() => ({ session, isLoading }), [isLoading, session]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const value = useContext(AuthContext);
  if (!value) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return value;
}

