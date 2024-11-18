import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk
import re

def extract_issues(text):
    # Find all lines that match the clean summary format
    issues = []
    lines = text.strip().split('\n')
    for line in lines:
        # Match lines that start with a path but:
        # 1. Don't have 'error:' or 'note:'
        # 2. Don't contain Xcode.app or other system paths
        # 3. Must be an actual issue line (usually contains a colon followed by a message)
        if (line.strip().startswith('/') and 
            not any(x in line for x in ['error:', 'note:', 'Xcode.app', '/Applications/', '/Library/']) and
            ': ' in line):  # This ensures it's an actual issue line
            
            # Remove any existing XML tags that might be in the text
            clean_line = re.sub(r'</?issue\d*>', '', line.strip())
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
    
    # Clear and update the output text area
    output_text_area.delete("1.0", tk.END)
    output_text_area.insert(tk.END, converted_text)
    
    # Automatically copy to clipboard
    root.clipboard_clear()
    root.clipboard_append(converted_text)
    
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

# Create the main window
root = tk.Tk()
root.title("Xcode Issue XML Converter")
root.geometry("800x600")

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

# Convert button
convert_button = tk.Button(root, text="Extract & Convert to XML", command=convert_and_copy)
convert_button.pack(pady=10)

# Status label (for copy confirmation)
status_label = tk.Label(root, text="", fg="green")
status_label.pack()

# Output text area
output_label = tk.Label(root, text="Extracted Issues in XML:")
output_label.pack(pady=(10, 0))

output_text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=90, height=15)
output_text_area.pack(padx=10, pady=10)

# Run the application
root.mainloop()
