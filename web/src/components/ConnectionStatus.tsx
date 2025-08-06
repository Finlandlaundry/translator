'use client';

import { WebSocketState } from '@/types';
import { cn } from '@/lib/utils';
import { 
  WifiIcon, 
  ExclamationTriangleIcon,
  ArrowPathIcon 
} from '@heroicons/react/24/outline';

interface ConnectionStatusProps {
  wsState: WebSocketState;
  useStreaming: boolean;
  onToggleStreaming: () => void;
  onReconnect?: () => void;
}

export default function ConnectionStatus({ 
  wsState, 
  useStreaming, 
  onToggleStreaming,
  onReconnect 
}: ConnectionStatusProps) {
  const getStatusIcon = () => {
    if (!useStreaming) {
      return <WifiIcon className="w-4 h-4 text-gray-500" />;
    }
    
    if (wsState.isConnecting) {
      return <ArrowPathIcon className="w-4 h-4 text-yellow-500 animate-spin" />;
    }
    
    if (wsState.error) {
      return <ExclamationTriangleIcon className="w-4 h-4 text-red-500" />;
    }
    
    if (wsState.isConnected) {
      return <WifiIcon className="w-4 h-4 text-green-500" />;
    }
    
    return <WifiIcon className="w-4 h-4 text-gray-500" />;
  };

  const getStatusText = () => {
    if (!useStreaming) {
      return 'REST API';
    }
    
    if (wsState.isConnecting) {
      return '연결 중...';
    }
    
    if (wsState.error) {
      return '연결 오류';
    }
    
    if (wsState.isConnected) {
      return '실시간 연결됨';
    }
    
    return '연결 끊김';
  };

  const getStatusColor = () => {
    if (!useStreaming) {
      return 'text-gray-600';
    }
    
    if (wsState.isConnecting) {
      return 'text-yellow-600';
    }
    
    if (wsState.error) {
      return 'text-red-600';
    }
    
    if (wsState.isConnected) {
      return 'text-green-600';
    }
    
    return 'text-gray-600';
  };

  return (
    <div className="flex items-center justify-between p-3 glass rounded-xl">
      <div className="flex items-center gap-2">
        {getStatusIcon()}
        <span className={cn('text-sm font-medium', getStatusColor())}>
          {getStatusText()}
        </span>
        {wsState.error && (
          <span className="text-xs text-red-500">
            ({wsState.error})
          </span>
        )}
      </div>
      
      <div className="flex items-center gap-2">
        {wsState.error && onReconnect && (
          <button
            onClick={onReconnect}
            className="px-2 py-1 text-xs bg-red-100 text-red-700 rounded-md hover:bg-red-200 transition-colors"
          >
            재연결
          </button>
        )}
        
        <button
          onClick={onToggleStreaming}
          className={cn(
            "px-3 py-1 text-xs rounded-md transition-colors",
            useStreaming
              ? "bg-primary-100 text-primary-700 hover:bg-primary-200"
              : "bg-gray-100 text-gray-700 hover:bg-gray-200"
          )}
        >
          {useStreaming ? '스트리밍' : 'REST'}
        </button>
      </div>
    </div>
  );
}