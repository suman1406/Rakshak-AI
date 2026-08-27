import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { mockApi } from '../../services/mockApi';
import { Case } from '../../types';
import { SeverityBadge, ReviewStatusBadge } from '../../components/shared/RoleBadge';
import { History, Search, FileText, ChevronRight } from 'lucide-react';

export const FarmerHistoryPage: React.FC = () => {
  const [cases, setCases] = useState<Case[]>([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchHistory = async () => {
      const data = await mockApi.getCases({ search });
      setCases(data);
      setLoading(false);
    };
    fetchHistory();
  }, [search]);

  return (
    <div className="space-y-6 font-sans">
      <div className="bg-pure-surface border border-structural p-6 rounded-3xl shadow-2xs space-y-2">
        <div className="flex items-center gap-2">
          <span className="p-1.5 bg-field-ink text-lime-signal rounded-lg">
            <History size={18} />
          </span>
          <h1 className="text-2xl font-extrabold text-field-ink">Scan History</h1>
        </div>
        <p className="text-xs text-muted-leaf">Previous field video scans for Patil Farm</p>
      </div>

      <div className="bg-pure-surface border border-structural p-6 rounded-3xl shadow-xs space-y-4">
        <div className="relative">
          <Search size={16} className="absolute left-3.5 top-3 text-muted-leaf" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search scans by Case ID, crop, or disease..."
            className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-structural bg-field-canvas text-xs outline-none"
          />
        </div>

        {loading ? (
          <div className="p-8 text-center text-xs text-muted-leaf">Loading history...</div>
        ) : cases.length === 0 ? (
          <div className="p-8 text-center text-xs text-muted-leaf">No field scans found matching your search.</div>
        ) : (
          <div className="space-y-3">
            {cases.map((c) => (
              <div
                key={c.id}
                className="p-4 bg-field-canvas rounded-2xl border border-structural flex flex-wrap items-center justify-between gap-4 text-xs"
              >
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="font-mono font-bold text-field-ink">#{c.id}</span>
                    <span className="text-[10px] text-muted-leaf">{new Date(c.submittedAt).toLocaleDateString()}</span>
                  </div>
                  <p className="font-bold text-field-ink">{c.aiIndication} ({c.confidence}% Confidence)</p>
                  <div className="flex items-center gap-2">
                    <SeverityBadge severity={c.severity} />
                    <ReviewStatusBadge status={c.reviewStatus} />
                  </div>
                </div>

                <Link
                  to={`/farmer/report/${c.id}`}
                  className="px-4 py-2 bg-pure-surface border border-structural font-bold text-xs rounded-xl hover:bg-gray-200 transition flex items-center gap-1.5"
                >
                  <FileText size={14} /> View Report
                </Link>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
