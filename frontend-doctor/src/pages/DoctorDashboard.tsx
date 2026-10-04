import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Users, Search, AlertCircle, Clock, ChevronRight, LogOut, Filter } from 'lucide-react';
import { Button, Card, KioskHeader, Badge, ProgressBar, Spinner } from '../components/ui';
import { doctorApi } from '../services/api';
import type { DoctorCase, ClinicalCase } from '../types';
import { useDoctorAuth } from '../services/auth';

export default function DoctorDashboard() {
  const navigate = useNavigate();
  const { token, logout } = useDoctorAuth();
  const [cases, setCases] = useState<DoctorCase[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [filterStream, setFilterStream] = useState<string>('all');

  useEffect(() => {
    if (!token) {
      navigate('/login');
      return;
    }
    loadCases();
  }, [token, navigate]);

  const loadCases = async () => {
    setLoading(true);
    try {
      const data = await doctorApi.cases();
      setCases(data.cases);
    } catch (e) {
      console.error('Failed to load cases', e);
    } finally {
      setLoading(false);
    }
  };

  const filtered = cases.filter(c => {
    const matchesSearch = c.patient_name.toLowerCase().includes(search.toLowerCase()) ||
                          c.department.toLowerCase().includes(search.toLowerCase());
    const matchesStream = filterStream === 'all' || c.mode === filterStream;
    return matchesSearch && matchesStream;
  });

  if (loading) return <div className="min-h-screen bg-slate-50 flex items-center justify-center"><Spinner size="lg" /></div>;

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      <KioskHeader
        title="Practitioner Dashboard"
        subtitle="Real-time patient intake queue"
        icon={<Users className="h-6 w-6 text-white" />}
        action={<Button variant="ghost" onClick={logout} className="text-slate-600 hover:text-red-600"><LogOut className="h-4 w-4 mr-2" /> Logout</Button>}
      />

      <div className="flex-1 px-4 md:px-8 py-8 max-w-6xl mx-auto w-full">
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 mb-8">
          <Card className="border-l-4 border-l-brand-600">
            <div className="text-sm font-medium text-slate-500">Total Pending</div>
            <div className="text-3xl font-bold text-slate-900">{cases.length}</div>
          </Card>
          <Card className="border-l-4 border-l-red-500">
            <div className="text-sm font-medium text-slate-500">High Priority / Red Flags</div>
            <div className="text-3xl font-bold text-red-600">{cases.filter(c => c.has_red_flags || c.priority === 'high').length}</div>
          </Card>
          <Card className="border-l-4 border-l-emerald-500">
            <div className="text-sm font-medium text-slate-500">Ready for Review</div>
            <div className="text-3xl font-bold text-emerald-600">{cases.filter(c => c.status === 'submitted').length}</div>
          </Card>
        </div>

        <div className="flex flex-col md:flex-row gap-4 mb-6 justify-between items-center">
          <div className="relative w-full md:w-96">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
            <input
              type="text"
              placeholder="Search patient or department..."
              className="w-full pl-10 pr-4 py-2 rounded-xl border-2 border-slate-200 focus:border-brand-500 outline-none transition-all"
              value={search}
              onChange={e => setSearch(e.target.value)}
            />
          </div>
          <div className="flex gap-2 items-center w-full md:w-auto overflow-x-auto pb-2 md:pb-0">
            <Filter className="h-4 w-4 text-slate-400 shrink-0" />
            <Button
              variant={filterStream === 'all' ? 'primary' : 'secondary'}
              size="sm"
              onClick={() => setFilterStream('all')}
            >All</Button>
            <Button
              variant={filterStream === 'allopathy' ? 'primary' : 'secondary'}
              size="sm"
              onClick={() => setFilterStream('allopathy')}
            >Allopathy</Button>
            <Button
              variant={filterStream === 'ayush' ? 'primary' : 'secondary'}
              size="sm"
              onClick={() => setFilterStream('ayush')}
            >AYUSH</Button>
          </div>
        </div>

        <div className="grid grid-cols-1 gap-4">
          {filtered.map(c => (
            <Card key={c.session_id} className={`hover:shadow-md transition-all cursor-pointer border-l-4 ${c.has_red_flags ? 'border-l-red-500 bg-red-50/30' : 'border-l-slate-200'}`} onClick={() => navigate(`/case/${c.session_id}`)}>
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div className="flex items-center gap-4">
                  <div className={`p-3 rounded-2xl ${c.has_red_flags ? 'bg-red-100 text-red-600' : 'bg-slate-100 text-slate-600'}`}>
                    {c.has_red_flags ? <AlertCircle className="h-6 w-6" /> : <UserIcon className="h-6 w-6" />}
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <h4 className="text-lg font-bold text-slate-900">{c.patient_name}</h4>
                      {c.has_red_flags && <Badge variant="danger">Emergency</Badge>}
                      <Badge variant={c.priority === 'high' ? 'danger' : 'neutral'}>{c.priority.toUpperCase()}</Badge>
                    </div>
                    <p className="text-sm text-slate-500">{c.department} • {c.mode.toUpperCase()} • Position: {c.queue_position}</p>
                  </div>
                </div>
                <div className="flex items-center gap-6">
                  <div className="text-right hidden md:block">
                    <div className="text-xs font-bold text-slate-400 uppercase">Wait Time</div>
                    <div className="text-sm font-semibold text-slate-700">{c.wait_time_mins} mins</div>
                  </div>
                  <Button variant="primary" size="md" className="whitespace-nowrap">
                    Review Case <ChevronRight className="h-4 w-4 ml-1" />
                  </Button>
                </div>
              </div>
            </Card>
          ))}
          {filtered.length === 0 && (
            <div className="py-20 text-center text-slate-500">No patients found matching the criteria.</div>
          )}
        </div>
      </div>
    </div>
  );
}

function UserIcon(props: any) {
  return <svg {...props} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>;
}
