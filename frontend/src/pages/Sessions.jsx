import React, { useState, useEffect } from 'react';
import { sessionService } from '../services/api';
import {
  Video,
  Plus,
  Play,
  UploadCloud,
  FileCheck,
  Trash2,
  Clock,
  Sparkles,
  AlertCircle
} from 'lucide-react';
import { Link } from 'react-router-dom';

export default function Sessions() {
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(true);

  // Create Session Modal State
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [formData, setFormData] = useState({
    title: '',
    course_name: '',
    instructor_name: '',
    description: '',
    expected_participant_count: 20,
    config: {
      min_attendance_pct: 60.0,
      min_observed_duration_sec: 30.0,
      frame_sample_interval_sec: 1.0,
      weight_visual: 0.35,
      weight_orientation: 0.35,
      weight_audio: 0.30
    }
  });

  // Upload Modal State
  const [uploadSession, setUploadSession] = useState(null);
  const [videoFile, setVideoFile] = useState(null);
  const [audioFile, setAudioFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState('');

  // Processing poll state
  const [processingStatus, setProcessingStatus] = useState({});

  useEffect(() => {
    fetchSessions();
  }, []);

  const fetchSessions = async () => {
    try {
      setLoading(true);
      const res = await sessionService.getAll();
      setSessions(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateSession = async (e) => {
    e.preventDefault();
    try {
      await sessionService.create(formData);
      setShowCreateModal(false);
      fetchSessions();
    } catch (err) {
      alert('Failed to create session');
    }
  };

  const handleDeleteSession = async (id) => {
    if (window.confirm('Delete this session and all associated analytics?')) {
      try {
        await sessionService.delete(id);
        fetchSessions();
      } catch (err) {
        alert('Failed to delete session');
      }
    }
  };

  const handleUploadSubmit = async (e) => {
    e.preventDefault();
    if (!videoFile && !audioFile) {
      setUploadError('Please choose at least a video or audio file.');
      return;
    }
    try {
      setUploading(true);
      setUploadError('');
      const data = new FormData();
      if (videoFile) data.append('video', videoFile);
      if (audioFile) data.append('audio', audioFile);

      await sessionService.uploadMedia(uploadSession.id, data);
      setUploadSession(null);
      setVideoFile(null);
      setAudioFile(null);
      fetchSessions();
    } catch (err) {
      setUploadError(err.response?.data?.detail || 'Media upload failed.');
    } finally {
      setUploading(false);
    }
  };

  const handleTriggerProcess = async (sessionId) => {
    try {
      await sessionService.triggerProcess(sessionId);
      fetchSessions();
      // Start polling status
      pollStatus(sessionId);
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to trigger processing.');
    }
  };

  const pollStatus = (sessionId) => {
    const interval = setInterval(async () => {
      try {
        const res = await sessionService.getStatus(sessionId);
        if (res.data) {
          setProcessingStatus((prev) => ({ ...prev, [sessionId]: res.data }));
          if (res.data.status === 'COMPLETED' || res.data.status === 'FAILED') {
            clearInterval(interval);
            fetchSessions();
          }
        }
      } catch (e) {
        clearInterval(interval);
      }
    }, 2000);
  };

  return (
    <div className="space-y-6 max-w-6xl">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-base font-semibold text-slate-900">Classroom Sessions</h2>
          <p className="text-xs text-slate-500">
            Create sessions, upload local video/audio, and run autonomous multimodal intelligence.
          </p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="inline-flex items-center gap-1.5 px-3.5 py-2 bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-medium rounded-lg shadow-xs transition-colors"
        >
          <Plus className="h-4 w-4" />
          Create Session
        </button>
      </div>

      {/* Sessions Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {sessions.length === 0 ? (
          <div className="col-span-full py-16 text-center bg-white rounded-xl border border-slate-200 text-slate-400 text-xs">
            No sessions created yet. Click "Create Session" above to begin.
          </div>
        ) : (
          sessions.map((s) => {
            const liveJob = processingStatus[s.id];
            return (
              <div
                key={s.id}
                className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs flex flex-col justify-between hover:border-slate-300 transition-all"
              >
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-[10px] font-semibold text-indigo-700 bg-indigo-50 px-2 py-0.5 rounded border border-indigo-100">
                      {s.course_name}
                    </span>
                    <span
                      className={`text-[10px] font-medium px-2 py-0.5 rounded-full ${
                        s.status === 'COMPLETED'
                          ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                          : s.status === 'PROCESSING' || s.status === 'QUEUED'
                          ? 'bg-indigo-50 text-indigo-700 border border-indigo-200 animate-pulse'
                          : 'bg-slate-100 text-slate-600'
                      }`}
                    >
                      {s.status}
                    </span>
                  </div>

                  <h3 className="text-sm font-semibold text-slate-900 line-clamp-1">{s.title}</h3>
                  <p className="text-xs text-slate-500 mt-0.5">{s.instructor_name}</p>
                  {s.description && (
                    <p className="text-[11px] text-slate-600 mt-2 line-clamp-2 bg-slate-50 p-2 rounded-md">
                      {s.description}
                    </p>
                  )}

                  {/* Processing progress bar if active */}
                  {(s.status === 'PROCESSING' || liveJob?.status === 'RUNNING') && (
                    <div className="mt-3 p-2.5 bg-indigo-50/60 border border-indigo-100 rounded-lg">
                      <div className="flex justify-between text-[10px] text-indigo-800 font-medium mb-1">
                        <span>{liveJob?.current_step || 'Analyzing streams...'}</span>
                        <span>{Math.round(liveJob?.progress || 0)}%</span>
                      </div>
                      <div className="w-full bg-indigo-200/50 rounded-full h-1.5 overflow-hidden">
                        <div
                          className="bg-indigo-600 h-1.5 rounded-full transition-all duration-300"
                          style={{ width: `${liveJob?.progress || 10}%` }}
                        ></div>
                      </div>
                    </div>
                  )}

                  <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-[11px] text-slate-400">
                    <span className="flex items-center gap-1">
                      <Clock className="h-3.5 w-3.5" />
                      {s.media_duration_sec ? `${Math.round(s.media_duration_sec)}s recorded` : 'No media yet'}
                    </span>
                    <span>Expected: {s.expected_participant_count}</span>
                  </div>
                </div>

                <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between gap-2">
                  <div className="flex items-center gap-1">
                    <button
                      onClick={() => setUploadSession(s)}
                      title="Upload Video/Audio"
                      className="p-1.5 text-slate-500 hover:text-indigo-600 hover:bg-slate-100 rounded-md transition-colors"
                    >
                      <UploadCloud className="h-4 w-4" />
                    </button>
                    {(s.video_path || s.audio_path) && s.status !== 'PROCESSING' && (
                      <button
                        onClick={() => handleTriggerProcess(s.id)}
                        title="Run Processing Pipeline"
                        className="p-1.5 text-emerald-600 hover:bg-emerald-50 rounded-md transition-colors"
                      >
                        <Play className="h-4 w-4" />
                      </button>
                    )}
                    <button
                      onClick={() => handleDeleteSession(s.id)}
                      title="Delete Session"
                      className="p-1.5 text-slate-400 hover:text-rose-600 hover:bg-slate-100 rounded-md transition-colors"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>

                  <div className="flex items-center gap-2">
                    <Link
                      to={`/attendance?sessionId=${s.id}`}
                      className="text-xs font-medium text-slate-600 hover:text-indigo-600 px-2 py-1 bg-slate-50 hover:bg-indigo-50 border border-slate-200 rounded-md"
                    >
                      Attendance
                    </Link>
                    <Link
                      to={`/engagement?sessionId=${s.id}`}
                      className="text-xs font-medium text-indigo-600 hover:text-indigo-800 px-2 py-1 bg-indigo-50 border border-indigo-100 rounded-md"
                    >
                      Analytics
                    </Link>
                  </div>
                </div>
              </div>
            );
          })
        )}
      </div>

      {/* Create Session Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 backdrop-blur-xs p-4">
          <div className="bg-white rounded-xl max-w-lg w-full p-6 shadow-xl border border-slate-200 max-h-[90vh] overflow-y-auto">
            <h3 className="text-sm font-semibold text-slate-900 mb-4">Create New Classroom Session</h3>
            <form onSubmit={handleCreateSession} className="space-y-3.5">
              <div>
                <label className="block text-xs font-medium text-slate-700 mb-1">Session Title *</label>
                <input
                  type="text"
                  required
                  value={formData.title}
                  onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                  placeholder="e.g. Distributed Computing - Lecture 08"
                  className="w-full px-3 py-2 bg-white border border-slate-200 rounded-lg text-xs focus:ring-1 focus:ring-indigo-500"
                />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-medium text-slate-700 mb-1">Course Code / Name *</label>
                  <input
                    type="text"
                    required
                    value={formData.course_name}
                    onChange={(e) => setFormData({ ...formData, course_name: e.target.value })}
                    placeholder="CS-501"
                    className="w-full px-3 py-2 bg-white border border-slate-200 rounded-lg text-xs"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-700 mb-1">Instructor Name *</label>
                  <input
                    type="text"
                    required
                    value={formData.instructor_name}
                    onChange={(e) => setFormData({ ...formData, instructor_name: e.target.value })}
                    placeholder="Prof. Alan Turing"
                    className="w-full px-3 py-2 bg-white border border-slate-200 rounded-lg text-xs"
                  />
                </div>
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-700 mb-1">Expected Attendees</label>
                <input
                  type="number"
                  value={formData.expected_participant_count}
                  onChange={(e) => setFormData({ ...formData, expected_participant_count: parseInt(e.target.value) || 0 })}
                  className="w-full px-3 py-2 bg-white border border-slate-200 rounded-lg text-xs"
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-700 mb-1">Description / Topic</label>
                <textarea
                  rows={2}
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  placeholder="Overview of Paxos consensus protocol..."
                  className="w-full px-3 py-2 bg-white border border-slate-200 rounded-lg text-xs"
                />
              </div>

              {/* Advanced Threshold Configuration */}
              <div className="p-3 bg-slate-50 border border-slate-200 rounded-lg space-y-2">
                <span className="text-[11px] font-semibold text-slate-700 block">Attendance & Fusion Thresholds</span>
                <div className="grid grid-cols-2 gap-3 text-xs">
                  <div>
                    <label className="block text-[10px] text-slate-500 mb-0.5">Min Attendance %</label>
                    <input
                      type="number"
                      value={formData.config.min_attendance_pct}
                      onChange={(e) =>
                        setFormData({
                          ...formData,
                          config: { ...formData.config, min_attendance_pct: parseFloat(e.target.value) }
                        })
                      }
                      className="w-full px-2 py-1 bg-white border border-slate-200 rounded text-xs"
                    />
                  </div>
                  <div>
                    <label className="block text-[10px] text-slate-500 mb-0.5">Min Observed (sec)</label>
                    <input
                      type="number"
                      value={formData.config.min_observed_duration_sec}
                      onChange={(e) =>
                        setFormData({
                          ...formData,
                          config: { ...formData.config, min_observed_duration_sec: parseFloat(e.target.value) }
                        })
                      }
                      className="w-full px-2 py-1 bg-white border border-slate-200 rounded text-xs"
                    />
                  </div>
                </div>
              </div>

              <div className="flex justify-end gap-2 pt-3 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="px-3.5 py-1.5 text-xs text-slate-600 hover:bg-slate-100 rounded-lg"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-3.5 py-1.5 text-xs font-medium text-white bg-indigo-600 hover:bg-indigo-700 rounded-lg"
                >
                  Create Session
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Media Upload Modal */}
      {uploadSession && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 backdrop-blur-xs p-4">
          <div className="bg-white rounded-xl max-w-md w-full p-6 shadow-xl border border-slate-200">
            <h3 className="text-sm font-semibold text-slate-900 mb-1">
              Upload Media: {uploadSession.title}
            </h3>
            <p className="text-xs text-slate-500 mb-4">
              Select local classroom MP4/AVI video or WAV/FLAC audio for offline processing.
            </p>
            {uploadError && (
              <div className="mb-4 p-2.5 bg-rose-50 border border-rose-200 text-rose-700 rounded-lg text-xs">
                {uploadError}
              </div>
            )}
            <form onSubmit={handleUploadSubmit} className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-slate-700 mb-1">Video File (MP4, AVI)</label>
                <input
                  type="file"
                  accept="video/*"
                  onChange={(e) => setVideoFile(e.target.files[0])}
                  className="w-full text-xs text-slate-500 file:mr-3 file:py-1.5 file:px-3 file:rounded-md file:border-0 file:text-xs file:font-medium file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100"
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-700 mb-1">Audio File (Optional WAV/MP3)</label>
                <input
                  type="file"
                  accept="audio/*"
                  onChange={(e) => setAudioFile(e.target.files[0])}
                  className="w-full text-xs text-slate-500 file:mr-3 file:py-1.5 file:px-3 file:rounded-md file:border-0 file:text-xs file:font-medium file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100"
                />
              </div>
              <div className="flex justify-end gap-2 pt-3 border-t border-slate-100">
                <button
                  type="button"
                  disabled={uploading}
                  onClick={() => setUploadSession(null)}
                  className="px-3.5 py-1.5 text-xs text-slate-600 hover:bg-slate-100 rounded-lg"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={uploading}
                  className="px-4 py-1.5 text-xs font-medium text-white bg-indigo-600 hover:bg-indigo-700 rounded-lg disabled:opacity-50 flex items-center gap-1.5"
                >
                  {uploading ? 'Uploading...' : 'Save Media'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
