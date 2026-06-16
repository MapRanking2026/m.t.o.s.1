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
  setActiveClientId: (clientId: string | null) => void;
  setActingIdentity: (identityId: string) => void;
}

export const useAppStore = create<AppState>((set) => ({
  activeClientId: null,
  actingIdentity: demoIdentities[0],
  setActiveClientId: (clientId) => set({ activeClientId: clientId }),
  setActingIdentity: (identityId) =>
    set((state) => ({
      actingIdentity:
        demoIdentities.find((identity) => identity.id === identityId) ?? state.actingIdentity,
    })),
}));
