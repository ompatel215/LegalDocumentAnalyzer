import React from 'react';
import { useParams } from 'react-router-dom';
import { useQuery } from 'react-query';
import axios from 'axios';
import {
  DocumentTextIcon,
  ExclamationTriangleIcon,
  ClipboardDocumentListIcon,
  TagIcon,
} from '@heroicons/react/24/outline';

interface DocumentAnalysis {
  id: string;
  title: string;
  content: string;
  summary: string;
  key_clauses: Array<{
    type: string;
    content: string;
    confidence: number;
  }>;
  risk_factors: Array<{
    type: string;
    description: string;
    severity: 'low' | 'medium' | 'high';
    pattern_matched: string;
  }>;
  entities: {
    organizations: string[];
    people: string[];
    dates: string[];
    money: string[];
    locations: string[];
  };
  metadata: {
    file_type: string;
    upload_date: string;
    last_modified: string;
    analysis_status: string;
  };
}

const DocumentAnalysis: React.FC = () => {
  const { documentId } = useParams<{ documentId: string }>();
  const { data: analysis, isLoading } = useQuery<DocumentAnalysis>(
    ['documentAnalysis', documentId],
    () => axios.get(`/api/v1/documents/${documentId}/analysis`).then((res) => res.data)
  );

  const getSeverityColor = (severity: 'low' | 'medium' | 'high') => {
    const colors = {
      low: 'bg-green-100 text-green-800',
      medium: 'bg-yellow-100 text-yellow-800',
      high: 'bg-red-100 text-red-800',
    };
    return colors[severity];
  };

  if (isLoading || !analysis) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900"></div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
      {/* Document Header */}
      <div className="md:flex md:items-center md:justify-between mb-8">
        <div className="flex-1 min-w-0">
          <h2 className="text-2xl font-bold leading-7 text-gray-900 sm:text-3xl sm:truncate">
            {analysis.title}
          </h2>
          <div className="mt-1 flex flex-col sm:flex-row sm:flex-wrap sm:mt-0 sm:space-x-6">
            <div className="mt-2 flex items-center text-sm text-gray-500">
              <DocumentTextIcon className="flex-shrink-0 mr-1.5 h-5 w-5 text-gray-400" />
              {analysis.metadata.file_type.toUpperCase()}
            </div>
            <div className="mt-2 flex items-center text-sm text-gray-500">
              <ClipboardDocumentListIcon className="flex-shrink-0 mr-1.5 h-5 w-5 text-gray-400" />
              Last modified: {new Date(analysis.metadata.last_modified).toLocaleDateString()}
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Summary Section */}
        <div className="bg-white shadow rounded-lg p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Summary</h3>
          <p className="text-gray-600">{analysis.summary}</p>
        </div>

        {/* Key Entities */}
        <div className="bg-white shadow rounded-lg p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Key Entities</h3>
          <div className="space-y-4">
            {Object.entries(analysis.entities).map(([type, entities]) => (
              entities.length > 0 && (
                <div key={type}>
                  <h4 className="text-sm font-medium text-gray-700 capitalize mb-2">{type}</h4>
                  <div className="flex flex-wrap gap-2">
                    {entities.map((entity, index) => (
                      <span
                        key={index}
                        className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800"
                      >
                        {entity}
                      </span>
                    ))}
                  </div>
                </div>
              )
            ))}
          </div>
        </div>

        {/* Key Clauses */}
        <div className="bg-white shadow rounded-lg p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Key Clauses</h3>
          <div className="space-y-4">
            {analysis.key_clauses.map((clause, index) => (
              <div key={index} className="border-l-4 border-blue-500 pl-4 py-2">
                <div className="flex items-center mb-2">
                  <TagIcon className="h-5 w-5 text-blue-500 mr-2" />
                  <span className="text-sm font-medium text-gray-700 capitalize">
                    {clause.type.replace('_', ' ')}
                  </span>
                  <span className="ml-2 text-xs text-gray-500">
                    {Math.round(clause.confidence * 100)}% confidence
                  </span>
                </div>
                <p className="text-gray-600 text-sm">{clause.content}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Risk Factors */}
        <div className="bg-white shadow rounded-lg p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Risk Factors</h3>
          <div className="space-y-4">
            {analysis.risk_factors.map((risk, index) => (
              <div key={index} className="border rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center">
                    <ExclamationTriangleIcon className="h-5 w-5 text-yellow-500 mr-2" />
                    <span className="text-sm font-medium text-gray-700 capitalize">
                      {risk.type.replace('_', ' ')}
                    </span>
                  </div>
                  <span
                    className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getSeverityColor(
                      risk.severity
                    )}`}
                  >
                    {risk.severity.toUpperCase()}
                  </span>
                </div>
                <p className="text-gray-600 text-sm">{risk.description}</p>
                <div className="mt-2">
                  <span className="text-xs text-gray-500">
                    Pattern matched: "{risk.pattern_matched}"
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default DocumentAnalysis; 