import { useState } from "react";
import Api from "../../api";
import "./Transaction.css";

export default function TransactionRequest({ accountId }) {
  const [amount, setAmount] = useState("");
  const [type, setType] = useState("deposit");
  const [message, setMessage] = useState("");

  const submit = async () => {
    setMessage("");
    if (!amount || amount <= 0) {
      setMessage("Enter a valid amount");
      return;
    }

    try {
      await Api.post(
        "userrequest/",
        {
          request_type: type,
          amount: amount,
          account: accountId,
          description: `${type} request`,
        },
        { withCredentials: true }
      );
      setMessage("Request sent to admin");
      setAmount("");
    } catch (err) {
      console.log(err);
      setMessage("Request failed. Try again.");
    }
  };

  return (
    <div className="transaction-request">
      <h3>Transaction Request</h3>

      {message && <div>{message}</div>}

      <select value={type} onChange={(e) => setType(e.target.value)}>
        <option value="deposit">Deposit</option>
        <option value="withdrawal">Withdraw</option>
      </select>

      <input
        type="number"
        placeholder="Amount"
        value={amount}
        onChange={(e) => setAmount(e.target.value)}
      />

      <button onClick={submit}>Send Request</button>
    </div>
  );
}
