import { useState, useCallback } from 'react'
import Header from './components/Header'
import ChatWindow from './components/ChatWindow'
import InputBar from './components/InputBar'
import styles from './App.module.css'

const WELCOME = {
  id: 'welcome',
  role: 'bot',
  content: "Hi! I'm RestroBot 🍽️ Ask me anything about restaurants in Roorkee — menus, prices, dietary options, and more.",
  timestamp: Date.now(),
}

function getSessionId() {
  const key = 'restrobot_session'
  let id = localStorage.getItem(key)
  if (!id) {
    id = crypto.randomUUID()
    localStorage.setItem(key, id)
  }
  return id
}

export default function App() {
  const [messages, setMessages] = useState([WELCOME])
  const [isLoading, setIsLoading] = useState(false)
  const [sessionId] = useState(getSessionId)

  const sendMessage = useCallback(async (query) => {
    const userMsg = { id: crypto.randomUUID(), role: 'user', content: query, timestamp: Date.now() }
    setMessages(prev => [...prev, userMsg])
    setIsLoading(true)

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, session_id: sessionId }),
      })

      if (!res.ok) {
        const err = await res.json().catch(() => ({}))
        throw new Error(err.error || `Server error ${res.status}`)
      }

      const data = await res.json()
      const botMsg = { id: crypto.randomUUID(), role: 'bot', content: data.response, metrics: data.metrics, exchangeId: data.exchange_id, timestamp: Date.now() }
      setMessages(prev => [...prev, botMsg])
    } catch (err) {
      const errMsg = {
        id: crypto.randomUUID(),
        role: 'error',
        content: `Something went wrong: ${err.message}`,
        timestamp: Date.now(),
      }
      setMessages(prev => [...prev, errMsg])
    } finally {
      setIsLoading(false)
    }
  }, [sessionId])

  const clearHistory = useCallback(async () => {
    await fetch(`/api/session/${sessionId}`, { method: 'DELETE' }).catch(() => {})
    setMessages([WELCOME])
  }, [sessionId])

  return (
    <div className={styles.layout}>
      <Header onClear={clearHistory} />
      <ChatWindow messages={messages} isLoading={isLoading} />
      <InputBar onSend={sendMessage} disabled={isLoading} />
    </div>
  )
}
