"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useTheme } from "@/context/ThemeContext";
import styles from "./chat.module.css";

interface SettingsModalProps {
  onClose: () => void;
  onLogout: () => void;
  showToast: (msg: string) => void;
}

export default function SettingsModal({ onClose, onLogout, showToast }: SettingsModalProps) {
  const router = useRouter();
  const { theme, setTheme } = useTheme();
  const [confirmDelete, setConfirmDelete] = useState(false);
  const [deleting, setDeleting] = useState(false);

  const handleDeleteAccount = async () => {
    if (!confirmDelete) {
      setConfirmDelete(true);
      return;
    }
    setDeleting(true);
    const res = await fetch("/api/user/profile", { method: "DELETE" });
    if (res.ok) {
      await fetch("/api/auth/logout", { method: "POST" });
      showToast("Account deleted");
      router.push("/");
    } else {
      showToast("Failed to delete account");
    }
    setDeleting(false);
  };

  return (
    <div className={styles.modalOverlay} onClick={onClose}>
      <div className={styles.modal} onClick={e => e.stopPropagation()}>
        <div className={styles.modalHeader}>
          <h2 className={styles.modalTitle}>Settings</h2>
          <button className={styles.modalClose} onClick={onClose}>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
          </button>
        </div>

        <div className={styles.modalSection}>
          <div className={styles.modalSectionTitle}>Theme</div>
          <div className={styles.themeOptions}>
            <div
              className={`${styles.themeOption} ${theme === "dark" ? styles.active : ""}`}
              onClick={() => { setTheme("dark"); showToast("Dark theme applied"); }}
            >
              🌙 Dark
            </div>
            <div
              className={`${styles.themeOption} ${theme === "light" ? styles.active : ""}`}
              onClick={() => { setTheme("light"); showToast("Light theme applied"); }}
            >
              ☀️ Light
            </div>
          </div>
        </div>

        <div className={`${styles.modalSection} ${styles.dangerZone}`}>
          <div className={styles.modalSectionTitle}>⚠ Danger Zone</div>
          <p className={styles.dangerZoneDesc}>
            {confirmDelete
              ? "This action cannot be undone. All your data including chats will be permanently deleted."
              : "Permanently delete your account and all associated data."}
          </p>
          <div className={styles.modalActions}>
            {confirmDelete && (
              <button className={`${styles.modalBtn} ${styles.modalBtnGhost}`} onClick={() => setConfirmDelete(false)}>Cancel</button>
            )}
            <button className={`${styles.modalBtn} ${styles.modalBtnDanger}`} onClick={handleDeleteAccount} disabled={deleting}>
              {confirmDelete ? "Yes, Delete My Account" : "Delete Account"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
