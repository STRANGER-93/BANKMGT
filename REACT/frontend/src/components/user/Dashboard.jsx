import { useEffect, useState } from "react";
import Api from "../../api";
import TransactionRequest from "./TransactionRequest";
import "./Dashboard.css";

export default function Dashboard() {
  const [account, setAccount] = useState(null);

  useEffect(() => {
    Api.get("user/accounts/", { withCredentials: true })
      .then((res) => {
        setAccount(res.data[0]);
      })
      .catch((err) => console.log(err));
  }, []);

  if (!account) return <p className="container">Loading...</p>;

  return (
    <div className="dashboard">
      <h2>Welcome, {account.user_name || account.username}</h2>

      <p>
        <strong>Account Number:</strong> {account.account_number}
      </p>
      <p>
        <strong>Account Type:</strong> {account.account_type}
      </p>
      <p>
        <strong>Balance:</strong> Rs{account.balance}
      </p>

      <TransactionRequest accountId={account.id} />
    </div>
  );
}
