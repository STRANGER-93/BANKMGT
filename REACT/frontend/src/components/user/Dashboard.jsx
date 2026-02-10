import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import Api from "../../api";
import TransactionRequest from "./TransactionRequest";
import "./Dashboard.css";

export default function Dashboard() {
  const [account, setAccount] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  const fetchAccount = async () => {
    try {
      const res = await Api.get("user/accounts/", { withCredentials: true });
      if (res.data.length > 0) setAccount(res.data[0]);
    } catch (err) {
      console.log(err);
      navigate("/");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAccount();
  }, []);

  const logoutUser = async () => {
    try {
      await Api.post("logout/", {}, { withCredentials: true });
      navigate("/");
    } catch (err) {
      console.log(err);
    }
  };

  // Polling to auto-update balance every 5 seconds
  useEffect(() => {
    const interval = setInterval(fetchAccount, 5000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="loading-screen">
        <div className="spinner"></div>
        <p>Loading your account...</p>
      </div>
    );
  }

  if (!account) {
    return (
      <div className="no-account">
        <h2>No account found</h2>
        <p>Please contact support to create an account.</p>
      </div>
    );
  }

  return (
    <div className="dashboard-container">
      {/* Navigation */}
      <nav className="dashboard-nav">
        <div className="nav-left">
          <div className="logo">
            <span className="logo-icon">🏦</span>
            <span className="logo-text">SecureBank</span>
          </div>
        </div>
        <div className="nav-right">
          <div className="user-profile">
            <span className="user-avatar">👤</span>
            <div className="user-details">
              <span className="user-name">{account.user_name}</span>
              <span className="user-role">Customer</span>
            </div>
          </div>
          <button onClick={logoutUser} className="logout-btn">
            <span className="logout-icon">🚪</span> Logout
          </button>
        </div>
      </nav>

      {/* Main Content */}
      <main className="dashboard-main">
        <div className="welcome-section">
          <h1 className="welcome-title">Welcome back, {account.user_name}!</h1>
          <p className="welcome-subtitle">Manage your finances securely</p>
          <div className="current-time">
            🕒 {new Date().toLocaleDateString("en-US", {
              weekday: "long",
              year: "numeric",
              month: "long",
              day: "numeric",
            })}
          </div>
        </div>

        <div className="summary-cards">
          <div className="summary-card">
            <div className="card-header">
              💰 Account Balance
            </div>
            <div className="card-content">
              <div className="amount">₹ {parseFloat(account.balance).toLocaleString()}</div>
              <div className="card-subtext">Available for withdrawal</div>
            </div>
          </div>

          <div className="summary-card">
            <div className="card-header">
              🏦 Account Details
            </div>
            <div className="card-content">
              <div className="account-number-display">{account.account_number}</div>
              <div className="card-subtext">
                <span className="account-type-badge">{account.account_type}</span>
                <span className={`status-badge ${account.status}`}>{account.status}</span>
              </div>
            </div>
          </div>
        </div>

        <div className="main-content-grid">
          <div className="content-column">
            <TransactionRequest 
              accountId={account.id} 
              onSuccess={fetchAccount} // Refresh balance after request
            />
          </div>
        </div>
      </main>
    </div>
  );
}
