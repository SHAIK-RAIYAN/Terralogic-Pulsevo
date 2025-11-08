import React, { useState, useEffect, useCallback, useContext } from 'react';
import './Tasks.css';
import { getTasks, getUsers, getProjectStats } from '../api/client';
import { Search, Upload, TrendingUp, TrendingDown } from 'lucide-react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';
import { DateFilterContext } from '../App';

function Tasks() {
  const { dateFilter } = useContext(DateFilterContext);
  const [tasks, setTasks] = useState([]);
  const [users, setUsers] = useState([]);
  const [projectStats, setProjectStats] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('All Tasks');
  const [assigneeFilter, setAssigneeFilter] = useState('all');
  const [showUpload, setShowUpload] = useState(false);
  
  // Pagination state
  const [currentPage, setCurrentPage] = useState(1);
  const tasksPerPage = 10;

  const fetchData = useCallback(async () => {
    try {
      const filters = {};
      if (statusFilter !== 'All Tasks') filters.status = statusFilter;
      if (assigneeFilter !== 'all') filters.assigned_to = assigneeFilter;
      if (searchTerm) filters.search = searchTerm;
      
      const [tasksRes, usersRes, statsRes] = await Promise.all([
        getTasks(filters, dateFilter),
        getUsers(),
        getProjectStats()
      ]);
      
      setTasks(tasksRes.data);
      setUsers(usersRes.data);
      setProjectStats(statsRes.data);
      setLoading(false);
      setCurrentPage(1); // Reset to first page when filters change
    } catch (error) {
      console.error('Error fetching tasks:', error);
      setLoading(false);
    }
  }, [statusFilter, assigneeFilter, searchTerm, dateFilter]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  // Pagination calculations
  const totalPages = Math.ceil(tasks.length / tasksPerPage);
  const indexOfLastTask = currentPage * tasksPerPage;
  const indexOfFirstTask = indexOfLastTask - tasksPerPage;
  const currentTasks = tasks.slice(indexOfFirstTask, indexOfLastTask);

  const handlePageChange = (pageNumber) => {
    setCurrentPage(pageNumber);
  };

  const handlePrevious = () => {
    if (currentPage > 1) {
      setCurrentPage(currentPage - 1);
    }
  };

  const handleNext = () => {
    if (currentPage < totalPages) {
      setCurrentPage(currentPage + 1);
    }
  };

  // Generate page numbers to display
  const getPageNumbers = () => {
    const pages = [];
    const maxPagesToShow = 5;
    
    if (totalPages <= maxPagesToShow) {
      // Show all pages if total is less than max
      for (let i = 1; i <= totalPages; i++) {
        pages.push(i);
      }
    } else {
      // Show first page, current page area, and last page
      if (currentPage <= 3) {
        for (let i = 1; i <= 4; i++) pages.push(i);
        pages.push('...');
        pages.push(totalPages);
      } else if (currentPage >= totalPages - 2) {
        pages.push(1);
        pages.push('...');
        for (let i = totalPages - 3; i <= totalPages; i++) pages.push(i);
      } else {
        pages.push(1);
        pages.push('...');
        pages.push(currentPage - 1);
        pages.push(currentPage);
        pages.push(currentPage + 1);
        pages.push('...');
        pages.push(totalPages);
      }
    }
    
    return pages;
  };

  // Prepare project charts data
  const projectTasksData = projectStats.map((p, i) => ({
    name: p.project,
    value: p.total,
    color: ['#ec4899', '#60a5fa', '#fbbf24'][i]
  }));

  const projectIssuesData = projectStats.map((p, i) => ({
    name: p.project,
    value: p.open,
    color: ['#ec4899', '#60a5fa', '#fbbf24'][i]
  }));

  if (loading) {
    return <div className="loading">Loading tasks...</div>;
  }

  return (
    <div className="tasks-page">
      <div className="tasks-header">
        <h1 className="page-title">Tasks</h1>
        <button className="upload-button" onClick={() => setShowUpload(!showUpload)}>
          <Upload size={18} />
          Upload
        </button>
      </div>

      {showUpload && (
        <div className="upload-modal">
          <div className="upload-content">
            <h3>Upload Files</h3>
            <div className="upload-area">
              <Upload size={48} color="#60a5fa" />
              <p>Drag and drop files here, or click to browse</p>
              <p className="upload-hint">PDF, DOCX, JPG, PNG up to 10MB each</p>
              <button className="browse-button">Browse Files</button>
            </div>
            <button className="close-upload" onClick={() => setShowUpload(false)}>Close</button>
          </div>
        </div>
      )}

      <div className="tasks-content">
        {/* Left Section - Task Management */}
        <div className="tasks-left">
          <div className="task-management-card">
            <h2 className="card-title">Task Management</h2>
            
            <div className="task-filters">
              <div className="search-box">
                <Search size={18} />
                <input
                  type="text"
                  placeholder="Search tasks..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </div>
              
              <select 
                className="status-filter"
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
              >
                <option>All Tasks</option>
                <option>Open</option>
                <option>In Progress</option>
                <option>Completed</option>
                <option>Blocked</option>
              </select>

              <select 
                className="assignee-filter"
                value={assigneeFilter}
                onChange={(e) => setAssigneeFilter(e.target.value)}
              >
                <option value="all">All Assignees</option>
                {users.map(user => (
                  <option key={user.user_id} value={user.user_id}>{user.name}</option>
                ))}
              </select>
            </div>

            <div className="tasks-table">
              <div className="table-header">
                <div className="th task-name">Task Name</div>
                <div className="th assignee">Assignee</div>
                <div className="th status">Status</div>
                <div className="th priority">Priority</div>
                <div className="th due-date">Due Date</div>
              </div>
              
              <div className="table-body">
                {tasks.length === 0 ? (
                  <div className="no-tasks">No tasks found</div>
                ) : (
                  currentTasks.map((task) => {
                    const assignee = users.find(u => u.user_id === task.assigned_to);
                    return (
                      <div key={task.task_id} className="table-row">
                        <div className="td task-name">{task.task_name}</div>
                        <div className="td assignee">
                          {assignee && (
                            <>
                              <div className="user-avatar-small" style={{
                                background: getAvatarColor(assignee.initials)
                              }}>
                                {assignee.initials}
                              </div>
                              <span>{assignee.name}</span>
                            </>
                          )}
                        </div>
                        <div className="td status">
                          <span className={`status-badge status-${task.status.toLowerCase().replace(' ', '-')}`}>
                            {task.status}
                          </span>
                        </div>
                        <div className="td priority">
                          <span className={`priority-badge priority-${task.priority.toLowerCase()}`}>
                            {task.priority}
                          </span>
                        </div>
                        <div className="td due-date">
                          {task.due_date ? new Date(task.due_date).toLocaleDateString() : '-'}
                        </div>
                      </div>
                    );
                  })
                )}
              </div>
            </div>

            {tasks.length > 0 && (
              <div className="pagination">
                <button 
                  className="page-btn" 
                  onClick={handlePrevious}
                  disabled={currentPage === 1}
                >
                  Previous
                </button>
                
                {getPageNumbers().map((page, index) => (
                  page === '...' ? (
                    <span key={`ellipsis-${index}`} className="page-ellipsis">...</span>
                  ) : (
                    <button
                      key={page}
                      className={`page-btn ${currentPage === page ? 'active' : ''}`}
                      onClick={() => handlePageChange(page)}
                    >
                      {page}
                    </button>
                  )
                ))}
                
                <button 
                  className="page-btn" 
                  onClick={handleNext}
                  disabled={currentPage === totalPages}
                >
                  Next
                </button>
                
                <span className="page-info">
                  Showing {indexOfFirstTask + 1}-{Math.min(indexOfLastTask, tasks.length)} of {tasks.length}
                </span>
              </div>
            )}
          </div>
        </div>

        {/* Right Section - Charts */}
        <div className="tasks-right">
          {/* Tasks by Project */}
          <div className="project-chart-card">
            <h3 className="chart-title">Tasks by Project</h3>
            <ResponsiveContainer width="100%" height={200}>
              <PieChart>
                <Pie
                  data={projectTasksData}
                  cx="50%"
                  cy="50%"
                  innerRadius={40}
                  outerRadius={80}
                  dataKey="value"
                >
                  {projectTasksData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
            <div className="chart-legend">
              {projectTasksData.map((item, i) => (
                <div key={i} className="legend-item">
                  <div className="legend-dot" style={{ background: item.color }}></div>
                  <span>{item.name}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Open Issues by Project */}
          <div className="project-chart-card">
            <h3 className="chart-title">Open Issues by Project</h3>
            <ResponsiveContainer width="100%" height={200}>
              <PieChart>
                <Pie
                  data={projectIssuesData}
                  cx="50%"
                  cy="50%"
                  innerRadius={40}
                  outerRadius={80}
                  dataKey="value"
                >
                  {projectIssuesData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
            <div className="chart-legend">
              {projectIssuesData.map((item, i) => (
                <div key={i} className="legend-item">
                  <div className="legend-dot" style={{ background: item.color }}></div>
                  <span>{item.name}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function getAvatarColor(initials) {
  const colors = [
    'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
    'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
    'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
    'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
  ];
  const hash = initials.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0);
  return colors[hash % colors.length];
}

export default Tasks;

