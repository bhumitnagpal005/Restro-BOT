import styles from './Header.module.css'

export default function Header({ onClear }) {
  return (
    <header className={styles.header}>
      <div className={styles.brand}>
        <span className={styles.icon}>🍽️</span>
        <div>
          <h1 className={styles.title}>RestroBot</h1>
          <p className={styles.subtitle}>Roorkee Restaurant Assistant</p>
        </div>
      </div>
      <button className={styles.clearBtn} onClick={onClear} title="Clear conversation">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <polyline points="3 6 5 6 21 6" />
          <path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6" />
          <path d="M10 11v6M14 11v6" />
          <path d="M9 6V4a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2" />
        </svg>
        Clear
      </button>
    </header>
  )
}
