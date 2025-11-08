import React, { useState } from 'react';
import './Queries.css';
import { sendChatQuery } from '../api/client';
import { Send, Sparkles } from 'lucide-react';

function Queries() {
  const [messages, setMessages] = useState([
    {
      type: 'bot',
      text: "Hello! I'm PulseVo AI. Ask me anything about your team's tasks and performance.\n\nTry questions like:\n• How many tasks are currently 'In Progress'?\n• Show me all overdue high-priority tasks\n• What is the status of the 'Mobile App' project?",
      timestamp: new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage = {
      type: 'user',
      text: input,
      timestamp: new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await sendChatQuery(input);
      const botMessage = {
        type: 'bot',
        text: response.data.response,
        timestamp: response.data.timestamp
      };
      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      console.error('Error sending query:', error);
      const errorMessage = {
        type: 'bot',
        text: "Sorry, I'm having trouble processing that request. Please try again.",
        timestamp: new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="queries-page">
      <div className="chat-container">
        <div className="chat-header">
          <div className="header-icon">
            <Sparkles size={24} color="#10b981" />
          </div>
          <div className="header-content">
            <h2>Conversational Query Interface</h2>
            <p>Ask questions about your team's productivity in natural language</p>
          </div>
        </div>

        <div className="chat-messages">
          {messages.map((message, index) => (
            <div key={index} className={`message ${message.type}`}>
              <div className="message-content">
                <p>{message.text}</p>
                <span className="message-time">{message.timestamp}</span>
              </div>
            </div>
          ))}
          
          {loading && (
            <div className="message bot">
              <div className="message-content">
                <div className="typing-indicator">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            </div>
          )}
        </div>

        <div className="chat-input-container">
          <input
            type="text"
            className="chat-input"
            placeholder="Ask me anything about your team's productivity..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
          />
          <button className="send-button" onClick={handleSend} disabled={!input.trim() || loading}>
            <Send size={20} />
            <span>Send</span>
          </button>
        </div>
      </div>
    </div>
  );
}

export default Queries;

