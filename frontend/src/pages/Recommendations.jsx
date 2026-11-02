import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { sessionService } from '../services/api';
import {
  Lightbulb,
  AlertTriangle,
  Info,
  CheckCircle,
  HelpCircle,
  Sparkles,
  ShieldAlert
} from 'lucide-react';

export default function Recommendations() {
  const [searchParams] = useSearchParams();
  const sessionIdParam = searchParams.get('sessionId');

  const [sessions, setSessions] = useState([]);
  const [selectedSessionId, setSelectedSessionId] = useState(sessionIdParam || '');
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchSessions();
  }, []);

  useEffect(() => {
    if (selectedSessionId) {
      fetchRecommendations(selectedSessionId);
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

  const fetchRecommendations = async (sessionId) => {
    try {
      setLoading(true);
      const res = await sessionService.getRecommendations(sessionId);
      setRecommendations(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const getSeverityBadge = (severity) => {
    switch (severity) {
      case 'HIGH':
        return (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-semibold bg-rose-50 text-rose-700 border border-rose-200">
            <AlertTriangle className="h-3 w-3" /> High Priority
          </span>
        );
      case 'MEDIUM':
        return (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-semibold bg-amber-50 text-amber-700 border border-amber-200">
            <AlertTriangle className="h-3 w-3" /> Medium Priority
          </span>
        );
      case 'LOW':
        return (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-semibold bg-blue-50 text-blue-700 border border-blue-200">
            <Info className="h-3 w-3" /> Low Priority
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
            <CheckCircle className="h-3 w-3" /> Positive Note
          </span>
        );
    }
  };

  return (
    <div className="space-y-6 max-w-5xl">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-base font-semibold text-slate-900">AI Teaching Suggestions</h2>
          <p className="text-xs text-slate-500">
            Local rule-based pedagogical advisory system derived strictly from empirical temporal metrics.
          </p>
        </div>

        {/* Session Selector */}
        <div className="flex items-center gap-2">
          <label className="text-xs font-medium text-slate-600">Select Session:</label>
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
        </div>
      </div>

      {/* Advisory Principles Banner */}
      <div className="p-4 bg-slate-900 text-white rounded-xl shadow-xs space-y-1.5">
        <div className="flex items-center gap-2 text-indigo-300 font-semibold text-xs">
          <Sparkles className="h-4 w-4" />
          <span>Strict Ethical & Advisory Guidelines</span>
        </div>
        <p className="text-xs text-slate-300 leading-relaxed">
          Suggestions are designed to assist instructors with pacing and classroom engagement techniques. Recommendations must never be used to grade, punish, or penalize students.
        </p>
      </div>

      {/* Recommendations Cards */}
      <div className="space-y-4">
        {loading ? (
          <div className="py-16 text-center text-slate-400 text-xs">
            Loading recommendations...
          </div>
        ) : recommendations.length === 0 ? (
          <div className="py-16 text-center bg-white border border-slate-200 rounded-xl text-slate-400 text-xs">
            No teaching suggestions generated for this session yet.
          </div>
        ) : (
          recommendations.map((rec) => (
            <div
              key={rec.id}
              className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs space-y-3"
            >
              <div className="flex items-start justify-between gap-4">
                <div>
                  <h3 className="text-sm font-semibold text-slate-900">{rec.title}</h3>
                  <div className="flex items-center gap-2 text-[11px] text-slate-400 mt-0.5">
                    <span>Metric: <strong className="text-slate-600 font-medium">{rec.supporting_metric}</strong></span>
                    {rec.timestamp_interval && (
                      <>
                        <span>•</span>
                        <span>Interval: {rec.timestamp_interval}</span>
                      </>
                    )}
                  </div>
                </div>
                {getSeverityBadge(rec.severity)}
              </div>

              <p className="text-xs text-slate-600 leading-relaxed">
                {rec.explanation}
              </p>

              {/* Action Box */}
              <div className="p-3 bg-indigo-50/50 border border-indigo-100 rounded-lg text-xs">
                <span className="font-semibold text-indigo-900 block mb-0.5">Suggested Action:</span>
                <span className="text-indigo-800">{rec.suggested_action}</span>
              </div>

              {/* Data Quality Caveat */}
              <div className="flex items-start gap-2 text-[11px] text-slate-400 pt-1">
                <ShieldAlert className="h-3.5 w-3.5 text-slate-400 shrink-0 mt-0.5" />
                <span><em>Caveat:</em> {rec.caveat}</span>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
