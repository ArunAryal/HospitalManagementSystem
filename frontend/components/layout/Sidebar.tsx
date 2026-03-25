'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  LayoutDashboard, Users, UserRound, CalendarDays,
  FileText, Pill, BedDouble, Receipt, Activity,
} from 'lucide-react';
import { cn } from '@/lib/utils';

const NAV = [
  { label: 'Dashboard',       href: '/',                 icon: LayoutDashboard },
  { label: 'Patients',        href: '/patients',         icon: Users },
  { label: 'Doctors',         href: '/doctors',          icon: UserRound },
  { label: 'Appointments',    href: '/appointments',     icon: CalendarDays },
  { label: 'Medical Records', href: '/medical-records',  icon: FileText },
  { label: 'Medicines',       href: '/medicines',        icon: Pill },
  { label: 'Rooms & Admissions', href: '/rooms',         icon: BedDouble },
  { label: 'Billing',         href: '/billing',          icon: Receipt },
];

export default function Sidebar() {
  const path = usePathname();

  return (
    <aside className="fixed inset-y-0 left-0 z-40 w-64 bg-white border-r border-slate-200 flex flex-col">
      {/* Logo */}
      <div className="flex items-center gap-3 px-5 py-5 border-b border-slate-100">
        <div className="w-8 h-8 rounded-lg bg-brand-600 flex items-center justify-center flex-shrink-0">
          <Activity className="w-4 h-4 text-white" />
        </div>
        <div>
          <p className="text-sm font-semibold text-slate-900 leading-tight">MediCore HMS</p>
          <p className="text-[10px] text-slate-400 font-medium tracking-wide uppercase">Hospital System</p>
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 px-3 py-4 space-y-0.5 overflow-y-auto">
        {NAV.map(({ label, href, icon: Icon }) => {
          const active = href === '/' ? path === '/' : path.startsWith(href);
          return (
            <Link
              key={href}
              href={href}
              className={cn(
                'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors duration-100',
                active
                  ? 'bg-brand-50 text-brand-700'
                  : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900',
              )}
            >
              <Icon className={cn('w-4 h-4 flex-shrink-0', active ? 'text-brand-600' : 'text-slate-400')} />
              {label}
            </Link>
          );
        })}
      </nav>

      {/* Footer */}
      <div className="px-5 py-4 border-t border-slate-100">
        <p className="text-[11px] text-slate-400">API: {process.env.NEXT_PUBLIC_API_URL || 'localhost:8000'}</p>
      </div>
    </aside>
  );
}
