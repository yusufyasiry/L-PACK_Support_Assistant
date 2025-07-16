import React, { useState, useRef, useEffect } from 'react';

const ChatInterface = ({ onSend }) => {
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState([]);
  const messagesEndRef = useRef(null);

  const handleSend = () => {
    if (!input.trim()) return;
    const userMessage = { sender: 'user', text: input };
    setMessages(prev => [...prev, userMessage]);
    onSend(input).then(response => {
      setMessages(prev => [...prev, { sender: 'bot', text: response }]);
    });
    setInput('');
  };

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const styles = {
    container: {
      display: 'flex',
      flexDirection: 'column',
      height: '100vh',
      maxWidth: '600px',
      margin: 'auto',
      border: '1px solid #ccc',
      borderRadius: '8px',
    },
    window: {
      flex: 1,
      padding: '16px',
      overflowY: 'auto',
      background: '#f9f9f9',
      display: 'flex',
      flexDirection: 'column',
    },
    message: {
      marginBottom: '12px',
      padding: '8px 12px',
      borderRadius: '16px',
      maxWidth: '75%',
    },
    userMessage: {
      background: '#007bff',
      color: '#fff',
      alignSelf: 'flex-end',
    },
    botMessage: {
      background: '#e5e5ea',
      color: '#000',
      alignSelf: 'flex-start',
    },
    inputContainer: {
      display: 'flex',
      padding: '12px',
      borderTop: '1px solid #ccc',
    },
    input: {
      flex: 1,
      padding: '8px',
      border: '1px solid #ccc',
      borderRadius: '4px',
      marginRight: '8px',
    },
    button: {
      padding: '8px 16px',
      border: 'none',
      borderRadius: '4px',
      background: '#007bff',
      color: '#fff',
      cursor: 'pointer',
    },
  };

  return (
    <div style={styles.container}>
      <div style={styles.window}>
        {messages.map((msg, i) => (
          <div
            key={i}
            style={{
              ...styles.message,
              ...(msg.sender === 'user' ? styles.userMessage : styles.botMessage),
            }}
          >
            {msg.text}
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>
      <div style={styles.inputContainer}>
        <input
          type="text"
          placeholder="Type your message..."
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && handleSend()}
          style={styles.input}
        />
        <button onClick={handleSend} style={styles.button}>Send</button>
      </div>
    </div>
  );
};

export default ChatInterface;
