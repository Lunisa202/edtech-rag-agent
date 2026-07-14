export interface Message {
  id: number;
  text: string;
  sender: 'user' | 'bot';
}

export interface ChatResponse {
  respuesta: string;
}