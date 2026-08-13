import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import { checkAuthStatus, login as loginRequest } from "../api/client";

interface AuthContextValue {
  authenticated: boolean | null; // null = still checking
  login: (password: string) => Promise<boolean>;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [authenticated, setAuthenticated] = useState<boolean | null>(null);

  useEffect(() => {
    checkAuthStatus().then(setAuthenticated);
  }, []);

  const login = async (password: string) => {
    const ok = await loginRequest(password);
    if (ok) setAuthenticated(true);
    return ok;
  };

  return <AuthContext.Provider value={{ authenticated, login }}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within an AuthProvider");
  return ctx;
}
