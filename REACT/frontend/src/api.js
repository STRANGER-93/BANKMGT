import axios from "axios";

const Api = axios.create({
  baseURL: "http://localhost:8000/api/",  // matches Django
  withCredentials: true,                  // needed for session auth
});

Api.defaults.xsrfCookieName = 'csrftoken';
Api.defaults.xsrfHeaderName = 'X-CSRFTOKEN';

export default Api;
