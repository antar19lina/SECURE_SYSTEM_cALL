import '../css/style.css';
import { setupAuth } from './auth.js';
import { setupFileManager } from './fileManager.js';
import { setupUI } from './ui.js';

// Initialize the application
function initApp() {
  const app = document.getElementById('app');
  
  // Check if user is logged in
  const currentUser = localStorage.getItem('currentUser');
  
  if (currentUser) {
    // User is logged in, show file manager
    setupFileManager(app, JSON.parse(currentUser));
  } else {
    // User is not logged in, show login page
    setupAuth(app);
  }
  
  // Setup UI components and event listeners
  setupUI();
}

// Start the application
initApp();