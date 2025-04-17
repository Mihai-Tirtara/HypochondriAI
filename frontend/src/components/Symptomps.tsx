import React, { useState } from 'react';
import { analyzeSymptoms, SymptomResponse } from '../services/api';

const SymptomForm: React.FC = () => {
  const [symptoms, setSymptoms] = useState('');
  const [userContext, setUserContext] = useState('');
  const [response, setResponse] = useState<SymptomResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!symptoms.trim()) {
      setError('Please describe your symptoms');
      return;
    }
    
    setLoading(true);
    setError(null);
    
    try {
      const result = await analyzeSymptoms({
        symptoms,
        userContext: userContext || undefined
      });
      
      setResponse(result);
    } catch (err) {
      console.error('Error:', err);
      setError('Failed to analyze symptoms. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-100">
      <div className="max-w-2xl mx-auto p-6 bg-white rounded-lg shadow-md">
        <h2 className="text-2xl font-bold mb-6 text-gray-800">What cancer you have today ?</h2>
        
        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label htmlFor="symptoms" className="block text-sm font-medium text-gray-700 mb-1">
              What symptoms are you experiencing?
            </label>
            <textarea
              id="symptoms"
              className="w-full p-3 border border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500"
              rows={4}
              value={symptoms}
              onChange={(e) => setSymptoms(e.target.value)}
              placeholder="Describe your symptoms in detail..."
              required
            />
          </div>
          
          <div className="mb-6">
            <label htmlFor="context" className="block text-sm font-medium text-gray-700 mb-1">
              Any additional context? (optional)
            </label>
            <textarea
              id="context"
              className="w-full p-3 border border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500"
              rows={2}
              value={userContext}
              onChange={(e) => setUserContext(e.target.value)}
              placeholder="E.g., recent stress, changes in lifestyle, etc."
            />
          </div>
          
          <button
            type="submit"
            className="w-full bg-primary-600 text-white py-2 px-4 rounded-md hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-opacity-50 transition duration-150 disabled:opacity-50"
            disabled={loading}
          >
            {loading ? 'Analyzing...' : 'Analyze Symptoms'}
          </button>
        </form>
        
        {error && (
          <div className="mt-6 p-4 bg-red-50 text-red-800 rounded-md">
            <p className="font-medium">Error</p>
            <p>{error}</p>
          </div>
        )}
        
        {response && (
          <div className="mt-8 p-6 bg-blue-50 rounded-md">
            <h3 className="text-lg font-semibold mb-4 text-gray-800">Analysis</h3>
            
            <div className="prose max-w-none">
              <p className="text-gray-800 whitespace-pre-line">{response.response}</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default SymptomForm;