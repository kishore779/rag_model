import React, { useState, useRef, useEffect } from "react";
import axios from "axios";
import "./index.css";

function App() {
  const [messages, setMessages] = useState([
    {
      type: "ai",
      text: "Hello! I'm your company policy assistant. Ask me anything about our internal policies and documents.",
      sources: [],
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    // Add user message
    const userMessage = {
      type: "user",
      text: input,
      sources: [],
    };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setLoading(true);

    try {
      // Call backend API
      const response = await axios.post("http://localhost:8000/api/chat", {
        question: input,
      });

      // Add AI response
      const aiMessage = {
        type: "ai",
        text: response.data.answer,
        sources: response.data.sources || [],
      };
      setMessages((prev) => [...prev, aiMessage]);
    } catch (error) {
      console.error("Error:", error);
      const errorMessage = {
        type: "ai",
        text: "Sorry, I encountered an error. Please try again or check that the backend is running.",
        sources: [],
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <div className="w-64 bg-gradient-to-b from-blue-600 to-blue-800 text-white p-6 flex flex-col">
        <h1 className="text-2xl font-bold mb-8">RAG Chatbot</h1>
        <p className="text-blue-100 text-sm">
          Ask questions about company policies and internal documents.
        </p>
      </div>

      {/* Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {messages.map((msg, idx) => (
            <div
              key={idx}
              className={`flex ${msg.type === "user" ? "justify-end" : "justify-start"}`}
            >
              <div
                className={`max-w-xl ${
                  msg.type === "user"
                    ? "bg-blue-600 text-white rounded-lg rounded-tr-none"
                    : "bg-white text-gray-800 rounded-lg rounded-tl-none border border-gray-200"
                } p-4`}
              >
                <p className="text-sm">{msg.text}</p>

                {/* Sources */}
                {msg.sources && msg.sources.length > 0 && (
                  <div className="mt-3 pt-3 border-t border-opacity-20 border-current">
                    <p
                      className={`text-xs font-semibold mb-2 ${
                        msg.type === "user" ? "text-blue-100" : "text-gray-600"
                      }`}
                    >
                      Sources:
                    </p>
                    <div className="flex flex-wrap gap-2">
                      {msg.sources.map((source, sidx) => (
                        <span
                          key={sidx}
                          className={`text-xs px-2 py-1 rounded ${
                            msg.type === "user"
                              ? "bg-blue-500 text-white"
                              : "bg-blue-100 text-blue-800"
                          }`}
                        >
                          {source}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          ))}

          {/* Loading Indicator */}
          {loading && (
            <div className="flex justify-start">
              <div className="bg-white text-gray-800 rounded-lg rounded-tl-none p-4 border border-gray-200">
                <div className="flex space-x-2">
                  <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce delay-100"></div>
                  <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce delay-200"></div>
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="border-t border-gray-200 bg-white p-6">
          <form onSubmit={handleSendMessage} className="flex gap-3">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask a question..."
              disabled={loading}
              className="flex-1 border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:border-blue-600 focus:ring-2 focus:ring-blue-100 disabled:bg-gray-100"
            />
            <button
              type="submit"
              disabled={loading || !input.trim()}
              className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 disabled:bg-gray-400 transition-colors font-medium"
            >
              Send
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}

export default App;
