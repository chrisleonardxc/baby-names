import { useState, type FormEvent } from "react";
import { useAuth } from "../context/AuthContext";

export function PasswordGate() {
  const { login } = useAuth();
  const [password, setPassword] = useState("");
  const [error, setError] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setError(false);
    const ok = await login(password);
    setSubmitting(false);
    if (!ok) setError(true);
  };

  return (
    <div className="password-gate">
      <form className="password-gate__card" onSubmit={handleSubmit}>
        <h1>Baby Name Finder</h1>
        <p>Enter the password to continue.</p>
        <input
          type="password"
          value={password}
          onChange={(e) => {
            setPassword(e.target.value);
            setError(false);
          }}
          autoFocus
          placeholder="Password"
        />
        {error && <p className="password-gate__error">Incorrect password.</p>}
        <button type="submit" disabled={submitting || !password}>
          {submitting ? "Checking…" : "Enter"}
        </button>
      </form>
    </div>
  );
}
