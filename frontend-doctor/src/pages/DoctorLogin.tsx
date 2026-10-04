import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Lock, User, LogIn } from 'lucide-react';
import { Button, Card, Input } from '../components/ui';
import { useDoctorAuth } from '../services/auth';

export default function DoctorLogin() {
  const navigate = useNavigate();
  const { setToken, setSession } = useDoctorAuth();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      // Mock login for prototype
      await new Promise(r => setTimeout(r, 800));
      setToken('mock-doctor-jwt');
      setSession({ access_token: 'mock-doctor-jwt', token_type: 'bearer', user_id: 'doc-1', role: 'physician' });
      navigate('/');
    } catch {
      alert('Invalid credentials');
    }
    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-slate-100 flex items-center justify-center p-6">
      <div className="w-full max-w-md animate-fade-in">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-brand-600 text-white shadow-xl mb-4">
            <Lock className="h-8 w-8" />
          </div>
          <h1 className="text-3xl font-bold text-slate-900">Physician Portal</h1>
          <p className="text-slate-500 mt-2">Secure clinical access for MediKiosk</p>
        </div>

        <Card>
          <form onSubmit={handleLogin} className="space-y-6">
            <Input label="Username" value={username} onChange={(e: React.ChangeEvent<HTMLInputElement>) => setUsername(e.target.value)} placeholder="doctor_id" required />
            <Input label="Password" type="password" value={password} onChange={(e: React.ChangeEvent<HTMLInputElement>) => setPassword(e.target.value)} placeholder="••••••••" required />
            <Button type="submit" variant="primary" size="lg" className="w-full" disabled={loading}>
              {loading ? 'Authenticating...' : 'Login to Dashboard'}
              <LogIn className="h-4 w-4 ml-2" />
            </Button>
          </form>
        </Card>
      </div>
    </div>
  );
}
