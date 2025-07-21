import React, { useState, useEffect, useRef } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { ConversationPublic, MessagePublic } from '../client/types.gen';
import { continueConversationV1ConversationsPost } from '../client/sdk.gen';

interface ConversationProps {
  initialConversation?: ConversationPublic;
}

const Conversation: React.FC<ConversationProps> = ({ initialConversation }) => {
  const location = useLocation();
  const navigate = useNavigate();
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  const [messages, setMessages] = useState<MessagePublic[]>([]);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [newMessage, setNewMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isTyping, setIsTyping] = useState(false);

  // Initialize conversation from location state or prop
  useEffect(() => {
    const conversation = location.state?.conversation || initialConversation;
    if (conversation?.messages) {
      setMessages(conversation.messages);
      setConversationId(conversation.id);
    }
  }, [location.state, initialConversation]);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const formatTime = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString([], { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newMessage.trim() || !conversationId) return;

    const userMessage: MessagePublic = {
      id: Date.now().toString(),
      content: newMessage,
      role: 'user',
      created_at: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setNewMessage('');
    setIsLoading(true);
    setIsTyping(true);

    try {
      const result = await continueConversationV1ConversationsPost({
        query: { conversation_id: conversationId },
        body: {
          content: newMessage,
          role: 'user'
        }
      });

      if (result.data?.messages) {
        // Update messages with the full conversation response
        setMessages(result.data.messages);
      }
    } catch (error) {
      console.error('Error sending message:', error);
      // Remove the user message on error
      setMessages(prev => prev.slice(0, -1));
    } finally {
      setIsLoading(false);
      setIsTyping(false);
    }
  };

  const handleBackToMain = () => {
    navigate('/');
  };

  return (
    <div className="h-screen flex flex-col bg-gradient-to-b from-purple-50 to-purple-100">
    {/* Header */}
    <div className="bg-gradient-to-r from-pink-400 to-purple-500 text-white py-4 shadow-lg">
      <div className="relative flex items-center justify-between w-full">
        {/* Left item: Back button */}
        <button
          onClick={handleBackToMain}
          className="flex items-left text-white hover:text-gray-200 transition-colors z-10 pl-4"
        >
          <svg className="w-5 h-5 mr-1 sm:w-6 sm:h-6 sm:mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
          <span className="text-sm sm:text-base">Back</span>
        </button>

        {/* Absolutely Centered Item: Health Assistant title and icon */}
        {/* This block is absolutely positioned to ensure it's truly centered */}
        <div className="absolute left-1/2 transform -translate-x-1/2 flex items-center">
          <div className="w-8 h-8 bg-white bg-opacity-20 rounded-full flex items-center justify-center mr-3 hidden sm:flex">
            <span className="text-lg">🤖</span>
          </div>
          <div className="text-center sm:text-left">
            <h1 className="text-base sm:text-lg font-semibold">Health Assistant</h1>
            <p className="text-xs sm:text-sm text-purple-100 hidden sm:block">Here to help with your health concerns</p>
          </div>
        </div>

        {/* Right spacer to balance flex layout */}
        <div className="flex items-center text-white opacity-0 pointer-events-none pr-4">
          <svg className="w-5 h-5 mr-1 sm:w-6 sm:h-6 sm:mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
          <span className="text-sm sm:text-base">Back</span>
        </div>

      </div>
      </div>

      {/* Messages Container */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 max-w-4xl mx-auto w-full">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-xs sm:max-w-md lg:max-w-lg xl:max-w-xl rounded-2xl p-4 ${
                message.role === 'user'
                  ? 'bg-gradient-to-r from-purple-500 to-purple-600 text-white rounded-br-sm'
                  : 'bg-white border border-gray-200 text-gray-800 rounded-bl-sm shadow-sm'
              }`}
            >
              <p className="text-sm sm:text-base leading-relaxed">{message.content}</p>
              <div className={`text-xs mt-2 ${
                message.role === 'user' ? 'text-purple-100' : 'text-gray-500'
              }`}>
                {message.created_at && formatTime(message.created_at)}
              </div>
            </div>
          </div>
        ))}

        {/* Typing Indicator */}
        {isTyping && (
          <div className="flex justify-start">
            <div className="bg-white border border-gray-200 text-gray-800 rounded-2xl rounded-bl-sm shadow-sm p-4 max-w-xs">
              <div className="flex space-x-1">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
              </div>
              <div className="text-xs text-gray-500 mt-2">typing...</div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Message Input */}
      <div className="bg-white border-t border-gray-200 p-4">
        <div className="max-w-4xl mx-auto">
          <form onSubmit={handleSendMessage} className="flex items-center space-x-3">
            <div className="flex-1 relative">
              <input
                type="text"
                value={newMessage}
                onChange={(e) => setNewMessage(e.target.value)}
                placeholder="Type your message..."
                className="w-full px-4 py-3 bg-gray-50 border border-gray-300 rounded-full focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all duration-200"
                disabled={isLoading}
              />
            </div>
            <button
              type="submit"
              disabled={!newMessage.trim() || isLoading}
              className="bg-gradient-to-r from-pink-400 to-purple-500 text-white p-3 rounded-full hover:from-pink-500 hover:to-purple-600 focus:outline-none focus:ring-4 focus:ring-purple-200 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg"
            >
              {isLoading ? (
                <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-white"></div>
              ) : (
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                </svg>
              )}
            </button>
          </form>
        </div>
      </div>

      {/* Disclaimer Footer */}
      <div className="bg-teal-50 border-t border-teal-200 p-3">
        <div className="max-w-4xl mx-auto text-center">
          <p className="text-teal-700 text-xs sm:text-sm">
            =� Remember: This is not a substitute for professional medical advice. Always consult healthcare providers for serious concerns.
          </p>
        </div>
      </div>
    </div>
  );
};

export default Conversation;