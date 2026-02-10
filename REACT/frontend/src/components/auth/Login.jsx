import { useState } from "react";
import { useNavigate } from "react-router-dom";
import Api from "../../api";
import "./Login.css";

export default function Login() {
  const navigate = useNavigate();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const handleLogin = async (e) => {
    e.preventDefault();
    setError("");

    try {
      await Api.post("login/", { username, password }, { withCredentials: true });
      navigate("/dashboard");
    } catch (err) {
      console.log(err.response?.data || err);
      setError("Invalid username or password");
    }
  };

  return (
    <div className="login-wrapper">
      <form className="login-box" onSubmit={handleLogin}>
        <h2>Login</h2>

        {error && <div className="error">{error}</div>}

        <input
          type="text"
          placeholder="Username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          required
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />

        <button type="submit">Login</button>

        <p>
          Don’t have an account? <a href="/register">Register here</a>
        </p>
      </form>
    </div>
  );
}
