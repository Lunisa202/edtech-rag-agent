import axios from 'axios';
import type { ChatResponse } from '../types/chat';

const API_URL = import.meta.env.VITE_API_URL;

export const chatService = {
  async sendMessage(pregunta: string): Promise<string> {
    try {
      const response = await axios.post<ChatResponse>(API_URL, { pregunta });
      return response.data.respuesta;
    } catch (error) {
      console.error('Error en la petición Axios:', error);
      throw new Error('Error al enviar el mensaje al backend', { cause: error });
    }
  }
};