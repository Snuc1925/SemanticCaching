import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import App from './App';
import { initAuth } from './auth';
import './styles.css';

const root = ReactDOM.createRoot(document.getElementById('root')!);

initAuth()
  .then(() =>
    root.render(
      <React.StrictMode>
        <BrowserRouter>
          <App />
        </BrowserRouter>
      </React.StrictMode>,
    ),
  )
  .catch((e) => {
    root.render(
      <div style={{ padding: 32 }}>
        <h2>Không kết nối được máy chủ đăng nhập</h2>
        <p>Kiểm tra Keycloak đang chạy ở {import.meta.env.VITE_KEYCLOAK_URL ?? 'http://localhost:8080'} rồi tải lại trang.</p>
        <pre>{String(e?.message ?? e)}</pre>
      </div>,
    );
  });
