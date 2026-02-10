import { useState } from "react";
import Api from "../../api";
import "./TransactionRequest.css";

export default function TransactionRequest({ accountId, onSuccess }) {
  const [requestType, setRequestType] = useState("deposit");
  const [amount, setAmount] = useState("");
  const [description, setDescription] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(""); setSuccess("");

    if (["deposit","withdrawal","loan_application"].includes(requestType) && (!amount || parseFloat(amount) <= 0)) {
      setError("Amount must be greater than 0");
      return;
    }

    try {
      await Api.post("userrequest/", {
        user: accountId,
        request_type: requestType,
        account: accountId,
        amount: parseFloat(amount) || 0,
        description: description || `${requestType} request`,
        status: "pending"
      }, { withCredentials: true });

      setSuccess(`${requestType} request submitted successfully! Waiting for admin approval.`);
      setAmount(""); setDescription("");

      if (onSuccess) onSuccess(); // Update dashboard balance
    } catch (err) {
      console.log(err.response?.data || err);
      setError(err.response?.data?.error || "Error submitting request");
    }
  };

  return (
    <div className="transaction-request">
      <h3>Create Transaction Request</h3>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Request Type</label>
          <select value={requestType} onChange={(e)=>setRequestType(e.target.value)} className="form-control">
            <option value="deposit">Deposit Money</option>
            <option value="withdrawal">Withdraw Money</option>
            <option value="account_issue">Account Issue</option>
            <option value="loan_application">Loan Application</option>
            <option value="other">Other</option>
          </select>
        </div>

        {["deposit","withdrawal","loan_application"].includes(requestType) && (
          <div className="form-group">
            <label>Amount (₹)</label>
            <input 
              type="number" step="0.01" min="0" 
              value={amount} 
              onChange={(e)=>setAmount(e.target.value)} 
              placeholder="Enter amount" 
              className="form-control"
              required
            />
          </div>
        )}

        <div className="form-group">
          <label>Description</label>
          <textarea 
            value={description} 
            onChange={(e)=>setDescription(e.target.value)}
            placeholder="Enter request description"
            className="form-control"
          />
        </div>

        {error && <div className="alert alert-error">{error}</div>}
        {success && <div className="alert alert-success">{success}</div>}

        <button type="submit" className="submit-btn">Submit Request</button>
      </form>
    </div>
  );
}
