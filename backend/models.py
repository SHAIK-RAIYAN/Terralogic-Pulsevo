"""
Data models reference for PULSEVO
Note: With Supabase, we don't need SQLAlchemy models.
This file is kept for reference of the data structure.
"""

# User model structure
# {
#     'user_id': str,  # Primary key (e.g., 'USER-001')
#     'name': str,
#     'email': str,
#     'initials': str,
#     'role': str,
#     'team': str,
#     'avatar_url': str,
#     'is_active': bool,
#     'created_at': datetime,
#     'updated_at': datetime
# }

# Task model structure
# {
#     'task_id': str,  # Primary key (e.g., 'TASK-0001')
#     'task_name': str,
#     'description': str,
#     'status': str,  # 'Open', 'In Progress', 'Completed', 'Blocked'
#     'priority': str,  # 'High', 'Medium', 'Low'
#     'project': str,  # 'Web Platform', 'Mobile App', 'API Services'
#     'assigned_to': str,  # Foreign key to users.user_id
#     'created_date': datetime,
#     'due_date': datetime,
#     'start_date': datetime,
#     'completed_date': datetime,
#     'estimated_hours': float,
#     'tags': str,  # Comma-separated tags
#     'blocked_reason': str,
#     'comments': str,
#     'updated_at': datetime
# }
