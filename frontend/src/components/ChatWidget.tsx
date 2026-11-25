import React, { useState, useEffect } from 'react';
import { Send, Sparkles, Bot, User, Loader2, Compass } from 'lucide-react';
import { ChatMessage, Itinerary } from '../types';
import { tripService } from '../services/api';

interface ChatWidgetProps {
  tripId: number;
  destination: string;
  onItineraryUpdated?: (itinerary: Itinerary) => void;
}

export const ChatWidget: React.FC<ChatWidgetProps> = ({ tripId, destination, onItineraryUpdated }) => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);

  useEffect(() => {
    setMessages([
      {
        role: 'assistant',
        content: `Hey there! I'm TravelPilot 🧭. Ready to plan your ${destination} trip? Let me know what you'd like to check out today!`
      }
    ]);
  }, [destination]);

  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [streamingText, setStreamingText] = useState<string>('');

  const sampleQuestions = [
    'Hi',
    'Top 5 Dishes in ' + destination,
    'Flight & Visa for ' + destination,
    'Hotels & Stays in ' + destination,
    'Reduce budget by 20%'
  ];

  const handleSend = async (textToSend?: string) => {
    const messageText = textToSend || input;
    if (!messageText.trim() || loading) return;

    const userMsg: ChatMessage = { role: 'user', content: messageText };
    setMessages((prev) => [...prev, userMsg]);
    setInput('');
    setLoading(true);
    setStreamingText('');

    try {
      const res = await tripService.sendChat(tripId, messageText);
      const fullReply = res.reply;

      // Fast Line-by-Line / Sentence Chunking Streaming Effect
      const sentences = fullReply.match(/[^.!?\n]+[.!?\n]+/g) || [fullReply];
      let accumulated = '';

      for (let i = 0; i < sentences.length; i++) {
        accumulated += sentences[i];
        setStreamingText(accumulated);
        await new Promise((resolve) => setTimeout(resolve, 10));
      }

      setMessages((prev) => [...prev, { role: 'assistant', content: fullReply }]);
      setStreamingText('');

      if (res.updated_itinerary && onItineraryUpdated) {
        onItineraryUpdated(res.updated_itinerary);
      }
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: "Sorry, I had trouble connecting. Let's try again!" }
      ]);
    } finally {
      setLoading(false);
      setStreamingText('');
    }
  };

  return (
    <div className="flex flex-col h-[650px] rounded-3xl bg-white border border-slate-200 shadow-lg overflow-hidden font-sans">
      {/* Mindtrip Header */}
      <div className="px-6 py-4 bg-slate-50 border-b border-slate-200 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-cyan-600 flex items-center justify-center text-white shadow-xs">
            <Compass className="w-5 h-5 text-white" />
          </div>
          <div>
            <h3 className="font-bold text-sm text-slate-900">Mindtrip AI Assistant</h3>
            <span className="text-xs text-cyan-700 font-semibold flex items-center gap-1">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
              Casual Human Chat • {destination}
            </span>
          </div>
        </div>
      </div>

      {/* Message List */}
      <div className="flex-1 p-6 overflow-y-auto space-y-4 bg-slate-50/40">
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`flex items-start gap-3 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            {msg.role === 'assistant' && (
              <div className="w-8 h-8 rounded-xl bg-cyan-100 border border-cyan-200 flex items-center justify-center text-cyan-700 shrink-0 shadow-2xs">
                <Bot className="w-4 h-4" />
              </div>
            )}

            <div
              className={`max-w-lg p-4 rounded-2xl text-sm leading-relaxed ${
                msg.role === 'user'
                  ? 'bg-cyan-600 text-white font-medium rounded-tr-none shadow-xs'
                  : 'bg-white border border-slate-200 text-slate-900 rounded-tl-none shadow-2xs whitespace-pre-wrap'
              }`}
            >
              {msg.content}
            </div>

            {msg.role === 'user' && (
              <div className="w-8 h-8 rounded-xl bg-slate-200 border border-slate-300 flex items-center justify-center text-slate-700 shrink-0">
                <User className="w-4 h-4" />
              </div>
            )}
          </div>
        ))}

        {/* Streaming Response Indicator */}
        {loading && (
          <div className="flex items-start gap-3 justify-start">
            <div className="w-8 h-8 rounded-xl bg-cyan-100 border border-cyan-200 flex items-center justify-center text-cyan-700 shrink-0">
              <Bot className="w-4 h-4" />
            </div>

            {streamingText ? (
              <div className="max-w-lg p-4 rounded-2xl text-sm leading-relaxed bg-white border border-slate-200 text-slate-900 rounded-tl-none shadow-2xs whitespace-pre-wrap animate-pulse">
                {streamingText}
              </div>
            ) : (
              <div className="px-4 py-3 rounded-2xl bg-white border border-slate-200 text-slate-500 text-xs flex items-center gap-2 shadow-2xs">
                <Loader2 className="w-4 h-4 animate-spin text-cyan-600" />
                <span>Typing...</span>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Predefined Quick Action Chips */}
      <div className="px-6 py-2.5 bg-slate-100/80 border-t border-slate-200 flex items-center gap-2 overflow-x-auto no-scrollbar">
        {sampleQuestions.map((q, idx) => (
          <button
            key={idx}
            onClick={() => handleSend(q)}
            disabled={loading}
            className="px-3.5 py-1.5 rounded-full bg-white hover:bg-slate-50 text-slate-700 font-bold text-xs whitespace-nowrap border border-slate-200 transition-colors shrink-0 shadow-2xs"
          >
            {q}
          </button>
        ))}
      </div>

      {/* Input Box */}
      <div className="p-4 bg-white border-t border-slate-200 flex items-center gap-3">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSend()}
          placeholder={`Message your assistant...`}
          className="flex-1 bg-slate-50 border border-slate-200 rounded-xl px-4 py-2.5 text-sm text-slate-900 placeholder-slate-400 focus:outline-none focus:border-cyan-600 transition-colors font-medium"
        />

        <button
          onClick={() => handleSend()}
          disabled={loading || !input.trim()}
          className="p-2.5 rounded-xl bg-cyan-600 hover:bg-cyan-700 text-white font-bold disabled:opacity-40 transition-all shadow-xs"
        >
          <Send className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
};
