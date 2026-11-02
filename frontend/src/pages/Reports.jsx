import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { sessionService } from '../services/api';
import {
  FileText,
  Download,
  FileSpreadsheet,
  FileCode,
  Calendar,
  Clock,
  User,
  CheckCircle2,
  AlertCircle
} from 'lucide-react';

export default function Reports() {
  const [searchParams] = useSearchParams();
  const sessionIdParam = searchParams.get('sessionId');

  const [sessions, setSessions] = useState([]);
  const [selectedSessionId, setSelectedSessionId] = useState(sessionIdParam || '');
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchSessions();
  }, []);

  useEffect(() => {
    if (selectedSessionId) {
      fetchReport(selectedSessionId);
    }
  }, [selectedSessionId]);

  const fetchSessions = async () => {
    try {
      const res = await sessionService.getAll();
      setSessions(res.data);
      if (!selectedSessionId && res.data.length > 0) {
        setSelectedSessionId(res.data[0].id);
      }
    } catch (err) {
      console.error(err);
    }
  };

  const fetchReport = async (sessionId) => {
    try {
      setLoading(true);
      const res = await sessionService.getReport(sessionId);
      setReport(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadCsv = () => {
    if (!selectedSessionId) return;
    window.open(sessionService.getExportCsvUrl(selectedSessionId), '_blank');
  };

  const handleDownloadJson = () => {
    if (!selectedSessionId) return;
    window.open(sessionService.getExportJsonUrl(selectedSessionId), '_blank');
  };

  return (
    <div className="space-y-6 max-w-5xl">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-base font-semibold text-slate-900">Session Intelligence Reports</h2>
          <p className="text-xs text-slate-500">
            Export comprehensive session attendance, multimodal timelines, and advisory summaries.
          </p>
        </div>

        {/* Session Selector & Downloads */}
        <div className="flex items-center gap-2">
          <select
            value={selectedSessionId}
            onChange={(e) => setSelectedSessionId(e.target.value)}
            className="px-3 py-1.5 bg-white border border-slate-200 rounded-lg text-xs font-medium focus:ring-1 focus:ring-indigo-500"
          >
            {sessions.map((s) => (
              <option key={s.id} value={s.id}>
                {s.title} ({s.course_name})
              </option>
            ))}
          </select>

          <button
            onClick={handleDownloadCsv}
            disabled={!report}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-white hover:bg-slate-50 border border-slate-200 text-slate-700 text-xs font-medium rounded-lg disabled:opacity-50"
          >
            <FileSpreadsheet className="h-3.5 w-3.5 text-emerald-600" />
            CSV
          </button>

          <button
            onClick={handleDownloadJson}
            disabled={!report}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-medium rounded-lg disabled:opacity-50"
          >
            <FileCode className="h-3.5 w-3.5" />
            JSON
          </button>
        </div>
      </div>

      {loading ? (
        <div className="py-20 text-center text-slate-400 text-xs">Loading report data...</div>
      ) : !report ? (
        <div className="py-20 text-center bg-white border border-slate-200 rounded-xl text-slate-400 text-xs">
          Select an analyzed session to generate report.
        </div>
      ) : (
        <div className="space-y-6">
          {/* Summary Header Card */}
          <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-xs space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between border-b border-slate-100 pb-4">
              <div>
                <span className="text-[10px] font-semibold text-indigo-700 bg-indigo-50 px-2 py-0.5 rounded border border-indigo-100">
                  {report.session.course_name}
                </span>
                <h3 className="text-base font-bold text-slate-900 mt-1">{report.session.title}</h3>
                <div className="flex items-center gap-3 text-xs text-slate-400 mt-1">
                  <span className="flex items-center gap-1">
                    <User className="h-3.5 w-3.5" /> {report.session.instructor_name}
                  </span>
                  <span>•</span>
                  <span className="flex items-center gap-1">
                    <Clock className="h-3.5 w-3.5" /> {Math.round(report.session.media_duration_sec || 0)}s duration
                  </span>
                </div>
              </div>
              <div className="mt-3 sm:mt-0 text-right">
                <span className="text-2xl font-black text-indigo-600">{report.summary.attendance_rate_pct}%</span>
                <span className="text-[10px] text-slate-400 block font-medium uppercase tracking-wider">Attendance Rate</span>
              </div>
            </div>

            {/* Quick Summary Metrics */}
            <div className="grid grid-cols-3 gap-4 pt-1 text-center">
              <div className="p-3 bg-slate-50 rounded-lg">
                <span className="text-xs text-slate-500 block">Observed Tracks</span>
                <span className="text-lg font-bold text-slate-800">{report.summary.total_observed_tracks}</span>
              </div>
              <div className="p-3 bg-slate-50 rounded-lg">
                <span className="text-xs text-slate-500 block">Verified Present</span>
                <span className="text-lg font-bold text-emerald-600">{report.summary.present_count}</span>
              </div>
              <div className="p-3 bg-slate-50 rounded-lg">
                <span className="text-xs text-slate-500 block">Teaching Suggestions</span>
                <span className="text-lg font-bold text-indigo-600">{report.summary.recommendations_count}</span>
              </div>
            </div>
          </div>

          {/* Attendance Table */}
          <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs">
            <h4 className="text-xs font-semibold text-slate-900 uppercase tracking-wider mb-3">
              Attendance Roster & Observation Evidence
            </h4>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-50 text-slate-500 border-b border-slate-100 font-semibold">
                  <tr>
                    <th className="py-2.5 px-3">Track ID</th>
                    <th className="py-2.5 px-3">Participant</th>
                    <th className="py-2.5 px-3">Coverage %</th>
                    <th className="py-2.5 px-3">Duration</th>
                    <th className="py-2.5 px-3">Status</th>
                    <th className="py-2.5 px-3">Quality</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {report.attendance.length === 0 ? (
                    <tr>
                      <td colSpan={6} className="py-6 text-center text-slate-400">No attendance data recorded</td>
                    </tr>
                  ) : (
                    report.attendance.map((a) => (
                      <tr key={a.id}>
                        <td className="py-2.5 px-3 font-mono font-medium text-slate-700">{a.anonymous_track_id}</td>
                        <td className="py-2.5 px-3 font-medium text-slate-800">{a.participant_name}</td>
                        <td className="py-2.5 px-3">{a.observed_pct}%</td>
                        <td className="py-2.5 px-3">{Math.round(a.total_observed_sec)}s</td>
                        <td className="py-2.5 px-3 font-semibold text-slate-700">{a.status}</td>
                        <td className="py-2.5 px-3 text-slate-500 text-[11px]">{a.evidence_quality}</td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
