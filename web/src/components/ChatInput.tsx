'use client';

import { useState, useRef, KeyboardEvent } from 'react';
import { PaperAirplaneIcon } from '@heroicons/react/24/solid';
import { cn } from '@/lib/utils';

interface ChatInputProps {
  onSendMessage: (message: string) => void;
  disabled?: boolean;
  placeholder?: string;
}

export default function ChatInput({ 
  onSendMessage, 
  disabled = false, 
  placeholder = "한국어 문장을 입력하세요..." 
}: ChatInputProps) {
  const [message, setMessage] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSubmit = () => {
    const trimmedMessage = message.trim();
    if (trimmedMessage && !disabled) {
      onSendMessage(trimmedMessage);
      setMessage('');
      
      // 텍스트영역 높이 리셋
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto';
      }
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleInput = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setMessage(e.target.value);
    
    // 자동 높이 조절
    const textarea = e.target;
    textarea.style.height = 'auto';
    textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
  };

  return (
    <div className="glass p-4 border-t">
      <div className="flex items-end gap-2 max-w-4xl mx-auto">
        <div className="flex-1 relative">
          <textarea
            ref={textareaRef}
            value={message}
            onChange={handleInput}
            onKeyDown={handleKeyDown}
            placeholder={placeholder}
            disabled={disabled}
            className={cn(
              "w-full p-3 pr-12 rounded-2xl border border-gray-300 resize-none",
              "focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent",
              "placeholder:text-gray-500 text-gray-900",
              "min-h-[48px] max-h-[120px]",
              disabled && "opacity-50 cursor-not-allowed"
            )}
            rows={1}
          />
          
          <button
            onClick={handleSubmit}
            disabled={disabled || !message.trim()}
            className={cn(
              "absolute right-2 bottom-2 p-2 rounded-full transition-colors",
              "text-white bg-primary-500 hover:bg-primary-600",
              "disabled:opacity-50 disabled:cursor-not-allowed",
              "disabled:hover:bg-primary-500"
            )}
          >
            <PaperAirplaneIcon className="w-4 h-4" />
          </button>
        </div>
      </div>
      
      <div className="flex items-center justify-between mt-2 text-xs text-gray-500 max-w-4xl mx-auto">
        <p>Enter로 전송, Shift+Enter로 줄바꿈</p>
        <p className={cn(
          "transition-colors",
          message.length > 500 ? "text-red-500" : "text-gray-400"
        )}>
          {message.length}/1000
        </p>
      </div>
    </div>
  );
}