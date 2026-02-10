import { BrowserRouter, Routes, Route } from "react-router-dom";
import Login from "./components/auth/Login";
import Register from "./components/auth/Register";
import Dashboard from "./components/user/Dashboard";
import TransactionRequest from "./components/user/TransactionRequest";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Home */}
        <Route path="/" element={<Login />} />

        {/* Auth */}
        <Route path="/register" element={<Register />} />

        {/* User */}
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/request" element={<TransactionRequest />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
