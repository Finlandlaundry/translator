export type StyleType = 'formal' | 'casual';

export interface ChatMessage {
  id: string;
  original_text: string;
  refined_text: string;
  reply_text: string;
  timestamp: Date;
  isLoading?: boolean;
  isStreaming?: boolean;
}

export interface ChatRequest {
  message: string;
  style: StyleType;
  session_id?: string;
}

export interface ChatResponse {
  refined_text: string;
  reply_text: string;
  session_id: string;
}

export interface StreamingMessage {
  type: 'refined' | 'reply_start' | 'reply_chunk' | 'reply_complete' | 'done' | 'error';
  content: string;
  session_id: string;
}

export interface ChatSettings {
  style: StyleType;
  useStreaming: boolean;
}

export interface WebSocketState {
  isConnected: boolean;
  isConnecting: boolean;
  error: string | null;
}