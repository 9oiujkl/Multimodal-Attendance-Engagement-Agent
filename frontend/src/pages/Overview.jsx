import React, { useState, useEffect } from 'react';
import { dashboardService, sessionService } from '../services/api';
import {
  Users,
  Video,
  ClipboardCheck,
  TrendingUp,
  Lightbulb,
  ArrowRight,
  Clock,
  Sparkles,
  AlertCircle
} from 'lucide-react';
import { Link } from 'react-router-dom';
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer
} from 'recharts';

export default function Overview() {
  const [summary, setSummary] = useState(null);
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [sumRes, sessRes] = await Promise.all([
        dashboardService.getSummary(),
        sessionService.getAll({ limit: 5 })
      ]);
      setSummary(sumRes.data);
      setSessions(sessRes.data);
    } catch (err) {
      console.error(err);
      setError('Unable to connect to local backend. Ensure FastAPI server is running on port 8000.');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64 text-slate-400 text-sm">
        Loading intelligence dashboard...
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-4 bg-amber-50 border border-amber-200 text-amber-800 rounded-xl text-sm flex items-center gap-3">
        <AlertCircle className="h-5 w-5 shrink-0" />
        <span>{error}</span>
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-7xl">
      {/* Metrics Row */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="p-5 bg-white border border-slate-200 rounded-xl shadow-xs">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-500 uppercase tracking-wider">Registered Participants</span>
            <Users className="h-4 w-4 text-indigo-500" />
          </div>
          <div className="text-2xl font-bold text-slate-900 mt-2">{summary?.total_participants || 0}</div>
          <div className="text-[11px] text-slate-400 mt-1">Classroom directory count</div>
        </div>

        <div className="p-5 bg-white border border-slate-200 rounded-xl shadow-xs">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-500 uppercase tracking-wider">Total Sessions</span>
            <Video className="h-4 w-4 text-indigo-500" />
          </div>
          <div className="text-2xl font-bold text-slate-900 mt-2">{summary?.total_sessions || 0}</div>
          <div className="text-[11px] text-slate-400 mt-1">{summary?.recent_sessions_count || 0} in past 7 days</div>
        </div>

        <div className="p-5 bg-white border border-slate-200 rounded-xl shadow-xs">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-500 uppercase tracking-wider">Avg. Attendance Rate</span>
            <ClipboardCheck className="h-4 w-4 text-emerald-500" />
          </div>
          <div className="text-2xl font-bold text-slate-900 mt-2">{summary?.average_attendance_pct || 0}%</div>
          <div className="text-[11px] text-slate-400 mt-1">Sustained presence proxy</div>
        </div>

        <div className="p-5 bg-white border border-slate-200 rounded-xl shadow-xs">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-500 uppercase tracking-wider">Avg. Engagement Proxy</span>
            <TrendingUp className="h-4 w-4 text-indigo-600" />
          </div>
          <div className="text-2xl font-bold text-slate-900 mt-2">{summary?.average_engagement_proxy || 0} / 100</div>
          <div className="text-[11px] text-slate-400 mt-1">Observable movement & audio</div>
        </div>
      </div>

      {/* Main Grid: Recent Sessions & Recommendations */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Sessions List */}
        <div className="lg:col-span-2 bg-white border border-slate-200 rounded-xl p-5 shadow-xs">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-sm font-semibold text-slate-900">Recent Sessions</h2>
              <p className="text-xs text-slate-500">Classroom recordings and analysis status</p>
            </div>
            <Link to="/sessions" className="text-xs font-medium text-indigo-600 hover:text-indigo-800 flex items-center gap-1">
              View all <ArrowRight className="h-3.5 w-3.5" />
            </Link>
          </div>

          {sessions.length === 0 ? (
            <div className="py-12 text-center text-slate-400 text-xs">
              No sessions created yet. Click "Sessions" in the sidebar to create and upload media.
            </div>
          ) : (
            <div className="divide-y divide-slate-100">
              {sessions.map((s) => (
                <div key={s.id} className="py-3.5 flex items-center justify-between">
                  <div>
                    <h3 className="text-xs font-semibold text-slate-800">{s.title}</h3>
                    <div className="text-[11px] text-slate-400 flex items-center gap-2 mt-0.5">
                      <span>{s.course_name}</span>
                      <span>•</span>
                      <span>{s.instructor_name}</span>
                      <span>•</span>
                      <span className="flex items-center gap-1">
                        <Clock className="h-3 w-3" />
                        {Math.round(s.media_duration_sec || 0)}s duration
                      </span>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <span
                      className={`px-2 py-0.5 text-[10px] rounded-full font-medium ${
                        s.status === 'COMPLETED'
                          ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                          : s.status === 'PROCESSING'
                          ? 'bg-indigo-50 text-indigo-700 border border-indigo-200 animate-pulse'
                          : 'bg-slate-100 text-slate-600'
                      }`}
                    >
                      {s.status}
                    </span>
                    <Link
                      to={`/attendance?sessionId=${s.id}`}
                      className="px-2.5 py-1 text-xs font-medium text-slate-600 hover:text-indigo-600 bg-slate-50 hover:bg-indigo-50 border border-slate-200 rounded-md transition-colors"
                    >
                      Details
                    </Link>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* AI Teaching Suggestions Snippet */}
        <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs flex flex-col justify-between">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <Sparkles className="h-4 w-4 text-amber-500" />
              <h2 className="text-sm font-semibold text-slate-900">Teaching Suggestions</h2>
            </div>
            <p className="text-xs text-slate-500 mb-4">Advisory pedagogical pointers based on observed patterns</p>

            {(!summary?.latest_recommendations || summary.latest_recommendations.length === 0) ? (
              <div className="py-8 text-center text-slate-400 text-xs">
                Process a video session to generate contextual teaching suggestions.
              </div>
            ) : (
              <div className="space-y-3">
                {summary.latest_recommendations.slice(0, 3).map((r) => (
                  <div key={r.id} className="p-3 bg-slate-50 border border-slate-100 rounded-lg">
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-xs font-semibold text-slate-800">{r.title}</span>
                      <span className="text-[10px] font-medium text-amber-700 bg-amber-50 px-1.5 py-0.5 rounded border border-amber-200">
                        {r.severity}
                      </span>
                    </div>
                    <p className="text-[11px] text-slate-600 line-clamp-2">{r.suggested_action}</p>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="mt-4 pt-3 border-t border-slate-100">
            <Link
              to="/recommendations"
              className="text-xs font-medium text-indigo-600 hover:text-indigo-800 flex items-center justify-between"
            >
              <span>Explore all suggestions</span>
              <ArrowRight className="h-3.5 w-3.5" />
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
