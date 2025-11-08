import axios from 'axios';
import { createClient } from '@supabase/supabase-js';

// Supabase configuration
const SUPABASE_URL = process.env.REACT_APP_SUPABASE_URL || 'https://xnefxjwmnyjfdvydmxtw.supabase.co';
const SUPABASE_ANON_KEY = process.env.REACT_APP_SUPABASE_ANON_KEY || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhuZWZ4andtbnlqZmR2eWRteHR3Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjIzNzMzMDEsImV4cCI6MjA3Nzk0OTMwMX0.CaN7dRmVvYynqusbxbrBaO6ULs23nSgaGSIdgEylQvI';

// Initialize Supabase client
export const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

// Backend API client (for complex queries and AI endpoints)
const API_BASE_URL = 'http://localhost:5001/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to all requests
apiClient.interceptors.request.use(async (config) => {
  const { data: { session } } = await supabase.auth.getSession();
  if (session?.access_token) {
    config.headers.Authorization = `Bearer ${session.access_token}`;
  }
  return config;
});

// ==================== SUPABASE REAL-TIME SUBSCRIPTIONS ====================

/**
 * Subscribe to real-time updates for tasks
 * @param {Function} callback - Function to call when tasks change
 * @returns {Function} Unsubscribe function
 */
export const subscribeToTasks = (callback) => {
  const channel = supabase
    .channel('tasks-changes')
    .on(
      'postgres_changes',
      {
        event: '*', // Listen to all changes (INSERT, UPDATE, DELETE)
        schema: 'public',
        table: 'tasks',
      },
      (payload) => {
        callback(payload);
      }
    )
    .subscribe();

  return () => {
    supabase.removeChannel(channel);
  };
};

/**
 * Subscribe to real-time updates for users
 * @param {Function} callback - Function to call when users change
 * @returns {Function} Unsubscribe function
 */
export const subscribeToUsers = (callback) => {
  const channel = supabase
    .channel('users-changes')
    .on(
      'postgres_changes',
      {
        event: '*',
        schema: 'public',
        table: 'users',
      },
      (payload) => {
        callback(payload);
      }
    )
    .subscribe();

  return () => {
    supabase.removeChannel(channel);
  };
};

/**
 * Subscribe to real-time updates for overview metrics
 * @param {Function} callback - Function to call when metrics change
 * @returns {Function} Unsubscribe function
 */
export const subscribeToOverview = (callback) => {
  const channel = supabase
    .channel('overview-changes')
    .on(
      'postgres_changes',
      {
        event: '*',
        schema: 'public',
        table: 'tasks',
      },
      () => {
        // When tasks change, fetch updated overview
        getOverview().then(response => callback(response.data));
      }
    )
    .subscribe();

  return () => {
    supabase.removeChannel(channel);
  };
};

// ==================== SUPABASE DIRECT QUERIES ====================

/**
 * Get tasks directly from Supabase with optional filters
 */
export const getTasksFromSupabase = async (filters = {}) => {
  let query = supabase.from('tasks').select('*');
  
  if (filters.status && filters.status !== 'All Tasks') {
    query = query.eq('status', filters.status);
  }
  if (filters.project) {
    query = query.eq('project', filters.project);
  }
  if (filters.assigned_to) {
    query = query.eq('assigned_to', filters.assigned_to);
  }
  if (filters.priority) {
    query = query.eq('priority', filters.priority);
  }
  if (filters.search) {
    query = query.ilike('task_name', `%${filters.search}%`);
  }
  if (filters.start_date && filters.end_date) {
    query = query.gte('created_date', filters.start_date).lte('created_date', filters.end_date);
  }
  
  const { data, error } = await query.order('created_date', { ascending: false });
  
  if (error) throw error;
  return { data };
};

/**
 * Get users directly from Supabase
 */
export const getUsersFromSupabase = async (search = '') => {
  let query = supabase.from('users').select('*');
  
  if (search) {
    query = query.ilike('name', `%${search}%`);
  }
  
  const { data, error } = await query;
  
  if (error) throw error;
  return { data };
};

/**
 * Get a single task from Supabase
 */
export const getTaskFromSupabase = async (taskId) => {
  const { data, error } = await supabase
    .from('tasks')
    .select('*')
    .eq('task_id', taskId)
    .single();
  
  if (error) throw error;
  return { data };
};

/**
 * Get a single user from Supabase
 */
export const getUserFromSupabase = async (userId) => {
  const { data, error } = await supabase
    .from('users')
    .select('*')
    .eq('user_id', userId)
    .single();
  
  if (error) throw error;
  return { data };
};

// ==================== DATE FILTER UTILITY ====================

/**
 * Get date range based on filter type
 * @param {string} filter - 'today', 'week', 'month', 'year', 'all'
 * @returns {Object} { start_date, end_date } or null for 'all'
 */
export const getDateRange = (filter) => {
  const now = new Date();
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
  
  switch (filter) {
    case 'today':
      return {
        start_date: today.toISOString(),
        end_date: new Date(today.getTime() + 24 * 60 * 60 * 1000).toISOString()
      };
    case 'week':
      const weekStart = new Date(today);
      weekStart.setDate(today.getDate() - today.getDay()); // Start of week (Sunday)
      return {
        start_date: weekStart.toISOString(),
        end_date: now.toISOString()
      };
    case 'month':
      const monthStart = new Date(today.getFullYear(), today.getMonth(), 1);
      return {
        start_date: monthStart.toISOString(),
        end_date: now.toISOString()
      };
    case 'year':
      const yearStart = new Date(today.getFullYear(), 0, 1);
      return {
        start_date: yearStart.toISOString(),
        end_date: now.toISOString()
      };
    case 'all':
    default:
      return null; // No date filter
  }
};

// ==================== BACKEND API ENDPOINTS (for complex queries) ====================

// Overview endpoints
export const getOverview = (dateFilter = 'all') => {
  const dateRange = getDateRange(dateFilter);
  const params = dateRange ? { start_date: dateRange.start_date, end_date: dateRange.end_date } : {};
  return apiClient.get('/overview', { params });
};

export const getDistribution = (dateFilter = 'all') => {
  const dateRange = getDateRange(dateFilter);
  const params = dateRange ? { start_date: dateRange.start_date, end_date: dateRange.end_date } : {};
  return apiClient.get('/distribution', { params });
};

export const getTrends = (dateFilter = 'all') => {
  const dateRange = getDateRange(dateFilter);
  const params = dateRange ? { start_date: dateRange.start_date, end_date: dateRange.end_date } : {};
  return apiClient.get('/trends', { params });
};

export const getTeams = () => apiClient.get('/teams');

export const getTeamPerformance = (dateFilter = 'all', teamFilter = 'all') => {
  const dateRange = getDateRange(dateFilter);
  const params = {};
  if (dateRange) {
    params.start_date = dateRange.start_date;
    params.end_date = dateRange.end_date;
  }
  if (teamFilter && teamFilter !== 'all') {
    params.team = teamFilter;
  }
  return apiClient.get('/team-performance', { params });
};

// Tasks endpoints (using backend for complex queries, or Supabase for simple ones)
export const getTasks = (filters = {}, dateFilter = 'all') => {
  const dateRange = getDateRange(dateFilter);
  if (dateRange) {
    filters.start_date = dateRange.start_date;
    filters.end_date = dateRange.end_date;
  }
  
  // Use Supabase for simple queries, backend for complex aggregations
  if (Object.keys(filters).length === 0 || (filters.status && filters.status === 'All Tasks' && !filters.search)) {
    return getTasksFromSupabase(filters).then(result => ({ data: result.data }));
  }
  const params = new URLSearchParams(filters).toString();
  return apiClient.get(`/tasks${params ? '?' + params : ''}`);
};

export const getTask = (taskId) => {
  return getTaskFromSupabase(taskId).then(result => ({ data: result.data }));
};

export const getProjects = () => apiClient.get('/projects');
export const getProjectStats = () => apiClient.get('/projects/stats');

// Users endpoints
export const getUsers = (search = '') => {
  return getUsersFromSupabase(search).then(result => ({ data: result.data }));
};

export const getUser = (userId) => {
  return getUserFromSupabase(userId).then(result => ({ data: result.data }));
};

// AI Insights endpoints (backend only - complex calculations)
export const getAISummary = (dateFilter = 'all') => {
  const dateRange = getDateRange(dateFilter);
  const params = dateRange ? { start_date: dateRange.start_date, end_date: dateRange.end_date } : {};
  return apiClient.get('/ai/summary', { params });
};

export const getClosurePerformance = (dateFilter = 'all') => {
  const dateRange = getDateRange(dateFilter);
  const params = dateRange ? { start_date: dateRange.start_date, end_date: dateRange.end_date } : {};
  return apiClient.get('/ai/closure-performance', { params });
};

export const getDueCompliance = (dateFilter = 'all') => {
  const dateRange = getDateRange(dateFilter);
  const params = dateRange ? { start_date: dateRange.start_date, end_date: dateRange.end_date } : {};
  return apiClient.get('/ai/due-compliance', { params });
};

export const getPredictions = (dateFilter = 'all') => {
  const dateRange = getDateRange(dateFilter);
  const params = dateRange ? { start_date: dateRange.start_date, end_date: dateRange.end_date } : {};
  return apiClient.get('/ai/predictions', { params });
};

export const getTeamBenchmarking = (dateFilter = 'all') => {
  const dateRange = getDateRange(dateFilter);
  const params = dateRange ? { start_date: dateRange.start_date, end_date: dateRange.end_date } : {};
  return apiClient.get('/ai/team-benchmarking', { params });
};

export const getProductivityTrends = (dateFilter = 'all') => {
  const dateRange = getDateRange(dateFilter);
  const params = dateRange ? { start_date: dateRange.start_date, end_date: dateRange.end_date } : {};
  return apiClient.get('/ai/productivity-trends', { params });
};

export const getSentiment = (dateFilter = 'all') => {
  const dateRange = getDateRange(dateFilter);
  const params = dateRange ? { start_date: dateRange.start_date, end_date: dateRange.end_date } : {};
  return apiClient.get('/ai/sentiment', { params });
};

// Comprehensive AI Dashboard (single endpoint for all AI insights)
export const getAIDashboard = (dateFilter = 'all') => {
  const dateRange = getDateRange(dateFilter);
  const params = dateRange ? { start_date: dateRange.start_date, end_date: dateRange.end_date } : {};
  return apiClient.get('/ai/dashboard', { params });
};

// Chat endpoint
export const sendChatQuery = (query) => apiClient.post('/chat', { query });

// Settings endpoints
export const getSettings = () => apiClient.get('/settings');
export const saveSettings = (settings) => apiClient.post('/settings', settings);

export default apiClient;
