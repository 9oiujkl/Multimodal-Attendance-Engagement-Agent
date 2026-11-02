import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { sessionService } from '../services/api';
import {
  TrendingUp,
  Activity,
  Mic,
  Eye,
  Sliders,
  AlertCircle
} from 'lucide-react';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';

export default function Engagement() {
  const [searchParams] = useSearchParams();
  const sessionIdParam = searchParams.get('sessionId');

  const [sessions, setSessions] = useState([]);
  const [selectedSessionId, setSelectedSessionId] = useState(sessionIdParam || '');
  const [metrics, setMetrics] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchSessions();
  }, []);

  useEffect(() => {
    if (selectedSessionId) {
      fetchEngagement(selectedSessionId);
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

  const fetchEngagement = async (sessionId) => {
    try {
      setLoading(true);
      const res = await sessionService.getEngagement(sessionId);
      setMetrics(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // Compute summary stats
  const validProxies = metrics.filter((m) => m.composite_engagement_proxy !== null);
  const avgProxy = validProxies.length > 0
    ? roundVal(validProxies.reduce((acc, m) => acc + m.composite_engagement_proxy, 0) / validProxies.length)
    : 0;

  const validMotion = metrics.filter((m) => m.visual_activity_index !== null);
  const avgMotion = validMotion.length > 0
    ? roundVal(validMotion.reduce((acc, m) => acc + m.visual_activity_index, 0) / validMotion.length)
    : 0;

  const validAudio = metrics.filter((m) => m.audio_activity_level !== null);
  const avgAudio = validAudio.length > 0
    ? roundVal(validAudio.reduce((acc, m) => acc + m.audio_activity_level, 0) / validAudio.length)
    : 0;

  function roundVal(v) {
    return Math.round(v * 10) / 10;
  }

  return (
    <div className="space-y-6 max-w-6xl">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-base font-semibold text-slate-900">Multimodal Engagement Analytics</h2>
          <p className="text-xs text-slate-500">
            Temporal fusion of observable visual movement, orientation stability, and audio interaction.
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

      {/* Observability Note Alert */}
      <div className="p-3.5 bg-indigo-50/60 border border-indigo-100 rounded-xl flex items-start gap-3 text-xs text-indigo-900">
        <AlertCircle className="h-4 w-4 text-indigo-600 shrink-0 mt-0.5" />
        <div className="leading-relaxed">
          <span className="font-semibold">Pedagogical Measurement Boundary:</span> Metrics represent observable behavioral indicators and estimated multimodal proxies. They do not claim to evaluate internal mental states, student comprehension, or emotion.
        </div>
      </div>

      {/* Aggregate Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="p-4 bg-white border border-slate-200 rounded-xl shadow-xs">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-500 uppercase tracking-wider">Composite Proxy</span>
            <TrendingUp className="h-4 w-4 text-indigo-600" />
          </div>
          <div className="text-2xl font-bold text-slate-900 mt-2">{avgProxy} / 100</div>
          <div className="text-[11px] text-slate-400 mt-1">Weighted fusion score</div>
        </div>

        <div className="p-4 bg-white border border-slate-200 rounded-xl shadow-xs">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-500 uppercase tracking-wider">Visual Movement Index</span>
            <Activity className="h-4 w-4 text-emerald-600" />
          </div>
          <div className="text-2xl font-bold text-slate-900 mt-2">{avgMotion} / 100</div>
          <div className="text-[11px] text-slate-400 mt-1">Optical flow & change ratio</div>
        </div>

        <div className="p-4 bg-white border border-slate-200 rounded-xl shadow-xs">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-500 uppercase tracking-wider">Audio Interaction Level</span>
            <Mic className="h-4 w-4 text-amber-600" />
          </div>
          <div className="text-2xl font-bold text-slate-900 mt-2">{avgAudio} / 100</div>
          <div className="text-[11px] text-slate-400 mt-1">RMS energy above silence threshold</div>
        </div>
      </div>

      {/* Main Charts */}
      <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs space-y-6">
        <div>
          <h3 className="text-sm font-semibold text-slate-900">Composite Engagement Proxy Over Time</h3>
          <p className="text-xs text-slate-500">Timeline of fused behavioral proxies across session duration</p>
        </div>

        {metrics.length === 0 ? (
          <div className="py-20 text-center text-slate-400 text-xs">
            No temporal metrics available for this session. Process a video or audio file to view trends.
          </div>
        ) : (
          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={metrics}>
                <defs>
                  <linearGradient id="colorProxy" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#4f46e5" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#4f46e5" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis
                  dataKey="timestamp_sec"
                  tickFormatter={(val) => `${Math.round(val)}s`}
                  tick={{ fontSize: 11, fill: '#64748b' }}
                />
                <YAxis domain={[0, 100]} tick={{ fontSize: 11, fill: '#64748b' }} />
                <Tooltip
                  formatter={(value) => [`${value} / 100`, 'Engagement Proxy']}
                  labelFormatter={(val) => `Time: ${Math.round(val)}s`}
                />
                <Area
                  type="monotone"
                  dataKey="composite_engagement_proxy"
                  stroke="#4f46e5"
                  strokeWidth={2}
                  fillOpacity={1}
                  fill="url(#colorProxy)"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>

      {/* Modality Breakdown Chart */}
      {metrics.length > 0 && (
        <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs space-y-4">
          <div>
            <h3 className="text-sm font-semibold text-slate-900">Modality Breakdown Comparison</h3>
            <p className="text-xs text-slate-500">Separated visual activity, orientation proxy, and audio levels</p>
          </div>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={metrics}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis
                  dataKey="timestamp_sec"
                  tickFormatter={(val) => `${Math.round(val)}s`}
                  tick={{ fontSize: 11, fill: '#64748b' }}
                />
                <YAxis domain={[0, 100]} tick={{ fontSize: 11, fill: '#64748b' }} />
                <Tooltip labelFormatter={(val) => `Time: ${Math.round(val)}s`} />
                <Legend wrapperStyle={{ fontSize: 11 }} />
                <Line
                  type="monotone"
                  dataKey="visual_activity_index"
                  name="Visual Movement"
                  stroke="#10b981"
                  strokeWidth={1.5}
                  dot={false}
                />
                <Line
                  type="monotone"
                  dataKey="head_pose_orientation_score"
                  name="Orientation Proxy"
                  stroke="#3b82f6"
                  strokeWidth={1.5}
                  dot={false}
                />
                <Line
                  type="monotone"
                  dataKey="audio_activity_level"
                  name="Audio Energy"
                  stroke="#f59e0b"
                  strokeWidth={1.5}
                  dot={false}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}
    </div>
  );
}
