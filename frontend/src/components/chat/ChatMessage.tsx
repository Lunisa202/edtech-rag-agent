/* eslint-disable @typescript-eslint/no-unused-vars */
import type { Message } from '../../types/chat';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface Props {
  msg: Message;
}

export const ChatMessage = ({ msg }: Props) => {
  const isUser = msg.sender === 'user';
  
  return (
    <div className={`shrink-0 max-w-[85%] p-4 text-sm shadow-sm transition-all overflow-hidden ${
      isUser
        ? 'bg-blue-600 text-white self-end rounded-2xl rounded-br-sm'
        : 'bg-white text-gray-800 self-start rounded-2xl rounded-bl-sm border border-gray-100'
    }`}>
      {isUser ? (
        <p>{msg.text}</p>
      ) : (
        <div className="markdown-content">
          <ReactMarkdown 
            remarkPlugins={[remarkGfm]}
            components={{
              p: ({ node, ...props }) => <p className="mb-2 last:mb-0" {...props} />,
              strong: ({ node, ...props }) => <strong className="font-bold" {...props} />,
              ul: ({ node, ...props }) => <ul className="list-disc pl-5 mb-2 space-y-1" {...props} />,
              ol: ({ node, ...props }) => <ol className="list-decimal pl-5 mb-2 space-y-1" {...props} />,
              li: ({ node, ...props }) => <li className="leading-relaxed" {...props} />,
              h1: ({ node, ...props }) => <h1 className="text-lg font-bold mb-2 mt-4 first:mt-0" {...props} />,
              h2: ({ node, ...props }) => <h2 className="text-base font-bold mb-2 mt-4 first:mt-0" {...props} />,
              h3: ({ node, ...props }) => <h3 className="text-sm font-bold mb-2 mt-3 first:mt-0" {...props} />,
              a: ({ node, ...props }) => (
                <a className="text-blue-600 underline hover:text-blue-800" target="_blank" rel="noopener noreferrer" {...props} />
              ),
            }}
          >
            {msg.text}
          </ReactMarkdown>
        </div>
      )}
    </div>
  );
};