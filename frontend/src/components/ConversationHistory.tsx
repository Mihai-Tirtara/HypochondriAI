import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getConversationsV1ConversationsGet } from '../client/sdk.gen';
import { ConversationPublic } from '../client/types.gen';

interface ConversationHistoryProps {
  isCollapsed: boolean;
  onToggle: () => void;
  userId: string;
}

const ConversationHistory: React.FC<ConversationHistoryProps> = ({ isCollapsed, onToggle, userId }) => {
  const navigate = useNavigate();
  const [conversations, setConversations] = useState<ConversationPublic[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (userId) {
      fetchConversations();
    }
  }, [userId]);

  const fetchConversations = async () => {
    setLoading(true);
    setError(null);

    try {
      const result = await getConversationsV1ConversationsGet({
        query: { user_id: userId }
      });

      if (result.data) {
        setConversations(result.data);
      }
    } catch (err) {
      console.error('Error fetching conversations:', err);
      setError('Failed to load conversation history');
    } finally {
      setLoading(false);
    }
  };

  const handleConversationClick = (conversation: ConversationPublic) => {
    navigate('/conversation', {
      state: { conversation }
    });
  };

  const getConversationDisplayText = (conversation: ConversationPublic) => {
    if (conversation.title) {
      return conversation.title;
    }

    if (conversation.messages && conversation.messages.length > 0) {
      const firstUserMessage = conversation.messages.find(m => m.role === 'user');
      if (firstUserMessage) {
        return firstUserMessage.content.length > 40
          ? firstUserMessage.content.substring(0, 40) + '...'
          : firstUserMessage.content;
      }
    }

    return 'New Conversation';
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const today = new Date();
    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);

    if (date.toDateString() === today.toDateString()) {
      return 'Today';
    } else if (date.toDateString() === yesterday.toDateString()) {
      return 'Yesterday';
    } else {
      return date.toLocaleDateString();
    }
  };

  return (
    <div className={`h-full bg-gray-50 border-r border-gray-200 ${
      isCollapsed ? 'w-16' : 'w-80'
    } ${isCollapsed ? 'md:w-16' : 'md:w-80'} ${isCollapsed ? 'hidden md:block' : 'block'}`}>
      {/* Header */}
      <div className={`border-b border-gray-200 bg-white ${isCollapsed ? 'p-2' : 'p-4'}`}>
        <button
          onClick={onToggle}
          className={`w-full flex items-center text-left bg-pink-500 text-white rounded-lg hover:bg-pink-600 ${
            isCollapsed
              ? 'justify-center p-3 aspect-square'
              : 'justify-between px-4 py-2'
          }`}
        >
          <span className="font-medium">
            {isCollapsed ? '☰' : '☰ Collapse Menu'}
          </span>
        </button>
      </div>

      {/* Content */}
      {!isCollapsed && (
        <div className="p-4">
          <h2 className="text-lg font-semibold text-gray-800 mb-4">
            Conversation History
          </h2>

          {loading && (
            <div className="flex items-center justify-center py-8">
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-pink-500"></div>
              <span className="ml-2 text-gray-600">Loading...</span>
            </div>
          )}

          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-3 mb-4">
              <p className="text-red-800 text-sm">{error}</p>
              <button
                onClick={fetchConversations}
                className="mt-2 text-red-600 hover:text-red-800 text-sm underline"
              >
                Try again
              </button>
            </div>
          )}

          {!loading && !error && conversations.length === 0 && (
            <div className="text-center py-8 text-gray-500">
              <div className="text-4xl mb-2">💬</div>
              <p className="text-sm">No conversations yet</p>
              <p className="text-xs mt-1">Start a new conversation to see history</p>
            </div>
          )}

          {!loading && !error && conversations.length > 0 && (
            <div className="space-y-2">
              {conversations.map((conversation) => (
                <button
                  key={conversation.id}
                  onClick={() => handleConversationClick(conversation)}
                  className="w-full text-left p-3 bg-white rounded-lg border border-gray-200 hover:border-pink-300 hover:bg-pink-50 group"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-900 truncate group-hover:text-pink-700">
                        {getConversationDisplayText(conversation)}
                      </p>
                      <p className="text-xs text-gray-500 mt-1">
                        {formatDate(conversation.created_at)}
                      </p>
                    </div>
                    <div className="ml-2 opacity-0 group-hover:opacity-100">
                      <span className="text-pink-500 text-sm">→</span>
                    </div>
                  </div>
                </button>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default ConversationHistory;
