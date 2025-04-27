// UI utilities and components

// Show a toast notification
export function showToast(message, type = 'info') {
  // Remove existing toast
  const existingToast = document.querySelector('.toast');
  if (existingToast) {
    existingToast.remove();
  }
  
  // Create toast element
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  
  // Set icon based on type
  let icon;
  switch (type) {
    case 'success':
      icon = 'fas fa-check-circle';
      break;
    case 'error':
      icon = 'fas fa-exclamation-circle';
      break;
    case 'warning':
      icon = 'fas fa-exclamation-triangle';
      break;
    default:
      icon = 'fas fa-info-circle';
  }
  
  // Set toast content
  toast.innerHTML = `
    <i class="toast-icon ${icon}"></i>
    <div class="toast-message">${message}</div>
  `;
  
  // Add toast to document
  document.body.appendChild(toast);
  
  // Auto remove toast after 3 seconds
  setTimeout(() => {
    toast.style.opacity = '0';
    setTimeout(() => {
      toast.remove();
    }, 300);
  }, 3000);
}

// Show a modal dialog
export function showModal({ title, content, size = 'medium', buttons, onConfirm, onCancel } = {}) {
  // Create modal elements
  const modalOverlay = document.createElement('div');
  modalOverlay.className = 'modal-overlay';
  
  const modal = document.createElement('div');
  modal.className = `modal modal-${size}`;
  
  // Set modal content
  modal.innerHTML = `
    <div class="modal-header">
      <h3 class="modal-title">${title}</h3>
      <button class="modal-close">&times;</button>
    </div>
    <div class="modal-content">
      ${content}
    </div>
    <div class="modal-footer">
      ${buttons ? 
        buttons.map(btn => 
          `<button class="btn ${btn.primary ? 'btn-primary' : ''} ${btn.danger ? 'btn-danger' : ''}" data-action="${btn.action}">${btn.text}</button>`
        ).join('') :
        `
          <button class="btn" data-action="cancel">Cancel</button>
          <button class="btn btn-primary" data-action="confirm">OK</button>
        `
      }
    </div>
  `;
  
  // Add modal to document
  modalOverlay.appendChild(modal);
  document.body.appendChild(modalOverlay);
  
  // Handle close button
  const closeBtn = modal.querySelector('.modal-close');
  closeBtn.addEventListener('click', () => {
    closeModal();
    if (onCancel) onCancel();
  });
  
  // Handle footer buttons
  const footerBtns = modal.querySelectorAll('.modal-footer .btn');
  footerBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const action = btn.getAttribute('data-action');
      
      if (action === 'confirm') {
        // If onConfirm returns false, don't close the modal
        if (onConfirm && onConfirm() === false) {
          return;
        }
      } else if (action === 'cancel') {
        if (onCancel) onCancel();
      }
      
      closeModal();
    });
  });
  
  // Handle escape key to close modal
  const handleKeyDown = (e) => {
    if (e.key === 'Escape') {
      closeModal();
      if (onCancel) onCancel();
    }
  };
  
  document.addEventListener('keydown', handleKeyDown);
  
  // Focus the first input element in the modal
  const firstInput = modal.querySelector('input, textarea, select');
  if (firstInput) {
    setTimeout(() => firstInput.focus(), 100);
  }
  
  // Close modal function
  function closeModal() {
    document.removeEventListener('keydown', handleKeyDown);
    modalOverlay.style.opacity = '0';
    setTimeout(() => {
      modalOverlay.remove();
    }, 300);
  }
  
  // Return close function
  return closeModal;
}

// Show context menu
export function showContextMenu(x, y, items) {
  // Remove existing context menu
  const existingMenu = document.querySelector('.context-menu');
  if (existingMenu) {
    existingMenu.remove();
  }
  
  // Create context menu element
  const menu = document.createElement('div');
  menu.className = 'context-menu';
  
  // Position menu
  menu.style.left = `${x}px`;
  menu.style.top = `${y}px`;
  
  // Generate menu items
  const menuHtml = items.map(item => {
    if (item.type === 'divider') {
      return `<div class="context-menu-divider"></div>`;
    }
    
    if (item.submenu) {
      // TODO: Implement sub-menus
      return `
        <div class="context-menu-item ${item.disabled ? 'disabled' : ''}" data-action="${item.action || ''}">
          ${item.icon ? `<i class="${item.icon}"></i>` : ''}
          <span>${item.label}</span>
          <i class="fas fa-chevron-right submenu-icon"></i>
        </div>
      `;
    }
    
    return `
      <div class="context-menu-item ${item.disabled ? 'disabled' : ''}" data-action="${item.action || ''}">
        ${item.icon ? `<i class="${item.icon}"></i>` : ''}
        <span>${item.label}</span>
        ${item.checked ? `<i class="fas fa-check"></i>` : ''}
      </div>
    `;
  }).join('');
  
  menu.innerHTML = menuHtml;
  
  // Add menu to document
  document.body.appendChild(menu);
  
  // Adjust position if menu goes off-screen
  const menuRect = menu.getBoundingClientRect();
  const windowWidth = window.innerWidth;
  const windowHeight = window.innerHeight;
  
  if (menuRect.right > windowWidth) {
    menu.style.left = `${windowWidth - menuRect.width - 10}px`;
  }
  
  if (menuRect.bottom > windowHeight) {
    menu.style.top = `${windowHeight - menuRect.height - 10}px`;
  }
  
  // Add event listeners for menu items
  menu.querySelectorAll('.context-menu-item:not(.disabled)').forEach(item => {
    item.addEventListener('click', () => {
      const action = item.getAttribute('data-action');
      if (action && typeof window[action] === 'function') {
        window[action]();
      } else {
        // Find the matching action in the items array
        const menuItem = items.find(i => i.label === item.querySelector('span').textContent);
        if (menuItem && menuItem.action && typeof menuItem.action === 'function') {
          menuItem.action();
        }
      }
      
      closeMenu();
    });
  });
  
  // Close menu when clicking outside
  function handleClickOutside(e) {
    if (!menu.contains(e.target)) {
      closeMenu();
    }
  }
  
  // Close menu function
  function closeMenu() {
    document.removeEventListener('click', handleClickOutside);
    menu.remove();
  }
  
  // Close menu when clicking outside (with a small delay to prevent immediate closing)
  setTimeout(() => {
    document.addEventListener('click', handleClickOutside);
  }, 100);
  
  // Return close function
  return closeMenu;
}

// Setup UI components and event listeners
export function setupUI() {
  // Add document click listener to close context menu
  document.addEventListener('click', () => {
    const contextMenu = document.querySelector('.context-menu');
    if (contextMenu) {
      contextMenu.remove();
    }
  });
  
  // Prevent default browser context menu
  document.addEventListener('contextmenu', (e) => {
    e.preventDefault();
  });
}

// Export UI components
export const ui = {
  showToast,
  showModal,
  showContextMenu,
};