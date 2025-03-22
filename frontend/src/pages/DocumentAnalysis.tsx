import React from 'react';
import { useParams } from 'react-router-dom';
import { useQuery } from 'react-query';
import axios from 'axios';
import {
  DocumentTextIcon,
  ClockIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  ChartBarIcon,
  UserIcon,
  TagIcon,
  BookOpenIcon,
} from '@heroicons/react/24/outline';

interface Statistics {
  word_count: number;
  sentence_count: number;
  reading_level: number;
  reading_time: number;
}

interface Risk {
  category: string;
  severity: string;
  context: string;
}

interface Clause {
  type: string;
  text: string;
}

interface Sentiment {
  polarity: number;
  subjectivity: number;
}

interface DocumentAnalysis {
  statistics: Statistics;
  summary: string;
  entities: Record<string, string[]>;
  key_clauses: Clause[];
  risks: Risk[];
  sentiment: Sentiment;
}

interface DocumentResponse {
  id: string;
  title: string;
  file_type: string;
  size: number;
  upload_date: string;
  last_modified: string;
  status: string;
  analysis: DocumentAnalysis;
  tags: string[];
}

const DocumentAnalysis: React.FC = () => {
  const { documentId } = useParams<{ documentId: string }>();

  const { data: document, isLoading, error } = useQuery<DocumentResponse>(
    ['document', documentId],
    () => axios.get(`/api/v1/documents/${documentId}`).then((res) => res.data),
    {
      refetchInterval: (data) => 
        data?.status === 'processing' || data?.status === 'pending' ? 5000 : false,
    }
  );

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-red-500">Error loading document analysis</div>
      </div>
    );
  }

  if (!document) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-gray-500">Document not found</div>
      </div>
    );
  }

  const getSeverityColor = (severity: string) => {
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

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'completed':
        return 'text-green-600 bg-green-100';
      case 'processing':
        return 'text-yellow-600 bg-yellow-100';
      case 'failed':
        return 'text-red-600 bg-red-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
      {/* Document Header */}
      <div className="bg-white shadow rounded-lg p-6 mb-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <DocumentTextIcon className="h-8 w-8 text-gray-400" />
            <div className="ml-4">
              <h1 className="text-2xl font-bold text-gray-900">{document.title}</h1>
              <div className="mt-1 flex items-center space-x-4 text-sm text-gray-500">
                <span>{document.file_type.toUpperCase()}</span>
                <span>•</span>
                <span>{formatFileSize(document.size)}</span>
                <span>•</span>
                <span>
                  Uploaded on {new Date(document.upload_date).toLocaleDateString()}
                </span>
              </div>
            </div>
          </div>
          <div className={`px-3 py-1 rounded-full ${getStatusColor(document.status)}`}>
            {document.status}
          </div>
        </div>
      </div>

      {document.status === 'processing' || document.status === 'pending' ? (
        <div className="bg-white shadow rounded-lg p-8 text-center">
          <ClockIcon className="mx-auto h-12 w-12 text-yellow-400" />
          <h3 className="mt-2 text-lg font-medium text-gray-900">Analysis in Progress</h3>
          <p className="mt-1 text-sm text-gray-500">
            Please wait while we analyze your document. This may take a few minutes.
          </p>
          <div className="mt-6">
            <div className="relative">
              <div className="overflow-hidden h-2 mb-4 text-xs flex rounded bg-yellow-200">
                <div className="animate-pulse w-full h-full bg-yellow-500"></div>
              </div>
            </div>
          </div>
        </div>
      ) : document.status === 'failed' ? (
        <div className="bg-white shadow rounded-lg p-8 text-center">
          <ExclamationTriangleIcon className="mx-auto h-12 w-12 text-red-400" />
          <h3 className="mt-2 text-lg font-medium text-gray-900">Analysis Failed</h3>
          <p className="mt-1 text-sm text-gray-500">
            We encountered an error while analyzing your document. Please try uploading it again.
          </p>
        </div>
      ) : (
        <div className="space-y-6">
          {/* Document Statistics */}
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-lg font-medium text-gray-900 mb-4">Document Statistics</h2>
            <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
              <div className="bg-gray-50 rounded-lg p-4">
                <div className="flex items-center">
                  <DocumentTextIcon className="h-6 w-6 text-gray-400" />
                  <div className="ml-3">
                    <div className="text-sm font-medium text-gray-500">Word Count</div>
                    <div className="text-lg font-semibold text-gray-900">
                      {document.analysis.statistics.word_count.toLocaleString()}
                    </div>
                  </div>
                </div>
              </div>
              <div className="bg-gray-50 rounded-lg p-4">
                <div className="flex items-center">
                  <BookOpenIcon className="h-6 w-6 text-gray-400" />
                  <div className="ml-3">
                    <div className="text-sm font-medium text-gray-500">Reading Time</div>
                    <div className="text-lg font-semibold text-gray-900">
                      {Math.ceil(document.analysis.statistics.reading_time)} min
                    </div>
                  </div>
                </div>
              </div>
              <div className="bg-gray-50 rounded-lg p-4">
                <div className="flex items-center">
                  <ChartBarIcon className="h-6 w-6 text-gray-400" />
                  <div className="ml-3">
                    <div className="text-sm font-medium text-gray-500">Reading Level</div>
                    <div className="text-lg font-semibold text-gray-900">
                      Grade {Math.round(document.analysis.statistics.reading_level)}
                    </div>
                  </div>
                </div>
              </div>
              <div className="bg-gray-50 rounded-lg p-4">
                <div className="flex items-center">
                  <TagIcon className="h-6 w-6 text-gray-400" />
                  <div className="ml-3">
                    <div className="text-sm font-medium text-gray-500">Sentiment</div>
                    <div className="text-lg font-semibold text-gray-900">
                      {document.analysis.sentiment.polarity > 0 ? 'Positive' : 
                       document.analysis.sentiment.polarity < 0 ? 'Negative' : 'Neutral'}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Document Summary */}
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-lg font-medium text-gray-900 mb-4">Summary</h2>
            <p className="text-gray-600 whitespace-pre-line">{document.analysis.summary}</p>
          </div>

          {/* Key Clauses */}
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-lg font-medium text-gray-900 mb-4">Key Clauses</h2>
            <div className="space-y-4">
              {document.analysis.key_clauses.map((clause, index) => (
                <div key={index} className="bg-gray-50 rounded-lg p-4">
                  <div className="font-medium text-gray-900 mb-2">{clause.type}</div>
                  <div className="text-gray-600">{clause.text}</div>
                </div>
              ))}
            </div>
          </div>

          {/* Risks */}
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-lg font-medium text-gray-900 mb-4">Identified Risks</h2>
            <div className="space-y-4">
              {document.analysis.risks.map((risk, index) => (
                <div key={index} className="bg-gray-50 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <div className="font-medium text-gray-900">{risk.category}</div>
                    <div className={`px-2 py-1 rounded-full text-sm ${getSeverityColor(risk.severity)}`}>
                      {risk.severity}
                    </div>
                  </div>
                  <div className="text-gray-600">{risk.context}</div>
                </div>
              ))}
            </div>
          </div>

          {/* Named Entities */}
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-lg font-medium text-gray-900 mb-4">Named Entities</h2>
            <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
              {Object.entries(document.analysis.entities).map(([category, entities]) => (
                <div key={category} className="bg-gray-50 rounded-lg p-4">
                  <div className="font-medium text-gray-900 mb-2">{category}</div>
                  <ul className="space-y-1">
                    {entities.map((entity, index) => (
                      <li key={index} className="text-gray-600">{entity}</li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default DocumentAnalysis; 