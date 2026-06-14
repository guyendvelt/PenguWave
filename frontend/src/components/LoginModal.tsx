import { useState } from "react";
import { login } from "../api";

interface LoginModalProps {
  onClose: () => void;
}

export default function LoginModal({ onClose }: LoginModalProps) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      // On success the backend sets the HttpOnly session cookie.
      await login(email, password);
      onClose();
      // Reload so authenticated views (events/users) fetch with the new session.
      window.location.reload();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Login failed");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <button className="modal-close" onClick={onClose}>
          ✕
        </button>
        <h2>Sign In</h2>
        <p style={{ color: "#666", marginBottom: 20, fontSize: 14 }}>
          Enter your credentials to access PenguWave
        </p>
        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: 12 }}>
            <label>Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@company.com"
            />
          </div>
          <div style={{ marginBottom: 16 }}>
            <label>Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
            />
          </div>
          {error && (
            <p style={{ color: "red", marginBottom: 12, fontSize: 14 }} role="alert">
              {error}
            </p>
          )}
          <button
            type="submit"
            className="btn-primary"
            style={{ width: "100%" }}
            disabled={submitting}
          >
            {submitting ? "Signing in…" : "Sign In"}
          </button>
        </form>
      </div>
    </div>
  );
}
