import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk
import re
import json
import os
from pathlib import Path

# Ensure profiles directory exists
PROFILES_DIR = Path.home() / '.xcode_converter_profiles'
PROFILES_DIR.mkdir(exist_ok=True)
PROFILES_FILE = PROFILES_DIR / 'profiles.json'
LAST_PROFILE_FILE = PROFILES_DIR / 'last_profile.txt'

def load_profiles():
    if PROFILES_FILE.exists():
        with open(PROFILES_FILE, 'r') as f:
            return json.load(f)
    return {}  # Return empty dict if no profiles exist

def save_profiles(profiles):
    with open(PROFILES_FILE, 'w') as f:
        json.dump(profiles, f, indent=2)

def save_last_profile(profile_name):
    with open(LAST_PROFILE_FILE, 'w') as f:
        f.write(profile_name)

def load_last_profile():
    if LAST_PROFILE_FILE.exists():
        with open(LAST_PROFILE_FILE, 'r') as f:
            return f.read().strip()
    return None

def extract_issues(text):
    # Find all lines that match the clean summary format
    issues = []
    lines = text.strip().split('\n')
    
    # System paths to exclude
    system_paths = ['Xcode.app', '/Applications/', '/Library/']
    
    # Error patterns to include
    error_patterns = [
        r'No such module',
        r'failed',
        r'Failed',
        r'error:',
        r'warning:',
        r'fatal error:',
        r'undefined symbol'
    ]
    
    for line in lines:
        line = line.strip()
        
        # Skip empty lines and system paths
        if not line or any(path in line for path in system_paths):
            continue
            
        # Check if line contains any error pattern or starts with a path and contains a message
        if (any(pattern.lower() in line.lower() for pattern in error_patterns) or
            (line.startswith('/') and ': ' in line)):
            
            # Remove any existing XML tags that might be in the text
            clean_line = re.sub(r'</?issue\d*>', '', line)
            
            # Don't add duplicate issues
            if clean_line not in issues:
                issues.append(clean_line)
    
    # Format each issue with numbered tags
    formatted_issues = []
    for i, issue in enumerate(issues, 1):
        formatted_issues.append(f"<issue{i}>{issue}</issue{i}>")
    
    return '\n\n'.join(formatted_issues)  # Add extra newline between issues for readability

def convert_and_copy():
    # Get the input text from the input text area
    input_text = input_text_area.get("1.0", tk.END).strip()
    
    if not input_text:  # Don't process if empty
        return
        
    # Extract and format the issues
    converted_text = extract_issues(input_text)
    
    # Get pretext and post-text if any
    pretext = pretext_text.get("1.0", tk.END).strip()
    posttext = posttext_text.get("1.0", tk.END).strip()
    
    # Combine pretext, converted text, and post-text
    final_text = converted_text
    if pretext:
        final_text = f"{pretext}\n\n{final_text}"
    if posttext:
        final_text = f"{final_text}\n\n{posttext}"
    
    # Clear and update the output text area
    output_text_area.delete("1.0", tk.END)
    output_text_area.insert(tk.END, final_text)
    
    # Automatically copy to clipboard
    root.clipboard_clear()
    root.clipboard_append(final_text)
    
    # Clear the input text area
    input_text_area.delete("1.0", tk.END)
    
    # Show a small confirmation message
    status_label.config(text="✓ Converted and copied to clipboard!")
    # Reset the status message after 2 seconds
    root.after(2000, lambda: status_label.config(text=""))

def on_paste(event):
    # After paste, if auto-convert is enabled, trigger conversion
    root.after(50, check_for_paste)  # Small delay to ensure paste completes

def check_for_paste():
    if auto_convert_var.get() and input_text_area.get("1.0", tk.END).strip():
        convert_and_copy()

def on_input_click(event):
    # Check if there's text in the input area
    if input_text_area.get("1.0", tk.END).strip():
        # Select all text
        input_text_area.tag_add(tk.SEL, "1.0", tk.END)
        # Set the insertion cursor to the end
        input_text_area.mark_set(tk.INSERT, tk.END)
        # Make sure the selection is visible
        input_text_area.see(tk.INSERT)
        return 'break'  # Prevents the default click behavior

def save_current_profile():
    profile_name = profile_var.get()
    if not profile_name:
        messagebox.showerror("Error", "Please select or enter a profile name")
        return
        
    profiles = load_profiles()
    profiles[profile_name] = {
        'pretext': pretext_text.get("1.0", tk.END).strip(),
        'posttext': posttext_text.get("1.0", tk.END).strip()
    }
    save_profiles(profiles)
    save_last_profile(profile_name)
    
    # Update profile dropdown if it's a new profile
    current_values = list(profile_dropdown['values'])
    if profile_name not in current_values:
        current_values.append(profile_name)
        profile_dropdown['values'] = sorted(current_values)
    
    messagebox.showinfo("Success", f"Profile '{profile_name}' saved successfully!")

def load_profile(*args):  # *args to handle both manual and trace callbacks
    profile_name = profile_var.get()
    if not profile_name:
        return
        
    profiles = load_profiles()
    if profile_name in profiles:
        profile = profiles[profile_name]
        pretext_text.delete("1.0", tk.END)
        pretext_text.insert("1.0", profile.get('pretext', ''))
        posttext_text.delete("1.0", tk.END)
        posttext_text.insert("1.0", profile.get('posttext', ''))
        save_last_profile(profile_name)

def delete_profile():
    profile_name = profile_var.get()
    if not profile_name:
        messagebox.showerror("Error", "Please select a profile to delete")
        return
        
    if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete profile '{profile_name}'?"):
        profiles = load_profiles()
        if profile_name in profiles:
            del profiles[profile_name]
            save_profiles(profiles)
            
            # Update profile dropdown
            profile_dropdown['values'] = sorted(profiles.keys())
            if profiles:
                profile_var.set(list(profiles.keys())[0])
            else:
                profile_var.set('')
            
            messagebox.showinfo("Success", f"Profile '{profile_name}' deleted successfully!")

# Create the main window
root = tk.Tk()
root.title("Xcode Issue XML Converter")
root.geometry("800x800")

# Profile management frame
profile_frame = tk.Frame(root)
profile_frame.pack(fill=tk.X, padx=10, pady=(10, 0))

profile_label = tk.Label(profile_frame, text="Profile:")
profile_label.pack(side=tk.LEFT, padx=(0, 10))

profile_var = tk.StringVar()
profiles = load_profiles()

profile_dropdown = ttk.Combobox(profile_frame, textvariable=profile_var, values=sorted(profiles.keys()))
profile_dropdown.pack(side=tk.LEFT, padx=(0, 10))
profile_dropdown.bind('<<ComboboxSelected>>', load_profile)

save_profile_btn = tk.Button(profile_frame, text="Save Profile", command=save_current_profile)
save_profile_btn.pack(side=tk.LEFT, padx=(0, 10))

delete_profile_btn = tk.Button(profile_frame, text="Delete Profile", command=delete_profile)
delete_profile_btn.pack(side=tk.LEFT)

# Load last used profile
last_profile = load_last_profile()
if last_profile and last_profile in profiles:
    profile_var.set(last_profile)
    load_profile()

# Input text area
input_label = tk.Label(root, text="Paste Xcode Issue Output:")
input_label.pack(pady=(10, 0))

input_text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=90, height=15)
input_text_area.pack(padx=10, pady=10)
# Bind the click event to the input text area
input_text_area.bind('<Button-1>', on_input_click)
# Bind paste event (Command+V or right-click paste)
input_text_area.bind('<<Paste>>', on_paste)

# Auto-convert checkbox
auto_convert_var = tk.BooleanVar()
auto_convert_checkbox = ttk.Checkbutton(
    root, 
    text="Auto Convert on Paste", 
    variable=auto_convert_var
)
auto_convert_checkbox.pack()

# Pretext field
pretext_frame = tk.Frame(root)
pretext_frame.pack(fill=tk.X, padx=10, pady=(0, 5))

pretext_label = tk.Label(pretext_frame, text="Message Pre-Text:")
pretext_label.pack(anchor='w', padx=(0, 10))

pretext_text = scrolledtext.ScrolledText(pretext_frame, wrap=tk.WORD, width=90, height=3)
pretext_text.pack(fill=tk.X, expand=True)

# Convert button
convert_button = tk.Button(root, text="Extract & Convert to XML", command=convert_and_copy)
convert_button.pack(pady=10)

# Status label (for copy confirmation)
status_label = tk.Label(root, text="", fg="green")
status_label.pack()

# Post-text field
posttext_frame = tk.Frame(root)
posttext_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

posttext_label = tk.Label(posttext_frame, text="Message Post-Text:")
posttext_label.pack(anchor='w', padx=(0, 10))

posttext_text = scrolledtext.ScrolledText(posttext_frame, wrap=tk.WORD, width=90, height=3)
posttext_text.pack(fill=tk.X, expand=True)

# Output text area
output_label = tk.Label(root, text="Extracted Issues in XML:")
output_label.pack(pady=(10, 0))

output_text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=90, height=15)
output_text_area.pack(padx=10, pady=10)

# Run the application
root.mainloop()
