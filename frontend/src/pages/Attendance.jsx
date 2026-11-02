import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { sessionService, participantService } from '../services/api';
import { ClipboardCheck, CheckCircle2, AlertTriangle, XCircle, HelpCircle, Edit3, Save, X } from 'lucide-react';

export default function Attendance() {
  const [searchParams] = useSearchParams();
  const sessionIdParam = searchParams.get('sessionId');

  const [sessions, setSessions] = useState([]);
  const [selectedSessionId, setSelectedSessionId] = useState(sessionIdParam || '');
  const [records, setRecords] = useState([]);
  const [participants, setParticipants] = useState([]);
  const [loading, setLoading] = useState(false);

  // Edit / Override state
  const [editingRecord, setEditingRecord] = useState(null);
  const [editStatus, setEditStatus] = useState('');
  const [editParticipantId, setEditParticipantId] = useState('');
  const [editNotes, setEditNotes] = useState('');

  useEffect(() => {
    fetchInitialData();
  }, []);

  useEffect(() => {
    if (selectedSessionId) {
      fetchAttendance(selectedSessionId);
    }
  }, [selectedSessionId]);

  const fetchInitialData = async () => {
    try {
      const [sessRes, partRes] = await Promise.all([
        sessionService.getAll(),
        participantService.getAll()
      ]);
      setSessions(sessRes.data);
      setParticipants(partRes.data);
      if (!selectedSessionId && sessRes.data.length > 0) {
        setSelectedSessionId(sessRes.data[0].id);
      }
    } catch (err) {
      console.error(err);
    }
  };

  const fetchAttendance = async (sessionId) => {
    try {
      setLoading(true);
      const res = await sessionService.getAttendance(sessionId);
      setRecords(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleStartEdit = (rec) => {
    setEditingRecord(rec);
    setEditStatus(rec.status);
    setEditParticipantId(rec.participant_id || '');
    setEditNotes(rec.override_notes || '');
  };

  const handleSaveEdit = async () => {
    if (!editingRecord) return;
    try {
      await sessionService.updateAttendanceRecord(selectedSessionId, editingRecord.id, {
        status: editStatus,
        participant_id: editParticipantId ? parseInt(editParticipantId) : null,
        override_notes: editNotes
      });
      setEditingRecord(null);
      fetchAttendance(selectedSessionId);
    } catch (err) {
      alert('Failed to update attendance record.');
    }
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'PRESENT':
        return (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
            <CheckCircle2 className="h-3 w-3" /> Present
          </span>
        );
      case 'PARTIAL':
        return (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-semibold bg-amber-50 text-amber-700 border border-amber-200">
            <AlertTriangle className="h-3 w-3" /> Partial
          </span>
        );
      case 'ABSENT':
        return (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-semibold bg-rose-50 text-rose-700 border border-rose-200">
            <XCircle className="h-3 w-3" /> Absent
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-semibold bg-slate-100 text-slate-700 border border-slate-200">
            <HelpCircle className="h-3 w-3" /> Needs Review
          </span>
        );
    }
  };

  return (
    <div className="space-y-6 max-w-6xl">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-base font-semibold text-slate-900">Attendance Verification</h2>
          <p className="text-xs text-slate-500">
            Sustained temporal presence. Never marked from a single frame; instructor manual overrides recorded.
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

      {/* Attendance Records Table */}
      <div className="bg-white border border-slate-200 rounded-xl overflow-hidden shadow-xs">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 text-slate-500 uppercase tracking-wider font-semibold border-b border-slate-200">
              <tr>
                <th className="py-3 px-4">Anonymous Track ID</th>
                <th className="py-3 px-4">Assigned Participant</th>
                <th className="py-3 px-4">Detected Interval</th>
                <th className="py-3 px-4">Observed Duration</th>
                <th className="py-3 px-4">Session Coverage</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4">Evidence Quality</th>
                <th className="py-3 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {loading ? (
                <tr>
                  <td colSpan={8} className="py-12 text-center text-slate-400 text-xs">
                    Loading attendance records...
                  </td>
                </tr>
              ) : records.length === 0 ? (
                <tr>
                  <td colSpan={8} className="py-12 text-center text-slate-400 text-xs">
                    No attendance records for this session yet. Upload media and run processing to generate tracks.
                  </td>
                </tr>
              ) : (
                records.map((r) => (
                  <tr key={r.id} className="hover:bg-slate-50/70 transition-colors">
                    <td className="py-3 px-4 font-mono font-semibold text-slate-800">{r.anonymous_track_id}</td>
                    <td className="py-3 px-4">
                      {r.participant ? (
                        <div>
                          <div className="font-semibold text-slate-900">{r.participant.name}</div>
                          <div className="text-[10px] text-slate-400 font-mono">{r.participant.roll_number}</div>
                        </div>
                      ) : (
                        <span className="text-slate-400 italic">Unassigned (Anonymous Track)</span>
                      )}
                    </td>
                    <td className="py-3 px-4 text-slate-600 font-mono">
                      {Math.round(r.first_detected_sec)}s – {Math.round(r.last_detected_sec)}s
                    </td>
                    <td className="py-3 px-4 text-slate-600 font-medium">
                      {Math.round(r.total_observed_sec)}s
                    </td>
                    <td className="py-3 px-4 font-medium text-slate-700">
                      {r.observed_pct}%
                    </td>
                    <td className="py-3 px-4">
                      {getStatusBadge(r.status)}
                      {r.is_manual_override && (
                        <span className="block text-[9px] text-indigo-600 font-medium mt-0.5">
                          Manual Override
                        </span>
                      )}
                    </td>
                    <td className="py-3 px-4">
                      <span className="text-[10px] font-medium text-slate-500 uppercase tracking-wider">
                        {r.evidence_quality}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-right">
                      <button
                        onClick={() => handleStartEdit(r)}
                        className="inline-flex items-center gap-1 px-2.5 py-1 text-[11px] font-medium text-slate-600 hover:text-indigo-600 bg-slate-50 hover:bg-indigo-50 border border-slate-200 rounded-md"
                      >
                        <Edit3 className="h-3 w-3" /> Associate / Edit
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Manual Association & Override Modal */}
      {editingRecord && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 backdrop-blur-xs p-4">
          <div className="bg-white rounded-xl max-w-md w-full p-6 shadow-xl border border-slate-200">
            <h3 className="text-sm font-semibold text-slate-900 mb-1">
              Associate & Override: {editingRecord.anonymous_track_id}
            </h3>
            <p className="text-xs text-slate-500 mb-4">
              Instructors can associate anonymous tracks with registered students and record corrections.
            </p>

            <div className="space-y-3.5">
              <div>
                <label className="block text-xs font-medium text-slate-700 mb-1">Associate Participant</label>
                <select
                  value={editParticipantId}
                  onChange={(e) => setEditParticipantId(e.target.value)}
                  className="w-full px-3 py-2 bg-white border border-slate-200 rounded-lg text-xs"
                >
                  <option value="">— Unassigned (Keep Anonymous) —</option>
                  {participants.map((p) => (
                    <option key={p.id} value={p.id}>
                      {p.name} ({p.roll_number})
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-700 mb-1">Attendance Status</label>
                <select
                  value={editStatus}
                  onChange={(e) => setEditStatus(e.target.value)}
                  className="w-full px-3 py-2 bg-white border border-slate-200 rounded-lg text-xs"
                >
                  <option value="PRESENT">PRESENT</option>
                  <option value="PARTIAL">PARTIAL</option>
                  <option value="ABSENT">ABSENT</option>
                  <option value="NEEDS_REVIEW">NEEDS_REVIEW</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-700 mb-1">Override Reason / Notes</label>
                <textarea
                  rows={2}
                  value={editNotes}
                  onChange={(e) => setEditNotes(e.target.value)}
                  placeholder="e.g. Instructor confirmed student was in rear row occlusion zone."
                  className="w-full px-3 py-2 bg-white border border-slate-200 rounded-lg text-xs"
                />
              </div>

              <div className="flex justify-end gap-2 pt-3 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setEditingRecord(null)}
                  className="px-3.5 py-1.5 text-xs text-slate-600 hover:bg-slate-100 rounded-lg"
                >
                  Cancel
                </button>
                <button
                  type="button"
                  onClick={handleSaveEdit}
                  className="px-4 py-1.5 text-xs font-medium text-white bg-indigo-600 hover:bg-indigo-700 rounded-lg"
                >
                  Save Override
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
