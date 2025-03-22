import React from 'react';
import { useParams } from 'react-router-dom';
import { useQuery } from 'react-query';
import axios from 'axios';
import {
  DocumentTextIcon,
  CalendarIcon,
  UserIcon,
  ExclamationTriangleIcon,
  DocumentMagnifyingGlassIcon,
  DocumentCheckIcon
} from '@heroicons/react/24/outline';

const DocumentAnalysis = () => {
  const { documentId } = useParams();
  const { data: analysis, isLoading } = useQuery(['documentAnalysis', documentId], async () => {
    const token = localStorage.getItem('token');
    const response = await axios.get(`http://localhost:8000/api/v1/documents/${documentId}/analysis`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    return response.data;
  });

  const getSeverityColor = (severity) => {
    switch (severity.toLowerCase()) {
      case 'high':
        return 'text-red-600 bg-red-100';
      case 'medium':
        return 'text-yellow-600 bg-yellow-100';
      case 'low':
        return 'text-green-600 bg-green-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-full">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto">
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-semibold text-gray-900">{analysis.title}</h1>
          <span className={`px-3 py-1 rounded-full text-sm font-medium ${
            analysis.analysis_status === 'completed'
              ? 'bg-green-100 text-green-800'
              : 'bg-yellow-100 text-yellow-800'
          }`}>
            {analysis.analysis_status}
          </span>
        </div>
        <div className="mt-2 flex items-center text-sm text-gray-500">
          <DocumentTextIcon className="h-5 w-5 mr-2" />
          <span>{analysis.document_type}</span>
          <CalendarIcon className="h-5 w-5 ml-4 mr-2" />
          <span>Last modified {new Date(analysis.upload_date).toLocaleDateString()}</span>
        </div>
      </div>

      <div className="bg-white shadow overflow-hidden sm:rounded-lg">
        <div className="px-4 py-5 sm:px-6">
          <h2 className="text-lg font-medium text-gray-900">Document Summary</h2>
        </div>
        <div className="border-t border-gray-200 px-4 py-5 sm:px-6">
          <p className="text-gray-700">{analysis.summary}</p>
        </div>
      </div>

      <div className="mt-8 grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Key Entities */}
        <div className="bg-white shadow overflow-hidden sm:rounded-lg">
          <div className="px-4 py-5 sm:px-6">
            <h2 className="text-lg font-medium text-gray-900">Key Entities</h2>
          </div>
          <div className="border-t border-gray-200">
            <ul className="divide-y divide-gray-200">
              {analysis.entities?.map((entity, index) => (
                <li key={index} className="px-4 py-3">
                  <div className="flex items-center">
                    <UserIcon className="h-5 w-5 text-gray-400 mr-2" />
                    <div>
                      <p className="text-sm font-medium text-gray-900">{entity.text}</p>
                      <p className="text-sm text-gray-500">{entity.type}</p>
                    </div>
                  </div>
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Key Clauses */}
        <div className="bg-white shadow overflow-hidden sm:rounded-lg">
          <div className="px-4 py-5 sm:px-6">
            <h2 className="text-lg font-medium text-gray-900">Key Clauses</h2>
          </div>
          <div className="border-t border-gray-200">
            <ul className="divide-y divide-gray-200">
              {analysis.key_clauses?.map((clause, index) => (
                <li key={index} className="px-4 py-3">
                  <div className="flex items-start">
                    <DocumentMagnifyingGlassIcon className="h-5 w-5 text-gray-400 mr-2 mt-1" />
                    <div>
                      <p className="text-sm font-medium text-gray-900">{clause.type}</p>
                      <p className="text-sm text-gray-500 mt-1">{clause.content}</p>
                    </div>
                  </div>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>

      {/* Risk Factors */}
      {analysis.risk_factors?.length > 0 && (
        <div className="mt-8 bg-white shadow overflow-hidden sm:rounded-lg">
          <div className="px-4 py-5 sm:px-6">
            <h2 className="text-lg font-medium text-gray-900">Risk Factors</h2>
          </div>
          <div className="border-t border-gray-200">
            <ul className="divide-y divide-gray-200">
              {analysis.risk_factors.map((risk, index) => (
                <li key={index} className="px-4 py-3">
                  <div className="flex items-start">
                    <ExclamationTriangleIcon className="h-5 w-5 text-red-400 mr-2 mt-1" />
                    <div className="flex-1">
                      <div className="flex items-center justify-between">
                        <p className="text-sm font-medium text-gray-900">{risk.type}</p>
                        <span className={`px-2 py-1 text-xs font-medium rounded-full ${getSeverityColor(risk.severity)}`}>
                          {risk.severity}
                        </span>
                      </div>
                      <p className="text-sm text-gray-500 mt-1">{risk.description}</p>
                    </div>
                  </div>
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}
    </div>
  );
};

export default DocumentAnalysis; 