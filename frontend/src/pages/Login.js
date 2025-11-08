import React from 'react';
import { Auth } from '@supabase/auth-ui-react';
import { ThemeSupa } from '@supabase/auth-ui-shared';
import { supabase } from '../api/client';
import './Login.css';

function Login() {
  return (
    <div className="login-container">
      <div className="login-card">
        <div className="login-header">
          <h1>PULSEVO</h1>
          <p>AI-Powered Team Productivity Analytics</p>
        </div>
        <Auth
          supabaseClient={supabase}
          appearance={{ theme: ThemeSupa }}
          theme="dark"
          providers={[]}
          redirectTo={window.location.origin}
        />
      </div>
    </div>
  );
}

export default Login;
