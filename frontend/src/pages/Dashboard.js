import React from 'react';
import { useQuery } from 'react-query';
import { Link } from 'react-router-dom';
import axios from 'axios';
import {
  DocumentTextIcon,
  DocumentCheckIcon,
  ClockIcon,
  ExclamationTriangleIcon,
} from '@heroicons/react/24/outline';

const StatCard = ({ title, value, icon: Icon, color }) => (
  <div className="bg-white overflow-hidden shadow rounded-lg">
    <div className="p-5">
      <div className="flex items-center">
        <div className="flex-shrink-0">
          <Icon className={`h-6 w-6 ${color}`} />
        </div>
        <div className="ml-5 w-0 flex-1">
          <dl>
            <dt className="text-sm font-medium text-gray-500 truncate">{title}</dt>
            <dd className="text-lg font-medium text-gray-900">{value}</dd>
          </dl>
        </div>
      </div>
    </div>
  </div>
);

const Dashboard = () => {
  const { data: stats, isLoading: statsLoading } = useQuery('dashboardStats', async () => {
    const token = localStorage.getItem('token');
    const response = await axios.get('http://localhost:8000/api/v1/dashboard/stats', {
      headers: { Authorization: `Bearer ${token}` }
    });
    return response.data;
  });

  const { data: recentActivity, isLoading: activityLoading } = useQuery('recentActivity', async () => {
    const token = localStorage.getItem('token');
    const response = await axios.get('http://localhost:8000/api/v1/dashboard/recent-activity', {
      headers: { Authorization: `Bearer ${token}` }
    });
    return response.data;
  });

  if (statsLoading || activityLoading) {
    return (
      <div className="flex justify-center items-center h-full">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-semibold text-gray-900">Dashboard</h1>
      </div>

      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard
          title="Total Documents"
          value={stats?.total_documents || 0}
          icon={DocumentTextIcon}
          color="text-blue-600"
        />
        <StatCard
          title="Analyzed Documents"
          value={stats?.documents_analyzed || 0}
          icon={DocumentCheckIcon}
          color="text-green-600"
        />
        <StatCard
          title="Pending Analysis"
          value={stats?.pending_analysis || 0}
          icon={ClockIcon}
          color="text-yellow-600"
        />
        <StatCard
          title="Risk Alerts"
          value={stats?.risk_alerts || 0}
          icon={ExclamationTriangleIcon}
          color="text-red-600"
        />
      </div>

      <div className="mt-8">
        <h2 className="text-lg font-medium text-gray-900 mb-4">Recent Documents</h2>
        <div className="bg-white shadow overflow-hidden sm:rounded-md">
          <ul className="divide-y divide-gray-200">
            {recentActivity?.recent_uploads?.map((doc) => (
              <li key={doc.id}>
                <Link to={`/documents/${doc.id}`} className="block hover:bg-gray-50">
                  <div className="px-4 py-4 sm:px-6">
                    <div className="flex items-center justify-between">
                      <div className="text-sm font-medium text-indigo-600 truncate">
                        {doc.title}
                      </div>
                      <div className="ml-2 flex-shrink-0 flex">
                        <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                          doc.analysis_status === 'completed' 
                            ? 'bg-green-100 text-green-800'
                            : 'bg-yellow-100 text-yellow-800'
                        }`}>
                          {doc.analysis_status}
                        </span>
                      </div>
                    </div>
                    <div className="mt-2 flex justify-between">
                      <div className="sm:flex">
                        <div className="text-sm text-gray-500">
                          Uploaded {new Date(doc.upload_date).toLocaleDateString()}
                        </div>
                      </div>
                    </div>
                  </div>
                </Link>
              </li>
            ))}
          </ul>
        </div>
      </div>

      {recentActivity?.high_risk_documents?.length > 0 && (
        <div className="mt-8">
          <h2 className="text-lg font-medium text-gray-900 mb-4">High Risk Documents</h2>
          <div className="bg-white shadow overflow-hidden sm:rounded-md">
            <ul className="divide-y divide-gray-200">
              {recentActivity.high_risk_documents.map((doc) => (
                <li key={doc.id}>
                  <Link to={`/documents/${doc.id}`} className="block hover:bg-gray-50">
                    <div className="px-4 py-4 sm:px-6">
                      <div className="flex items-center justify-between">
                        <div className="text-sm font-medium text-red-600 truncate">
                          {doc.title}
                        </div>
                        <div className="ml-2 flex-shrink-0 flex">
                          <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-red-100 text-red-800">
                            High Risk
                          </span>
                        </div>
                      </div>
                      <div className="mt-2">
                        <div className="text-sm text-gray-500">
                          {doc.risk_factors.length} high risk factors identified
                        </div>
                      </div>
                    </div>
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}
    </div>
  );
};

export default Dashboard; 