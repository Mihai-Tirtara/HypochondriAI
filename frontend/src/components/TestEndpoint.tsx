import React, { useState } from 'react';
import { startConversationTestNewPost } from '../client/sdk.gen';
import { MessageRole, ConversationPublic } from '../client/types.gen';

const TestEndpoint: React.FC = () => {
  const [message, setMessage] = useState('');
  const [response, setResponse] = useState<ConversationPublic | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!message.trim()) {
      setError('Please enter a message');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // This directly tests the router_test.post("/new") endpoint
      const result = await startConversationTestNewPost({
        body: {
          content: message,
          role: 'user'
        }
      });

      setResponse(result.data ?? null);
      console.log('Server response:', result.data);
    } catch (err) {
      console.error('Error:', err);
      setError('Failed to test endpoint. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto p-6 bg-white rounded-lg shadow-md">
      <h2 className="text-2xl font-bold mb-6">Test /test/new Endpoint</h2>

      <form onSubmit={handleSubmit}>
        <div className="mb-4">
          <label htmlFor="message" className="block text-sm font-medium text-gray-700 mb-1">
            Message to send
          </label>
          <textarea
            id="message"
            className="w-full p-3 border border-gray-300 rounded-md"
            rows={3}
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="Enter your message..."
            required
          />
        </div>

        <button
          type="submit"
          className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:opacity-50"
          disabled={loading}
        >
          {loading ? 'Sending...' : 'Send Test Request'}
        </button>
      </form>

      {error && (
        <div className="mt-4 p-3 bg-red-50 text-red-800 rounded-md">
          <p>{error}</p>
        </div>
      )}

      {response && (
        <div className="mt-6">
          <h3 className="text-lg font-semibold mb-2">Response:</h3>
          <div className="p-4 bg-gray-50 rounded-md overflow-auto">
            <pre className="text-sm whitespace-pre-wrap">{JSON.stringify(response, null, 2)}</pre>
          </div>

          {response.messages && response.messages.length > 0 && (
            <div className="mt-4">
              <h4 className="font-medium mb-2">Messages:</h4>
              <div className="space-y-3">
                {response.messages.map((msg) => (
                  <div
                    key={msg.id}
                    className={`p-3 rounded-md ${msg.role === 'user' ? 'bg-blue-50' : 'bg-green-50'}`}
                  >
                    <p className="text-xs text-gray-500 mb-1">{msg.role}</p>
                    <p>{msg.content}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default TestEndpoint;
