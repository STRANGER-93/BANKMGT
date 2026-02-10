import { useState } from "react";
import { useNavigate } from "react-router-dom";
import Api from "../../api";
import "./Register.css";

export default function Register() {
  const navigate = useNavigate();
  const [form, setForm] = useState({
    username: "",
    first_name: "",
    phone: "",
    email: "",
    password: "",
    account_type: "savings",
  });

  const [error, setError] = useState("");

  const submit = async (e) => {
    e.preventDefault();
    setError("");

    try {
      await Api.post("register/", form); // baseURL already /api/
      alert("Registered Successfully. Now login.");
      navigate("/");
    } catch (err) {
      console.log(err.response?.data || err);
      setError("Registration failed. Try again.");
    }
  };

  return (
    <div className="register-wrapper">
      <form className="register-box" onSubmit={submit}>
        <h2>Register</h2>

        {error && <div className="error">{error}</div>}

        <input
          placeholder="Username"
          value={form.username}
          onChange={(e) => setForm({ ...form, username: e.target.value })}
          required
        />
        <input
          placeholder="Full Name"
          value={form.first_name}
          onChange={(e) => setForm({ ...form, first_name: e.target.value })}
          required
        />
        <input
          placeholder="Phone"
          value={form.phone}
          onChange={(e) => setForm({ ...form, phone: e.target.value })}
          required
        />
        <input
          placeholder="Email"
          type="email"
          value={form.email}
          onChange={(e) => setForm({ ...form, email: e.target.value })}
          required
        />
        <select
          value={form.account_type}
          onChange={(e) => setForm({ ...form, account_type: e.target.value })}
        >
          <option value="savings">Savings</option>
          <option value="current">Current</option>
        </select>
        <input
          placeholder="Password"
          type="password"
          value={form.password}
          onChange={(e) => setForm({ ...form, password: e.target.value })}
          required
        />

        <button type="submit">Register</button>

        <p>
          Already have an account? <a href="/">Login here</a>
        </p>
      </form>
    </div>
  );
}
