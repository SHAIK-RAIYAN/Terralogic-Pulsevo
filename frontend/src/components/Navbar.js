import React, { useContext, useState } from 'react';
import './Navbar.css';
import { Activity, User, LogOut } from 'lucide-react';
import { DateFilterContext } from '../App';
import { supabase } from '../api/client';

function Navbar() {
  const { dateFilter, setDateFilter, session } = useContext(DateFilterContext);
  const [showMenu, setShowMenu] = useState(false);

  const handleLogout = async () => {
    await supabase.auth.signOut();
  };

  const handleDateFilterChange = (e) => {
    setDateFilter(e.target.value);
  };

  return (
    <nav className="navbar">
      <div className="navbar-left">
        <Activity size={24} className="logo-icon" />
        <span className="logo-text">PULSEVO</span>
      </div>
      <div className="navbar-right">
        <select 
          className="time-selector"
          value={dateFilter}
          onChange={handleDateFilterChange}
        >
          <option value="today">Today</option>
          <option value="week">This Week</option>
          <option value="month">This Month</option>
          <option value="year">This Year</option>
          <option value="all">All</option>
        </select>
        <div className="profile-menu">
          <button className="profile-button" onClick={() => setShowMenu(!showMenu)}>
            <User size={20} />
          </button>
          {showMenu && (
            <div className="profile-dropdown">
              <div className="profile-email">{session?.user?.email}</div>
              <button className="logout-button" onClick={handleLogout}>
                <LogOut size={16} />
                Logout
              </button>
            </div>
          )}
        </div>
      </div>
    </nav>
  );
}

export default Navbar;

