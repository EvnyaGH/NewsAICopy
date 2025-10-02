import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080';

const apiClient = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    },
    timeout: 10000,
    withCredentials: true,
});

export const api = {
    // login
    login: async (credentials) => {
        return apiClient.post('/api/v1/login', credentials);
    },

    // register
    register: async (userData) => {
        return apiClient.post('/api/v1/register', userData);
    },

    // verify email
    verifyEmail: async (token) => {
        return apiClient.post('/api/v1/verify-email', {token});
    },

    // resend email verification
    resendEmailVerification: async (credentials) => {
        return apiClient.post('/api/v1/resend-email-verification', credentials);
    },

    // logout
    logout: async () => {
        return apiClient.post('/api/v1/logout', {});
    },

    // check current user
    getCurrentUser: async () => {
        return apiClient.get('/api/v1/users/me');
    },

    // get news feed
    // getFeed: async (page = 1, limit = 10) => {
    //     return apiClient.get(`/api/v1/news/feed?page=${page}&limit=${limit}`);
    // },

    //get news feed with optional category filter
    getFeed: async (page = 1, limit = 10, category /* 可选 */) => {
        const params = new URLSearchParams({ page, limit });
        if (category) params.set("category", category);
        return apiClient.get(`/api/v1/news/feed?${params.toString()}`);
    },

    // get article detail
    getArticle: async (articleId) => {
        return apiClient.get(`/api/v1/news/articles/${articleId}`);
    },

    // search articles
    searchArticles: async (query, page = 1, limit = 10) => {
        return apiClient.get(`/api/v1/news/search?q=${encodeURIComponent(query)}&page=${page}&limit=${limit}`);
    },

    // bookmark management
    bookmarkArticle: async (articleId) => {
        return apiClient.post(`/api/v1/bookmarks/${articleId}`);
    },

    unbookmarkArticle: async (articleId) => {
        return apiClient.delete(`/api/v1/bookmarks/${articleId}`);
    },

    getBookmarks: async (page = 1, limit = 10) => {
        return apiClient.get(`/api/v1/bookmarks?page=${page}&limit=${limit}`);
    },

    // get fields and subtopics
    getFields: async () => {
        return apiClient.get('/api/v1/fields');
    },

    // get user interests
    getInterests: async () => {
        return apiClient.get('/api/v1/users/me/interests');
    },

    // update user interests
    updateInterests: async (payload /* { fields: string[], subtopics: string[] } */) => {
        return apiClient.put('/api/v1/users/me/interests', payload);
    },

};