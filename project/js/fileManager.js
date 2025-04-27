import { showModal, showToast, showContextMenu } from './ui.js';
import { logout } from './auth.js';
import { fileOperations } from './fileOperations.js';

// Demo data for files and folders
const DEMO_DATA = {
  'root': [
    { id: '1', name: 'Documents', type: 'folder', parent: 'root' },
    { id: '2', name: 'Images', type: 'folder', parent: 'root' },
    { id: '3', name: 'Videos', type: 'folder', parent: 'root' },
    { id: '4', name: 'Project.docx', type: 'file', size: '25 KB', modified: '2023-09-15', parent: 'root' },
    { id: '5', name: 'Notes.txt', type: 'file', size: '2 KB', modified: '2023-09-18', parent: 'root', content: 'These are my notes for the project.' },
    { id: '6', name: 'Budget.xlsx', type: 'file', size: '18 KB', modified: '2023-09-10', parent: 'root' },
  ],
  '1': [
    { id: '7', name: 'Resume.pdf', type: 'file', size: '120 KB', modified: '2023-08-20', parent: '1' },
    { id: '8', name: 'Report.docx', type: 'file', size: '45 KB', modified: '2023-09-05', parent: '1' },
    { id: '9', name: 'Work', type: 'folder', parent: '1' },
  ],
  '2': [
    { id: '10', name: 'Vacation.jpg', type: 'file', size: '2.5 MB', modified: '2023-07-15', parent: '2' },
    { id: '11', name: 'Profile.png', type: 'file', size: '500 KB', modified: '2023-08-10', parent: '2' },
  ],
  '3': [
    { id: '12', name: 'Tutorial.mp4', type: 'file', size: '15 MB', modified: '2023-06-25', parent: '3' },
  ],
  '9': [
    { id: '13', name: 'Presentation.pptx', type: 'file', size: '8 MB', modified: '2023-09-01', parent: '9' },
  ]
};

// Current state of the file manager
let state = {
  currentPath: 'root',
  currentPathName: 'Home',
  pathHistory: [],
  viewMode: 'grid', // 'grid' or 'list'
  selectedItems: [],
  clipboard: {
    items: [],
    operation: null // 'copy' or 'cut'
  }
};

// Setup file manager
export function setupFileManager(container, user) {
  // Create file manager structure
  container.innerHTML = `
    <div class="file-manager">
      <header class="header">
        <div class="header-left">
          <div class="app-logo">FileManager Pro</div>
        </div>
        <div class="header-right">
          <button id="themeToggle" class="action-button">
            <i class="fas fa-moon"></i>
          </button>
          <div class="user-info">
            <div class="user-avatar">${user.fullName.charAt(0)}</div>
            <span>${user.fullName}</span>
          </div>
          <button id="logoutBtn" class="action-button">
            <i class="fas fa-sign-out-alt"></i>
            Logout
          </button>
        </div>
      </header>
      
      <nav class="navbar">
        <div class="nav-buttons">
          <button id="backBtn" class="action-button" disabled>
            <i class="fas fa-arrow-left"></i>
          </button>
          <button id="reloadBtn" class="action-button">
            <i class="fas fa-sync-alt"></i>
          </button>
          <button id="newFolderBtn" class="action-button">
            <i class="fas fa-folder-plus"></i>
            New Folder
          </button>
          <button id="newFileBtn" class="action-button">
            <i class="fas fa-file-plus"></i>
            New File
          </button>
          <button id="uploadBtn" class="action-button">
            <i class="fas fa-upload"></i>
            Upload
          </button>
        </div>
        <div class="path-bar">
          <i class="fas fa-home"></i>
          <span id="currentPath">Home</span>
        </div>
        <div class="search-bar">
          <i class="fas fa-search"></i>
          <input type="text" id="searchInput" placeholder="Search files...">
        </div>
      </nav>
      
      <div class="main-container">
        <aside class="sidebar">
          <div class="sidebar-section">
            <h3>Favorites</h3>
            <div class="sidebar-item" data-path="root">
              <i class="fas fa-home"></i>
              <span>Home</span>
            </div>
            <div class="sidebar-item">
              <i class="fas fa-star"></i>
              <span>Starred</span>
            </div>
            <div class="sidebar-item">
              <i class="fas fa-clock"></i>
              <span>Recent</span>
            </div>
          </div>
          
          <div class="sidebar-section">
            <h3>Categories</h3>
            <div class="sidebar-item">
              <i class="fas fa-file-alt"></i>
              <span>Documents</span>
            </div>
            <div class="sidebar-item">
              <i class="fas fa-image"></i>
              <span>Images</span>
            </div>
            <div class="sidebar-item">
              <i class="fas fa-video"></i>
              <span>Videos</span>
            </div>
            <div class="sidebar-item">
              <i class="fas fa-music"></i>
              <span>Audio</span>
            </div>
          </div>
        </aside>
        
        <main class="main-content">
          <div class="files-view" id="filesView"></div>
        </main>
      </div>
      
      <footer class="status-bar">
        <div id="itemCount">0 items</div>
        <div id="storageInfo">Free space: 15.5 GB / 20 GB</div>
      </footer>
    </div>
  `;
  
  // Load initial files
  loadFiles(state.currentPath);
  
  // Setup event listeners
  setupEventListeners();
}

// Load files for the current path
function loadFiles(path) {
  const filesView = document.getElementById('filesView');
  const files = DEMO_DATA[path] || [];
  
  // Update state
  state.currentPath = path;
  updateBreadcrumb();
  
  // Update back button state
  document.getElementById('backBtn').disabled = state.pathHistory.length === 0;
  
  // Render files
  if (state.viewMode === 'grid') {
    renderGridView(filesView, files);
  } else {
    renderListView(filesView, files);
  }
  
  // Update item count
  document.getElementById('itemCount').textContent = `${files.length} items`;
}

// Render files in grid view
function renderGridView(container, files) {
  container.className = 'files-view file-grid';
  
  if (files.length === 0) {
    container.innerHTML = `<div class="empty-folder">This folder is empty</div>`;
    return;
  }
  
  container.innerHTML = files.map(file => `
    <div class="file-item" data-id="${file.id}" data-type="${file.type}">
      <div class="file-item-icon ${file.type}">
        <i class="fas ${file.type === 'folder' ? 'fa-folder' : getFileIcon(file.name)}"></i>
      </div>
      <div class="file-item-name">${file.name}</div>
    </div>
  `).join('');
}

// Render files in list view
function renderListView(container, files) {
  container.className = 'files-view file-list';
  
  if (files.length === 0) {
    container.innerHTML = `<div class="empty-folder">This folder is empty</div>`;
    return;
  }
  
  container.innerHTML = `
    <div class="file-list-header">
      <div class="file-list-header-cell" style="width: 50%">Name</div>
      <div class="file-list-header-cell" style="width: 15%">Type</div>
      <div class="file-list-header-cell" style="width: 15%">Size</div>
      <div class="file-list-header-cell" style="width: 20%">Modified</div>
    </div>
    ${files.map(file => `
      <div class="file-list-row" data-id="${file.id}" data-type="${file.type}">
        <div class="file-list-cell">
          <i class="fas ${file.type === 'folder' ? 'fa-folder' : getFileIcon(file.name)}"></i>
          ${file.name}
        </div>
        <div class="file-list-cell">${file.type === 'folder' ? 'Folder' : getFileType(file.name)}</div>
        <div class="file-list-cell">${file.type === 'folder' ? '--' : file.size}</div>
        <div class="file-list-cell">${file.modified || '--'}</div>
      </div>
    `).join('')}
  `;
}

// Update breadcrumb navigation
function updateBreadcrumb() {
  const currentPathEl = document.getElementById('currentPath');
  currentPathEl.textContent = state.currentPathName;
}

// Get file icon based on file extension
function getFileIcon(filename) {
  const ext = filename.split('.').pop().toLowerCase();
  
  switch(ext) {
    case 'pdf': return 'fa-file-pdf';
    case 'doc':
    case 'docx': return 'fa-file-word';
    case 'xls':
    case 'xlsx': return 'fa-file-excel';
    case 'ppt':
    case 'pptx': return 'fa-file-powerpoint';
    case 'jpg':
    case 'jpeg':
    case 'png':
    case 'gif': return 'fa-file-image';
    case 'mp3':
    case 'wav': return 'fa-file-audio';
    case 'mp4':
    case 'avi':
    case 'mov': return 'fa-file-video';
    case 'zip':
    case 'rar': return 'fa-file-archive';
    case 'txt': return 'fa-file-alt';
    default: return 'fa-file';
  }
}

// Get file type based on file extension
function getFileType(filename) {
  const ext = filename.split('.').pop().toLowerCase();
  
  switch(ext) {
    case 'pdf': return 'PDF Document';
    case 'doc':
    case 'docx': return 'Word Document';
    case 'xls':
    case 'xlsx': return 'Excel Spreadsheet';
    case 'ppt':
    case 'pptx': return 'PowerPoint';
    case 'jpg':
    case 'jpeg':
    case 'png':
    case 'gif': return 'Image';
    case 'mp3':
    case 'wav': return 'Audio';
    case 'mp4':
    case 'avi':
    case 'mov': return 'Video';
    case 'zip':
    case 'rar': return 'Archive';
    case 'txt': return 'Text File';
    default: return 'File';
  }
}

// Setup event listeners for file manager
function setupEventListeners() {
  // Logout button
  document.getElementById('logoutBtn').addEventListener('click', logout);
  
  // Theme toggle
  document.getElementById('themeToggle').addEventListener('click', toggleTheme);
  
  // Back button
  document.getElementById('backBtn').addEventListener('click', goBack);
  
  // Reload button
  document.getElementById('reloadBtn').addEventListener('click', () => loadFiles(state.currentPath));
  
  // New folder button
  document.getElementById('newFolderBtn').addEventListener('click', createNewFolder);
  
  // New file button
  document.getElementById('newFileBtn').addEventListener('click', createNewFile);
  
  // Sidebar navigation
  document.querySelectorAll('.sidebar-item[data-path]').forEach(item => {
    item.addEventListener('click', () => {
      const path = item.getAttribute('data-path');
      state.pathHistory.push({ path: state.currentPath, name: state.currentPathName });
      state.currentPathName = item.querySelector('span').textContent;
      loadFiles(path);
    });
  });
  
  // File/folder click
  document.getElementById('filesView').addEventListener('click', (e) => {
    const fileItem = e.target.closest('.file-item, .file-list-row');
    if (!fileItem) return;
    
    const fileId = fileItem.getAttribute('data-id');
    const fileType = fileItem.getAttribute('data-type');
    
    if (fileType === 'folder') {
      // Navigate to folder
      state.pathHistory.push({ path: state.currentPath, name: state.currentPathName });
      
      // Find folder name in current data
      const folderData = DEMO_DATA[state.currentPath].find(item => item.id === fileId);
      state.currentPathName = folderData.name;
      
      loadFiles(fileId);
    } else {
      // Open file preview
      openFilePreview(fileId);
    }
  });
  
  // Context menu
  document.getElementById('filesView').addEventListener('contextmenu', (e) => {
    e.preventDefault();
    
    const fileItem = e.target.closest('.file-item, .file-list-row');
    if (!fileItem) {
      // Show context menu for empty space
      showContextMenu(e.pageX, e.pageY, [
        { 
          label: 'New Folder', 
          icon: 'fas fa-folder-plus', 
          action: createNewFolder 
        },
        { 
          label: 'New File', 
          icon: 'fas fa-file-plus', 
          action: createNewFile 
        },
        { 
          label: 'Paste', 
          icon: 'fas fa-paste', 
          action: pasteItems,
          disabled: state.clipboard.items.length === 0
        },
        { type: 'divider' },
        { 
          label: 'View', 
          icon: 'fas fa-th', 
          submenu: [
            { 
              label: 'Grid', 
              icon: 'fas fa-th', 
              action: () => switchView('grid'),
              checked: state.viewMode === 'grid' 
            },
            { 
              label: 'List', 
              icon: 'fas fa-list', 
              action: () => switchView('list'),
              checked: state.viewMode === 'list' 
            }
          ]
        }
      ]);
      return;
    }
    
    const fileId = fileItem.getAttribute('data-id');
    const fileType = fileItem.getAttribute('data-type');
    
    // Show context menu for file/folder
    const fileData = DEMO_DATA[state.currentPath].find(item => item.id === fileId);
    
    showContextMenu(e.pageX, e.pageY, [
      { 
        label: `Open ${fileType === 'folder' ? 'Folder' : 'File'}`, 
        icon: `fas ${fileType === 'folder' ? 'fa-folder-open' : 'fa-file-alt'}`, 
        action: () => {
          if (fileType === 'folder') {
            state.pathHistory.push({ path: state.currentPath, name: state.currentPathName });
            state.currentPathName = fileData.name;
            loadFiles(fileId);
          } else {
            openFilePreview(fileId);
          }
        }
      },
      { type: 'divider' },
      { 
        label: 'Cut', 
        icon: 'fas fa-cut', 
        action: () => cutItem(fileId) 
      },
      { 
        label: 'Copy', 
        icon: 'fas fa-copy', 
        action: () => copyItem(fileId) 
      },
      { 
        label: 'Rename', 
        icon: 'fas fa-edit', 
        action: () => renameItem(fileId) 
      },
      { type: 'divider' },
      { 
        label: 'Delete', 
        icon: 'fas fa-trash-alt', 
        action: () => deleteItem(fileId) 
      }
    ]);
  });
}

// Toggle between light and dark theme
function toggleTheme() {
  const body = document.body;
  const themeToggle = document.getElementById('themeToggle');
  
  body.classList.toggle('dark-mode');
  
  // Update theme toggle icon
  if (body.classList.contains('dark-mode')) {
    themeToggle.innerHTML = '<i class="fas fa-sun"></i>';
  } else {
    themeToggle.innerHTML = '<i class="fas fa-moon"></i>';
  }
}

// Navigate back to previous folder
function goBack() {
  if (state.pathHistory.length === 0) return;
  
  const prevPath = state.pathHistory.pop();
  state.currentPathName = prevPath.name;
  loadFiles(prevPath.path);
}

// Switch between grid and list view
function switchView(mode) {
  state.viewMode = mode;
  loadFiles(state.currentPath);
}

// Create a new folder
function createNewFolder() {
  showModal({
    title: 'Create New Folder',
    content: `
      <div class="form-group">
        <label for="folderName">Folder Name</label>
        <input type="text" id="folderName" name="folderName" required>
      </div>
    `,
    onConfirm: () => {
      const folderName = document.getElementById('folderName').value.trim();
      
      if (!folderName) {
        showToast('Please enter a folder name', 'error');
        return false; // Prevent modal from closing
      }
      
      // Check if folder name already exists
      if (DEMO_DATA[state.currentPath].some(item => item.name === folderName && item.type === 'folder')) {
        showToast('A folder with this name already exists', 'error');
        return false; // Prevent modal from closing
      }
      
      // Create new folder
      const newId = Date.now().toString();
      DEMO_DATA[state.currentPath].push({
        id: newId,
        name: folderName,
        type: 'folder',
        parent: state.currentPath
      });
      
      // Create empty folder contents
      DEMO_DATA[newId] = [];
      
      // Refresh view
      loadFiles(state.currentPath);
      
      showToast(`Folder "${folderName}" created successfully`, 'success');
      return true; // Allow modal to close
    }
  });
}

// Create a new file
function createNewFile() {
  showModal({
    title: 'Create New File',
    content: `
      <div class="form-group">
        <label for="fileName">File Name</label>
        <input type="text" id="fileName" name="fileName" required>
      </div>
      <div class="form-group">
        <label for="fileContent">File Content</label>
        <textarea id="fileContent" name="fileContent" rows="6"></textarea>
      </div>
    `,
    onConfirm: () => {
      const fileName = document.getElementById('fileName').value.trim();
      const fileContent = document.getElementById('fileContent').value;
      
      if (!fileName) {
        showToast('Please enter a file name', 'error');
        return false; // Prevent modal from closing
      }
      
      // Check if file name already exists
      if (DEMO_DATA[state.currentPath].some(item => item.name === fileName && item.type === 'file')) {
        showToast('A file with this name already exists', 'error');
        return false; // Prevent modal from closing
      }
      
      // Create new file
      const newId = Date.now().toString();
      DEMO_DATA[state.currentPath].push({
        id: newId,
        name: fileName,
        type: 'file',
        size: `${fileContent.length} bytes`,
        modified: new Date().toISOString().split('T')[0],
        parent: state.currentPath,
        content: fileContent
      });
      
      // Refresh view
      loadFiles(state.currentPath);
      
      showToast(`File "${fileName}" created successfully`, 'success');
      return true; // Allow modal to close
    }
  });
}

// Open file preview
function openFilePreview(fileId) {
  const fileData = DEMO_DATA[state.currentPath].find(item => item.id === fileId);
  
  if (!fileData) {
    showToast('File not found', 'error');
    return;
  }
  
  const fileContent = fileData.content || 'This file cannot be previewed.';
  const isTextFile = fileData.name.endsWith('.txt');
  
  showModal({
    title: `File Preview: ${fileData.name}`,
    size: 'large',
    content: `
      <div class="file-preview-content">
        ${isTextFile ? 
          `<textarea id="filePreviewContent">${fileContent}</textarea>` : 
          `<div>${fileContent}</div>`
        }
      </div>
    `,
    buttons: isTextFile ? 
      [
        { text: 'Cancel', action: 'cancel' },
        { text: 'Save', action: 'confirm', primary: true }
      ] : 
      [
        { text: 'Close', action: 'cancel' }
      ],
    onConfirm: () => {
      if (isTextFile) {
        const newContent = document.getElementById('filePreviewContent').value;
        fileData.content = newContent;
        fileData.modified = new Date().toISOString().split('T')[0];
        showToast('File saved successfully', 'success');
      }
      return true;
    }
  });
}

// Cut file/folder
function cutItem(itemId) {
  state.clipboard = {
    items: [itemId],
    operation: 'cut'
  };
  
  showToast('Item ready to be moved. Use paste in the destination folder.', 'success');
}

// Copy file/folder
function copyItem(itemId) {
  state.clipboard = {
    items: [itemId],
    operation: 'copy'
  };
  
  showToast('Item copied to clipboard. Use paste in the destination folder.', 'success');
}

// Paste items from clipboard
function pasteItems() {
  if (state.clipboard.items.length === 0) {
    showToast('Clipboard is empty', 'error');
    return;
  }
  
  state.clipboard.items.forEach(itemId => {
    const sourceParent = findParentFolder(itemId);
    const item = DEMO_DATA[sourceParent].find(item => item.id === itemId);
    
    if (!item) {
      showToast('Item not found', 'error');
      return;
    }
    
    // Check if item with same name already exists in destination
    const nameExists = DEMO_DATA[state.currentPath].some(
      existingItem => existingItem.name === item.name && existingItem.type === item.type
    );
    
    if (nameExists) {
      showToast(`An item named "${item.name}" already exists in the destination folder`, 'error');
      return;
    }
    
    if (state.clipboard.operation === 'copy') {
      // For copy operation, create a new item with new ID
      const newId = Date.now().toString();
      const newItem = { ...item, id: newId, parent: state.currentPath };
      
      DEMO_DATA[state.currentPath].push(newItem);
      
      // If it's a folder, copy its contents recursively
      if (item.type === 'folder' && DEMO_DATA[item.id]) {
        DEMO_DATA[newId] = JSON.parse(JSON.stringify(DEMO_DATA[item.id]));
        // Update parent references
        DEMO_DATA[newId].forEach(subItem => {
          subItem.parent = newId;
        });
      }
      
      showToast(`"${item.name}" copied successfully`, 'success');
    } else if (state.clipboard.operation === 'cut') {
      // For cut operation, move the item
      item.parent = state.currentPath;
      
      // Remove from source
      DEMO_DATA[sourceParent] = DEMO_DATA[sourceParent].filter(i => i.id !== itemId);
      
      // Add to destination
      DEMO_DATA[state.currentPath].push(item);
      
      showToast(`"${item.name}" moved successfully`, 'success');
    }
  });
  
  // Clear clipboard after paste
  state.clipboard = { items: [], operation: null };
  
  // Refresh view
  loadFiles(state.currentPath);
}

// Find parent folder of an item
function findParentFolder(itemId) {
  for (const folderId in DEMO_DATA) {
    const items = DEMO_DATA[folderId];
    if (items.some(item => item.id === itemId)) {
      return folderId;
    }
  }
  return null;
}

// Rename file/folder
function renameItem(itemId) {
  const item = DEMO_DATA[state.currentPath].find(item => item.id === itemId);
  
  if (!item) {
    showToast('Item not found', 'error');
    return;
  }
  
  showModal({
    title: `Rename ${item.type === 'folder' ? 'Folder' : 'File'}`,
    content: `
      <div class="form-group">
        <label for="newName">New Name</label>
        <input type="text" id="newName" name="newName" value="${item.name}" required>
      </div>
    `,
    onConfirm: () => {
      const newName = document.getElementById('newName').value.trim();
      
      if (!newName) {
        showToast('Please enter a name', 'error');
        return false; // Prevent modal from closing
      }
      
      // Check if name already exists
      if (DEMO_DATA[state.currentPath].some(i => i.name === newName && i.id !== itemId)) {
        showToast('An item with this name already exists', 'error');
        return false; // Prevent modal from closing
      }
      
      // Update name
      item.name = newName;
      
      // Refresh view
      loadFiles(state.currentPath);
      
      showToast('Item renamed successfully', 'success');
      return true; // Allow modal to close
    }
  });
}

// Delete file/folder
function deleteItem(itemId) {
  const item = DEMO_DATA[state.currentPath].find(item => item.id === itemId);
  
  if (!item) {
    showToast('Item not found', 'error');
    return;
  }
  
  showModal({
    title: 'Confirm Deletion',
    content: `
      <p>Are you sure you want to delete "${item.name}"?</p>
      ${item.type === 'folder' ? '<p class="text-error">This will delete all files and folders inside it.</p>' : ''}
    `,
    buttons: [
      { text: 'Cancel', action: 'cancel' },
      { text: 'Delete', action: 'confirm', primary: true, danger: true }
    ],
    onConfirm: () => {
      // Remove item from current folder
      DEMO_DATA[state.currentPath] = DEMO_DATA[state.currentPath].filter(i => i.id !== itemId);
      
      // If it's a folder, clean up its contents recursively
      if (item.type === 'folder') {
        deleteFolder(itemId);
      }
      
      // Refresh view
      loadFiles(state.currentPath);
      
      showToast(`"${item.name}" deleted successfully`, 'success');
      return true;
    }
  });
}

// Recursively delete folder and its contents
function deleteFolder(folderId) {
  // Delete contents first
  if (DEMO_DATA[folderId]) {
    for (const item of DEMO_DATA[folderId]) {
      if (item.type === 'folder') {
        deleteFolder(item.id);
      }
    }
    
    // Delete folder entry
    delete DEMO_DATA[folderId];
  }
}

// Export functions used by other modules
export const fileManager = {
  loadFiles,
  getState: () => state,
};