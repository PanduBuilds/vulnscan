// API configuration
let apiBase = 'http://localhost:8087';

// If env var is set, use it
if (import.meta.env.VITE_API_BASE_URL) {
    apiBase = import.meta.env.VITE_API_BASE_URL;
}
// If we are on a real domain (not localhost), use relative path (let Nginx proxy handle it)
else if (typeof window !== 'undefined' && window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1') {
    apiBase = '';
}

export const API_BASE_URL = apiBase;
