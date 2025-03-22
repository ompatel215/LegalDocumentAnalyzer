import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  HomeIcon,
  DocumentTextIcon,
  ChartBarIcon,
  CogIcon,
  FolderIcon,
  ArrowUpTrayIcon
} from '@heroicons/react/24/outline';

const navigation = [
  { name: 'Dashboard', href: '/', icon: HomeIcon },
  { name: 'Upload Document', href: '/upload', icon: ArrowUpTrayIcon },
  { name: 'Documents', href: '/documents', icon: FolderIcon },
  { name: 'Analysis', href: '/analysis', icon: ChartBarIcon },
  { name: 'Settings', href: '/settings', icon: CogIcon },
];

const Sidebar: React.FC = () => {
  return (
    <div className="w-64 bg-white shadow-sm">
      <div className="h-full px-3 py-4 overflow-y-auto">
        <nav className="space-y-2">
          {navigation.map((item) => (
            <NavLink
              key={item.name}
              to={item.href}
              className={({ isActive }) =>
                `flex items-center px-3 py-2 text-sm font-medium rounded-lg ${
                  isActive
                    ? 'bg-indigo-50 text-indigo-600'
                    : 'text-gray-900 hover:bg-gray-100'
                }`
              }
            >
              <item.icon
                className={`flex-shrink-0 w-6 h-6 mr-3 ${
                  location.pathname === item.href
                    ? 'text-indigo-600'
                    : 'text-gray-500'
                }`}
                aria-hidden="true"
              />
              {item.name}
            </NavLink>
          ))}
        </nav>
      </div>
    </div>
  );
};

export default Sidebar; 