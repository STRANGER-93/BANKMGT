import axios from "axios";

const Api = axios.create({
  baseURL: "http://localhost:8000/api/",
  withCredentials: true, // important for session auth
});

export default Api;