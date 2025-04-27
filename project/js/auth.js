import { showToast } from './ui.js';

// Default credentials for demo purposes
const DEMO_USERS = [
  { username: 'admin', password: 'admin', fullName: 'Administrator' },
  { username: 'user', password: 'user', fullName: 'Regular User' }
];

// Setup authentication
export function setupAuth(container) {
  // Create login form
  container.innerHTML = `
    <div class="login-container">
      <form class="login-form" id="loginForm">
        <h2>FileManager Pro</h2>
        <div class="form-group">
          <label for="username">Username</label>
          <input type="text" id="username" name="username" required>
        </div>
        <div class="form-group">
          <label for="password">Password</label>
          <input type="password" id="password" name="password" required>
        </div>
        <button type="submit" class="btn btn-primary btn-block">Login</button>
      </form>
    </div>
  `;
  
  // Add event listener to login form
  const loginForm = document.getElementById('loginForm');
  loginForm.addEventListener('submit', handleLogin);
}

// Handle login form submission
function handleLogin(event) {
  event.preventDefault();
  
  const username = document.getElementById('username').value;
  const password = document.getElementById('password').value;
  
  // Authenticate user (in a real app, this would be a server request)
  const user = authenticateUser(username, password);
  
  if (user) {
    // Store user in localStorage (in a real app, use a secure method like JWT)
    localStorage.setItem('currentUser', JSON.stringify(user));
    
    // Show success message
    showToast('Login successful!', 'success');
    
    // Reload the app to show file manager
    setTimeout(() => {
      window.location.reload();
    }, 1000);
  } else {
    showToast('Invalid username or password', 'error');
  }
}

// Authenticate user against demo users
function authenticateUser(username, password) {
  return DEMO_USERS.find(user => 
    user.username === username && user.password === password
  );
}

// Logout function
export function logout() {
  // Remove user from localStorage
  localStorage.removeItem('currentUser');
  
  // Show success message
  showToast('Logged out successfully!', 'success');
  
  // Reload the app to show login page
  setTimeout(() => {
    window.location.reload();
  }, 1000);
}