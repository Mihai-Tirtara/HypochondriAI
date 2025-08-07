import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getUserByNameV1NameGet, startConversationV1NewPost } from '../client/sdk.gen';
import ConversationHistory from './ConversationHistory';

const Home: React.FC = () => {
  const navigate = useNavigate();
  const [symptoms, setSymptoms] = useState('');
  const [additionalDetails, setAdditionalDetails] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isHistoryCollapsed, setIsHistoryCollapsed] = useState(false);
  const [userId, setUserId] = useState<string>('');

  // Fetch user ID on component mount
  // Using the predefine superuser "admin" for simplicity
  // This is a temporary solution until user authentication is implemented
  useEffect(() => {
    const fetchUserId = async () => {
      try {
        const result = await getUserByNameV1NameGet({
          query: { user_name: "admin" }
        });

        if (result.data) {
          setUserId(result.data.id);
        }
      } catch (err) {
        console.error('Error', err);
        setError('Failed to find user');
      }
    };

    fetchUserId();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!symptoms.trim()) {
      setError('Please enter your symptoms');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // Combine symptoms and additional details into a single message
      const message = additionalDetails.trim()
        ? `${symptoms}\n\nAdditional details: ${additionalDetails}`
        : symptoms;

      const result = await startConversationV1NewPost({
        body: {
          content: message,
          role: 'user'
        },
        query: {
          user_id: userId
        }
      });

      // Navigate to conversation page with the response data
      navigate('/conversation', {
        state: { conversation: result.data }
      });
    } catch (err) {
      console.error('Error:', err);
      setError('Failed to start conversation. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex h-screen bg-white">
      {/* Conversation History Sidebar */}
      <ConversationHistory
        isCollapsed={isHistoryCollapsed}
        onToggle={() => setIsHistoryCollapsed(!isHistoryCollapsed)}
        userId={userId}
      />

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Mobile Menu Toggle */}
        <div className="md:hidden p-4 bg-white border-b border-gray-200">
          <button
            onClick={() => setIsHistoryCollapsed(!isHistoryCollapsed)}
            className="bg-pink-500 text-white px-4 py-2 rounded-lg hover:bg-pink-600 transition-colors"
          >
            {isHistoryCollapsed ? '☰ Show History' : '✕ Hide History'}
          </button>
        </div>

        {/* Scrollable Content Area */}
        <div className="flex-1 overflow-y-auto flex items-center justify-center p-4 md:p-6 lg:p-8">
          <div className="w-full max-w-2xl">
      {/* Header Section */}
      <div className="text-center mb-6 sm:mb-8">
        <div className="inline-flex items-center justify-center w-12 h-12 sm:w-16 sm:h-16 bg-purple-100 rounded-full mb-4">
          <span className="text-xl sm:text-2xl">💭</span>
        </div>
        <h1 className="text-2xl sm:text-3xl lg:text-4xl font-bold text-gray-800 mb-2">
          What cancer you have today ?
        </h1>
        <p className="text-gray-600 text-sm sm:text-base lg:text-lg">
          I'm here to help you understand your symptoms
        </p>
      </div>

      {/* Main Card Container */}
      <div className="bg-white rounded-2xl sm:rounded-3xl shadow-lg border border-gray-200 p-6 sm:p-8">
        {/* Step Indicator */}
        <div className="bg-gray-50 rounded-xl sm:rounded-2xl p-3 sm:p-4 mb-6 flex items-center">
          <div className="w-3 h-3 sm:w-4 sm:h-4 bg-red-500 rounded-full mr-3"></div>
          <span className="font-semibold text-gray-800 text-sm sm:text-base">
            Step 1: Tell me your symptoms
          </span>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Symptoms Input */}
          <div>
            <label htmlFor="symptoms" className="block text-gray-800 font-semibold mb-3 flex items-center text-sm sm:text-base">
              <span className="mr-2 text-lg">🩺</span>
              What symptoms are you experiencing?
            </label>
            <div className="relative">
              <textarea
                id="symptoms"
                value={symptoms}
                onChange={(e) => setSymptoms(e.target.value)}
                className="w-full h-20 sm:h-24 px-4 py-3 bg-gray-50 border border-gray-300 rounded-xl resize-none focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all duration-200 text-sm sm:text-base"
                placeholder="Type your symptoms here..."
                required
              />
              {!symptoms && (
                <div className="absolute left-4 bottom-2 text-xs sm:text-sm text-gray-400">
                  e.g., "I have a persistent headache and feel dizzy"
                </div>
              )}
            </div>
          </div>

          {/* Additional Details Input */}
          <div>
            <label htmlFor="additionalDetails" className="block text-gray-800 font-semibold mb-3 flex items-center text-sm sm:text-base">
              <span className="mr-2 text-lg">📋</span>
              Additional details (optional)
            </label>
            <div className="relative">
              <textarea
                id="additionalDetails"
                value={additionalDetails}
                onChange={(e) => setAdditionalDetails(e.target.value)}
                className="w-full h-24 sm:h-28 px-4 py-3 bg-gray-50 border border-gray-300 rounded-xl resize-none focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all duration-200 text-sm sm:text-base"
                placeholder="When did it start? How severe is it?"
              />
              {!additionalDetails && (
                <div className="absolute left-4 bottom-2 text-xs sm:text-sm text-gray-400">
                  Any other details that might be helpful...
                </div>
              )}
            </div>
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={!symptoms.trim() || loading}
            className="w-full bg-gradient-to-r from-pink-400 to-purple-500 text-white font-semibold py-4 px-6 rounded-3xl hover:from-pink-500 hover:to-purple-600 focus:outline-none focus:ring-4 focus:ring-purple-200 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg text-sm sm:text-base min-h-[44px] sm:min-h-[48px]"
          >
            {loading ? (
              <div className="flex items-center justify-center">
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                Analyzing...
              </div>
            ) : (
              <div className="flex items-center justify-center">
                <span className="mr-2">Start Conversation</span>
                <span className="text-lg">💬</span>
              </div>
            )}
          </button>
        </form>

        {/* Error Display */}
        {error && (
          <div className="mt-6 p-4 bg-red-50 border border-red-200 rounded-xl">
            <div className="flex items-center">
              <span className="text-red-500 mr-2">❌</span>
              <p className="text-red-800 font-medium text-sm sm:text-base">{error}</p>
            </div>
          </div>
        )}

        {/* Privacy Notice */}
        <div className="mt-6 bg-teal-50 border border-teal-200 rounded-xl p-4">
          <div className="text-center">
            <p className="text-teal-700 text-xs sm:text-sm">
              This is not a substitute for professional medical advice
            </p>
          </div>
        </div>
      </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Home;
