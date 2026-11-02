import React from 'react';
import { NavLink, Outlet } from 'react-router-dom';
import {
  LayoutDashboard,
  Users,
  Video,
  ClipboardCheck,
  TrendingUp,
  Lightbulb,
  FileText,
  ShieldCheck,
  GraduationCap
} from 'lucide-react';

const navigation = [
  { name: 'Overview', to: '/', icon: LayoutDashboard },
  { name: 'Participants', to: '/participants', icon: Users },
  { name: 'Sessions', to: '/sessions', icon: Video },
  { name: 'Attendance', to: '/attendance', icon: ClipboardCheck },
  { name: 'Engagement Analytics', to: '/engagement', icon: TrendingUp },
  { name: 'AI Teaching Suggestions', to: '/recommendations', icon: Lightbulb },
  { name: 'Session Reports', to: '/reports', icon: FileText },
];

export default function Layout() {
  return (
    <div className="flex h-screen bg-slate-50 text-slate-800 font-sans antialiased overflow-hidden">
      {/* Sidebar */}
      <aside className="w-64 bg-white border-r border-slate-200 flex flex-col justify-between shadow-xs">
        <div>
          {/* Logo & Header */}
          <div className="h-16 flex items-center gap-3 px-6 border-b border-slate-100">
            <div className="h-9 w-9 rounded-lg bg-indigo-600 flex items-center justify-center text-white shadow-sm">
              <GraduationCap className="h-5 w-5" />
            </div>
            <div>
              <span className="font-semibold text-slate-900 text-sm tracking-tight block">EduMultimodal</span>
              <span className="text-[10px] text-slate-400 uppercase tracking-wider font-medium">Privacy-First AI</span>
            </div>
          </div>

          {/* Nav Links */}
          <nav className="p-3 space-y-1">
            {navigation.map((item) => {
              const Icon = item.icon;
              return (
                <NavLink
                  key={item.name}
                  to={item.to}
                  end={item.to === '/'}
                  className={({ isActive }) =>
                    `flex items-center gap-3 px-3.5 py-2.5 rounded-lg text-xs font-medium transition-colors ${
                      isActive
                        ? 'bg-indigo-50 text-indigo-700 font-semibold'
                        : 'text-slate-600 hover:bg-slate-100/70 hover:text-slate-900'
                    }`
                  }
                >
                  <Icon className="h-4 w-4 shrink-0" />
                  <span>{item.name}</span>
                </NavLink>
              );
            })}
          </nav>
        </div>

        {/* Privacy & Mode Footnote */}
        <div className="p-4 m-3 rounded-xl bg-slate-50 border border-slate-200 text-slate-500 text-[11px] leading-relaxed">
          <div className="flex items-center gap-1.5 text-emerald-700 font-medium mb-1">
            <ShieldCheck className="h-3.5 w-3.5" />
            <span>Anonymous Processing</span>
          </div>
          <p className="text-[10px] text-slate-500">
            No biometric face crops or voiceprints stored. Offline verifiable processing.
          </p>
        </div>
      </aside>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Top Navbar */}
        <header className="h-16 bg-white border-b border-slate-200 flex items-center justify-between px-8">
          <div>
            <h1 className="text-base font-semibold text-slate-800">Multimodal Attendance & Engagement Intelligence</h1>
            <p className="text-xs text-slate-500">Observable temporal movement and audio interaction proxies</p>
          </div>
          <div className="flex items-center gap-3">
            <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-emerald-50 text-emerald-700 border border-emerald-200/60">
              <span className="h-1.5 w-1.5 rounded-full bg-emerald-500"></span>
              Local Engine Offline Ready
            </span>
          </div>
        </header>

        {/* Page Content Viewport */}
        <main className="flex-1 overflow-y-auto p-8">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
