// API configuration
// Uses Vite environment variable if available, otherwise falls back to localhost:8085
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8085';
