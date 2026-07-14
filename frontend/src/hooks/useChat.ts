import { useState } from 'react';
import type { Message } from '../types/chat';
import { chatService } from '../services/api';

export const useChat = () => {
  const [messages, setMessages] = useState<Message[]>([
    { id: 1, text: '¡Hola! Soy el asistente virtual. ¿En qué puedo ayudarte con los cursos o políticas?', sender: 'bot' }
  ]);
  const [isLoading, setIsLoading] = useState(false);

  const sendMessage = async (text: string) => {
    const userMessage: Message = { id: Date.now(), text, sender: 'user' };
    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const respuestaBot = await chatService.sendMessage(text);
      setMessages((prev) => [...prev, { id: Date.now() + 1, text: respuestaBot, sender: 'bot' }]);
    } catch (error) {
      console.error("Error en la comunicación:", error);
      setMessages((prev) => [...prev, { 
        id: Date.now() + 1, 
        text: 'Hubo un problema de conexión. Por favor, intenta de nuevo.', 
        sender: 'bot' 
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  return { messages, isLoading, sendMessage };
};