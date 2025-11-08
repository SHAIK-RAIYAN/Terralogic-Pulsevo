# PULSEVO - Team Productivity Dashboard

A real-time team productivity dashboard with AI-powered insights, built for the Hackathon Nellore 2025.

## 🚀 Features

- **Real-Time Dashboard**: Live metrics for team performance and task tracking
- **Task Management**: Comprehensive task tracking with filters and search
- **AI Insights**: AI-powered summaries, predictions, and sentiment analysis
- **Team Benchmarking**: Compare team performance across multiple metrics
- **Conversational Queries**: Natural language interface for data queries
- **Multi-Project Support**: Track tasks across Web Platform, Mobile App, and API Services

## 🏗️ Tech Stack

### Backend
- **Flask** - Python web framework
- **SQLite3** - Lightweight database
- **Flask-SQLAlchemy** - ORM for database operations
- **Flask-CORS** - Cross-origin resource sharing

### Frontend
- **React 18** - UI library
- **Recharts** - Beautiful charts and visualizations
- **Axios** - HTTP client
- **Lucide React** - Modern icon library

## 📁 Project Structure

```
PULSEVO/
├── backend/                    # Flask Backend
│   ├── app.py                 # Main Flask application
│   ├── models.py              # Database models (Users, Tasks)
│   ├── database.py            # Database configuration
│   ├── seed_data.py           # Sample data generator
│   ├── pulsevo.db            # SQLite database (generated)
│   └── requirements.txt       # Python dependencies
│
├── frontend/                   # React Frontend
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── components/        # Reusable components
│   │   │   ├── Navbar.js
│   │   │   └── Sidebar.js
│   │   ├── pages/            # Main pages
│   │   │   ├── Overview.js
│   │   │   ├── Tasks.js
│   │   │   ├── AIInsights.js
│   │   │   ├── Queries.js
│   │   │   └── Settings.js
│   │   ├── api/
│   │   │   └── client.js     # API calls
│   │   ├── App.js
│   │   └── index.js
│   └── package.json
│
└── README.md
```

## ⚙️ Setup Instructions

### Prerequisites

- **Python 3.8+** installed
- **Node.js 16+** and npm installed
- Terminal/Command Prompt

### Backend Setup

1. **Navigate to backend directory**
```bash
cd /Terralogic-Pulsevo/backend
```

2. **Install Python dependencies**
```bash
pip3 install -r requirements.txt
```

3. **Generate sample data**
```bash
python3 seed_data.py
```

You should see output like:
```
🌱 Starting database seeding...
✅ Cleared existing data
✅ Created 11 users
✅ Created 100 tasks
✅ Database seeding completed successfully!
```

4. **Start the Flask server**
```bash
python3 app.py
```

The backend will run on **http://localhost:5000**

### Frontend Setup

1. **Open a new terminal window**

2. **Navigate to frontend directory**
```bash
cd /Terralogic-Pulsevo/frontend
```

3. **Install Node dependencies**
```bash
npm install
```

4. **Start the React development server**
```bash
npm start
```

The frontend will automatically open at **http://localhost:3000**

## 🎯 Using the Application

### Overview Page
- View real-time metrics: Open Tasks, In Progress, Closed Today, Completion Rate
- See 7-day trend analysis with interactive charts
- Monitor team performance with bar charts

### Tasks Page
- Browse all tasks with user statistics
- Filter by status: All Tasks, Open, In Progress, Completed, Blocked
- Search for specific team members
- View tasks by project (pie charts)

### AI Insights Page
- Read AI-generated productivity summaries
- View task closure performance metrics
- See predictive analytics (sprint completion, workload forecast)
- Compare team benchmarking across 4 teams
- Analyze team sentiment from communications

### Queries Page
- Ask natural language questions like:
  - "How many bugs did we close this sprint?"
  - "Show me blocked tasks"
  - "What's our team velocity?"
- Get instant AI-powered responses

### Settings Page
- Configure GitHub and Trello API integrations
- Manage notification preferences
- Toggle task updates, AI insights, and daily digest

## 📊 Database Structure

### Users Table
```python
- user_id: Primary key
- name: Full name
- email: Email address
- initials: Display initials
- role: Job role (Developer, Designer, etc.)
- team: Team name (Your Team, Alpha Team, etc.)
- is_active: Active status
```

### Tasks Table
```python
- task_id: Primary key
- task_name: Task title
- description: Detailed description
- status: Open, In Progress, Completed, Blocked
- priority: High, Medium, Low
- project: Web Platform, Mobile App, API Services
- assigned_to: Foreign key to Users
- created_date, due_date, start_date, completed_date
- estimated_hours: Time estimation
- tags: Comma-separated tags
- blocked_reason: Why task is blocked (if applicable)
- comments: Task notes
```

## 🔥 API Endpoints

### Overview Endpoints
- `GET /api/overview` - Dashboard metrics
- `GET /api/distribution` - Task distribution pie chart
- `GET /api/trends` - 7-day trend data
- `GET /api/team-performance` - Team performance stats

### Tasks Endpoints
- `GET /api/tasks?status=&project=&search=` - Get tasks with filters
- `GET /api/tasks/:id` - Get single task
- `GET /api/projects` - Get all projects
- `GET /api/projects/stats` - Task counts by project

### Users Endpoints
- `GET /api/users?search=` - Get all users with stats
- `GET /api/users/:id` - Get single user

### AI Insights Endpoints
- `GET /api/ai/summary` - AI-powered summary
- `GET /api/ai/closure-performance` - Closure metrics
- `GET /api/ai/due-compliance` - Due date compliance
- `GET /api/ai/predictions` - Predictive analytics
- `GET /api/ai/team-benchmarking` - Team comparison
- `GET /api/ai/productivity-trends` - 4-week trends
- `GET /api/ai/sentiment` - Sentiment analysis

### Chat Endpoint
- `POST /api/chat` - Send conversational query

### Settings Endpoints
- `GET /api/settings` - Get current settings
- `POST /api/settings` - Save settings

## 🎨 Design Highlights

- **Dark Theme**: Modern dark UI matching mockups
- **Gradient Accents**: Beautiful gradient cards and buttons
- **Responsive Layout**: Works on desktop, tablet, and mobile
- **Real-time Updates**: Auto-refresh every 10 seconds
- **Smooth Animations**: Subtle animations for better UX
- **Color-coded Status**: Visual indicators for task states

## 🔧 Troubleshooting

### Backend Issues

**Port 5000 already in use:**
```bash
# Change port in app.py:
app.run(debug=True, port=5001)  # Use different port
```

**Database not found:**
```bash
# Regenerate database:
python3 seed_data.py
```

### Frontend Issues

**Dependencies not installing:**
```bash
# Clear cache and reinstall:
rm -rf node_modules package-lock.json
npm install
```

**CORS errors:**
- Ensure backend is running on port 5000
- Check Flask-CORS is installed

## 📈 Sample Data

The application comes with pre-populated data:
- **11 users** across 4 teams (Your Team, Alpha Team, Beta Team, Gamma Team)
- **100 tasks** distributed across 3 projects
  - ~38% Open
  - ~24% In Progress
  - ~26% Completed
  - ~12% Blocked

## 🚀 Future Enhancements

- Real GitHub/Trello API integration
- Advanced AI models (OpenAI GPT, Hugging Face)
- WebSocket for true real-time updates
- Export reports to PDF
- Email notifications
- Multi-language support
- Dark/Light theme toggle

## 👥 Team

Built for Hackathon Nellore 2025

## 📝 License

MIT License - Feel free to use this project for learning and development

---

## 🎉 Quick Start Commands

```bash
# Terminal 1 - Backend
cd /Terralogic-Pulsevo/backend
pip3 install -r requirements.txt
python3 seed_data.py
python3 app.py

# Terminal 2 - Frontend  
cd /Terralogic-Pulsevo/frontend
npm install
npm start
```

**Access the app at: http://localhost:3000** 🚀

---

For questions or issues, please check the troubleshooting section or create an issue in the repository.

Happy coding! 💻

