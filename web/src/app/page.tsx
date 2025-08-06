'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import { 
  ChatMessage as ChatMessageType, 
  StyleType, 
  ChatSettings, 
  WebSocketState,
  StreamingMessage,
  ChatRequest
} from '@/types';
import ChatMessage from '@/components/ChatMessage';
import ChatInput from '@/components/ChatInput';
import StyleSelector from '@/components/StyleSelector';
import ConnectionStatus from '@/components/ConnectionStatus';
import { apiClient } from '@/lib/api';
import { WebSocketClient } from '@/lib/websocket';
import { generateId, getSessionId } from '@/lib/utils';

export default function ChatPage() {
  const [messages, setMessages] = useState<ChatMessageType[]>([]);
  const [settings, setSettings] = useState<ChatSettings>({
    style: 'formal',
    useStreaming: true
  });
  const [wsState, setWsState] = useState<WebSocketState>({
    isConnected: false,
    isConnecting: false,
    error: null
  });
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string>('');

  const wsClientRef = useRef<WebSocketClient | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const currentMessageRef = useRef<ChatMessageType | null>(null);

  // 스크롤을 하단으로 이동
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // 세션 ID 초기화
  useEffect(() => {
    setSessionId(getSessionId());
  }, []);

  // WebSocket 연결 설정
  const connectWebSocket = useCallback(async () => {
    if (!settings.useStreaming) return;

    setWsState(prev => ({ ...prev, isConnecting: true, error: null }));

    try {
      wsClientRef.current = new WebSocketClient();
      await wsClientRef.current.connect();

      setWsState({
        isConnected: true,
        isConnecting: false,
        error: null
      });

      // 메시지 수신 핸들러
      wsClientRef.current.onMessage((message: StreamingMessage) => {
        handleStreamingMessage(message);
      });

      // 에러 핸들러
      wsClientRef.current.onError((error) => {
        console.error('WebSocket 에러:', error);
        setWsState(prev => ({
          ...prev,
          isConnected: false,
          isConnecting: false,
          error: '연결 오류'
        }));
      });

      // 연결 종료 핸들러
      wsClientRef.current.onClose((event) => {
        console.log('WebSocket 연결 종료:', event.code, event.reason);
        setWsState(prev => ({
          ...prev,
          isConnected: false,
          isConnecting: false,
          error: event.code !== 1000 ? '연결이 끊어졌습니다' : null
        }));
      });

    } catch (error) {
      console.error('WebSocket 연결 실패:', error);
      setWsState({
        isConnected: false,
        isConnecting: false,
        error: '연결 실패'
      });
    }
  }, [settings.useStreaming]);

  // 스트리밍 메시지 처리
  const handleStreamingMessage = (message: StreamingMessage) => {
    switch (message.type) {
      case 'refined':
        if (currentMessageRef.current) {
          currentMessageRef.current.refined_text = message.content;
          setMessages(prev => [...prev.slice(0, -1), { ...currentMessageRef.current! }]);
        }
        break;

      case 'reply_start':
        if (currentMessageRef.current) {
          currentMessageRef.current.isStreaming = true;
          currentMessageRef.current.reply_text = '';
          setMessages(prev => [...prev.slice(0, -1), { ...currentMessageRef.current! }]);
        }
        break;

      case 'reply_chunk':
        if (currentMessageRef.current) {
          currentMessageRef.current.reply_text += message.content;
          setMessages(prev => [...prev.slice(0, -1), { ...currentMessageRef.current! }]);
        }
        break;

      case 'reply_complete':
      case 'done':
        if (currentMessageRef.current) {
          currentMessageRef.current.isLoading = false;
          currentMessageRef.current.isStreaming = false;
          setMessages(prev => [...prev.slice(0, -1), { ...currentMessageRef.current! }]);
          currentMessageRef.current = null;
        }
        setIsLoading(false);
        break;

      case 'error':
        console.error('서버 에러:', message.content);
        if (currentMessageRef.current) {
          currentMessageRef.current.isLoading = false;
          currentMessageRef.current.isStreaming = false;
          currentMessageRef.current.refined_text = '오류가 발생했습니다.';
          currentMessageRef.current.reply_text = message.content;
          setMessages(prev => [...prev.slice(0, -1), { ...currentMessageRef.current! }]);
          currentMessageRef.current = null;
        }
        setIsLoading(false);
        break;
    }
  };

  // WebSocket 연결/해제
  useEffect(() => {
    if (settings.useStreaming) {
      connectWebSocket();
    } else {
      wsClientRef.current?.close();
      setWsState({
        isConnected: false,
        isConnecting: false,
        error: null
      });
    }

    return () => {
      wsClientRef.current?.close();
    };
  }, [settings.useStreaming, connectWebSocket]);

  // 메시지 전송 (REST API)
  const sendMessageRest = async (message: string) => {
    setIsLoading(true);

    const newMessage: ChatMessageType = {
      id: generateId(),
      original_text: message,
      refined_text: '',
      reply_text: '',
      timestamp: new Date(),
      isLoading: true
    };

    setMessages(prev => [...prev, newMessage]);

    try {
      const request: ChatRequest = {
        message,
        style: settings.style,
        session_id: sessionId
      };

      const response = await apiClient.chat(request);

      setMessages(prev => prev.map(msg => 
        msg.id === newMessage.id 
          ? {
              ...msg,
              refined_text: response.refined_text,
              reply_text: response.reply_text,
              isLoading: false
            }
          : msg
      ));

    } catch (error) {
      console.error('메시지 전송 실패:', error);
      setMessages(prev => prev.map(msg => 
        msg.id === newMessage.id 
          ? {
              ...msg,
              refined_text: '오류가 발생했습니다.',
              reply_text: error instanceof Error ? error.message : '알 수 없는 오류가 발생했습니다.',
              isLoading: false
            }
          : msg
      ));
    } finally {
      setIsLoading(false);
    }
  };

  // 메시지 전송 (WebSocket)
  const sendMessageWebSocket = async (message: string) => {
    if (!wsClientRef.current?.isConnected()) {
      throw new Error('WebSocket이 연결되지 않았습니다.');
    }

    setIsLoading(true);

    const newMessage: ChatMessageType = {
      id: generateId(),
      original_text: message,
      refined_text: '',
      reply_text: '',
      timestamp: new Date(),
      isLoading: true
    };

    setMessages(prev => [...prev, newMessage]);
    currentMessageRef.current = newMessage;

    try {
      const request: ChatRequest = {
        message,
        style: settings.style,
        session_id: sessionId
      };

      await wsClientRef.current.sendMessage(request);

    } catch (error) {
      console.error('WebSocket 메시지 전송 실패:', error);
      setMessages(prev => prev.map(msg => 
        msg.id === newMessage.id 
          ? {
              ...msg,
              refined_text: '오류가 발생했습니다.',
              reply_text: error instanceof Error ? error.message : '메시지 전송에 실패했습니다.',
              isLoading: false
            }
          : msg
      ));
      currentMessageRef.current = null;
      setIsLoading(false);
    }
  };

  // 메시지 전송 핸들러
  const handleSendMessage = async (message: string) => {
    if (isLoading) return;

    try {
      if (settings.useStreaming && wsState.isConnected) {
        await sendMessageWebSocket(message);
      } else {
        await sendMessageRest(message);
      }
    } catch (error) {
      console.error('메시지 전송 중 오류:', error);
    }
  };

  // 스타일 변경 핸들러
  const handleStyleChange = (style: StyleType) => {
    setSettings(prev => ({ ...prev, style }));
  };

  // 스트리밍 토글 핸들러
  const handleToggleStreaming = () => {
    setSettings(prev => ({ ...prev, useStreaming: !prev.useStreaming }));
  };

  // 재연결 핸들러
  const handleReconnect = () => {
    connectWebSocket();
  };

  return (
    <div className="min-h-screen flex flex-col bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* 헤더 */}
      <header className="glass border-b p-4">
        <div className="max-w-4xl mx-auto">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h1 className="text-2xl font-bold text-gray-800">
                한국어 교정 챗봇
              </h1>
              <p className="text-sm text-gray-600">
                유학생을 위한 자연스러운 한국어 문장 교정 및 대화 서비스
              </p>
            </div>
          </div>
          
          <div className="space-y-3">
            <StyleSelector
              style={settings.style}
              onStyleChange={handleStyleChange}
              disabled={isLoading}
            />
            
            <ConnectionStatus
              wsState={wsState}
              useStreaming={settings.useStreaming}
              onToggleStreaming={handleToggleStreaming}
              onReconnect={handleReconnect}
            />
          </div>
        </div>
      </header>

      {/* 채팅 영역 */}
      <main className="flex-1 overflow-hidden">
        <div className="h-full max-w-4xl mx-auto flex flex-col">
          {/* 메시지 목록 */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4 scrollbar-hide">
            {messages.length === 0 ? (
              <div className="flex-1 flex items-center justify-center">
                <div className="text-center space-y-4">
                  <div className="text-6xl">💬</div>
                  <h2 className="text-xl font-semibold text-gray-700">
                    안녕하세요!
                  </h2>
                  <p className="text-gray-500 max-w-md">
                    한국어 문장을 입력하시면 자연스럽게 교정해드리고, 
                    친근한 대화로 응답해드릴게요.
                  </p>
                </div>
              </div>
            ) : (
              messages.map((message) => (
                <ChatMessage key={message.id} message={message} />
              ))
            )}
            <div ref={messagesEndRef} />
          </div>
        </div>
      </main>

      {/* 입력 영역 */}
      <ChatInput
        onSendMessage={handleSendMessage}
        disabled={isLoading || (settings.useStreaming && !wsState.isConnected)}
        placeholder={
          settings.useStreaming && !wsState.isConnected
            ? "WebSocket 연결을 기다리는 중..."
            : "한국어 문장을 입력하세요..."
        }
      />
    </div>
  );
}