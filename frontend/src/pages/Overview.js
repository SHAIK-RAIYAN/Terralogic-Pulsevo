import React, { useState, useEffect, useContext } from 'react';
import './Overview.css';
import { getOverview, getDistribution, getTrends, getTeamPerformance, getTeams } from '../api/client';
import { PieChart, Pie, Cell, LineChart, Line, BarChart, Bar, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { TrendingUp, TrendingDown, Clock } from 'lucide-react';
import { DateFilterContext } from '../App';

function Overview() {
  const { dateFilter } = useContext(DateFilterContext);
  const [metrics, setMetrics] = useState(null);
  const [distribution, setDistribution] = useState([]);
  const [trends, setTrends] = useState([]);
  const [teamPerformance, setTeamPerformance] = useState([]);
  const [teams, setTeams] = useState([]);
  const [selectedTeam, setSelectedTeam] = useState('all');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchTeams();
  }, []);

  useEffect(() => {
    fetchData();
    // Auto-refresh every 10 seconds
    const interval = setInterval(fetchData, 10000);
    return () => clearInterval(interval);
  }, [dateFilter, selectedTeam]);

  const fetchTeams = async () => {
    try {
      const response = await getTeams();
      setTeams(response.data);
    } catch (error) {
      console.error('Error fetching teams:', error);
    }
  };

  const fetchData = async () => {
    try {
      const [metricsRes, distRes, trendsRes, teamRes] = await Promise.all([
        getOverview(dateFilter),
        getDistribution(dateFilter),
        getTrends(dateFilter),
        getTeamPerformance(dateFilter, selectedTeam)
      ]);
      
      setMetrics(metricsRes.data);
      setDistribution(distRes.data);
      setTrends(trendsRes.data);
      setTeamPerformance(teamRes.data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching overview data:', error);
      // Set default empty data to prevent crashes
      setMetrics({
        open_tasks: 0,
        open_change: 0,
        in_progress: 0,
        progress_change: 0,
        completed_today: 0,
        today_change: 0,
        completion_rate: 0,
        rate_change: 0,
        total_tasks: 0
      });
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="loading">Loading dashboard...</div>;
  }

  if (!metrics) {
    return <div className="loading">Unable to load data. Please check your connection.</div>;
  }

  return (
    <div className="overview-page">
      <h1 className="page-title">Overview</h1>
      
      {/* Metric Cards */}
      <div className="metrics-grid">
        <MetricCard
          title="Open Tasks"
          value={metrics.open_tasks}
          change={metrics.open_change}
          color="blue"
        />
        <MetricCard
          title="In Progress"
          value={metrics.in_progress}
          change={metrics.progress_change}
          color="green"
        />
        <MetricCard
          title="Closed Today"
          value={metrics.completed_today}
          change={metrics.today_change}
          color="green"
        />
        <MetricCard
          title="Completion Rate"
          value={`${metrics.completion_rate}%`}
          change={metrics.rate_change}
          color="green"
        />
      </div>

      {/* Charts Row */}
      <div className="charts-row">
        {/* Task Distribution */}
        <div className="chart-card">
          <h3 className="chart-title">Task Distribution ({metrics.total_tasks})</h3>
          <div className="pie-chart-container">
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={distribution}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={100}
                  paddingAngle={2}
                  dataKey="value"
                >
                  {distribution.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
            <div className="pie-legend">
              {distribution.map((item, index) => (
                <div key={index} className="pie-legend-item">
                  <div className="legend-color" style={{ background: item.color }}></div>
                  <span>{item.name}: {item.value}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* 7-Day Trend Analysis */}
        <div className="chart-card">
          <h3 className="chart-title">Trend Analysis</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={trends}>
              <XAxis dataKey="date" stroke="#6b7280" />
              <YAxis stroke="#6b7280" />
              <Tooltip 
                contentStyle={{ background: '#1a1a2e', border: '1px solid #2a2a3e' }}
              />
              <Legend />
              <Line 
                type="monotone" 
                dataKey="completed" 
                stroke="#10b981" 
                strokeWidth={2}
                name="Tasks Completed"
              />
              <Line 
                type="monotone" 
                dataKey="created" 
                stroke="#60a5fa" 
                strokeWidth={2}
                name="Tasks Created"
              />
              <Line 
                type="monotone" 
                dataKey="in_progress" 
                stroke="#a78bfa" 
                strokeWidth={2}
                name="Tasks In Progress"
              />
            </LineChart>
          </ResponsiveContainer>
          <div className="trend-stats">
            <div className="stat">
              <span className="stat-label">Avg. Daily Completion</span>
              <span className="stat-value">
                {trends.length > 0 
                  ? (trends.reduce((sum, t) => sum + t.completed, 0) / trends.length).toFixed(1)
                  : '0.0'} tasks
              </span>
            </div>
            <div className="stat">
              <span className="stat-label">Avg. Daily Creation</span>
              <span className="stat-value">
                {trends.length > 0 
                  ? (trends.reduce((sum, t) => sum + t.created, 0) / trends.length).toFixed(1)
                  : '0.0'} tasks
              </span>
            </div>
            <div className="stat">
              <span className="stat-label">Avg. In Progress</span>
              <span className="stat-value">
                {trends.length > 0 
                  ? (trends.reduce((sum, t) => sum + t.in_progress, 0) / trends.length).toFixed(1)
                  : '0.0'} tasks
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Team Performance */}
      <div className="chart-card full-width">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
          <h3 className="chart-title">Team Performance</h3>
          <select 
            value={selectedTeam}
            onChange={(e) => setSelectedTeam(e.target.value)}
            style={{
              padding: '8px 16px',
              borderRadius: '6px',
              border: '1px solid #2a2a3e',
              background: '#1a1a2e',
              color: '#e5e7eb',
              fontSize: '14px',
              cursor: 'pointer'
            }}
          >
            <option value="all">All Teams</option>
            {teams.map((team) => (
              <option key={team} value={team}>{team}</option>
            ))}
          </select>
        </div>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={teamPerformance}>
            <XAxis dataKey="name" stroke="#6b7280" />
            <YAxis stroke="#6b7280" />
            <Tooltip 
              contentStyle={{ background: '#1a1a2e', border: '1px solid #2a2a3e' }}
            />
            <Legend />
            <Bar dataKey="completed" fill="#10b981" name="Completed" />
            <Bar dataKey="in_progress" fill="#60a5fa" name="In Progress" />
            <Bar dataKey="open" fill="#a78bfa" name="Open" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

function MetricCard({ title, value, change, color, subtitle }) {
  const isPositive = change > 0;
  const isNegative = change < 0;
  
  return (
    <div className={`metric-card ${color}`}>
      <div className="metric-header">
        <span className="metric-title">{title}</span>
      </div>
      <div className="metric-value">{value}</div>
      {subtitle && <div className="metric-subtitle"><Clock size={14} /> {subtitle}</div>}
      <div className={`metric-change ${isPositive ? 'positive' : isNegative ? 'negative' : ''}`}>
        {isPositive ? <TrendingUp size={14} /> : isNegative ? <TrendingDown size={14} /> : null}
        <span>{Math.abs(change)}% vs last week</span>
      </div>
    </div>
  );
}

export default Overview;

