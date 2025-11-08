  import React, { useState, useEffect, useContext } from 'react';
  import './AIInsights.css';
  import { getAIDashboard } from '../api/client';
  import { Sparkles, TrendingUp, AlertTriangle, CheckCircle, Users } from 'lucide-react';
  import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend } from 'recharts';
  import { DateFilterContext } from '../App';

  function AIInsights() {
    const { dateFilter } = useContext(DateFilterContext);
    const [summary, setSummary] = useState(null);
    const [closure, setClosure] = useState(null);
    const [compliance, setCompliance] = useState(null);
    const [predictions, setPredictions] = useState(null);
    const [teams, setTeams] = useState([]);
    const [trends, setTrends] = useState([]);
    const [sentiment, setSentiment] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
      fetchData();
    }, [dateFilter]);

    const fetchData = async () => {
      try {
        // Single comprehensive AI dashboard call
        const dashboardRes = await getAIDashboard(dateFilter);
        const data = dashboardRes.data;
        
        // Extract all sections from the comprehensive response
        setSummary(data.summary);
        setClosure(data.closure);
        setCompliance(data.compliance);
        setPredictions(data.predictions);
        setTeams(data.benchmarking.teams);
        setTrends(data.benchmarking.trends);
        setSentiment(data.sentiment);
        setLoading(false);
      } catch (error) {
        console.error('Error fetching AI insights:', error);
        setLoading(false);
      }
    };

    if (loading) {
      return <div className="loading">Loading AI insights...</div>;
    }

    return (
      <div className="ai-insights-page">
        <h1 className="page-title">AI Insights</h1>

        {/* AI Summary */}
        <div className="ai-summary-card">
          <div className="summary-icon">
            <Sparkles size={24} color="#10b981" />
          </div>
          <div className="summary-content">
            <h3>AI-Powered Summary</h3>
            <p>{summary.summary}</p>
          </div>
        </div>

        {/* Metrics Row */}
        <div className="metrics-row">
          <div className="metric-box">
            <div className="metric-icon">
              <TrendingUp size={20} color="#10b981" />
            </div>
            <div>
              <h4>Task Closure Performance</h4>
              <div className="metric-values">
                <div className="metric-item">
                  <span className="label">Current Avg</span>
                  <span className="value">{closure.current_avg}h</span>
                </div>
                <div className="metric-item">
                  <span className="label">Previous Avg</span>
                  <span className="value">{closure.previous_avg}h</span>
                </div>
              </div>
            </div>
          </div>

          <div className="metric-box">
            <div className="metric-icon">
              <AlertTriangle size={20} color="#f59e0b" />
            </div>
            <div>
              <h4>Blocked Tasks Alert</h4>
              <div className="metric-values">
                <div className="metric-item">
                  <span className="label">Blocked Tasks</span>
                  <span className="value danger">{closure.blocked_tasks}</span>
                </div>
                <div className="metric-item">
                  <span className="label">% of Total</span>
                  <span className="value">{closure.blocked_percentage}%</span>
                </div>
              </div>
            </div>
          </div>

          <div className="metric-box">
            <div className="metric-icon">
              <CheckCircle size={20} color="#3b82f6" />
            </div>
            <div>
              <h4>Due Date Compliance</h4>
              <div className="metric-values">
                <div className="metric-item">
                  <span className="label">Overdue</span>
                  <span className="value danger">{compliance.overdue}</span>
                </div>
                <div className="metric-item">
                  <span className="label">On Time</span>
                  <span className="value success">{compliance.on_time}</span>
                </div>
              </div>
            </div>
          </div>

          <div className="metric-box">
            <div className="metric-icon">
              <Users size={20} color="#8b5cf6" />
            </div>
            <div>
              <h4>In Progress Status</h4>
              <div className="metric-values">
                <div className="metric-item">
                  <span className="label">Active Tasks</span>
                  <span className="value">{compliance.active_tasks}</span>
                </div>
                <div className="metric-item">
                  <span className="label">Avg Active Time</span>
                  <span className="value">{compliance.avg_active_time}h</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Predictions */}
        <div className="predictions-card">
          <h3>Predictive Performance Analysis</h3>
          <p className="subtitle">Based on historical data patterns and current velocity</p>
          
          <div className="prediction-grid">
            <div className="prediction-item">
              <span className="pred-label">Projected Sprint Completion</span>
              <div className="progress-bar">
                <div className="progress-fill" style={{ width: `${predictions.sprint_completion}%` }}></div>
              </div>
              <span className="pred-value">{predictions.sprint_completion}%</span>
            </div>
            
            <div className="prediction-item">
              <span className="pred-label">Next Week Workload</span>
              <span className="pred-value-large">{predictions.next_week_workload}</span>
              <span className="pred-detail">~{predictions.expected_tasks} tasks expected</span>
            </div>
            
            <div className="prediction-item">
              <span className="pred-label">Risk Level</span>
              <span className="pred-value-large success">{predictions.risk_level}</span>
              <span className="pred-detail">{predictions.risk_description}</span>
            </div>
          </div>
        </div>

        {/* Team Benchmarking */}
        <div className="benchmarking-card">
          <div className="bench-header">
            <Users size={24} color="#10b981" />
            <div>
              <h3>Team Benchmarking</h3>
              <p>AI-powered comparison across teams</p>
            </div>
          </div>

          {/* Trends Chart */}
          <div className="trends-chart">
            <h4>4-Week Productivity Trends</h4>
            <ResponsiveContainer width="100%" height={250}>
              <LineChart data={trends}>
                <XAxis dataKey="week" stroke="#6b7280" />
                <YAxis stroke="#6b7280" />
                <Tooltip
                  contentStyle={{ background: '#1a1a2e', border: '1px solid #2a2a3e' }}
                />
                <Legend />
                <Line type="monotone" dataKey="your_team" stroke="#60a5fa" strokeWidth={2} name="Your Team" />
                <Line type="monotone" dataKey="alpha_team" stroke="#a78bfa" strokeWidth={2} name="Alpha Team" />
                <Line type="monotone" dataKey="beta_team" stroke="#10b981" strokeWidth={2} name="Beta Team" />
                <Line type="monotone" dataKey="gamma_team" stroke="#fbbf24" strokeWidth={2} name="Gamma Team" />
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* Team Cards */}
          <div className="team-cards-grid">
            {teams.map((team) => (
              <div key={team.name} className={`team-card ${team.rank === 1 ? 'top-rank' : ''}`}>
                {team.badge && <span className="badge">{team.badge}</span>}
                <h4>{team.name}</h4>
                <div className="team-stats">
                  <div className="stat">
                    <span className="stat-label">Total Tasks</span>
                    <span className="stat-value">{team.total_tasks}</span>
                  </div>
                  <div className="stat">
                    <span className="stat-label">Velocity</span>
                    <span className="stat-value">{team.velocity}/wk</span>
                  </div>
                  <div className="stat">
                    <span className="stat-label">Efficiency</span>
                    <span className="stat-value">{team.efficiency}%</span>
                  </div>
                  <div className="stat">
                    <span className="stat-label">Rank</span>
                    <span className="stat-value rank">#{team.rank}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Insights */}
          <div className="bench-insights">
            <Sparkles size={20} color="#10b981" />
            <div>
              <h4>Benchmarking Insights</h4>
              <p>Your team ranks #2 with 8 tasks behind Alpha Team. Velocity increased 22% over 4 weeks, outpacing Beta (+16%) and Gamma (+29%). Focus on efficiency improvements to reach #1 position.</p>
            </div>
          </div>
        </div>

        {/* Sentiment Analysis */}
        <div className="sentiment-card">
          <h3>Team Communication Sentiment</h3>
          <p className="subtitle">Analyzed from commit messages and task comments</p>
          
          <div className="sentiment-bars">
            <div className="sentiment-bar">
              <span className="bar-label">Positive</span>
              <div className="bar">
                <div className="bar-fill positive" style={{ width: `${sentiment.positive}%` }}></div>
              </div>
              <span className="bar-value">{sentiment.positive}%</span>
            </div>
            
            <div className="sentiment-bar">
              <span className="bar-label">Neutral</span>
              <div className="bar">
                <div className="bar-fill neutral" style={{ width: `${sentiment.neutral}%` }}></div>
              </div>
              <span className="bar-value">{sentiment.neutral}%</span>
            </div>
            
            <div className="sentiment-bar">
              <span className="bar-label">Negative</span>
              <div className="bar">
                <div className="bar-fill negative" style={{ width: `${sentiment.negative}%` }}></div>
              </div>
              <span className="bar-value">{sentiment.negative}%</span>
            </div>
          </div>

          <div className="sentiment-insight">
            <Sparkles size={18} color="#10b981" />
            <p>{sentiment.insight}</p>
          </div>
        </div>
      </div>
    );
  }

  export default AIInsights;

