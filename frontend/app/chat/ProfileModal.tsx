"use client";

import { useState } from "react";
import styles from "./chat.module.css";

interface ProfileModalProps {
  user: { username: string; email: string };
  onClose: () => void;
  onUpdate: (user: { username: string; email: string }) => void;
  showToast: (msg: string) => void;
}

export default function ProfileModal({ user, onClose, onUpdate, showToast }: ProfileModalProps) {
  const [username, setUsername] = useState(user.username);
  const [currentPw, setCurrentPw] = useState("");
  const [newPw, setNewPw] = useState("");
  const [msg, setMsg] = useState<{ type: "success" | "error"; text: string } | null>(null);
  const [loading, setLoading] = useState(false);

  const handleUpdateUsername = async () => {
    if (!username.trim() || username.trim().length < 3) {
      setMsg({ type: "error", text: "Username must be at least 3 characters" });
      return;
    }
    setLoading(true);
    const res = await fetch("/api/user/profile", {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username: username.trim() }),
    });
    const data = await res.json();
    setLoading(false);
    if (res.ok) {
      onUpdate({ ...user, username: username.trim().toLowerCase() });
      showToast("Username updated!");
      setMsg({ type: "success", text: "Username updated successfully" });
    } else {
      setMsg({ type: "error", text: data.error });
    }
  };

  const handleChangePassword = async () => {
    if (!currentPw || !newPw) {
      setMsg({ type: "error", text: "Both fields are required" });
      return;
    }
    setLoading(true);
    const res = await fetch("/api/user/password", {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ currentPassword: currentPw, newPassword: newPw }),
    });
    const data = await res.json();
    setLoading(false);
    if (res.ok) {
      setCurrentPw("");
      setNewPw("");
      showToast("Password changed!");
      setMsg({ type: "success", text: "Password changed successfully" });
    } else {
      setMsg({ type: "error", text: data.error });
    }
  };

  return (
    <div className={styles.modalOverlay} onClick={onClose}>
      <div className={styles.modal} onClick={e => e.stopPropagation()}>
        <div className={styles.modalHeader}>
          <h2 className={styles.modalTitle}>Profile</h2>
          <button className={styles.modalClose} onClick={onClose}>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
          </button>
        </div>

        {msg && <div className={`${styles.modalMsg} ${msg.type === "success" ? styles.modalMsgSuccess : styles.modalMsgError}`}>{msg.text}</div>}

        <div className={styles.modalSection}>
          <div className={styles.modalSectionTitle}>Email</div>
          <input className={styles.modalInput} value={user.email} disabled style={{ opacity: 0.6, cursor: "not-allowed" }} />
        </div>

        <div className={styles.modalSection}>
          <div className={styles.modalSectionTitle}>Username</div>
          <input className={styles.modalInput} value={username} onChange={e => setUsername(e.target.value)} placeholder="New username" />
          <div className={styles.modalActions}>
            <button className={`${styles.modalBtn} ${styles.modalBtnPrimary}`} onClick={handleUpdateUsername} disabled={loading}>Save Username</button>
          </div>
        </div>

        <div className={styles.modalSection}>
          <div className={styles.modalSectionTitle}>Change Password</div>
          <input className={styles.modalInput} type="password" value={currentPw} onChange={e => setCurrentPw(e.target.value)} placeholder="Current password" />
          <input className={styles.modalInput} type="password" value={newPw} onChange={e => setNewPw(e.target.value)} placeholder="New password (min 6 chars)" />
          <div className={styles.modalActions}>
            <button className={`${styles.modalBtn} ${styles.modalBtnPrimary}`} onClick={handleChangePassword} disabled={loading}>Change Password</button>
          </div>
        </div>
      </div>
    </div>
  );
}
