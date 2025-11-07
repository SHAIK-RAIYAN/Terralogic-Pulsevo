"""
Generate realistic sample data for PULSEVO dashboard
"""
from app import app, db
from models import User, Task
from datetime import datetime, timedelta
import random

def clear_data():
    """Clear existing data"""
    with app.app_context():
        Task.query.delete()
        User.query.delete()
        db.session.commit()
        print("✅ Cleared existing data")

def generate_users():
    """Generate sample users - 30 users across 4 teams"""
    users_data = [
        # Your Team (10 members)
        {'name': 'Alice Johnson', 'role': 'Frontend Developer', 'team': 'Your Team'},
        {'name': 'Bob Smith', 'role': 'Backend Developer', 'team': 'Your Team'},
        {'name': 'Carol Davis', 'role': 'UX Designer', 'team': 'Your Team'},
        {'name': 'David Lee', 'role': 'Full Stack Developer', 'team': 'Your Team'},
        {'name': 'Emma Wilson', 'role': 'DevOps Engineer', 'team': 'Your Team'},
        {'name': 'Frank Martinez', 'role': 'QA Engineer', 'team': 'Your Team'},
        {'name': 'Sarah Mitchell', 'role': 'Frontend Developer', 'team': 'Your Team'},
        {'name': 'Michael Brown', 'role': 'Backend Developer', 'team': 'Your Team'},
        {'name': 'Jennifer White', 'role': 'Product Manager', 'team': 'Your Team'},
        {'name': 'Robert Garcia', 'role': 'Data Analyst', 'team': 'Your Team'},
        
        # Alpha Team (8 members)
        {'name': 'Grace Chen', 'role': 'Product Manager', 'team': 'Alpha Team'},
        {'name': 'Henry Taylor', 'role': 'Backend Developer', 'team': 'Alpha Team'},
        {'name': 'Olivia Martinez', 'role': 'Frontend Developer', 'team': 'Alpha Team'},
        {'name': 'James Wilson', 'role': 'Full Stack Developer', 'team': 'Alpha Team'},
        {'name': 'Sophia Anderson', 'role': 'UX Designer', 'team': 'Alpha Team'},
        {'name': 'William Thomas', 'role': 'DevOps Engineer', 'team': 'Alpha Team'},
        {'name': 'Isabella Moore', 'role': 'QA Engineer', 'team': 'Alpha Team'},
        {'name': 'Daniel Jackson', 'role': 'Backend Developer', 'team': 'Alpha Team'},
        
        # Beta Team (6 members)
        {'name': 'Iris Anderson', 'role': 'Frontend Developer', 'team': 'Beta Team'},
        {'name': 'Shane Williams', 'role': 'Full Stack Developer', 'team': 'Beta Team'},
        {'name': 'Emily Harris', 'role': 'Backend Developer', 'team': 'Beta Team'},
        {'name': 'Matthew Clark', 'role': 'UX Designer', 'team': 'Beta Team'},
        {'name': 'Ava Lewis', 'role': 'QA Engineer', 'team': 'Beta Team'},
        {'name': 'Ryan Robinson', 'role': 'DevOps Engineer', 'team': 'Beta Team'},
        
        # Gamma Team (6 members)
        {'name': 'Georgia Lopez', 'role': 'DevOps Engineer', 'team': 'Gamma Team'},
        {'name': 'Ethan Walker', 'role': 'Backend Developer', 'team': 'Gamma Team'},
        {'name': 'Mia Hall', 'role': 'Frontend Developer', 'team': 'Gamma Team'},
        {'name': 'Alexander Young', 'role': 'Full Stack Developer', 'team': 'Gamma Team'},
        {'name': 'Charlotte King', 'role': 'Product Manager', 'team': 'Gamma Team'},
        {'name': 'Benjamin Wright', 'role': 'QA Engineer', 'team': 'Gamma Team'},
    ]
    
    users = []
    with app.app_context():
        for idx, user_data in enumerate(users_data, 1):
            # Create initials
            name_parts = user_data['name'].split()
            initials = ''.join([part[0] for part in name_parts])
            
            user = User(
                user_id=f'USER-{idx:03d}',
                name=user_data['name'],
                email=f"{user_data['name'].lower().replace(' ', '.')}@company.com",
                initials=initials,
                role=user_data['role'],
                team=user_data['team'],
                is_active=True
            )
            db.session.add(user)
            users.append(user)
        
        db.session.commit()
        print(f"✅ Created {len(users)} users across 4 teams")
        print(f"   • Your Team: 10 members")
        print(f"   • Alpha Team: 8 members")
        print(f"   • Beta Team: 6 members")
        print(f"   • Gamma Team: 6 members")
        return users

def generate_tasks():
    """Generate 2000 realistic tasks with varied time ranges"""
    
    # Expanded task templates with more variety
    task_templates = [
        # Web Platform tasks
        {'name': 'Implement user authentication flow', 'project': 'Web Platform', 'priority': 'High', 'tags': 'authentication,security'},
        {'name': 'Fix responsive design on mobile', 'project': 'Web Platform', 'priority': 'High', 'tags': 'bug,ui,mobile'},
        {'name': 'Add dark mode support', 'project': 'Web Platform', 'priority': 'Medium', 'tags': 'feature,ui'},
        {'name': 'Optimize image loading performance', 'project': 'Web Platform', 'priority': 'Medium', 'tags': 'performance,optimization'},
        {'name': 'Update homepage hero section', 'project': 'Web Platform', 'priority': 'Low', 'tags': 'ui,content'},
        {'name': 'Integrate analytics tracking', 'project': 'Web Platform', 'priority': 'Medium', 'tags': 'analytics,feature'},
        {'name': 'Fix navigation menu bug', 'project': 'Web Platform', 'priority': 'High', 'tags': 'bug,navigation'},
        {'name': 'Add email notifications', 'project': 'Web Platform', 'priority': 'Medium', 'tags': 'feature,notifications'},
        {'name': 'Implement search functionality', 'project': 'Web Platform', 'priority': 'High', 'tags': 'feature,search'},
        {'name': 'Update terms of service page', 'project': 'Web Platform', 'priority': 'Low', 'tags': 'content,legal'},
        {'name': 'Create user profile page', 'project': 'Web Platform', 'priority': 'High', 'tags': 'feature,ui'},
        {'name': 'Fix CSS layout issues', 'project': 'Web Platform', 'priority': 'Medium', 'tags': 'bug,css'},
        {'name': 'Add social login integration', 'project': 'Web Platform', 'priority': 'Medium', 'tags': 'feature,authentication'},
        {'name': 'Improve form validation', 'project': 'Web Platform', 'priority': 'Low', 'tags': 'enhancement,ux'},
        {'name': 'Update footer links', 'project': 'Web Platform', 'priority': 'Low', 'tags': 'content'},
        
        # Mobile App tasks
        {'name': 'Fix crash on iOS 16', 'project': 'Mobile App', 'priority': 'High', 'tags': 'bug,ios,crash'},
        {'name': 'Implement push notifications', 'project': 'Mobile App', 'priority': 'High', 'tags': 'feature,notifications'},
        {'name': 'Add biometric authentication', 'project': 'Mobile App', 'priority': 'Medium', 'tags': 'feature,security'},
        {'name': 'Optimize battery usage', 'project': 'Mobile App', 'priority': 'Medium', 'tags': 'performance,optimization'},
        {'name': 'Update app icon and splash screen', 'project': 'Mobile App', 'priority': 'Low', 'tags': 'ui,branding'},
        {'name': 'Fix camera permission issue', 'project': 'Mobile App', 'priority': 'High', 'tags': 'bug,permissions'},
        {'name': 'Add offline mode support', 'project': 'Mobile App', 'priority': 'High', 'tags': 'feature,offline'},
        {'name': 'Implement in-app purchases', 'project': 'Mobile App', 'priority': 'Medium', 'tags': 'feature,monetization'},
        {'name': 'Update to latest React Native', 'project': 'Mobile App', 'priority': 'Medium', 'tags': 'maintenance,upgrade'},
        {'name': 'Add social media sharing', 'project': 'Mobile App', 'priority': 'Low', 'tags': 'feature,social'},
        {'name': 'Fix Android memory leak', 'project': 'Mobile App', 'priority': 'High', 'tags': 'bug,android,performance'},
        {'name': 'Implement location tracking', 'project': 'Mobile App', 'priority': 'Medium', 'tags': 'feature,location'},
        {'name': 'Add multi-language support', 'project': 'Mobile App', 'priority': 'Medium', 'tags': 'feature,i18n'},
        {'name': 'Fix keyboard overlay issue', 'project': 'Mobile App', 'priority': 'Low', 'tags': 'bug,ui'},
        {'name': 'Optimize app size', 'project': 'Mobile App', 'priority': 'Medium', 'tags': 'performance,optimization'},
        
        # API Services tasks
        {'name': 'Fix memory leak in user service', 'project': 'API Services', 'priority': 'High', 'tags': 'bug,performance'},
        {'name': 'Implement rate limiting', 'project': 'API Services', 'priority': 'High', 'tags': 'feature,security'},
        {'name': 'Add API versioning', 'project': 'API Services', 'priority': 'Medium', 'tags': 'feature,api'},
        {'name': 'Update database indexes', 'project': 'API Services', 'priority': 'Medium', 'tags': 'performance,database'},
        {'name': 'Write API documentation', 'project': 'API Services', 'priority': 'Medium', 'tags': 'documentation'},
        {'name': 'Fix authentication token expiry', 'project': 'API Services', 'priority': 'High', 'tags': 'bug,authentication'},
        {'name': 'Implement caching layer', 'project': 'API Services', 'priority': 'High', 'tags': 'feature,performance'},
        {'name': 'Add error tracking integration', 'project': 'API Services', 'priority': 'Medium', 'tags': 'monitoring,feature'},
        {'name': 'Optimize SQL queries', 'project': 'API Services', 'priority': 'Medium', 'tags': 'performance,database'},
        {'name': 'Set up CI/CD pipeline', 'project': 'API Services', 'priority': 'High', 'tags': 'devops,automation'},
        {'name': 'Add GraphQL endpoint', 'project': 'API Services', 'priority': 'Medium', 'tags': 'feature,api'},
        {'name': 'Fix database connection pool', 'project': 'API Services', 'priority': 'High', 'tags': 'bug,database'},
        {'name': 'Implement webhook system', 'project': 'API Services', 'priority': 'Medium', 'tags': 'feature,integration'},
        {'name': 'Add request logging', 'project': 'API Services', 'priority': 'Low', 'tags': 'monitoring,logging'},
        {'name': 'Upgrade PostgreSQL version', 'project': 'API Services', 'priority': 'Medium', 'tags': 'maintenance,database'},
        
        # Generic/Cross-project tasks
        {'name': 'Code review for PR', 'project': 'Web Platform', 'priority': 'Medium', 'tags': 'review'},
        {'name': 'Update dependencies', 'project': 'Mobile App', 'priority': 'Low', 'tags': 'maintenance'},
        {'name': 'Fix security vulnerability', 'project': 'API Services', 'priority': 'High', 'tags': 'bug,security'},
        {'name': 'Refactor authentication middleware', 'project': 'API Services', 'priority': 'Medium', 'tags': 'refactor'},
        {'name': 'Add unit tests', 'project': 'Web Platform', 'priority': 'Medium', 'tags': 'testing'},
        {'name': 'Design onboarding flow', 'project': 'Mobile App', 'priority': 'High', 'tags': 'design,ux'},
        {'name': 'Setup monitoring dashboard', 'project': 'API Services', 'priority': 'Medium', 'tags': 'monitoring,devops'},
        {'name': 'Conduct user testing', 'project': 'Web Platform', 'priority': 'High', 'tags': 'research,ux'},
        {'name': 'Optimize Docker images', 'project': 'API Services', 'priority': 'Low', 'tags': 'devops,optimization'},
        {'name': 'Update accessibility features', 'project': 'Web Platform', 'priority': 'Medium', 'tags': 'ui,accessibility'},
    ]
    
    # Status distribution: ~35% Open, ~28% In Progress, ~30% Completed, ~7% Blocked
    statuses = ['Open'] * 35 + ['In Progress'] * 28 + ['Completed'] * 30 + ['Blocked'] * 7
    
    with app.app_context():
        users = User.query.all()
        user_ids = [user.user_id for user in users]
        
        tasks = []
        num_tasks = 2000
        
        print(f"⏳ Generating {num_tasks} tasks with realistic data...")
        
        for idx in range(1, num_tasks + 1):
            # Cycle through templates and add variation
            template = task_templates[(idx - 1) % len(task_templates)]
            status = random.choice(statuses)
            
            # More realistic time ranges: 1-90 days ago
            days_ago = random.randint(1, 90)
            created_date = datetime.now() - timedelta(days=days_ago)
            
            # Add some time variation (different times of day)
            created_date = created_date.replace(
                hour=random.randint(8, 18),
                minute=random.randint(0, 59),
                second=random.randint(0, 59)
            )
            
            start_date = None
            completed_date = None
            blocked_reason = None
            
            if status in ['In Progress', 'Completed']:
                # Start date: 0-5 days after creation
                start_date = created_date + timedelta(
                    days=random.randint(0, 5),
                    hours=random.randint(0, 23)
                )
            
            if status == 'Completed':
                # Completion time: 4-240 hours after start (realistic work times)
                work_hours = random.choice([4, 8, 12, 16, 24, 40, 80, 120, 160, 240])
                completed_date = start_date + timedelta(hours=work_hours)
            
            if status == 'Blocked':
                blocked_reason = random.choice([
                    'Waiting for API access from external team',
                    'Dependency on TASK-' + str(random.randint(1, idx-1)) if idx > 1 else 'Dependency on another task',
                    'Waiting for client approval',
                    'Technical blocker - need architecture decision',
                    'Waiting for design assets',
                    'Blocked by infrastructure issues',
                    'Pending security review',
                    'Missing requirements clarification',
                    'Third-party service integration pending'
                ])
            
            # Due date: 7-30 days after creation
            due_date = created_date + timedelta(days=random.randint(7, 30))
            
            # Varied estimated hours based on priority
            if template['priority'] == 'High':
                estimated_hours = random.choice([8, 16, 24, 40])
            elif template['priority'] == 'Medium':
                estimated_hours = random.choice([4, 8, 16, 24])
            else:
                estimated_hours = random.choice([2, 4, 8])
            
            # Add task number variation to task names
            task_name_variations = [
                template['name'],
                f"{template['name']} - Phase {random.randint(1, 3)}",
                f"{template['name']} v{random.randint(1, 5)}",
                template['name'],  # Keep original more often
                template['name'],
            ]
            
            task = Task(
                task_id=f'TASK-{idx:04d}',
                task_name=random.choice(task_name_variations),
                description=f"Detailed description for {template['name']}. This task requires proper planning and implementation. Task ID: {idx}",
                status=status,
                priority=template['priority'],
                project=template['project'],
                assigned_to=random.choice(user_ids),
                created_date=created_date,
                due_date=due_date,
                start_date=start_date,
                completed_date=completed_date,
                estimated_hours=estimated_hours,
                tags=template['tags'],
                blocked_reason=blocked_reason,
                comments=f"Task created on {created_date.strftime('%Y-%m-%d')}. Assigned to team member."
            )
            db.session.add(task)
            tasks.append(task)
            
            # Commit in batches for better performance
            if idx % 500 == 0:
                db.session.commit()
                print(f"   ✓ Generated {idx}/{num_tasks} tasks...")
        
        db.session.commit()
        print(f"✅ Created {len(tasks)} tasks with realistic time ranges")
        
        # Print statistics
        print("\n📊 Task Statistics:")
        print(f"   Open: {Task.query.filter_by(status='Open').count()}")
        print(f"   In Progress: {Task.query.filter_by(status='In Progress').count()}")
        print(f"   Completed: {Task.query.filter_by(status='Completed').count()}")
        print(f"   Blocked: {Task.query.filter_by(status='Blocked').count()}")
        print(f"   Total: {Task.query.count()}")

def seed_all():
    """Run all seed functions"""
    print("🌱 Starting database seeding...")
    print("="*50)
    
    clear_data()
    generate_users()
    generate_tasks()
    
    print("="*50)
    print("✅ Database seeding completed successfully!")
    print("🚀 You can now start the Flask server")

if __name__ == '__main__':
    seed_all()

