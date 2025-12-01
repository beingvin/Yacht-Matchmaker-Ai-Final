'use client';

import React, { useState, useEffect, useRef } from 'react';
import { Send, Loader2, MessageCircle, ClipboardSignature } from 'lucide-react';

// --- PERSISTENT USER ID LOGIC (Fixed for stable session) ---
// This function ensures the same user_id is retrieved from localStorage for every chat,
// allowing the backend session service to maintain chat history.
const generateUUID = (): string => {
  if (typeof crypto !== 'undefined' && typeof crypto.randomUUID === 'function') {
    return crypto.randomUUID();
  }
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    const r = Math.random() * 16 | 0;
    const v = c === 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
};

console.log(generateUUID())

const getPersistentUserId = (): string => {
  if (typeof window === 'undefined') return 'default-server-user';
  let userId = localStorage.getItem('adk_chat_user_id');
  if (!userId) {
    userId = generateUUID(); 
    localStorage.setItem('adk_chat_user_id', userId);
  }
  return userId;
};

console.log(getPersistentUserId())
// ---------------------------------------------------------------------------------


interface Message {
  id: string;
  text: string;
  sender: 'user' | 'agent';
}

export default function YachtChatApp() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [userInput, setUserInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [userId, setUserId] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Initialize User ID and initial message on mount
  useEffect(() => {
    setUserId(getPersistentUserId());
    // Initial greeting message
    setMessages([{ id: generateUUID(), text: "Welcome to Yacht Matchmaker! To get started, please tell me your desired location, date, number of guests, and occasion.", sender: 'agent' }]);
  }, []);

  // Scroll to the bottom whenever messages update
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async (e?: React.FormEvent) => {
    e?.preventDefault();
    const trimmedInput = userInput.trim();
    if (!trimmedInput || isLoading || !userId) return;

    setIsLoading(true);
    setUserInput('');

    // Add user message immediately
    const userMessage: Message = { id: generateUUID(), text: trimmedInput, sender: 'user' };
    setMessages(prev => [...prev, userMessage]);

    // Add agent thinking indicator
    const thinkingId = generateUUID();
    setMessages(prev => [...prev, { id: thinkingId, text: 'Agent is thinking...', sender: 'agent' }]);

    try {
      // Step 1: Client calls the API route using the stable userId
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: userId, message: trimmedInput }),
      });

      if (!response.ok) {
        throw new Error('Network response was not ok');
      }

      const data = await response.json();
      console.log(data)
      const agentResponseText = data.response;

      // Step 2: Replace thinking indicator with actual agent response
      setMessages(prev => {
        const newMessages = prev.filter(msg => msg.id !== thinkingId);
        newMessages.push({ id: generateUUID(), text: agentResponseText, sender: 'agent' });
        return newMessages;
      });

    } catch (error) {
      console.error("Chat API Error:", error);
      // Remove thinking indicator and show error
      setMessages(prev => {
        const newMessages = prev.filter(msg => msg.id !== thinkingId);
        newMessages.push({ id: generateUUID(), text: "Sorry, I ran into an error. Please try again or check the server logs.", sender: 'agent' });
        return newMessages;
      });
    } finally {
      setIsLoading(false);
    }
  };

  const MessageBubble = ({ message }: { message: Message }) => (
    <div className={`flex w-full ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
      <div
        className={`max-w-[80%] rounded-xl px-4 py-3 shadow-md transition-all duration-300 ${
          message.sender === 'user'
            ? 'bg-blue-600 text-white rounded-br-none'
            : 'bg-gray-100 text-gray-800 rounded-tl-none'
        }`}
      >
        <p className="whitespace-pre-wrap">{message.text}</p>
      </div>
    </div>
  );

  return (
    <div className="flex h-screen bg-gray-50 antialiased">
      <div className="w-full flex flex-col max-w-4xl mx-auto shadow-2xl rounded-lg overflow-hidden my-4">
        
        {/* Header */}
        <header className="flex items-center justify-between p-4 bg-white border-b border-gray-200 shadow-sm">
          <div className="flex items-center">
            <MessageCircle className="w-6 h-6 text-blue-600 mr-3" />
            <h1 className="text-xl font-bold text-gray-800">Yacht Matchmaker AI</h1>
          </div>
          <div className="text-xs text-gray-500 hidden sm:block">
            User ID: <span className="font-mono">{userId.substring(0, 8)}...</span>
          </div>
        </header>

        {/* Message Window */}
        <main className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50">
          {messages.map((message) => (
            <MessageBubble key={message.id} message={message} />
          ))}
          <div ref={messagesEndRef} />
        </main>

        {/* Input Area */}
        <footer className="p-4 bg-white border-t border-gray-200">
          <form onSubmit={handleSend} className="flex space-x-3">
            <input
              type="text"
              value={userInput}
              onChange={(e) => setUserInput(e.target.value)}
              placeholder={isLoading ? "Waiting for response..." : "Ask me about your charter needs..."}
              className="flex-1 p-3  text-blue-900 border-gray-300 rounded-xl focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100"
              disabled={isLoading}
            />
            <button
              type="submit"
              className="bg-blue-600 text-white p-3 rounded-xl hover:bg-blue-700 transition duration-150 flex items-center justify-center disabled:bg-blue-300"
              disabled={isLoading || !userInput.trim()}
              aria-label="Send Message"
            >
              {isLoading ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : (
                <Send className="w-5 h-5" />
              )}
            </button>
          </form>
        </footer>
      </div>
    </div>
  );
}