"use client";

import { useState } from "react";
import styles from "./chat.module.css";

interface Chat {
  id: string;
  title: string;
  updatedAt: string;
}

interface SidebarProps {
  open: boolean;
  onClose: () => void;
  chats: Chat[];
  activeChatId: string | null;
  searchQuery: string;
  onSearchChange: (q: string) => void;
  onSelectChat: (id: string) => void;
  onNewChat: () => void;
  onDelete: (id: string) => void;
  onRename: (id: string, title: string) => void;
  onOpenProfile: () => void;
  onOpenSettings: () => void;
  onLogout: () => void;
}

export default function Sidebar({
  open, onClose, chats, activeChatId, searchQuery,
  onSearchChange, onSelectChat, onNewChat, onDelete, onRename,
  onOpenProfile, onOpenSettings, onLogout,
}: SidebarProps) {
  const [renamingId, setRenamingId] = useState<string | null>(null);
  const [renameValue, setRenameValue] = useState("");

  const startRename = (chat: Chat) => {
    setRenamingId(chat.id);
    setRenameValue(chat.title);
  };

  const submitRename = (id: string) => {
    if (renameValue.trim()) onRename(id, renameValue.trim());
    setRenamingId(null);
  };

  return (
    <div className={`${styles.sidebar} ${open ? "" : styles.closed}`}>
      <div className={styles.sidebarHeader}>
        <div className={styles.sidebarLogo}>
          <div className={styles.sidebarLogoIcon}>G</div>
          <div className={styles.sidebarLogoText}>GEN DATA <span>AI</span></div>
        </div>
        <button className={styles.sidebarClose} onClick={onClose} aria-label="Close sidebar">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
        </button>
      </div>

      <button className={styles.newChatBtn} onClick={onNewChat}>
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
        New Chat
      </button>

      <div className={styles.sidebarSearch}>
        <div className={styles.searchWrap}>
          <svg className={styles.searchIcon} width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
          <input className={styles.searchInput} placeholder="Search chats..." value={searchQuery} onChange={e => onSearchChange(e.target.value)} />
        </div>
      </div>

      <div className={styles.chatList}>
        {chats.length === 0 ? (
          <div className={styles.emptyChats}>No chats yet. Start a new one!</div>
        ) : (
          chats.map(chat => (
            <div key={chat.id} className={`${styles.chatItem} ${activeChatId === chat.id ? styles.active : ""}`} onClick={() => onSelectChat(chat.id)}>
              <svg className={styles.chatItemIcon} width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"/></svg>
              {renamingId === chat.id ? (
                <input className={styles.renameInput} value={renameValue} onChange={e => setRenameValue(e.target.value)} onBlur={() => submitRename(chat.id)} onKeyDown={e => { if (e.key === "Enter") submitRename(chat.id); if (e.key === "Escape") setRenamingId(null); }} autoFocus onClick={e => e.stopPropagation()} />
              ) : (
                <span className={styles.chatItemTitle}>{chat.title}</span>
              )}
              <div className={styles.chatItemActions}>
                <button className={styles.chatItemBtn} onClick={e => { e.stopPropagation(); startRename(chat); }} title="Rename">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M17 3a2.85 2.83 0 114 4L7.5 20.5 2 22l1.5-5.5z"/></svg>
                </button>
                <button className={`${styles.chatItemBtn} ${styles.deleteBtn}`} onClick={e => { e.stopPropagation(); onDelete(chat.id); }} title="Delete">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2"/></svg>
                </button>
              </div>
            </div>
          ))
        )}
      </div>

      <div className={styles.sidebarFooter}>
        <button className={styles.sidebarFooterBtn} onClick={onOpenProfile}>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
          Profile
        </button>
        <button className={styles.sidebarFooterBtn} onClick={onOpenSettings}>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 010 2.83 2 2 0 01-2.83 0l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-4 0v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83-2.83l.06-.06A1.65 1.65 0 004.68 15a1.65 1.65 0 00-1.51-1H3a2 2 0 010-4h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 012.83-2.83l.06.06A1.65 1.65 0 009 4.68a1.65 1.65 0 001-1.51V3a2 2 0 014 0v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 2.83l-.06.06A1.65 1.65 0 0019.4 9a1.65 1.65 0 001.51 1H21a2 2 0 010 4h-.09a1.65 1.65 0 00-1.51 1z"/></svg>
          Settings
        </button>
        <button className={styles.sidebarFooterBtn} onClick={onLogout}>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>
          Logout
        </button>
      </div>
    </div>
  );
}
