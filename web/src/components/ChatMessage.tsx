'use client';

import { ChatMessage as ChatMessageType } from '@/types';
import { formatTime } from '@/lib/utils';
import { CheckIcon, PencilIcon, ChatBubbleLeftIcon } from '@heroicons/react/24/outline';

interface ChatMessageProps {
  message: ChatMessageType;
}

export default function ChatMessage({ message }: ChatMessageProps) {
  return (
    <div className="message-group fade-in">
      {/* 원문 (사용자 입력) */}
      <div className="flex justify-end mb-2">
        <div className="chat-bubble chat-bubble-user">
          <div className="flex items-start gap-2">
            <div className="flex-1">
              <p className="text-sm font-medium mb-1">원문</p>
              <p>{message.original_text}</p>
            </div>
          </div>
          <p className="text-xs opacity-80 mt-2">
            {formatTime(message.timestamp)}
          </p>
        </div>
      </div>

      {/* 교정문 */}
      <div className="flex justify-start mb-2">
        <div className="chat-bubble chat-bubble-refined">
          <div className="flex items-start gap-2">
            <PencilIcon className="w-4 h-4 mt-1 flex-shrink-0" />
            <div className="flex-1">
              <p className="text-sm font-medium mb-1">교정문</p>
              {message.isLoading ? (
                <div className="loading-dots">
                  <div></div>
                  <div></div>
                  <div></div>
                </div>
              ) : (
                <p>{message.refined_text}</p>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* 봇 응답 */}
      <div className="flex justify-start">
        <div className="chat-bubble chat-bubble-bot">
          <div className="flex items-start gap-2">
            <ChatBubbleLeftIcon className="w-4 h-4 mt-1 flex-shrink-0" />
            <div className="flex-1">
              <p className="text-sm font-medium mb-1">응답</p>
              {message.isLoading ? (
                <div className="loading-dots">
                  <div></div>
                  <div></div>
                  <div></div>
                </div>
              ) : message.isStreaming ? (
                <div className="flex items-center gap-2">
                  <p>{message.reply_text}</p>
                  <span className="typing-indicator">|</span>
                </div>
              ) : (
                <p>{message.reply_text}</p>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}