import { useState } from 'react'
import styles from './InputBar.module.css'

export default function InputBar({ onSend, disabled }) {
  const [value, setValue] = useState('')

  const submit = () => {
    const trimmed = value.trim()
    if (!trimmed || disabled) return
    onSend(trimmed)
    setValue('')
  }

  const handleKey = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      submit()
    }
  }

  return (
    <div className={styles.bar}>
      <div className={styles.inputWrapper}>
        <textarea
          className={styles.input}
          placeholder="Ask about menus, prices, dietary options…"
          value={value}
          onChange={e => setValue(e.target.value)}
          onKeyDown={handleKey}
          disabled={disabled}
          rows={1}
        />
        <button
          className={styles.sendBtn}
          onClick={submit}
          disabled={disabled || !value.trim()}
          aria-label="Send"
        >
          <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
            <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z" />
          </svg>
        </button>
      </div>
      <p className={styles.hint}>Press Enter to send · Shift+Enter for new line</p>
    </div>
  )
}
