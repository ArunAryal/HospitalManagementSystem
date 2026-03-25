'use client';

import { usePathname } from 'next/navigation';
import { Bell, Search } from 'lucide-react';

const TITLES: Record<string, string> = {
  '/':                 'Dashboard',
  '/patients':         'Patients',
  '/doctors':          'Doctors',
  '/appointments':     'Appointments',
  '/medical-records':  'Medical Records',
  '/medicines':        'Medicines',
  '/rooms':            'Rooms & Admissions',
  '/billing':          'Billing',
};

export default function Topbar() {
  const path = usePathname();
  const base = '/' + (path.split('/').filter(Boolean)[0] ?? '');
  const title = TITLES[path] ?? TITLES[base] ?? 'HMS';

  return (
    <header className="sticky top-0 z-30 h-14 bg-white/80 backdrop-blur border-b border-slate-200 flex items-center justify-between px-6">
      <h1 className="text-sm font-semibold text-slate-900">{title}</h1>
      <div className="flex items-center gap-2">
        <button className="w-8 h-8 flex items-center justify-center rounded-lg text-slate-400 hover:bg-slate-100 transition-colors">
          <Bell className="w-4 h-4" />
        </button>
        <div className="w-7 h-7 rounded-full bg-brand-100 flex items-center justify-center">
          <span className="text-xs font-semibold text-brand-700">A</span>
        </div>
      </div>
    </header>
  );
}
