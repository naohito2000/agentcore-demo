import React, { useState, useEffect } from 'react';
import './App.css';

const API_URL = process.env.REACT_APP_API_URL;
const API_KEY = process.env.REACT_APP_API_KEY;

function App() {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');
  
  useEffect(() => {
    fetchTasks();
  }, []);
  
  // 環境変数チェック
  if (!API_URL || !API_KEY) {
    return (
      <div className="App">
        <div className="error">
          <h2>Configuration Error</h2>
          <p>REACT_APP_API_URL and REACT_APP_API_KEY must be set</p>
        </div>
      </div>
    );
  }

  const fetchTasks = async () => {
    try {
      const response = await fetch(API_URL, {
        headers: {
          'x-api-key': API_KEY
        }
      });
      const data = await response.json();
      setTasks(data.tasks || []);
    } catch (error) {
      console.error('Error fetching tasks:', error);
    } finally {
      setLoading(false);
    }
  };

  const deleteTask = async (taskId) => {
    if (!window.confirm('このタスクを削除しますか？')) {
      return;
    }
    
    try {
      const response = await fetch(`${API_URL}/${taskId}`, {
        method: 'DELETE',
        headers: {
          'x-api-key': API_KEY
        }
      });
      
      if (response.ok) {
        // タスク一覧を再取得
        fetchTasks();
      } else {
        console.error('Failed to delete task');
      }
    } catch (error) {
      console.error('Error deleting task:', error);
    }
  };

  const filteredTasks = tasks.filter(task => {
    if (filter === 'all') return true;
    return task.status === filter;
  });

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'high': return '#ef4444';
      case 'medium': return '#f59e0b';
      case 'low': return '#10b981';
      default: return '#6b7280';
    }
  };

  if (loading) {
    return <div className="loading">Loading tasks...</div>;
  }

  return (
    <div className="App">
      <header className="header">
        <h1>🎯 AgentCore Task Manager</h1>
        <p>DevOps Assistant Tasks</p>
      </header>

      <div className="filters">
        <button 
          className={filter === 'all' ? 'active' : ''} 
          onClick={() => setFilter('all')}
        >
          All ({tasks.length})
        </button>
        <button 
          className={filter === 'todo' ? 'active' : ''} 
          onClick={() => setFilter('todo')}
        >
          Todo ({tasks.filter(t => t.status === 'todo').length})
        </button>
        <button 
          className={filter === 'in_progress' ? 'active' : ''} 
          onClick={() => setFilter('in_progress')}
        >
          In Progress ({tasks.filter(t => t.status === 'in_progress').length})
        </button>
        <button 
          className={filter === 'done' ? 'active' : ''} 
          onClick={() => setFilter('done')}
        >
          Done ({tasks.filter(t => t.status === 'done').length})
        </button>
      </div>

      <div className="tasks">
        {filteredTasks.length === 0 ? (
          <div className="empty">No tasks found</div>
        ) : (
          filteredTasks.map(task => (
            <div key={task.id} className="task-card">
              <div className="task-header">
                <div className="task-title-row">
                  <h3>{task.title}</h3>
                  <button 
                    className="delete-button"
                    onClick={() => deleteTask(task.id)}
                    title="削除"
                  >
                    🗑️
                  </button>
                </div>
                <span 
                  className="priority-badge" 
                  style={{ backgroundColor: getPriorityColor(task.priority) }}
                >
                  {task.priority}
                </span>
              </div>
              <p className="task-description">{task.description}</p>
              <div className="task-meta">
                {task.assignee && <span>👤 {task.assignee}</span>}
                {task.due_date && <span>📅 {task.due_date}</span>}
                <span className="status">{task.status}</span>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

export default App;
