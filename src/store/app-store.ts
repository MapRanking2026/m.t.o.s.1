import { create } from "zustand";

import type { DemoIdentity } from "@/types/mtos";

export const demoIdentities: DemoIdentity[] = [
  {
    id: "user_1",
    fullName: "Ariana Cole",
    role: "admin",
    tenantUserId: import.meta.env.VITE_DEMO_TENANT_USER_ID_ADMIN ?? null,
  },
  {
    id: "user_2",
    fullName: "Mila Grant",
    role: "account_manager",
    tenantUserId: import.meta.env.VITE_DEMO_TENANT_USER_ID_AM1 ?? null,
  },
  {
    id: "user_3",
    fullName: "Leo Parker",
    role: "account_manager",
    tenantUserId: import.meta.env.VITE_DEMO_TENANT_USER_ID_AM2 ?? null,
  },
];

interface AppState {
  activeClientId: string | null;
  actingIdentity: DemoIdentity;
  accessToken: string | null;
  authUserId: string | null;
  setActiveClientId: (clientId: string | null) => void;
  setActingIdentity: (identityId: string) => void;
  setAuthSession: (payload: { accessToken: string | null; authUserId: string | null }) => void;
}

export const useAppStore = create<AppState>((set) => ({
  activeClientId: null,
  actingIdentity: demoIdentities[0],
  accessToken: null,
  authUserId: null,
  setActiveClientId: (clientId) => set({ activeClientId: clientId }),
  setActingIdentity: (identityId) =>
    set((state) => ({
      actingIdentity:
        demoIdentities.find((identity) => identity.id === identityId) ?? state.actingIdentity,
    })),
  setAuthSession: ({ accessToken, authUserId }) => set({ accessToken, authUserId }),
}));
