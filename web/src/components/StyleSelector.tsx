'use client';

import { StyleType } from '@/types';
import { cn } from '@/lib/utils';

interface StyleSelectorProps {
  style: StyleType;
  onStyleChange: (style: StyleType) => void;
  disabled?: boolean;
}

export default function StyleSelector({ style, onStyleChange, disabled = false }: StyleSelectorProps) {
  const styles = [
    {
      value: 'formal' as StyleType,
      label: '정중하게',
      description: '존댓말, 정중한 표현',
      icon: '🎩'
    },
    {
      value: 'casual' as StyleType,
      label: '친근하게',
      description: '캐주얼, 친근한 말투',
      icon: '😊'
    }
  ];

  return (
    <div className="space-y-2">
      <p className="text-sm font-medium text-gray-700">응답 스타일</p>
      <div className="flex gap-2">
        {styles.map((styleOption) => (
          <button
            key={styleOption.value}
            onClick={() => onStyleChange(styleOption.value)}
            disabled={disabled}
            className={cn(
              "flex-1 p-3 rounded-xl border-2 transition-all",
              "text-left hover:shadow-sm",
              style === styleOption.value
                ? "border-primary-500 bg-primary-50 text-primary-900"
                : "border-gray-200 bg-white text-gray-700 hover:border-gray-300",
              disabled && "opacity-50 cursor-not-allowed"
            )}
          >
            <div className="flex items-center gap-2 mb-1">
              <span className="text-lg">{styleOption.icon}</span>
              <span className="font-medium">{styleOption.label}</span>
            </div>
            <p className="text-xs text-gray-500">{styleOption.description}</p>
          </button>
        ))}
      </div>
    </div>
  );
}