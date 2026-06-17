import { create } from "zustand";

interface AppState {
  activeClientId: string | null;
  accessToken: string | null;
  authUserId: string | null;
  setActiveClientId: (clientId: string | null) => void;
  setAuthSession: (payload: { accessToken: string | null; authUserId: string | null }) => void;
}

export const useAppStore = create<AppState>((set) => ({
  activeClientId: null,
  accessToken: null,
  authUserId: null,
  setActiveClientId: (clientId) => set({ activeClientId: clientId }),
  setAuthSession: ({ accessToken, authUserId }) => set({ accessToken, authUserId }),
}));
