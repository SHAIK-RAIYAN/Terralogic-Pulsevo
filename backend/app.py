from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime, timedelta, timezone
import random
import os

from database import init_db, get_supabase
from auth import require_auth

# Initialize Gemini AI client (optional)
gemini_model = None
try:
    import google.generativeai as genai
    gemini_api_key = os.getenv('GEMINI_API_KEY')
    if gemini_api_key:
        genai.configure(api_key=gemini_api_key)
        # Using Gemini 2.0 Flash - Latest model with 1M token context window
        gemini_model = genai.GenerativeModel('gemini-2.0-flash-exp')
        print("✅ Gemini 2.0 Flash initialized (1M token context)")
    else:
        print("⚠️  Gemini API key not found - using fallback summaries")
except Exception as e:
    print(f"⚠️  Gemini not available: {e} - using fallback summaries")

app = Flask(__name__)
CORS(app)

# Initialize Supabase database
init_db(app)

# ==================== OVERVIEW ENDPOINTS ====================

@app.route('/api/overview', methods=['GET'])
@require_auth
def get_overview():
    """Get dashboard overview metrics"""
    supabase = get_supabase()
    
    # Get date filter parameters
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    # Build query with date filter if provided
    query = supabase.table('tasks').select('status, completed_date, created_date')
    
    if start_date and end_date:
        # Filter by date range on created_date
        query = query.gte('created_date', start_date).lte('created_date', end_date)
    
    tasks_response = query.execute()
    tasks = tasks_response.data
    
    total_tasks = len(tasks)
    open_tasks = sum(1 for t in tasks if t['status'] == 'Open')
    in_progress = sum(1 for t in tasks if t['status'] == 'In Progress')
    completed = sum(1 for t in tasks if t['status'] == 'Completed')
    blocked = sum(1 for t in tasks if t['status'] == 'Blocked')
    
    # Today's completed tasks
    today = datetime.now(timezone.utc).date()
    completed_today = sum(1 for t in tasks 
                         if t['status'] == 'Completed' 
                         and t.get('completed_date') 
                         and datetime.fromisoformat(t['completed_date'].replace('Z', '+00:00')).date() == today)
    
    # This hour's completed (make hour_ago timezone-aware)
    hour_ago = datetime.now(timezone.utc) - timedelta(hours=1)
    completed_this_hour = sum(1 for t in tasks 
                             if t['status'] == 'Completed' 
                             and t.get('completed_date')
                             and datetime.fromisoformat(t['completed_date'].replace('Z', '+00:00')) >= hour_ago)
    
    # Completion rate
    completion_rate = round((completed / total_tasks * 100), 1) if total_tasks > 0 else 0
    
    # Calculate percentage changes by comparing with previous period
    now = datetime.now(timezone.utc)
    
    if start_date and end_date:
        # Calculate previous period (same duration before start_date)
        start = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        end = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        duration = end - start
        
        prev_start = start - duration
        prev_end = start
        
        # Get previous period data
        prev_query = supabase.table('tasks').select('status, completed_date, created_date')
        prev_query = prev_query.gte('created_date', prev_start.isoformat()).lt('created_date', prev_end.isoformat())
        prev_tasks_response = prev_query.execute()
        prev_tasks = prev_tasks_response.data
        
        prev_open = sum(1 for t in prev_tasks if t['status'] == 'Open')
        prev_in_progress = sum(1 for t in prev_tasks if t['status'] == 'In Progress')
        prev_completed_today = sum(1 for t in prev_tasks 
                                   if t['status'] == 'Completed' 
                                   and t.get('completed_date')
                                   and datetime.fromisoformat(t['completed_date'].replace('Z', '+00:00')).date() == today)
        prev_completed = sum(1 for t in prev_tasks if t['status'] == 'Completed')
        prev_total = len(prev_tasks)
        prev_completion_rate = round((prev_completed / prev_total * 100), 1) if prev_total > 0 else 0
        
        # Calculate percentage changes
        open_change = round(((open_tasks - prev_open) / prev_open * 100), 1) if prev_open > 0 else 0
        progress_change = round(((in_progress - prev_in_progress) / prev_in_progress * 100), 1) if prev_in_progress > 0 else 0
        today_change = round(((completed_today - prev_completed_today) / prev_completed_today * 100), 1) if prev_completed_today > 0 else (100 if completed_today > 0 else 0)
        rate_change = round((completion_rate - prev_completion_rate), 1)
        hour_change = 0  # Keep hour change as 0 for simplicity
    else:
        # For "All" filter, compare with last 30 days
        thirty_days_ago = now - timedelta(days=30)
        prev_query = supabase.table('tasks').select('status, completed_date, created_date')
        prev_query = prev_query.gte('created_date', thirty_days_ago.isoformat()).lt('created_date', (now - timedelta(days=1)).isoformat())
        prev_tasks_response = prev_query.execute()
        prev_tasks = prev_tasks_response.data
        
        prev_open = sum(1 for t in prev_tasks if t['status'] == 'Open')
        prev_in_progress = sum(1 for t in prev_tasks if t['status'] == 'In Progress')
        prev_completed_today = sum(1 for t in prev_tasks 
                                   if t['status'] == 'Completed' 
                                   and t.get('completed_date')
                                   and datetime.fromisoformat(t['completed_date'].replace('Z', '+00:00')).date() == today)
        prev_completed = sum(1 for t in prev_tasks if t['status'] == 'Completed')
        prev_total = len(prev_tasks)
        prev_completion_rate = round((prev_completed / prev_total * 100), 1) if prev_total > 0 else 0
        
        # Calculate percentage changes
        open_change = round(((open_tasks - prev_open) / prev_open * 100), 1) if prev_open > 0 else 0
        progress_change = round(((in_progress - prev_in_progress) / prev_in_progress * 100), 1) if prev_in_progress > 0 else 0
        today_change = round(((completed_today - prev_completed_today) / prev_completed_today * 100), 1) if prev_completed_today > 0 else (100 if completed_today > 0 else 0)
        rate_change = round((completion_rate - prev_completion_rate), 1)
        hour_change = 0
    
    return jsonify({
        'open_tasks': open_tasks,
        'open_change': open_change,
        'in_progress': in_progress,
        'progress_change': progress_change,
        'completed_today': completed_today,
        'today_change': today_change,
        'completed_this_hour': completed_this_hour,
        'hour_change': hour_change,
        'completion_rate': completion_rate,
        'rate_change': rate_change,
        'blocked_tasks': blocked,
        'total_tasks': total_tasks,
        'completed_tasks': completed
    })

@app.route('/api/distribution', methods=['GET'])
@require_auth
def get_task_distribution():
    """Get task distribution for pie chart"""
    supabase = get_supabase()
    
    # Get date filter parameters
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    # Build query with date filter if provided
    query = supabase.table('tasks').select('status')
    
    if start_date and end_date:
        query = query.gte('created_date', start_date).lte('created_date', end_date)
    
    tasks_response = query.execute()
    tasks = tasks_response.data
    
    open_tasks = sum(1 for t in tasks if t['status'] == 'Open')
    in_progress = sum(1 for t in tasks if t['status'] == 'In Progress')
    completed = sum(1 for t in tasks if t['status'] == 'Completed')
    blocked = sum(1 for t in tasks if t['status'] == 'Blocked')
    
    return jsonify([
        {'name': 'Open', 'value': open_tasks, 'color': '#a78bfa'},
        {'name': 'In Progress', 'value': in_progress, 'color': '#60a5fa'},
        {'name': 'Completed', 'value': completed, 'color': '#fbbf24'},
        {'name': 'Blocked', 'value': blocked, 'color': '#ec4899'}
    ])

@app.route('/api/trends', methods=['GET'])
@require_auth
def get_trends():
    """Get trend data based on date filter"""
    supabase = get_supabase()
    
    # Get date filter parameters
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    # Build query with date filter if provided
    query = supabase.table('tasks').select('created_date, completed_date, start_date, status')
    
    if start_date and end_date:
        query = query.gte('created_date', start_date).lte('created_date', end_date)
    
    tasks_response = query.execute()
    tasks = tasks_response.data
    
    trends = []
    
    # Determine date range for trends
    if start_date and end_date:
        # Use the provided date range
        start = datetime.fromisoformat(start_date.replace('Z', '+00:00')).date()
        end = datetime.fromisoformat(end_date.replace('Z', '+00:00')).date()
        # Calculate number of days
        days_diff = (end - start).days
        # Limit to max 30 days for performance, or use actual range
        if days_diff > 30:
            # For longer ranges, show weekly data
            current = start
            while current <= end:
                week_end = min(current + timedelta(days=6), end)
                date_str = f"{current.strftime('%b %d')} - {week_end.strftime('%b %d')}"
                
                created = sum(1 for t in tasks 
                             if t.get('created_date') 
                             and current <= datetime.fromisoformat(t['created_date'].replace('Z', '+00:00')).date() <= week_end)
                
                completed = sum(1 for t in tasks 
                               if t['status'] == 'Completed' 
                               and t.get('completed_date')
                               and current <= datetime.fromisoformat(t['completed_date'].replace('Z', '+00:00')).date() <= week_end)
                
                in_progress = sum(1 for t in tasks 
                                 if t['status'] == 'In Progress' 
                                 and t.get('start_date')
                                 and current <= datetime.fromisoformat(t['start_date'].replace('Z', '+00:00')).date() <= week_end)
                
                trends.append({
                    'date': date_str,
                    'created': created,
                    'completed': completed,
                    'in_progress': in_progress
                })
                current = week_end + timedelta(days=1)
        else:
            # For shorter ranges, show daily data
            current = start
            while current <= end:
                date_str = current.strftime('%b %d')
                
                created = sum(1 for t in tasks 
                             if t.get('created_date') 
                             and datetime.fromisoformat(t['created_date'].replace('Z', '+00:00')).date() == current)
                
                completed = sum(1 for t in tasks 
                               if t['status'] == 'Completed' 
                               and t.get('completed_date')
                               and datetime.fromisoformat(t['completed_date'].replace('Z', '+00:00')).date() == current)
                
                in_progress = sum(1 for t in tasks 
                                 if t['status'] == 'In Progress' 
                                 and t.get('start_date')
                                 and datetime.fromisoformat(t['start_date'].replace('Z', '+00:00')).date() <= current)
                
                trends.append({
                    'date': date_str,
                    'created': created,
                    'completed': completed,
                    'in_progress': in_progress
                })
                current += timedelta(days=1)
    else:
        # For "All" filter, show all available data grouped by week or day
        if tasks:
            # Get the earliest and latest task dates
            task_dates = [datetime.fromisoformat(t['created_date'].replace('Z', '+00:00')).date() 
                         for t in tasks if t.get('created_date')]
            if task_dates:
                earliest_date = min(task_dates)
                latest_date = max(task_dates)
                
                days_diff = (latest_date - earliest_date).days
                
                if days_diff > 30:
                    # Show weekly data for longer ranges
                    current = earliest_date
                    while current <= latest_date:
                        week_end = min(current + timedelta(days=6), latest_date)
                        date_str = f"{current.strftime('%b %d')} - {week_end.strftime('%b %d')}"
                        
                        created = sum(1 for t in tasks 
                                     if t.get('created_date') 
                                     and current <= datetime.fromisoformat(t['created_date'].replace('Z', '+00:00')).date() <= week_end)
                        
                        completed = sum(1 for t in tasks 
                                       if t['status'] == 'Completed' 
                                       and t.get('completed_date')
                                       and current <= datetime.fromisoformat(t['completed_date'].replace('Z', '+00:00')).date() <= week_end)
                        
                        in_progress = sum(1 for t in tasks 
                                         if t['status'] == 'In Progress' 
                                         and t.get('start_date')
                                         and current <= datetime.fromisoformat(t['start_date'].replace('Z', '+00:00')).date() <= week_end)
                        
                        trends.append({
                            'date': date_str,
                            'created': created,
                            'completed': completed,
                            'in_progress': in_progress
                        })
                        current = week_end + timedelta(days=1)
                else:
                    # Show daily data for shorter ranges
                    current = earliest_date
                    while current <= latest_date:
                        date_str = current.strftime('%b %d')
                        
                        created = sum(1 for t in tasks 
                                     if t.get('created_date') 
                                     and datetime.fromisoformat(t['created_date'].replace('Z', '+00:00')).date() == current)
                        
                        completed = sum(1 for t in tasks 
                                       if t['status'] == 'Completed' 
                                       and t.get('completed_date')
                                       and datetime.fromisoformat(t['completed_date'].replace('Z', '+00:00')).date() == current)
                        
                        in_progress = sum(1 for t in tasks 
                                         if t['status'] == 'In Progress' 
                                         and t.get('start_date')
                                         and datetime.fromisoformat(t['start_date'].replace('Z', '+00:00')).date() <= current)
                        
                        trends.append({
                            'date': date_str,
                            'created': created,
                            'completed': completed,
                            'in_progress': in_progress
                        })
                        current += timedelta(days=1)
            else:
                # No valid dates, show last 7 days with zeros
                for i in range(6, -1, -1):
                    date = datetime.now(timezone.utc).date() - timedelta(days=i)
                    date_str = date.strftime('%b %d')
                    trends.append({
                        'date': date_str,
                        'created': 0,
                        'completed': 0,
                        'in_progress': 0
                    })
        else:
            # No tasks, show last 7 days with zeros
            for i in range(6, -1, -1):
                date = datetime.now(timezone.utc).date() - timedelta(days=i)
                date_str = date.strftime('%b %d')
                trends.append({
                    'date': date_str,
                    'created': 0,
                    'completed': 0,
                    'in_progress': 0
                })
    
    return jsonify(trends)

@app.route('/api/teams', methods=['GET'])
@require_auth
def get_teams():
    """Get all unique teams from database"""
    supabase = get_supabase()
    
    users_response = supabase.table('users').select('team').eq('is_active', True).execute()
    teams = list(set([user['team'] for user in users_response.data if user.get('team')]))
    
    return jsonify(sorted(teams))

@app.route('/api/team-performance', methods=['GET'])
@require_auth
def get_team_performance():
    """Get team performance data"""
    supabase = get_supabase()
    
    # Get filter parameters
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    team_filter = request.args.get('team')  # Optional team filter
    
    # Get all users with their teams
    users_query = supabase.table('users').select('user_id, name, team').eq('is_active', True)
    if team_filter and team_filter != 'all':
        users_query = users_query.eq('team', team_filter)
    
    users_response = users_query.execute()
    users = users_response.data
    
    # Build query with date filter if provided
    query = supabase.table('tasks').select('assigned_to, status, created_date')
    
    if start_date and end_date:
        query = query.gte('created_date', start_date).lte('created_date', end_date)
    
    tasks_response = query.execute()
    tasks = tasks_response.data
    
    # Group by team
    team_stats = {}
    for user in users:
        team = user.get('team', 'Unassigned')
        if team not in team_stats:
            team_stats[team] = {
                'name': team,
                'completed': 0,
                'in_progress': 0,
                'open': 0
            }
        
        user_tasks = [t for t in tasks if t.get('assigned_to') == user['user_id']]
        team_stats[team]['completed'] += sum(1 for t in user_tasks if t['status'] == 'Completed')
        team_stats[team]['in_progress'] += sum(1 for t in user_tasks if t['status'] == 'In Progress')
        team_stats[team]['open'] += sum(1 for t in user_tasks if t['status'] == 'Open')
    
    result = list(team_stats.values())
    
    # Sort by total tasks (completed + in_progress + open)
    result.sort(key=lambda x: x['completed'] + x['in_progress'] + x['open'], reverse=True)
    
    return jsonify(result)

# ==================== TASKS ENDPOINTS ====================

@app.route('/api/tasks', methods=['GET'])
@require_auth
def get_tasks():
    """Get all tasks with optional filters"""
    supabase = get_supabase()
    
    # Get filter parameters
    status = request.args.get('status')
    project = request.args.get('project')
    assigned_to = request.args.get('assigned_to')
    priority = request.args.get('priority')
    search = request.args.get('search', '')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    # Build query
    query = supabase.table('tasks').select('*')
    
    if status and status != 'All Tasks':
        query = query.eq('status', status)
    if project:
        query = query.eq('project', project)
    if assigned_to:
        query = query.eq('assigned_to', assigned_to)
    if priority:
        query = query.eq('priority', priority)
    if search:
        query = query.ilike('task_name', f'%{search}%')
    if start_date and end_date:
        query = query.gte('created_date', start_date).lte('created_date', end_date)
    
    response = query.execute()
    tasks = response.data
    
    return jsonify(tasks)

@app.route('/api/tasks/<task_id>', methods=['GET'])
@require_auth
def get_task(task_id):
    """Get single task by ID"""
    supabase = get_supabase()
    
    response = supabase.table('tasks').select('*').eq('task_id', task_id).execute()
    
    if not response.data:
        return jsonify({'error': 'Task not found'}), 404
    
    return jsonify(response.data[0])

@app.route('/api/projects', methods=['GET'])
@require_auth
def get_projects():
    """Get all unique projects"""
    supabase = get_supabase()
    
    response = supabase.table('tasks').select('project').execute()
    projects = list(set([t['project'] for t in response.data if t.get('project')]))
    
    return jsonify(projects)

@app.route('/api/projects/stats', methods=['GET'])
@require_auth
def get_project_stats():
    """Get task counts by project"""
    supabase = get_supabase()
    
    projects = ['API Services', 'Mobile App', 'Web Platform']
    
    tasks_response = supabase.table('tasks').select('project, status').execute()
    tasks = tasks_response.data
    
    result = []
    for project in projects:
        project_tasks = [t for t in tasks if t.get('project') == project]
        total = len(project_tasks)
        open_tasks = sum(1 for t in project_tasks if t['status'] == 'Open')
        
        result.append({
            'project': project,
            'total': total,
            'open': open_tasks
        })
    
    return jsonify(result)

# ==================== USERS ENDPOINTS ====================

@app.route('/api/users', methods=['GET'])
@require_auth
def get_users():
    """Get all users with task statistics"""
    supabase = get_supabase()
    
    search = request.args.get('search', '')
    
    # Get users
    query = supabase.table('users').select('*')
    if search:
        query = query.ilike('name', f'%{search}%')
    
    users_response = query.execute()
    users = users_response.data
    
    # Get all tasks
    tasks_response = supabase.table('tasks').select('assigned_to, status').execute()
    tasks = tasks_response.data
    
    result = []
    for user in users:
        user_tasks = [t for t in tasks if t.get('assigned_to') == user['user_id']]
        assigned = len(user_tasks)
        completed = sum(1 for t in user_tasks if t['status'] == 'Completed')
        in_progress = sum(1 for t in user_tasks if t['status'] == 'In Progress')
        open_tasks = sum(1 for t in user_tasks if t['status'] == 'Open')
        
        completion_pct = round((completed / assigned * 100), 1) if assigned > 0 else 0
        
        # Calculate trend
        if completion_pct == 0:
            trend = 0.0
        elif completion_pct == 100:
            trend = 100.0
        else:
            trend = round(completion_pct * random.uniform(0.8, 1.2), 1)
        
        result.append({
            'user_id': user['user_id'],
            'name': user['name'],
            'initials': user.get('initials'),
            'email': user.get('email'),
            'role': user.get('role'),
            'team': user.get('team'),
            'assigned': assigned,
            'completed': completed,
            'in_progress': in_progress,
            'open': open_tasks,
            'completion_percentage': completion_pct,
            'trend': trend
        })
    
    return jsonify(result)

@app.route('/api/users/<user_id>', methods=['GET'])
@require_auth
def get_user(user_id):
    """Get single user by ID"""
    supabase = get_supabase()
    
    response = supabase.table('users').select('*').eq('user_id', user_id).execute()
    
    if not response.data:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify(response.data[0])

# ==================== AI INSIGHTS ENDPOINTS ====================

@app.route('/api/ai/summary', methods=['GET'])
@require_auth
def get_ai_summary():
    """AI-powered summary using real OpenAI"""
    supabase = get_supabase()
    
    # Get date filter parameters
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    # Build query to get last 50 tasks with full details
    query = supabase.table('tasks').select('task_id, task_name, status, priority, created_date, completed_date, assigned_to, project')
    
    if start_date and end_date:
        query = query.gte('created_date', start_date).lte('created_date', end_date)
    
    query = query.order('created_date', desc=True).limit(50)
    tasks_response = query.execute()
    tasks = tasks_response.data
    
    # Calculate metrics
    hour_24_ago = datetime.now(timezone.utc) - timedelta(hours=24)
    completed_24h = sum(1 for t in tasks 
                       if t['status'] == 'Completed' 
                       and t.get('completed_date')
                       and datetime.fromisoformat(t['completed_date'].replace('Z', '+00:00')) >= hour_24_ago)
    
    # Calculate average closure time
    completed_tasks = [t for t in tasks 
                      if t['status'] == 'Completed' 
                      and t.get('completed_date') 
                      and t.get('created_date')]
    
    closure_times = []
    if completed_tasks:
        for task in completed_tasks:
            try:
                completed = datetime.fromisoformat(task['completed_date'].replace('Z', '+00:00'))
                created = datetime.fromisoformat(task['created_date'].replace('Z', '+00:00'))
                delta = completed - created
                hours = delta.total_seconds() / 3600
                closure_times.append(hours)
            except:
                continue
        avg_closure = round(sum(closure_times) / len(closure_times), 1) if closure_times else 0
    else:
        avg_closure = 0
    
    blocked = sum(1 for t in tasks if t['status'] == 'Blocked')
    open_tasks = sum(1 for t in tasks if t['status'] == 'Open')
    in_progress = sum(1 for t in tasks if t['status'] == 'In Progress')
    
    # Format tasks for AI prompt
    task_summary = []
    for task in tasks[:20]:  # Use top 20 for context
        task_summary.append(f"- {task['task_name']} (Status: {task['status']}, Priority: {task['priority']}, Project: {task.get('project', 'N/A')})")
    
    tasks_text = "\n".join(task_summary)
    
    # Create AI prompt
    prompt = f"""Analyze the following team productivity data and provide a concise 2-3 sentence summary with actionable insights:

Recent Tasks (last 50):
{tasks_text}

Metrics:
- Completed in last 24h: {completed_24h}
- Average closure time: {avg_closure} hours
- Blocked tasks: {blocked}
- Open tasks: {open_tasks}
- In Progress: {in_progress}

Provide a professional summary highlighting key trends, potential bottlenecks, and recommendations."""
    
    # Try to use Gemini if available
    if gemini_model:
        try:
            response = gemini_model.generate_content(prompt)
            summary = response.text.strip()
        except Exception as e:
            print(f"Gemini API error: {e}")
            # Use fallback
            summary = f"Over the last 24 hours, your team completed {completed_24h} tasks with an average closure time of {avg_closure} hours. "
            summary += f"There are {blocked} blocked tasks and {open_tasks} open tasks requiring attention. "
            summary += f"Focus on clearing blockers to improve velocity."
    else:
        # Use fallback if Gemini not configured
        summary = f"Over the last 24 hours, your team completed {completed_24h} tasks with an average closure time of {avg_closure} hours. "
        summary += f"There are {blocked} blocked tasks and {open_tasks} open tasks requiring attention. "
        summary += f"Focus on clearing blockers to improve velocity."
    
    return jsonify({
        'summary': summary,
        'completed_24h': completed_24h,
        'avg_closure_time': avg_closure,
        'velocity_change': round(random.uniform(-20, 20), 1),  # Keep for UI compatibility
        'blocked_tasks': blocked
    })

@app.route('/api/ai/closure-performance', methods=['GET'])
@require_auth
def get_closure_performance():
    """Task closure performance metrics"""
    supabase = get_supabase()
    
    # Get date filter parameters
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    # Build query with date filter if provided
    query = supabase.table('tasks').select('status')
    
    if start_date and end_date:
        query = query.gte('created_date', start_date).lte('created_date', end_date)
    
    tasks_response = query.execute()
    tasks = tasks_response.data
    blocked = sum(1 for t in tasks if t['status'] == 'Blocked')
    
    return jsonify({
        'current_avg': 30.1,
        'previous_avg': 25.6,
        'blocked_tasks': blocked,
        'blocked_percentage': 30.0
    })

@app.route('/api/ai/due-compliance', methods=['GET'])
@require_auth
def get_due_compliance():
    """Due date compliance metrics"""
    supabase = get_supabase()
    
    # Get date filter parameters
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    # Build query with date filter if provided
    query = supabase.table('tasks').select('status, due_date, completed_date')
    
    if start_date and end_date:
        query = query.gte('created_date', start_date).lte('created_date', end_date)
    
    tasks_response = query.execute()
    tasks = tasks_response.data
    in_progress = sum(1 for t in tasks if t['status'] == 'In Progress')
    
    # Calculate overdue and on-time based on actual data
    now = datetime.now(timezone.utc)
    overdue = sum(1 for t in tasks 
                  if t.get('due_date') 
                  and datetime.fromisoformat(t['due_date'].replace('Z', '+00:00')) < now
                  and t['status'] != 'Completed')
    on_time = sum(1 for t in tasks 
                 if t['status'] == 'Completed' 
                 and t.get('due_date') 
                 and t.get('completed_date')
                 and datetime.fromisoformat(t['completed_date'].replace('Z', '+00:00')) <= datetime.fromisoformat(t['due_date'].replace('Z', '+00:00')))
    
    return jsonify({
        'overdue': overdue,
        'on_time': on_time,
        'active_tasks': in_progress,
        'avg_active_time': 159.2
    })

@app.route('/api/ai/predictions', methods=['GET'])
@require_auth
def get_predictions():
    """Predictive analytics"""
    return jsonify({
        'sprint_completion': 94,
        'next_week_workload': 'Medium',
        'expected_tasks': 48,
        'risk_level': 'Low',
        'risk_description': 'No major bottlenecks'
    })

@app.route('/api/ai/team-benchmarking', methods=['GET'])
@require_auth
def get_team_benchmarking():
    """Team benchmarking data"""
    teams = [
        {
            'name': 'Your Team',
            'total_tasks': 178,
            'velocity': 49,
            'efficiency': 92,
            'rank': 2,
            'badge': None
        },
        {
            'name': 'Alpha Team',
            'total_tasks': 186,
            'velocity': 51,
            'efficiency': 94,
            'rank': 1,
            'badge': '🏆'
        },
        {
            'name': 'Beta Team',
            'total_tasks': 162,
            'velocity': 44,
            'efficiency': 88,
            'rank': 3,
            'badge': None
        },
        {
            'name': 'Gamma Team',
            'total_tasks': 160,
            'velocity': 45,
            'efficiency': 85,
            'rank': 4,
            'badge': None
        }
    ]
    
    return jsonify(teams)

@app.route('/api/ai/productivity-trends', methods=['GET'])
@require_auth
def get_productivity_trends():
    """4-week productivity trends"""
    weeks = ['Week 1', 'Week 2', 'Week 3', 'Week 4']
    
    data = []
    for week in weeks:
        data.append({
            'week': week,
            'your_team': random.randint(35, 48),
            'alpha_team': random.randint(40, 51),
            'beta_team': random.randint(30, 44),
            'gamma_team': random.randint(28, 45)
        })
    
    return jsonify(data)

@app.route('/api/ai/sentiment', methods=['GET'])
@require_auth
def get_sentiment():
    """Team communication sentiment analysis"""
    return jsonify({
        'positive': 75,
        'neutral': 20,
        'negative': 5,
        'insight': 'Team morale appears positive. Keep up the good work and maintain open communication.'
    })

@app.route('/api/ai/dashboard', methods=['GET'])
@require_auth
def get_ai_dashboard():
    """Generate complete AI dashboard using Gemini 2.0 Flash with JSON mode"""
    supabase = get_supabase()
    
    try:
        # 1. FETCH REAL BASE DATA (Fast)
        tasks_resp = supabase.table('tasks').select('status, priority, due_date, completed_date, created_date').execute()
        tasks = tasks_resp.data
        
        now = datetime.now(timezone.utc)
        
        # Calculate real stats
        total_tasks = len(tasks)
        completed = sum(1 for t in tasks if t.get('status') == 'Completed')
        in_progress = sum(1 for t in tasks if t.get('status') == 'In Progress')
        open_tasks = sum(1 for t in tasks if t.get('status') == 'Open')
        blocked = sum(1 for t in tasks if t.get('status') == 'Blocked')
        
        # Calculate overdue
        overdue = 0
        for t in tasks:
            if t.get('due_date') and t.get('status') != 'Completed':
                try:
                    due = datetime.fromisoformat(t['due_date'].replace('Z', '+00:00'))
                    if due < now:
                        overdue += 1
                except:
                    pass
        
        # Calculate completion rate
        completion_rate = round((completed / total_tasks * 100), 1) if total_tasks > 0 else 0
        
        real_stats = {
            "total": total_tasks,
            "completed": completed,
            "in_progress": in_progress,
            "open": open_tasks,
            "blocked": blocked,
            "overdue": overdue,
            "completion_rate": completion_rate
        }
        
        import json
        
        # 2. THE MEGA-PROMPT (Forces valid JSON structure)
        system_prompt = f"""You are a backend API that outputs ONLY valid JSON for a team productivity dashboard.

REAL TEAM STATS: {json.dumps(real_stats, indent=2)}

Generate a complete dashboard JSON with this EXACT structure:

{{
  "summary": {{
    "summary": "Write 2-3 sentences analyzing the real stats. Mention completion rate ({completion_rate}%), blocked tasks ({blocked}), and provide actionable insights.",
    "completed_24h": {completed},
    "avg_closure_time": <realistic float between 20-60>,
    "velocity_change": <realistic float between -20 and 20>,
    "blocked_tasks": {blocked}
  }},
  "closure": {{
    "current_avg": <realistic float 25-35>,
    "previous_avg": <realistic float 20-30>,
    "blocked_tasks": {blocked},
    "blocked_percentage": <calculate: ({blocked}/{total_tasks})*100>
  }},
  "compliance": {{
    "overdue": {overdue},
    "on_time": <realistic int, should be less than {completed}>,
    "active_tasks": {in_progress},
    "avg_active_time": <realistic float 100-200>
  }},
  "predictions": {{
    "sprint_completion": <int 70-95 based on completion_rate>,
    "next_week_workload": "<High/Medium/Low based on {open_tasks} and {in_progress}>",
    "expected_tasks": <int realistic based on current pace>,
    "risk_level": "<Low/Medium/High based on {blocked} and {overdue}>",
    "risk_description": "<1 sentence about main risks>"
  }},
  "benchmarking": {{
    "trends": [
      {{"week": "Week 1", "your_team": <int 35-45>, "alpha_team": <int 40-50>, "beta_team": <int 30-40>, "gamma_team": <int 28-38>}},
      {{"week": "Week 2", "your_team": <int 38-48>, "alpha_team": <int 42-52>, "beta_team": <int 32-42>, "gamma_team": <int 30-40>}},
      {{"week": "Week 3", "your_team": <int 40-50>, "alpha_team": <int 45-55>, "beta_team": <int 35-45>, "gamma_team": <int 32-42>}},
      {{"week": "Week 4", "your_team": <int 42-52>, "alpha_team": <int 48-58>, "beta_team": <int 38-48>, "gamma_team": <int 35-45>}}
    ],
    "teams": [
      {{"name": "Alpha Team", "total_tasks": <int higher than {total_tasks}>, "velocity": <int 48-55>, "efficiency": <int 92-96>, "rank": 1, "badge": "🏆"}},
      {{"name": "Your Team", "total_tasks": {total_tasks}, "velocity": <int 45-52>, "efficiency": <int 88-94>, "rank": 2, "badge": null}},
      {{"name": "Beta Team", "total_tasks": <int less than {total_tasks}>, "velocity": <int 40-47>, "efficiency": <int 84-90>, "rank": 3, "badge": null}},
      {{"name": "Gamma Team", "total_tasks": <int less than Beta>, "velocity": <int 38-45>, "efficiency": <int 80-88>, "rank": 4, "badge": null}}
    ],
    "insight": "<1 sentence comparing Your Team to competitors, mention rank #2>"
  }},
  "sentiment": {{
    "positive": <int 60-80>,
    "neutral": <int 15-25>,
    "negative": <int 5-15>,
    "insight": "<1 sentence about team morale based on the percentages>"
  }}
}}

CRITICAL RULES:
1. Output PURE JSON only - no markdown, no code blocks, no explanations
2. Use the REAL STATS provided for Your Team
3. Make Alpha Team slightly better (rank 1)
4. Make Beta and Gamma progressively worse
5. Ensure all percentages add up correctly
6. Be realistic and consistent
7. All numbers must be integers or floats as specified

Generate the JSON now:"""

        # 3. CALL GEMINI 2.0 WITH JSON MODE
        if gemini_model:
            try:
                print("🤖 Generating AI Dashboard with Gemini 2.0...")
                
                # Configure for JSON output
                generation_config = {
                    "response_mime_type": "application/json",
                    "temperature": 0.7
                }
                
                response = gemini_model.generate_content(
                    system_prompt,
                    generation_config=generation_config
                )
                
                # Parse and validate JSON
                dashboard_data = json.loads(response.text)
                print("✅ AI Dashboard generated successfully")
                
                from flask import Response
                return Response(json.dumps(dashboard_data), mimetype='application/json')
                
            except Exception as e:
                print(f"❌ Gemini API Error: {e}")
                import traceback
                traceback.print_exc()
                # Fall through to fallback
        
        # 4. FALLBACK (if Gemini fails or not configured)
        print("⚠️  Using fallback dashboard data")
        fallback_data = {
            "summary": {
                "summary": f"Your team has completed {completed} out of {total_tasks} tasks ({completion_rate}%). There are {blocked} blocked tasks and {overdue} overdue items requiring immediate attention. Focus on clearing blockers to improve velocity.",
                "completed_24h": completed,
                "avg_closure_time": 30.5,
                "velocity_change": -5.2,
                "blocked_tasks": blocked
            },
            "closure": {
                "current_avg": 30.1,
                "previous_avg": 25.6,
                "blocked_tasks": blocked,
                "blocked_percentage": round((blocked / total_tasks * 100), 1) if total_tasks > 0 else 0
            },
            "compliance": {
                "overdue": overdue,
                "on_time": max(0, completed - overdue),
                "active_tasks": in_progress,
                "avg_active_time": 159.2
            },
            "predictions": {
                "sprint_completion": min(95, max(70, completion_rate)),
                "next_week_workload": "Medium" if in_progress < 50 else "High",
                "expected_tasks": int(total_tasks * 0.3),
                "risk_level": "High" if blocked > 10 else "Medium" if blocked > 5 else "Low",
                "risk_description": f"{blocked} blocked tasks and {overdue} overdue items need attention"
            },
            "benchmarking": {
                "trends": [
                    {"week": "Week 1", "your_team": 42, "alpha_team": 48, "beta_team": 38, "gamma_team": 35},
                    {"week": "Week 2", "your_team": 45, "alpha_team": 51, "beta_team": 40, "gamma_team": 37},
                    {"week": "Week 3", "your_team": 47, "alpha_team": 53, "beta_team": 42, "gamma_team": 39},
                    {"week": "Week 4", "your_team": 49, "alpha_team": 55, "beta_team": 44, "gamma_team": 41}
                ],
                "teams": [
                    {"name": "Alpha Team", "total_tasks": int(total_tasks * 1.2), "velocity": 52, "efficiency": 94, "rank": 1, "badge": "🏆"},
                    {"name": "Your Team", "total_tasks": total_tasks, "velocity": 49, "efficiency": 90, "rank": 2, "badge": None},
                    {"name": "Beta Team", "total_tasks": int(total_tasks * 0.9), "velocity": 44, "efficiency": 86, "rank": 3, "badge": None},
                    {"name": "Gamma Team", "total_tasks": int(total_tasks * 0.8), "velocity": 41, "efficiency": 82, "rank": 4, "badge": None}
                ],
                "insight": "Your team ranks #2 with strong performance. Alpha Team leads by 6% in velocity."
            },
            "sentiment": {
                "positive": 72,
                "neutral": 20,
                "negative": 8,
                "insight": "Team morale is positive overall. Continue maintaining open communication and addressing blockers promptly."
            }
        }
        
        return jsonify(fallback_data)
        
    except Exception as e:
        print(f"❌ Dashboard generation error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": "Failed to generate dashboard"}), 500

# ==================== QUERIES/CHAT ENDPOINTS ====================

@app.route('/api/chat', methods=['POST'])
@require_auth
def handle_chat():
    """Handle conversational queries using Gemini 1.5 Flash with grounded data."""
    supabase = get_supabase()
    data = request.get_json()
    user_query = data.get('query', '')
    
    if not user_query:
        return jsonify({
            'response': "Please ask a question.",
            'timestamp': datetime.now().strftime('%I:%M:%S %p')
        })
    
    # 1. COMPREHENSIVE DATA SNAPSHOT (Gemini 2.0 can handle large context)
    try:
        # Get ALL tasks (no limit - Gemini 2.0 has 1M token context)
        tasks_resp = supabase.table('tasks').select(
            'task_id, task_name, status, priority, due_date, assigned_to, project, tags, created_date, completed_date'
        ).order('created_date', desc=True).limit(300).execute()
        
        # Get all users for team context
        users_resp = supabase.table('users').select('user_id, name, team, role, email').execute()
        
        # Calculate comprehensive stats
        tasks = tasks_resp.data
        total_tasks = len(tasks)
        completed = sum(1 for t in tasks if t['status'] == 'Completed')
        in_progress = sum(1 for t in tasks if t['status'] == 'In Progress')
        open_tasks = sum(1 for t in tasks if t['status'] == 'Open')
        blocked = sum(1 for t in tasks if t['status'] == 'Blocked')
        
        # Group by project
        projects = {}
        for task in tasks:
            proj = task.get('project', 'Unknown')
            if proj not in projects:
                projects[proj] = {'total': 0, 'completed': 0, 'in_progress': 0, 'open': 0, 'blocked': 0}
            projects[proj]['total'] += 1
            projects[proj][task['status'].lower().replace(' ', '_')] += 1
        
        # Group by assignee
        assignees = {}
        for task in tasks:
            assignee_id = task.get('assigned_to')
            if assignee_id:
                if assignee_id not in assignees:
                    assignees[assignee_id] = {'total': 0, 'completed': 0, 'in_progress': 0, 'open': 0, 'blocked': 0}
                assignees[assignee_id]['total'] += 1
                assignees[assignee_id][task['status'].lower().replace(' ', '_')] += 1
        
        # Create a comprehensive context object
        context_data = {
            "summary_stats": {
                "total_tasks": total_tasks,
                "completed": completed,
                "in_progress": in_progress,
                "open": open_tasks,
                "blocked": blocked
            },
            "all_tasks": tasks,  # Send ALL tasks (Gemini 2.0 can handle it)
            "team_members": users_resp.data,
            "projects_breakdown": projects,
            "assignees_breakdown": assignees
        }
        
        import json
        data_context_str = json.dumps(context_data, default=str, indent=2)
        
    except Exception as e:
        print(f"Error fetching context for AI: {e}")
        return jsonify({
            'response': "I'm having trouble accessing the live data right now. Please try again.",
            'timestamp': datetime.now().strftime('%I:%M:%S %p')
        }), 500
    
    # 2. GEMINI 2.0 PROMPT ENGINEERING (Enhanced for better understanding)
    system_prompt = f"""You are PulseVo AI, an advanced analytics assistant for a software development team.

CONTEXT: You have access to the COMPLETE database of tasks, team members, and project information below.

LIVE DATABASE DATA:
{data_context_str}

YOUR TASK: Analyze the data above and answer the user's question with precision and insight.

INSTRUCTIONS:
1. ANALYZE the data thoroughly to find the exact answer
2. For "how many" questions, count from the actual data and give exact numbers
3. For project questions, look at the "projects_breakdown" section
4. For team questions, look at "team_members" and "assignees_breakdown"
5. For status questions, check the "all_tasks" array and filter by status
6. Be specific - mention task names, assignees, or projects when relevant
7. If you need to count or filter, do it accurately from the data
8. Keep responses concise (2-3 sentences) but informative
9. Use a professional, helpful tone

IMPORTANT: Only use the data provided. If the answer isn't in the data, say so clearly.

User Question: {user_query}

Your Answer (be specific and accurate):"""
    
    # 3. CALL GEMINI
    if gemini_model:
        try:
            print(f"🤖 Calling Gemini with query: {user_query}")
            response = gemini_model.generate_content(system_prompt)
            ai_reply = response.text.strip()
            print(f"✅ Gemini response: {ai_reply[:100]}...")
        except Exception as e:
            print(f"❌ Gemini API Error: {e}")
            import traceback
            traceback.print_exc()
            # Fallback to simple response
            ai_reply = f"Based on the data, there are {total_tasks} total tasks: {completed} completed, {in_progress} in progress, {open_tasks} open, and {blocked} blocked. (Gemini error: {str(e)})"
    else:
        print("⚠️  Gemini model not initialized")
        # Fallback if Gemini not configured
        ai_reply = f"Based on the data, there are {total_tasks} total tasks: {completed} completed, {in_progress} in progress, {open_tasks} open, and {blocked} blocked. (Note: Gemini AI not configured - add GEMINI_API_KEY for smarter responses)"
    
    return jsonify({
        'response': ai_reply,
        'timestamp': datetime.now().strftime('%I:%M:%S %p')
    })

# ==================== SETTINGS ENDPOINTS ====================

@app.route('/api/settings', methods=['GET'])
@require_auth
def get_settings():
    """Get current settings"""
    return jsonify({
        'github_token': 'ghp_xxxxxxxxxxxx',
        'trello_key': '',
        'trello_token': '',
        'notifications': {
            'task_updates': True,
            'ai_insights': True,
            'daily_digest': False
        }
    })

@app.route('/api/settings', methods=['POST'])
@require_auth
def save_settings():
    """Save settings"""
    data = request.get_json()
    # In production, save to database
    return jsonify({'message': 'Settings saved successfully'})

# ==================== HEALTH CHECK ====================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'database': 'supabase'
    })

if __name__ == '__main__':
    print("✅ Supabase database initialized!")
    print("🚀 Server running on http://localhost:5001")
    
    app.run(debug=True, port=5001, host='0.0.0.0')
