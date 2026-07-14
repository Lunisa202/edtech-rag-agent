import { useState } from 'react';

interface Props {
  onSend: (text: string) => void;
  disabled: boolean;
}

export const ChatInput = ({ onSend, disabled }: Props) => {
  const [inputValue, setInputValue] = useState('');

  const handleSend = () => {
    if (!inputValue.trim()) return;
    onSend(inputValue);
    setInputValue('');
  };

  return (
    <div className="p-4 bg-white border-t border-gray-100 flex gap-3">
      <input
        type="text"
        value={inputValue}
        onChange={(e) => setInputValue(e.target.value)}
        onKeyDown={(e) => e.key === 'Enter' && handleSend()}
        placeholder="Escribe tu consulta..."
        disabled={disabled}
        className="flex-1 border border-gray-300 rounded-xl px-4 py-2.5 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 text-sm disabled:bg-gray-50 transition-colors"
      />
      <button
        onClick={handleSend}
        disabled={disabled || !inputValue.trim()}
        className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2.5 rounded-xl text-sm font-semibold transition-colors disabled:bg-blue-300 disabled:cursor-not-allowed"
      >
        Enviar
      </button>
    </div>
  );
};