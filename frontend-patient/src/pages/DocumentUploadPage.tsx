import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, ArrowRight, Upload, FileText, CheckCircle, AlertTriangle, Loader2, RefreshCw } from 'lucide-react';
import { Button, Card, KioskHeader, LoadingState, ErrorState, InfoBanner, Badge } from '../components/ui';
import { ocrApi } from '../services/api';
import type { ClinicalDocument } from '../types';

export default function DocumentUploadPage() {
  const navigate = useNavigate();
  const [docs, setDocs] = useState<ClinicalDocument[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);

  const sessionId = JSON.parse(sessionStorage.getItem('medikiosk_session') || '{}').session_id || 'demo-session-001';

  const loadDocs = async () => {
    setLoading(true);
    try {
      const data = await ocrApi.list(sessionId);
      setDocs(data.documents);
      setTotal(data.total);
      setError(null);
    } catch (e) {
      setError('Failed to load documents');
    }
    setLoading(false);
  };

  useEffect(() => { loadDocs(); }, []);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files?.[0]) setFile(e.target.files[0]);
  };

  const handleUpload = async () => {
    if (!file) return;
    setUploading(true);
    try {
      await ocrApi.upload(sessionId, file);
      setFile(null);
      await loadDocs();
    } catch {
      // ignore for demo
    }
    setUploading(false);
  };

  const handleRefresh = () => loadDocs();

  if (loading) return <LoadingState title="Loading documents…" />;
  if (error) return <ErrorState title={error} onRetry={loadDocs} />;

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      <KioskHeader title="Document Upload" subtitle="Upload prescriptions, lab reports, or discharge summaries" icon={<Upload className="h-6 w-6 text-white" />} />
      <div className="flex-1 px-4 md:px-8 py-8 max-w-3xl mx-auto w-full">
        <Card className="mb-6">
          <h3 className="text-lg font-semibold text-slate-900 mb-2">Upload a new document</h3>
          <div className="flex items-center gap-3">
            <input type="file" accept={'.pdf,.png,.jpg,.jpeg'} onChange={handleFileChange} className="border border-slate-300 rounded-lg p-2" />
            <Button onClick={handleUpload} disabled={!file || uploading} variant="primary" size="md">
              {uploading ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : <Upload className="h-4 w-4 mr-1" />} {uploading ? 'Uploading…' : 'Upload'}
            </Button>
            <Button onClick={handleRefresh} variant="ghost" size="sm" title="Refresh list"><RefreshCw className="h-4 w-4" /></Button>
          </div>
        </Card>

        <Card>
          <h3 className="text-lg font-semibold text-slate-900 mb-3">Your Documents ({total})</h3>
          {docs.length === 0 ? (
            <p className="text-slate-500">No documents uploaded yet.</p>
          ) : (
            <ul className="space-y-4">
              {docs.map(doc => (
                <li key={doc.document_id} className="flex items-start gap-4 p-3 border border-slate-200 rounded-lg bg-white">
                  <div className="shrink-0">
                    <FileText className="h-6 w-6 text-slate-600" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="font-medium text-slate-800 truncate">{doc.original_filename}</p>
                    <p className="text-sm text-slate-500">Status: <Badge variant={doc.processing_status === 'completed' ? 'success' : doc.processing_status === 'processing' ? 'info' : 'danger'}>{doc.processing_status}</Badge></p>
                    {doc.warnings?.length && (
                      <InfoBanner kind="warning" title="Processing warnings" detail={doc.warnings.join(', ')} />
                    )}
                    {doc.processing_status === 'completed' && doc.requires_verification && (
                      <Button variant="secondary" size="sm" onClick={() => navigate(`/ocr/verify/${doc.document_id}`)} className="mt-2">Verify</Button>
                    )}
                  </div>
                </li>
              ))}
            </ul>
          )}
        </Card>

        <div className="mt-6 flex justify-between">
          <Button variant="ghost" onClick={() => navigate('/conversation')}><ArrowLeft className="h-4 w-4" /> Back to History</Button>
          <Button variant="primary" onClick={() => navigate('/queue')}>View Queue <ArrowRight className="h-4 w-4" /></Button>
        </div>
      </div>
    </div>
  );
}
