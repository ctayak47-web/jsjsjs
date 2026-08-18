import { create } from "zustand";
import { User } from "@/types";

interface AuthState {
  user: User | null;
  uid: string | null;
  isLoading: boolean;
  error: string | null;
  setUser: (user: User | null) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  uid: null,
  isLoading: true,
  error: null,
  setUser: (user) => set({ user, uid: user?.uid || null }),
  setLoading: (loading) => set({ isLoading: loading }),
  setError: (error) => set({ error }),
  logout: () => set({ user: null, uid: null, error: null }),
}));
