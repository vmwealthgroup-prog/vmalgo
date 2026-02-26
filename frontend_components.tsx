// src/components/layout/RootLayout.tsx
'use client';

import React from 'react';
import { motion } from 'framer-motion';
import Navbar from './Navbar';
import Sidebar from './Sidebar';

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const [sidebarOpen, setSidebarOpen] = React.useState(true);

  return (
    <div className="min-h-screen bg-gradient-to-br from-dark-950 via-dark-900 to-dark-950">
      {/* Animated background elements */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <motion.div
          className="absolute top-0 left-0 w-1/3 h-1/3 bg-electric-500/5 rounded-full blur-3xl"
          animate={{ x: [0, 100, 0], y: [0, -100, 0] }}
          transition={{ duration: 20, repeat: Infinity }}
        />
        <motion.div
          className="absolute bottom-0 right-0 w-1/3 h-1/3 bg-accent-green/3 rounded-full blur-3xl"
          animate={{ x: [0, -100, 0], y: [0, 100, 0] }}
          transition={{ duration: 25, repeat: Infinity, delay: 2 }}
        />
      </div>

      <Navbar onMenuClick={() => setSidebarOpen(!sidebarOpen)} />

      <div className="flex pt-16 z-40">
        <Sidebar isOpen={sidebarOpen} />
        
        <main className="flex-1 overflow-auto">
          <div className="p-6 lg:p-8">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
            >
              {children}
            </motion.div>
          </div>
        </main>
      </div>
    </div>
  );
}

// src/components/layout/Navbar.tsx
'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { useAuth } from '@/hooks/useAuth';

interface NavbarProps {
  onMenuClick: () => void;
}

export default function Navbar({ onMenuClick }: NavbarProps) {
  const { user, logout } = useAuth();
  const [isDropdownOpen, setIsDropdownOpen] = React.useState(false);

  return (
    <nav className="fixed top-0 w-full z-50 glass backdrop-blur-xl border-b border-white/10">
      <div className="px-6 py-4 flex items-center justify-between">
        <motion.div
          className="flex items-center gap-4"
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
        >
          <button
            onClick={onMenuClick}
            className="p-2 hover:bg-white/10 rounded-lg transition-colors lg:hidden"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
          
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-accent-blue to-accent-green flex items-center justify-center font-bold text-dark-950">
              VM
            </div>
            <div className="hidden sm:block">
              <p className="text-sm font-semibold text-white">VM Algo</p>
              <p className="text-xs text-gray-400">Research Lab</p>
            </div>
          </div>
        </motion.div>

        <motion.div
          className="flex items-center gap-4"
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
        >
          {/* Notifications */}
          <button className="relative p-2 hover:bg-white/10 rounded-lg transition-colors">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
            </svg>
            <span className="absolute top-1 right-1 w-2 h-2 bg-accent-red rounded-full animate-pulse" />
          </button>

          {/* User Menu */}
          <div className="relative">
            <button
              onClick={() => setIsDropdownOpen(!isDropdownOpen)}
              className="flex items-center gap-2 p-2 hover:bg-white/10 rounded-lg transition-colors"
            >
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-electric-400 to-accent-blue" />
              <span className="hidden sm:inline text-sm font-medium">{user?.name}</span>
            </button>

            {isDropdownOpen && (
              <motion.div
                className="absolute right-0 mt-2 w-48 glass rounded-lg p-2"
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
              >
                <button className="w-full text-left px-4 py-2 text-sm hover:bg-white/10 rounded transition-colors">
                  Profile
                </button>
                <button className="w-full text-left px-4 py-2 text-sm hover:bg-white/10 rounded transition-colors">
                  Settings
                </button>
                <button className="w-full text-left px-4 py-2 text-sm hover:bg-white/10 rounded transition-colors">
                  API Keys
                </button>
                <hr className="my-2 border-white/10" />
                <button
                  onClick={logout}
                  className="w-full text-left px-4 py-2 text-sm hover:bg-red-500/20 text-red-400 rounded transition-colors"
                >
                  Logout
                </button>
              </motion.div>
            )}
          </div>
        </motion.div>
      </div>
    </nav>
  );
}

// src/components/layout/Sidebar.tsx
'use client';

import React from 'react';
import { motion } from 'framer-motion';
import Link from 'next/link';
import { usePathname } from 'next/navigation';

interface SidebarProps {
  isOpen: boolean;
}

const menuItems = [
  { icon: '📊', label: 'Dashboard', href: '/dashboard' },
  { icon: '🔍', label: 'Scanner', href: '/scanner' },
  { icon: '⚙️', label: 'Strategy Builder', href: '/strategy-builder' },
  { icon: '📈', label: 'Backtest', href: '/backtest' },
  { icon: '💼', label: 'Portfolio', href: '/portfolio' },
  { icon: '🤖', label: 'AI Research', href: '/ai-research' },
  { icon: '⚡', label: 'Auto Trading', href: '/auto-trading' },
  { icon: '📱', label: 'Alerts', href: '/alerts' },
];

const adminItems = [
  { icon: '👥', label: 'Users', href: '/admin/users' },
  { icon: '✅', label: 'Approve Strategies', href: '/admin/strategies' },
  { icon: '💰', label: 'Revenue', href: '/admin/revenue' },
  { icon: '⚙️', label: 'Monitoring', href: '/admin/monitoring' },
];

export default function Sidebar({ isOpen }: SidebarProps) {
  const pathname = usePathname();

  return (
    <motion.aside
      className={`fixed left-0 top-16 h-[calc(100vh-64px)] w-64 glass border-r border-white/10 overflow-y-auto transition-all duration-300 z-40 ${
        isOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'
      }`}
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
    >
      <div className="p-6">
        <nav className="space-y-2">
          <p className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-4">
            Trading
          </p>
          {menuItems.map((item, index) => (
            <Link key={item.href} href={item.href}>
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.05 }}
                className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-all ${
                  pathname === item.href
                    ? 'bg-accent-blue/20 text-accent-blue'
                    : 'hover:bg-white/5 text-gray-300'
                }`}
              >
                <span className="text-xl">{item.icon}</span>
                <span className="text-sm font-medium">{item.label}</span>
              </motion.div>
            </Link>
          ))}

          <p className="text-xs font-semibold text-gray-500 uppercase tracking-wider mt-8 mb-4">
            Admin
          </p>
          {adminItems.map((item, index) => (
            <Link key={item.href} href={item.href}>
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: (menuItems.length + index) * 0.05 }}
                className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-all ${
                  pathname === item.href
                    ? 'bg-accent-blue/20 text-accent-blue'
                    : 'hover:bg-white/5 text-gray-300'
                }`}
              >
                <span className="text-xl">{item.icon}</span>
                <span className="text-sm font-medium">{item.label}</span>
              </motion.div>
            </Link>
          ))}
        </nav>
      </div>
    </motion.aside>
  );
}

// src/components/common/Card.tsx
'use client';

import React from 'react';
import { motion, MotionProps } from 'framer-motion';

interface CardProps extends MotionProps {
  children: React.ReactNode;
  className?: string;
  glassmorphism?: boolean;
  hover?: boolean;
}

export default function Card({
  children,
  className = '',
  glassmorphism = true,
  hover = false,
  ...motionProps
}: CardProps) {
  return (
    <motion.div
      className={`
        rounded-xl p-6 transition-all duration-300
        ${glassmorphism ? 'glass' : 'bg-dark-800 border border-white/10'}
        ${hover ? 'hover:shadow-elevation-2 hover:border-accent-blue/30' : ''}
        ${className}
      `}
      whileHover={hover ? { y: -4 } : undefined}
      {...motionProps}
    >
      {children}
    </motion.div>
  );
}

// src/components/common/Button.tsx
'use client';

import React from 'react';
import { motion } from 'framer-motion';

interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'danger' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  isLoading?: boolean;
}

export default function Button({
  variant = 'primary',
  size = 'md',
  isLoading = false,
  children,
  className = '',
  ...props
}: ButtonProps) {
  const baseStyles =
    'font-semibold rounded-lg transition-all duration-300 flex items-center justify-center gap-2';

  const variants = {
    primary:
      'bg-gradient-to-r from-accent-blue to-accent-green text-dark-950 hover:shadow-neon-blue hover:scale-105 disabled:opacity-50',
    secondary:
      'bg-transparent border-2 border-accent-blue text-accent-blue hover:bg-accent-blue/10',
    danger: 'bg-accent-red/20 border border-accent-red text-accent-red hover:bg-accent-red/30',
    ghost: 'text-gray-300 hover:text-white hover:bg-white/5',
  };

  const sizes = {
    sm: 'px-3 py-2 text-sm',
    md: 'px-4 py-2.5 text-base',
    lg: 'px-6 py-3 text-lg',
  };

  return (
    <motion.button
      className={`${baseStyles} ${variants[variant]} ${sizes[size]} ${className}`}
      whileHover={{ scale: isLoading ? 1 : 1.05 }}
      whileTap={{ scale: 0.95 }}
      disabled={isLoading || props.disabled}
      {...props}
    >
      {isLoading && (
        <motion.div
          className="w-4 h-4 border-2 border-current border-t-transparent rounded-full"
          animate={{ rotate: 360 }}
          transition={{ duration: 1, repeat: Infinity }}
        />
      )}
      {children}
    </motion.button>
  );
}

// src/components/common/GlassPill.tsx
'use client';

import React from 'react';
import { motion } from 'framer-motion';

interface GlassPillProps {
  label: string;
  value: string | number;
  icon?: React.ReactNode;
  trend?: 'up' | 'down' | 'neutral';
  change?: number;
}

export default function GlassPill({
  label,
  value,
  icon,
  trend,
  change,
}: GlassPillProps) {
  const trendColor =
    trend === 'up'
      ? 'text-accent-green'
      : trend === 'down'
      ? 'text-accent-red'
      : 'text-gray-400';

  return (
    <motion.div
      className="glass rounded-xl p-4 flex items-center justify-between"
      whileHover={{ y: -2 }}
    >
      <div>
        <p className="text-xs text-gray-400 uppercase tracking-wider font-semibold">
          {label}
        </p>
        <p className="text-2xl font-bold mt-1">{value}</p>
        {change !== undefined && (
          <p className={`text-xs mt-1 ${trendColor}`}>
            {trend === 'up' ? '↑' : trend === 'down' ? '↓' : '→'} {Math.abs(change)}%
          </p>
        )}
      </div>
      {icon && <div className="text-3xl opacity-60">{icon}</div>}
    </motion.div>
  );
}
