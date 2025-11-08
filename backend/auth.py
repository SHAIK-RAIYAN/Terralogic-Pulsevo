import os
import jwt
from functools import wraps
from flask import request, jsonify
from dotenv import load_dotenv

load_dotenv()

SUPABASE_JWT_SECRET = os.getenv('SUPABASE_JWT_SECRET')

def require_auth(f):
    """Decorator to require Supabase JWT authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return jsonify({'error': 'No authorization header'}), 401
        
        try:
            # Extract token from "Bearer <token>"
            token = auth_header.split(' ')[1] if ' ' in auth_header else auth_header
            
            # Verify JWT token
            payload = jwt.decode(
                token,
                SUPABASE_JWT_SECRET,
                algorithms=['HS256'],
                audience='authenticated'
            )
            
            # Add user info to request context
            request.user_id = payload.get('sub')
            request.user_email = payload.get('email')
            
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
        except Exception as e:
            return jsonify({'error': f'Authentication failed: {str(e)}'}), 401
        
        return f(*args, **kwargs)
    
    return decorated_function
