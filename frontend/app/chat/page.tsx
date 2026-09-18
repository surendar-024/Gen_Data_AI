"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import { useRouter } from "next/navigation";
import { saveAs } from "file-saver";
import styles from "./chat.module.css";
import Sidebar from "./Sidebar";
import TopBar from "./TopBar";
import ProfileModal from "./ProfileModal";
import SettingsModal from "./SettingsModal";

interface Message {
  role: "user" | "assistant";
  content: string;
  dataset?: Record<string, unknown>[];
  schema?: Record<string, unknown>;
}

interface Chat {
  id: string;
  title: string;
  updatedAt: string;
}

export default function ChatPage() {
  const router = useRouter();
  const [user, setUser] = useState<{ username: string; email: string } | null>(null);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [chats, setChats] = useState<Chat[]>([]);
  const [activeChatId, setActiveChatId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [showProfile, setShowProfile] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [toast, setToast] = useState("");
  const [recording, setRecording] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const recognitionRef = useRef<SpeechRecognition | null>(null);

  // Load user and chats
  useEffect(() => {
    fetch("/api/auth/me").then(r => r.json()).then(d => {
      if (d.authenticated) setUser(d.user);
      else router.push("/login");
    });
    loadChats();
  }, [router]);

  const loadChats = async () => {
    const res = await fetch("/api/chats");
    const data = await res.json();
    if (data.chats) setChats(data.chats);
  };

  const loadChat = useCallback(async (chatId: string) => {
    const res = await fetch(`/api/chats/${chatId}`);
    const data = await res.json();
    if (data.messages) {
      setMessages(data.messages);
      setActiveChatId(chatId);
    }
  }, []);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "48px";
      textareaRef.current.style.height = textareaRef.current.scrollHeight + "px";
    }
  }, [input]);

  const showToast = (msg: string) => {
    setToast(msg);
    setTimeout(() => setToast(""), 3000);
  };

  const handleNewChat = () => {
    setActiveChatId(null);
    setMessages([]);
    setInput("");
  };

  const handleSend = async () => {
    if (!input.trim() || loading) return;
    const prompt = input.trim();
    setInput("");

    const userMsg: Message = { role: "user", content: prompt };
    setMessages(prev => [...prev, userMsg]);
    setLoading(true);

    try {
      const res = await fetch("/api/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt, chatId: activeChatId }),
      });
      const data = await res.json();

      if (!res.ok) {
        setMessages(prev => [...prev, { role: "assistant", content: data.error || "Generation failed." }]);
      } else {
        const assistantMsg: Message = {
          role: "assistant",
          content: data.message,
          dataset: data.dataset,
          schema: data.schema,
        };
        setMessages(prev => [...prev, assistantMsg]);
        if (!activeChatId && data.chatId) setActiveChatId(data.chatId);
        loadChats();
      }
    } catch {
      setMessages(prev => [...prev, { role: "assistant", content: "Network error. Please try again." }]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleDelete = async (chatId: string) => {
    await fetch(`/api/chats/${chatId}`, { method: "DELETE" });
    if (activeChatId === chatId) handleNewChat();
    loadChats();
  };

  const handleRename = async (chatId: string, title: string) => {
    await fetch(`/api/chats/${chatId}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title }),
    });
    loadChats();
  };

  const handleLogout = async () => {
    await fetch("/api/auth/logout", { method: "POST" });
    router.push("/login");
  };

  // Voice input
  const toggleVoice = () => {
    if (recording) {
      recognitionRef.current?.stop();
      setRecording(false);
      return;
    }
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SR) { showToast("Voice input not supported"); return; }
    const recognition = new SR();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = "en-US";
    recognition.onresult = (e: SpeechRecognitionEvent) => {
      const t = e.results[0][0].transcript;
      setInput(prev => prev + (prev ? " " : "") + t);
    };
    recognition.onerror = () => setRecording(false);
    recognition.onend = () => setRecording(false);
    recognitionRef.current = recognition;
    recognition.start();
    setRecording(true);
  };

  // Build a clean filename from the active chat title
  const getFileName = (ext: string) => {
    const chat = chats.find(c => c.id === activeChatId);
    const base = chat?.title || "dataset";
    // Sanitize: lowercase, replace non-alphanumeric with underscore, trim
    const clean = base
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, "_")
      .replace(/^_+|_+$/g, "")
      .substring(0, 50);
    return `${clean || "dataset"}.${ext}`;
  };

  // Download helpers — using file-saver for reliable cross-browser downloads
  const downloadCSV = (dataset: Record<string, unknown>[]) => {
    if (!dataset.length) return;
    const keys = Object.keys(dataset[0]);
    const csvRows = [
      keys.join(","),
      ...dataset.map(row =>
        keys.map(k => {
          const val = String(row[k] ?? "").replace(/"/g, '""');
          return `"${val}"`;
        }).join(",")
      ),
    ];
    const csvString = csvRows.join("\n");
    const blob = new Blob([csvString], { type: "text/csv;charset=utf-8" });
    saveAs(blob, getFileName("csv"));
    showToast("CSV downloaded!");
  };

  const downloadJSON = (dataset: Record<string, unknown>[]) => {
    if (!dataset.length) return;
    const jsonString = JSON.stringify(dataset, null, 2);
    const blob = new Blob([jsonString], { type: "application/json;charset=utf-8" });
    saveAs(blob, getFileName("json"));
    showToast("JSON downloaded!");
  };

  const shareDataset = () => {
    const url = `${window.location.origin}/chat${activeChatId ? `?id=${activeChatId}` : ""}`;
    navigator.clipboard.writeText(url);
    showToast("Share link copied to clipboard!");
  };

  const handleHint = (prompt: string) => { setInput(prompt); };

  const filteredChats = chats.filter(c => c.title.toLowerCase().includes(searchQuery.toLowerCase()));

  if (!user) return null;

  return (
    <div className={styles.chatLayout}>
      <Sidebar
        open={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
        chats={filteredChats}
        activeChatId={activeChatId}
        searchQuery={searchQuery}
        onSearchChange={setSearchQuery}
        onSelectChat={loadChat}
        onNewChat={handleNewChat}
        onDelete={handleDelete}
        onRename={handleRename}
        onOpenProfile={() => setShowProfile(true)}
        onOpenSettings={() => setShowSettings(true)}
        onLogout={handleLogout}
      />

      {sidebarOpen && (
        <div className={styles.sidebarOverlay} onClick={() => setSidebarOpen(false)} />
      )}

      <div className={styles.main}>
        <TopBar
          title={activeChatId ? chats.find(c => c.id === activeChatId)?.title || "Chat" : "New Chat"}
          username={user.username}
          onToggleSidebar={() => setSidebarOpen(!sidebarOpen)}
        />

        <div className={styles.messagesArea}>
          {messages.length === 0 ? (
            <div className={styles.welcome}>
              <div className={styles.welcomeIcon}>✦</div>
              <h2 className={styles.welcomeTitle}>
                Welcome, <span className="gradient-text-primary">{user.username}</span>!
              </h2>
              <p className={styles.welcomeSubtitle}>
                Describe the dataset you need in plain English. I&apos;ll generate it for you instantly.
              </p>
              <div className={styles.welcomeHints}>
                {[
                  { label: "Students", text: "Generate 20 students with name, age between 18-25, GPA, and department" },
                  { label: "Employees", text: "Create 50 employees with name, salary between 40000-120000, and department" },
                  { label: "Healthcare", text: "Generate 30 patients with name, age, diagnosis, and blood type" },
                  { label: "Sales", text: "Create 100 orders with product name, quantity, price, and customer name" },
                ].map((h, i) => (
                  <div key={i} className={styles.hintCard} onClick={() => handleHint(h.text)}>
                    <div className={styles.hintCardLabel}>{h.label}</div>
                    {h.text}
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <>
              {messages.map((msg, i) => (
                <div key={i} className={styles.messageGroup}>
                  {msg.role === "user" ? (
                    <div className={styles.userMessage}>{msg.content}</div>
                  ) : (
                    <div className={styles.assistantMessage}>
                      <div className={styles.assistantHeader}>
                        <div className={styles.assistantIcon}>G</div>
                        <span className={styles.assistantLabel}>GEN DATA AI</span>
                      </div>
                      <div className={styles.assistantText}>{msg.content}</div>
                      {msg.dataset && msg.dataset.length > 0 && (
                        <div className={styles.datasetWrap}>
                          <div className={styles.datasetToolbar}>
                            <span className={styles.datasetInfo}>
                              {msg.dataset.length} rows × {Object.keys(msg.dataset[0]).length} columns
                            </span>
                            <div className={styles.datasetActions}>
                              <button className={styles.datasetBtn} onClick={() => downloadCSV(msg.dataset!)}>
                                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4M7 10l5 5 5-5M12 15V3"/></svg>
                                CSV
                              </button>
                              <button className={styles.datasetBtn} onClick={() => downloadJSON(msg.dataset!)}>
                                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4M7 10l5 5 5-5M12 15V3"/></svg>
                                JSON
                              </button>
                              <button className={`${styles.datasetBtn} ${styles.primary}`} onClick={shareDataset}>
                                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><line x1="8.59" y1="13.51" x2="15.42" y2="17.49"/><line x1="15.41" y1="6.51" x2="8.59" y2="10.49"/></svg>
                                Share
                              </button>
                            </div>
                          </div>
                          <div className={styles.datasetTableWrap}>
                            <table className={styles.datasetTable}>
                              <thead>
                                <tr>{Object.keys(msg.dataset[0]).map(k => <th key={k}>{k}</th>)}</tr>
                              </thead>
                              <tbody>
                                {msg.dataset.map((row, ri) => (
                                  <tr key={ri}>{Object.values(row).map((v, ci) => <td key={ci}>{String(v)}</td>)}</tr>
                                ))}
                              </tbody>
                            </table>
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              ))}
              {loading && (
                <div className={styles.generating}>
                  <div className={styles.generatingDots}><span/><span/><span/></div>
                  Generating your dataset...
                </div>
              )}
            </>
          )}
          <div ref={messagesEndRef} />
        </div>

        <div className={styles.inputArea}>
          <div className={styles.inputWrap}>
            <textarea
              ref={textareaRef}
              className={styles.chatInput}
              placeholder="Describe the dataset you need..."
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              rows={1}
              disabled={loading}
            />
            <button className={`${styles.micBtn} ${recording ? styles.recording : ""}`} onClick={toggleVoice} title="Voice input">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 1a3 3 0 00-3 3v8a3 3 0 006 0V4a3 3 0 00-3-3z"/><path d="M19 10v2a7 7 0 01-14 0v-2"/><line x1="12" y1="19" x2="12" y2="23"/><line x1="8" y1="23" x2="16" y2="23"/></svg>
            </button>
            <button className={styles.sendBtn} onClick={handleSend} disabled={loading || !input.trim()} title="Send">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>
            </button>
          </div>
        </div>
      </div>

      {showProfile && <ProfileModal user={user} onClose={() => setShowProfile(false)} onUpdate={(u) => setUser(u)} showToast={showToast} />}
      {showSettings && <SettingsModal onClose={() => setShowSettings(false)} onLogout={handleLogout} showToast={showToast} />}
      {toast && <div className={styles.toast}>{toast}</div>}
    </div>
  );
}
