import { useEffect, useRef } from 'react';
import { Navbar } from './components/layout/Navbar';
import { ChatMessage } from './components/chat/ChatMessage';
import { ChatInput } from './components/chat/ChatInput';
import { useChat } from './hooks/useChat';
import styles from './App.module.css';

function App() {
  const { messages, isLoading, sendMessage } = useChat();
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };
  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  return (
    <div className="flex flex-col h-screen w-full bg-gray-50 font-sans">
      <Navbar />
      
      <main className="flex-1 flex justify-center items-center p-4 sm:p-6 overflow-hidden">
        <div className={`w-full max-w-2xl h-full max-h-[800px] flex flex-col bg-gray-50 ${styles.chatContainer}`}>
          
          <div className="flex-1 overflow-y-auto p-4 sm:p-6 flex flex-col gap-5">
            {messages.map((msg) => (
              <ChatMessage key={msg.id} msg={msg} />
            ))}
            
            {isLoading && (
              <div className="bg-white border border-gray-100 text-gray-400 self-start p-3.5 rounded-2xl rounded-bl-sm text-sm shadow-sm animate-pulse">
                Analizando base de conocimiento...
              </div>
            )}

            {/* Elemento invisible que actúa como destino del scroll */}
            <div ref={messagesEndRef} />
          </div>

          <ChatInput onSend={sendMessage} disabled={isLoading} />
        </div>
      </main>
    </div>
  );
}

export default App;