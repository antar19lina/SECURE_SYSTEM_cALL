#raw file just the python file to see how the managment is done to run the proper project execute PROJECT folder


import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog, ttk
import os
import shutil
import logging
import hashlib
from tkinter import font

# Set up logging
logging.basicConfig(filename='file_management.log', level=logging.INFO, format='%(asctime)s - %(message)s')

# Secure hashed passwords
USER_CREDENTIALS = {
    "admin": hashlib.sha256("password123".encode()).hexdigest()
}

# Theme configurations
THEMES = {
    "light": {
        "bg": "#f0f0f0",
        "fg": "#333333",
        "button_bg": "#e0e0e0",
        "button_fg": "#333333",
        "highlight_bg": "#4a86e8",
        "highlight_fg": "#ffffff",
        "entry_bg": "#ffffff",
        "frame_bg": "#f5f5f5",
        "listbox_bg": "#ffffff",
        "listbox_fg": "#333333"
    },
    "dark": {
        "bg": "#2d2d2d",
        "fg": "#e0e0e0",
        "button_bg": "#444444",
        "button_fg": "#e0e0e0",
        "highlight_bg": "#4a86e8",
        "highlight_fg": "#ffffff",
        "entry_bg": "#3d3d3d",
        "frame_bg": "#363636",
        "listbox_bg": "#3d3d3d",
        "listbox_fg": "#e0e0e0"
    },
    "blue": {
        "bg": "#1a2733",
        "fg": "#e0e0e0",
        "button_bg": "#2c4356",
        "button_fg": "#e0e0e0",
        "highlight_bg": "#4a86e8",
        "highlight_fg": "#ffffff",
        "entry_bg": "#2c3e50",
        "frame_bg": "#1e3040",
        "listbox_bg": "#2c3e50",
        "listbox_fg": "#e0e0e0"
    },
    "green": {
        "bg": "#1e3b2c",
        "fg": "#e0e0e0",
        "button_bg": "#2c5641",
        "button_fg": "#e0e0e0",
        "highlight_bg": "#4caf50",
        "highlight_fg": "#ffffff",
        "entry_bg": "#2c4a3e",
        "frame_bg": "#1e3b2c",
        "listbox_bg": "#2c4a3e",
        "listbox_fg": "#e0e0e0"
    }
}

class FileManagerApp:
    def __init__(self, master):
        self.master = master
        self.master.title("File Management System")
        self.master.geometry("800x600")
        self.master.minsize(800, 600)
        
        # Set custom fonts
        self.title_font = font.Font(family="Helvetica", size=14, weight="bold")
        self.normal_font = font.Font(family="Helvetica", size=10)
        self.button_font = font.Font(family="Helvetica", size=10)
        
        self.username = None
        self.current_theme = "light"
        self.recent_files = []
        
        # Create a style for ttk widgets
        self.style = ttk.Style()
        
        # Set icon (you would need to replace with your own icon file)
        try:
            self.master.iconbitmap("file_manager_icon.ico")
        except:
            pass
            
        self.setup_login()
        
    def apply_theme(self, theme_name):
        if theme_name not in THEMES:
            theme_name = "light"
            
        theme = THEMES[theme_name]
        self.current_theme = theme_name
        
        # Configure ttk style
        self.style.configure('TButton', 
                             background=theme["button_bg"], 
                             foreground=theme["button_fg"],
                             font=self.button_font)
        
        self.style.configure('TLabel', 
                             background=theme["bg"], 
                             foreground=theme["fg"],
                             font=self.normal_font)
        
        self.style.configure('TFrame', 
                             background=theme["frame_bg"])
        
        self.style.configure('TEntry', 
                             fieldbackground=theme["entry_bg"],
                             foreground=theme["fg"])
        
        self.style.map('TButton',
                       background=[('active', theme["highlight_bg"])],
                       foreground=[('active', theme["highlight_fg"])])
        
        # Apply to main window
        self.master.configure(bg=theme["bg"])
        
        # Apply to all frames and widgets
        for widget in self.master.winfo_children():
            widget_class = widget.winfo_class()
            if widget_class in ('Frame', 'Labelframe'):
                widget.configure(bg=theme["frame_bg"])
                for child in widget.winfo_children():
                    child_class = child.winfo_class()
                    if child_class == 'Label':
                        child.configure(bg=theme["frame_bg"], fg=theme["fg"])
                    elif child_class == 'Button':
                        child.configure(bg=theme["button_bg"], fg=theme["button_fg"],
                                       activebackground=theme["highlight_bg"],
                                       activeforeground=theme["highlight_fg"])
                    elif child_class == 'Entry':
                        child.configure(bg=theme["entry_bg"], fg=theme["fg"],
                                       insertbackground=theme["fg"])
                    elif child_class == 'Listbox':
                        child.configure(bg=theme["listbox_bg"], fg=theme["listbox_fg"],
                                       selectbackground=theme["highlight_bg"],
                                       selectforeground=theme["highlight_fg"])

    def setup_login(self):
        # Create a frame with a nice background
        self.login_container = tk.Frame(self.master)
        self.login_container.pack(fill=tk.BOTH, expand=True)
        
        # Center the login form
        self.login_frame = tk.Frame(self.login_container)
        self.login_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        # App title
        tk.Label(self.login_frame, text="File Management System", font=self.title_font).grid(row=0, column=0, columnspan=2, pady=20)
        
        # Username field
        tk.Label(self.login_frame, text="Username:", font=self.normal_font).grid(row=1, column=0, sticky=tk.W, pady=5)
        self.entry_username = tk.Entry(self.login_frame, font=self.normal_font, width=25)
        self.entry_username.grid(row=1, column=1, pady=5, padx=10)
        
        # Password field
        tk.Label(self.login_frame, text="Password:", font=self.normal_font).grid(row=2, column=0, sticky=tk.W, pady=5)
        self.entry_password = tk.Entry(self.login_frame, show='•', font=self.normal_font, width=25)
        self.entry_password.grid(row=2, column=1, pady=5, padx=10)
        
        # Login button
        login_button = tk.Button(self.login_frame, text="Login", command=self.login, 
                                font=self.button_font, width=15, relief=tk.RAISED,
                                cursor="hand2")
        login_button.grid(row=3, column=0, columnspan=2, pady=20)
        
        # Bind Enter key to login
        self.entry_password.bind('<Return>', lambda event: self.login())
        
        # Apply initial theme
        self.apply_theme(self.current_theme)

    def login(self):
        username = self.entry_username.get()
        password = hashlib.sha256(self.entry_password.get().encode()).hexdigest()

        if username in USER_CREDENTIALS and USER_CREDENTIALS[username] == password:
            self.username = username
            logging.info(f"{username} logged in.")
            self.show_file_management()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")

    def show_file_management(self):
        # Destroy login frame
        self.login_container.destroy()
        
        # Create main container
        self.main_container = tk.Frame(self.master)
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        # Create sidebar for actions
        self.sidebar = tk.Frame(self.main_container, width=200)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
        
        # Create content area
        self.content_area = tk.Frame(self.main_container)
        self.content_area.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # User info section
        user_frame = tk.Frame(self.sidebar)
        user_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(user_frame, text=f"Welcome, {self.username}", font=self.title_font).pack(anchor=tk.W)
        
        # Separator
        ttk.Separator(self.sidebar, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
        
        # Action buttons in sidebar
        actions = [
            ("Create File", self.create_file),
            ("Delete File", self.delete_file),
            ("Open File", self.open_file),
            ("Edit File", self.edit_file),
            ("Rename File", self.rename_file),
            ("Move File", self.move_file),
            ("Copy File", self.copy_file),
            ("Search File", self.search_file),
            ("Create Folder", self.create_folder),
            ("Delete Folder", self.delete_folder)
        ]
        
        for text, command in actions:
            btn = tk.Button(self.sidebar, text=text, command=command, 
                          font=self.button_font, width=18, anchor=tk.W,
                          relief=tk.FLAT, cursor="hand2", pady=5)
            btn.pack(fill=tk.X, pady=2)
        
        # Separator
        ttk.Separator(self.sidebar, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
        
        # Theme selection
        theme_frame = tk.Frame(self.sidebar)
        theme_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(theme_frame, text="Select Theme:", font=self.normal_font).pack(anchor=tk.W)
        
        # Theme dropdown
        self.theme_var = tk.StringVar(value=self.current_theme.capitalize())
        theme_options = ["Light", "Dark", "Blue", "Green"]
        
        theme_menu = ttk.Combobox(theme_frame, textvariable=self.theme_var, 
                                 values=theme_options, state="readonly",
                                 font=self.normal_font)
        theme_menu.pack(fill=tk.X, pady=5)
        theme_menu.bind("<<ComboboxSelected>>", self.change_theme)
        
        # Logout button at bottom of sidebar
        logout_btn = tk.Button(self.sidebar, text="Logout", command=self.logout,
                             font=self.button_font, width=18, anchor=tk.W,
                             relief=tk.FLAT, cursor="hand2", pady=5)
        logout_btn.pack(fill=tk.X, pady=10, side=tk.BOTTOM)
        
        # Content area - Recent Files
        self.recent_files_frame = tk.LabelFrame(self.content_area, text="Recent Files", font=self.normal_font)
        self.recent_files_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Search bar
        search_frame = tk.Frame(self.recent_files_frame)
        search_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.filter_recent_files)
        
        tk.Label(search_frame, text="Filter:", font=self.normal_font).pack(side=tk.LEFT, padx=5)
        search_entry = tk.Entry(search_frame, textvariable=self.search_var, font=self.normal_font)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Recent files list with scrollbar
        list_frame = tk.Frame(self.recent_files_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.recent_files_listbox = tk.Listbox(list_frame, font=self.normal_font,
                                             selectmode=tk.SINGLE, 
                                             yscrollcommand=scrollbar.set)
        self.recent_files_listbox.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.recent_files_listbox.yview)
        
        # Bind double-click to open file
        self.recent_files_listbox.bind('<Double-Button-1>', self.open_recent_file)
        
        # Right-click context menu
        self.context_menu = tk.Menu(self.recent_files_listbox, tearoff=0, font=self.normal_font)
        self.context_menu.add_command(label="Open", command=lambda: self.open_recent_file(None))
        self.context_menu.add_command(label="Edit", command=self.edit_recent_file)
        self.context_menu.add_command(label="Delete", command=self.delete_recent_file)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Copy Path", command=self.copy_path_to_clipboard)
        
        self.recent_files_listbox.bind("<Button-3>", self.show_context_menu)
        
        # Status bar
        self.status_bar = tk.Label(self.master, text="Ready", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Enable drag and drop
        self.master.drop_target_register(tk.DND_FILES)
        self.master.dnd_bind('<<Drop>>', self.drop)
        
        # Update recent files list
        self.update_recent_files()
        
        # Apply theme
        self.apply_theme(self.current_theme)

    def change_theme(self, event):
        selected_theme = self.theme_var.get().lower()
        self.apply_theme(selected_theme)
        self.status_bar.config(text=f"Theme changed to {selected_theme}")
        logging.info(f"{self.username} changed theme to {selected_theme}")

    def filter_recent_files(self, *args):
        search_term = self.search_var.get().lower()
        self.recent_files_listbox.delete(0, tk.END)
        
        for file in self.recent_files:
            if search_term in os.path.basename(file).lower():
                self.recent_files_listbox.insert(tk.END, file)

    def show_context_menu(self, event):
        try:
            self.recent_files_listbox.selection_clear(0, tk.END)
            self.recent_files_listbox.selection_set(self.recent_files_listbox.nearest(event.y))
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()

    def copy_path_to_clipboard(self):
        try:
            selected_index = self.recent_files_listbox.curselection()[0]
            selected_file = self.recent_files_listbox.get(selected_index)
            self.master.clipboard_clear()
            self.master.clipboard_append(selected_file)
            self.status_bar.config(text=f"Path copied to clipboard: {selected_file}")
        except IndexError:
            pass

    def update_recent_files(self):
        self.recent_files_listbox.delete(0, tk.END)
        for file in self.recent_files:
            self.recent_files_listbox.insert(tk.END, file)

    def open_recent_file(self, event):
        try:
            selected_index = self.recent_files_listbox.curselection()[0]
            selected_file = self.recent_files_listbox.get(selected_index)
            self.open_file(selected_file)
        except IndexError:
            pass

    def edit_recent_file(self):
        try:
            selected_index = self.recent_files_listbox.curselection()[0]
            selected_file = self.recent_files_listbox.get(selected_index)
            self.edit_file(selected_file)
        except IndexError:
            pass

    def delete_recent_file(self):
        try:
            selected_index = self.recent_files_listbox.curselection()[0]
            selected_file = self.recent_files_listbox.get(selected_index)
            
            if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete {os.path.basename(selected_file)}?"):
                if os.path.exists(selected_file):
                    os.remove(selected_file)
                    self.recent_files.remove(selected_file)
                    self.update_recent_files()
                    self.status_bar.config(text=f"Deleted: {selected_file}")
                    logging.info(f"{self.username} deleted file: {selected_file}")
        except IndexError:
            pass

    def drop(self, event):
        files = event.data.split()
        for file in files:
            if os.path.isfile(file):
                if file not in self.recent_files:
                    self.recent_files.append(file)
                self.update_recent_files()
                self.status_bar.config(text=f"Added via drag and drop: {file}")
                logging.info(f"{self.username} added file via drag and drop: {file}")

    def create_file(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".txt")
        if file_path:
            with open(file_path, 'w') as f:
                f.write("")
            if file_path not in self.recent_files:
                self.recent_files.append(file_path)
            self.update_recent_files()
            self.status_bar.config(text=f"Created: {file_path}")
            logging.info(f"{self.username} created file: {file_path}")

    def delete_file(self, file_path=None):
        if not file_path:
            file_path = filedialog.askopenfilename()
        if file_path and os.path.exists(file_path):
            if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete {os.path.basename(file_path)}?"):
                os.remove(file_path)
                if file_path in self.recent_files:
                    self.recent_files.remove(file_path)
                self.update_recent_files()
                self.status_bar.config(text=f"Deleted: {file_path}")
                logging.info(f"{self.username} deleted file: {file_path}")

    def open_file(self, file_path=None):
        if not file_path:
            file_path = filedialog.askopenfilename()
        if file_path and os.path.exists(file_path):
            try:
                os.startfile(file_path)
                if file_path not in self.recent_files:
                    self.recent_files.append(file_path)
                self.update_recent_files()
                self.status_bar.config(text=f"Opened: {file_path}")
                logging.info(f"{self.username} opened file: {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not open file: {str(e)}")

    def edit_file(self, file_path=None):
        if not file_path:
            file_path = filedialog.askopenfilename()
        if file_path and os.path.exists(file_path):
            try:
                # Create a new window for editing
                edit_window = tk.Toplevel(self.master)
                edit_window.title(f"Edit: {os.path.basename(file_path)}")
                edit_window.geometry("600x400")
                
                # Apply current theme
                theme = THEMES[self.current_theme]
                edit_window.configure(bg=theme["bg"])
                
                # Create text widget with scrollbar
                text_frame = tk.Frame(edit_window, bg=theme["frame_bg"])
                text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
                
                scrollbar = tk.Scrollbar(text_frame)
                scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
                
                text_widget = tk.Text(text_frame, font=self.normal_font, 
                                    bg=theme["entry_bg"], fg=theme["fg"],
                                    insertbackground=theme["fg"],
                                    yscrollcommand=scrollbar.set)
                text_widget.pack(fill=tk.BOTH, expand=True)
                scrollbar.config(command=text_widget.yview)
                
                # Load file content
                with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read()
                    text_widget.insert(tk.END, content)
                
                # Button frame
                button_frame = tk.Frame(edit_window, bg=theme["frame_bg"])
                button_frame.pack(fill=tk.X, padx=10, pady=10)
                
                # Save button
                def save_file():
                    try:
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(text_widget.get(1.0, tk.END))
                        self.status_bar.config(text=f"Saved: {file_path}")
                        logging.info(f"{self.username} edited file: {file_path}")
                        edit_window.destroy()
                    except Exception as e:
                        messagebox.showerror("Error", f"Could not save file: {str(e)}")
                
                save_button = tk.Button(button_frame, text="Save", command=save_file,
                                      bg=theme["button_bg"], fg=theme["button_fg"],
                                      font=self.button_font, width=10)
                save_button.pack(side=tk.RIGHT, padx=5)
                
                # Cancel button
                cancel_button = tk.Button(button_frame, text="Cancel", command=edit_window.destroy,
                                        bg=theme["button_bg"], fg=theme["button_fg"],
                                        font=self.button_font, width=10)
                cancel_button.pack(side=tk.RIGHT, padx=5)
                
            except Exception as e:
                messagebox.showerror("Error", f"Could not edit file: {str(e)}")

    def rename_file(self):
        file_path = filedialog.askopenfilename()
        if file_path and os.path.exists(file_path):
            dir_name = os.path.dirname(file_path)
            old_name = os.path.basename(file_path)
            
            new_name = simpledialog.askstring("Rename File", "Enter new name:", initialvalue=old_name)
            
            if new_name and new_name != old_name:
                new_path = os.path.join(dir_name, new_name)
                
                try:
                    os.rename(file_path, new_path)
                    
                    # Update recent files list
                    if file_path in self.recent_files:
                        self.recent_files.remove(file_path)
                        self.recent_files.append(new_path)
                    
                    self.update_recent_files()
                    self.status_bar.config(text=f"Renamed: {old_name} to {new_name}")
                    logging.info(f"{self.username} renamed file from {file_path} to {new_path}")
                except Exception as e:
                    messagebox.showerror("Error", f"Could not rename file: {str(e)}")

    def create_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            new_folder_name = simpledialog.askstring("Create Folder", "Enter folder name:")
            if new_folder_name:
                new_folder_path = os.path.join(folder_path, new_folder_name)
                try:
                    os.makedirs(new_folder_path, exist_ok=True)
                    self.status_bar.config(text=f"Created folder: {new_folder_path}")
                    logging.info(f"{self.username} created folder: {new_folder_path}")
                except Exception as e:
                    messagebox.showerror("Error", f"Could not create folder: {str(e)}")

    def delete_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path and os.path.exists(folder_path):
            if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete the folder and ALL its contents?\n{folder_path}"):
                try:
                    shutil.rmtree(folder_path)
                    self.status_bar.config(text=f"Deleted folder: {folder_path}")
                    logging.info(f"{self.username} deleted folder: {folder_path}")
                except Exception as e:
                    messagebox.showerror("Error", f"Could not delete folder: {str(e)}")

    def move_file(self):
        file_path = filedialog.askopenfilename(title="Select file to move")
        if file_path and os.path.exists(file_path):
            destination = filedialog.askdirectory(title="Select destination folder")
            if destination and os.path.exists(destination):
                try:
                    dest_path = os.path.join(destination, os.path.basename(file_path))
                    shutil.move(file_path, dest_path)
                    
                    # Update recent files list
                    if file_path in self.recent_files:
                        self.recent_files.remove(file_path)
                        self.recent_files.append(dest_path)
                    
                    self.update_recent_files()
                    self.status_bar.config(text=f"Moved: {file_path} to {destination}")
                    logging.info(f"{self.username} moved file {file_path} to {destination}")
                except Exception as e:
                    messagebox.showerror("Error", f"Could not move file: {str(e)}")

    def copy_file(self):
        file_path = filedialog.askopenfilename(title="Select file to copy")
        if file_path and os.path.exists(file_path):
            destination = filedialog.askdirectory(title="Select destination folder")
            if destination and os.path.exists(destination):
                try:
                    dest_path = os.path.join(destination, os.path.basename(file_path))
                    shutil.copy2(file_path, dest_path)
                    
                    # Add to recent files
                    if dest_path not in self.recent_files:
                        self.recent_files.append(dest_path)
                    
                    self.update_recent_files()
                    self.status_bar.config(text=f"Copied: {file_path} to {destination}")
                    logging.info(f"{self.username} copied file {file_path} to {destination}")
                except Exception as e:
                    messagebox.showerror("Error", f"Could not copy file: {str(e)}")

    def search_file(self):
        search_window = tk.Toplevel(self.master)
        search_window.title("Search Files")
        search_window.geometry("600x400")
        search_window.transient(self.master)
        search_window.grab_set()
        
        # Apply current theme
        theme = THEMES[self.current_theme]
        search_window.configure(bg=theme["bg"])
        
        # Search options frame
        options_frame = tk.Frame(search_window, bg=theme["frame_bg"])
        options_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Search term
        tk.Label(options_frame, text="Search term:", bg=theme["frame_bg"], fg=theme["fg"], 
               font=self.normal_font).grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        
        search_term_var = tk.StringVar()
        search_term_entry = tk.Entry(options_frame, textvariable=search_term_var, 
                                   font=self.normal_font, bg=theme["entry_bg"], fg=theme["fg"])
        search_term_entry.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)
        search_term_entry.focus_set()
        
        # Search location
        tk.Label(options_frame, text="Search in:", bg=theme["frame_bg"], fg=theme["fg"], 
               font=self.normal_font).grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        
        location_var = tk.StringVar(value=os.path.expanduser("~"))
        location_entry = tk.Entry(options_frame, textvariable=location_var, 
                                font=self.normal_font, bg=theme["entry_bg"], fg=theme["fg"])
        location_entry.grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)
        
        browse_button = tk.Button(options_frame, text="Browse", 
                                font=self.normal_font, bg=theme["button_bg"], fg=theme["button_fg"],
                                command=lambda: location_var.set(filedialog.askdirectory()))
        browse_button.grid(row=1, column=2, padx=5, pady=5)
        
        # Search options
        options_frame.columnconfigure(1, weight=1)
        
        options_inner_frame = tk.Frame(options_frame, bg=theme["frame_bg"])
        options_inner_frame.grid(row=2, column=0, columnspan=3, sticky=tk.W, padx=5, pady=5)
        
        case_sensitive_var = tk.BooleanVar(value=False)
        case_check = tk.Checkbutton(options_inner_frame, text="Case sensitive", 
                                   variable=case_sensitive_var,
                                   bg=theme["frame_bg"], fg=theme["fg"],
                                   selectcolor=theme["entry_bg"],
                                   font=self.normal_font)
        case_check.pack(side=tk.LEFT, padx=5)
        
        search_contents_var = tk.BooleanVar(value=False)
        contents_check = tk.Checkbutton(options_inner_frame, text="Search file contents", 
                                      variable=search_contents_var,
                                      bg=theme["frame_bg"], fg=theme["fg"],
                                      selectcolor=theme["entry_bg"],
                                      font=self.normal_font)
        contents_check.pack(side=tk.LEFT, padx=5)
        
        # Results frame
        results_frame = tk.LabelFrame(search_window, text="Search Results", 
                                    bg=theme["frame_bg"], fg=theme["fg"],
                                    font=self.normal_font)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Results list with scrollbar
        scrollbar = tk.Scrollbar(results_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        results_list = tk.Listbox(results_frame, font=self.normal_font,
                                bg=theme["listbox_bg"], fg=theme["listbox_fg"],
                                selectbackground=theme["highlight_bg"],
                                selectforeground=theme["highlight_fg"],
                                yscrollcommand=scrollbar.set)
        results_list.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar.config(command=results_list.yview)
        
        # Double-click to open file
        results_list.bind('<Double-Button-1>', lambda e: self.open_search_result(results_list))
        
        # Button frame
        button_frame = tk.Frame(search_window, bg=theme["frame_bg"])
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Search function
        def perform_search():
            search_term = search_term_var.get()
            location = location_var.get()
            case_sensitive = case_sensitive_var.get()
            search_contents = search_contents_var.get()
            
            if not search_term or not location or not os.path.exists(location):
                messagebox.showerror("Error", "Please enter a valid search term and location")
                return
            
            results_list.delete(0, tk.END)
            results_list.insert(tk.END, "Searching...")
            search_window.update()
            
            found_files = []
            
            try:
                for root, dirs, files in os.walk(location):
                    for file in files:
                        if not case_sensitive:
                            file_lower = file.lower()
                            search_term_lower = search_term.lower()
                            if search_term_lower in file_lower:
                                found_files.append(os.path.join(root, file))
                        else:
                            if search_term in file:
                                found_files.append(os.path.join(root, file))
                        
                        # Search in file contents if requested
                        if search_contents and len(found_files) < 1000:  # Limit to prevent hanging
                            try:
                                file_path = os.path.join(root, file)
                                # Skip binary files
                                if os.path.getsize(file_path) > 1024 * 1024:  # Skip files > 1MB
                                    continue
                                    
                                with open(file_path, 'r', errors='ignore') as f:
                                    content = f.read()
                                    if not case_sensitive:
                                        if search_term_lower in content.lower() and file_path not in found_files:
                                            found_files.append(file_path)
                                    else:
                                        if search_term in content and file_path not in found_files:
                                            found_files.append(file_path)
                            except:
                                # Skip files that can't be read
                                pass
            except Exception as e:
                messagebox.showerror("Error", f"Search error: {str(e)}")
            
            results_list.delete(0, tk.END)
            
            if found_files:
                for file in found_files:
                    results_list.insert(tk.END, file)
                self.status_bar.config(text=f"Found {len(found_files)} files matching '{search_term}'")
            else:
                results_list.insert(tk.END, "No files found")
                self.status_bar.config(text=f"No files found matching '{search_term}'")
        
        # Open selected search result
        def open_search_result(listbox):
            try:
                selected_index = listbox.curselection()[0]
                selected_file = listbox.get(selected_index)
                if selected_file != "No files found" and selected_file != "Searching...":
                    self.open_file(selected_file)
            except IndexError:
                pass
        
        # Search button
        search_button = tk.Button(button_frame, text="Search", command=perform_search,
                                bg=theme["button_bg"], fg=theme["button_fg"],
                                font=self.button_font, width=10)
        search_button.pack(side=tk.RIGHT, padx=5)
        
        # Close button
        close_button = tk.Button(button_frame, text="Close", command=search_window.destroy,
                               bg=theme["button_bg"], fg=theme["button_fg"],
                               font=self.button_font, width=10)
        close_button.pack(side=tk.RIGHT, padx=5)
        
        # Bind Enter key to search
        search_term_entry.bind('<Return>', lambda event: perform_search())

    def logout(self):
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            logging.info(f"{self.username} logged out.")
            self.username = None
            self.main_container.destroy()
            self.setup_login()
            self.status_bar.config(text="Logged out")

if __name__ == "__main__":
    root = tk.Tk()
    
    # Enable drag and drop
    try:
        import tkinterdnd2
        root = tkinterdnd2.TkinterDnD.Tk()
    except:
        root = tk.Tk()
        print("Drag and drop functionality not available. Install tkinterdnd2 for this feature.")
    
    app = FileManagerApp(root)
    root.mainloop()
