import { createContext, useContext, useState, useCallback, useEffect, ReactNode } from 'react';
import type { PatientIdentity, PatientSession, ClinicalCase } from '../types';
import { sessionApi } from './api';

interface AuthCtx {
  token: string | null;
  session: PatientSession | null;
  identity: PatientIdentity | null;
  caseData: ClinicalCase | null;
  setToken: (t: string | null) => void;
  setSession: (s: PatientSession | null) => void;
  setIdentity: (i: PatientIdentity | null) => void;
  setCase: (c: ClinicalCase | null) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthCtx | null>(null);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [token, setToken] = useState<string | null>(sessionStorage.getItem('medikiosk_token'));
  const [session, setSession] = useState<PatientSession | null>(null);
  const [identity, setIdentity] = useState<PatientIdentity | null>(null);
  const [caseData, setCase] = useState<ClinicalCase | null>(null);

  const logout = useCallback(() => { sessionStorage.removeItem('medikiosk_token'); setToken(null); setSession(null); setIdentity(null); setCase(null); }, []);

  useEffect(() => { if (token) sessionStorage.setItem('medikiosk_token', token); else sessionStorage.removeItem('medikiosk_token'); }, [token]);

  return (
    <AuthContext.Provider value={{ token, session, identity, caseData, setToken, setSession, setIdentity, setCase, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => { const c = useContext(AuthContext); if (!c) throw new Error('useAuth outside provider'); return c; };
