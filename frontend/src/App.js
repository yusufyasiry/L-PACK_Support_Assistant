import React from 'react';
import ChatInterface from './components/ChatInterface';

// this is your RAG‐backend call; adapt URL+payload as needed
async function queryRAGBackend(prompt) {
  const res = await fetch('/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question: prompt })
  });
  const { answer } = await res.json();
  return answer;
}

function App() {
  return (
    <div style={{ height: '100vh' }}>
      <ChatInterface onSend={queryRAGBackend} />
    </div>
  );
}

export default App;
