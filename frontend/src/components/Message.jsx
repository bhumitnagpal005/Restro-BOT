import MetricsPanel from './MetricsPanel'
import styles from './Message.module.css'

function formatTime(ts) {
  return new Date(ts).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

export default function Message({ message }) {
  const isUser = message.role === 'user'
  const isError = message.role === 'error'

  return (
    <div className={`${styles.row} ${isUser ? styles.rowUser : styles.rowBot}`}>
      {!isUser && (
        <div className={styles.avatar}>🤖</div>
      )}
      <div className={`${styles.bubbleWrapper} ${isUser ? styles.wrapperUser : styles.wrapperBot}`}>
        <div className={`${styles.bubble} ${isUser ? styles.user : isError ? styles.error : styles.bot}`}>
          <p className={styles.content}>{message.content}</p>
          <span className={styles.time}>{formatTime(message.timestamp)}</span>
        </div>
        {message.role === 'bot' && message.metrics && (
          <MetricsPanel metrics={message.metrics} exchangeId={message.exchangeId} />
        )}
      </div>
      {isUser && (
        <div className={styles.avatar}>👤</div>
      )}
    </div>
  )
}
