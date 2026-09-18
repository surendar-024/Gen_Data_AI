"use client";

import styles from "./chat.module.css";

interface TopBarProps {
  title: string;
  username: string;
  onToggleSidebar: () => void;
}

export default function TopBar({ title, username, onToggleSidebar }: TopBarProps) {
  return (
    <div className={styles.topBar}>
      <div className={styles.topBarLeft}>
        <button className={styles.sidebarToggle} onClick={onToggleSidebar} aria-label="Toggle sidebar">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <line x1="3" y1="6" x2="21" y2="6" />
            <line x1="3" y1="12" x2="21" y2="12" />
            <line x1="3" y1="18" x2="21" y2="18" />
          </svg>
        </button>
        <span className={styles.topBarTitle}>{title}</span>
      </div>
      <div className={styles.topBarRight}>
        <div className={styles.userAvatar}>
          {username.charAt(0).toUpperCase()}
        </div>
      </div>
    </div>
  );
}
