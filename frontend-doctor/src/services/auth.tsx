import { createContext, useContext, useState, useCallback, useEffect, ReactNode } from 'react';
import { doctorApi } from './api';
import type { PhysicianSession, DoctorCase, ClinicalCase } from '../types';

interface DoctorAuthCtx {
  token: string | null;
  session: PhysicianSession | null;
  setToken: (t: string | null) => void;
  setSession: (s: PhysicianSession | null) => void;
  logout: () => void;
}

const DoctorAuthContext = createContext<DoctorAuthCtx | null>(null);

export const DoctorAuthProvider = ({ children }: { children: ReactNode }) => {
  const [token, setToken] = useState<string | null>(sessionStorage.getItem('medikiosk_doctor_token'));
  const [session, setSession] = useState<PhysicianSession | null>(null);

  const logout = useCallback(() => {
    sessionStorage.removeItem('medikiosk_doctor_token');
    setToken(null);
    setSession(null);
  }, []);

  useEffect(() => {
    if (token) sessionStorage.setItem('medikiosk_doctor_token', token);
    else sessionStorage.removeItem('medikiosk_doctor_token');
  }, [token]);

  return (
    <DoctorAuthContext.Provider value={{ token, session, setToken, setSession, logout }}>
      {children}
    </DoctorAuthContext.Provider>
  );
};

export const useDoctorAuth = () => {
  const c = useContext(DoctorAuthContext);
  if (!c) throw new Error('useDoctorAuth outside provider');
  return c;
};
