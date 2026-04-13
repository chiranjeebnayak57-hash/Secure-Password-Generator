import string
import secrets
import tkinter as tk
from tkinter import ttk, messagebox
import datetime
import os

# --- Logic: Core Password Generation ---

class PasswordPolicy:
    def __init__(self, length, use_upper=True, use_lower=True, use_digits=True, use_symbols=True, safe_symbols_only=False):
        self.length = length
        self.use_upper = use_upper
        self.use_lower = use_lower
        self.use_digits = use_digits
        self.use_symbols = use_symbols
        self.symbols = "!@#$%^&*" if safe_symbols_only else string.punctuation

class PasswordGenerator:
    def __init__(self):
        self.policies = {
            "Social Media": PasswordPolicy(length=16),
            "Banking Portal": PasswordPolicy(length=12, safe_symbols_only=True),
            "Corporate/Enterprise": PasswordPolicy(length=24),
            "Wi-Fi Network": PasswordPolicy(length=20, use_symbols=False),
            "Numeric PIN": PasswordPolicy(length=6, use_upper=False, use_lower=False, use_symbols=False)
        }

    def generate(self, platform_name: str) -> str:
        policy = self.policies.get(platform_name, self.policies["Social Media"])

        pool = ""
        password_chars = []

        if policy.use_upper:
            pool += string.ascii_uppercase
            password_chars.append(secrets.choice(string.ascii_uppercase))
        if policy.use_lower:
            pool += string.ascii_lowercase
            password_chars.append(secrets.choice(string.ascii_lowercase))
        if policy.use_digits:
            pool += string.digits
            password_chars.append(secrets.choice(string.digits))
        if policy.use_symbols:
            pool += policy.symbols
            password_chars.append(secrets.choice(policy.symbols))

        remaining_length = policy.length - len(password_chars)
        for _ in range(remaining_length):
            password_chars.append(secrets.choice(pool))

        secure_random = secrets.SystemRandom()
        secure_random.shuffle(password_chars)

        return "".join(password_chars)

# --- GUI: Tkinter Application ---

class PasswordApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Secure Password Generator")
        self.root.geometry("420x350") # Increased height to fit new fields
        self.root.resizable(False, False)

        self.main_frame = ttk.Frame(self.root, padding="20")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.generator = PasswordGenerator()
        self.save_file = "saved_passwords.txt" # Define the save file name

        self.create_widgets()

    def create_widgets(self):
        # 1. Title Label
        title_label = ttk.Label(
            self.main_frame,
            text="Platform-Aware Generator",
            font=("Helvetica", 14, "bold")
        )
        title_label.pack(pady=(0, 15))

        # 2. Platform Selection
        platform_frame = ttk.Frame(self.main_frame)
        platform_frame.pack(fill=tk.X, pady=5)

        ttk.Label(platform_frame, text="Select Platform:").pack(side=tk.LEFT, padx=(0, 10))

        self.platform_var = tk.StringVar()
        self.platform_combo = ttk.Combobox(
            platform_frame,
            textvariable=self.platform_var,
            state="readonly",
            values=list(self.generator.policies.keys())
        )
        self.platform_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.platform_combo.current(0)

        # 3. Generate Button
        generate_btn = ttk.Button(self.main_frame, text="Generate Password", command=self.on_generate)
        generate_btn.pack(pady=15)

        # 4. Result Display Field & Copy
        result_frame = ttk.Frame(self.main_frame)
        result_frame.pack(fill=tk.X)

        self.result_var = tk.StringVar()
        self.result_entry = ttk.Entry(
            result_frame,
            textvariable=self.result_var,
            font=("Courier", 12),
            state="readonly",
            justify="center"
        )
        self.result_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        copy_btn = ttk.Button(result_frame, text="Copy", command=self.on_copy)
        copy_btn.pack(side=tk.RIGHT)

        # Divider Line
        ttk.Separator(self.main_frame, orient='horizontal').pack(fill=tk.X, pady=15)

        # 5. Save Section (Note & Save Button)
        ttk.Label(self.main_frame, text="Add a note (e.g., 'Work Email'):").pack(anchor=tk.W)

        save_frame = ttk.Frame(self.main_frame)
        save_frame.pack(fill=tk.X, pady=(5, 0))

        self.note_var = tk.StringVar()
        self.note_entry = ttk.Entry(save_frame, textvariable=self.note_var)
        self.note_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        save_btn = ttk.Button(save_frame, text="Save to File", command=self.on_save)
        save_btn.pack(side=tk.RIGHT)

    def on_generate(self):
        selected_platform = self.platform_var.get()
        new_password = self.generator.generate(selected_platform)

        self.result_entry.config(state="normal")
        self.result_var.set(new_password)
        self.result_entry.config(state="readonly")

    def on_copy(self):
        password = self.result_var.get()
        if password:
            self.root.clipboard_clear()
            self.root.clipboard_append(password)
            messagebox.showinfo("Copied", "Password copied to clipboard!", parent=self.root)
        else:
            messagebox.showwarning("Empty", "Generate a password first.", parent=self.root)

    def on_save(self):
        """Appends the generated password and note to a local text file."""
        password = self.result_var.get()
        note = self.note_var.get().strip()
        platform = self.platform_var.get()

        # Input Validation
        if not password:
            messagebox.showwarning("Error", "Please generate a password first.", parent=self.root)
            return
        if not note:
            messagebox.showwarning("Error", "Please enter a note so you know what this password is for.", parent=self.root)
            return

        # File writing logic
        try:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Use "a" mode to append to the file rather than overwriting it
            with open(self.save_file, "a", encoding="utf-8") as file:
                file.write(f"[{timestamp}]\n")
                file.write(f"Platform: {platform}\n")
                file.write(f"Note:     {note}\n")
                file.write(f"Password: {password}\n")
                file.write("-" * 40 + "\n")

            # Alert user and clear fields for security
            messagebox.showinfo("Success", f"Password securely saved to:\n{os.path.abspath(self.save_file)}", parent=self.root)

            # Clear the GUI fields after successful save
            self.note_var.set("")
            self.result_entry.config(state="normal")
            self.result_var.set("")
            self.result_entry.config(state="readonly")

        except Exception as e:
            messagebox.showerror("File Error", f"Could not save the file.\nDetails: {str(e)}", parent=self.root)

# --- Application Startup ---
if __name__ == "__main__":
    root = tk.Tk()

    style = ttk.Style()
    if "vista" in style.theme_names():
        style.theme_use("vista")
    elif "clam" in style.theme_names():
        style.theme_use("clam")

    app = PasswordApp(root)
    root.mainloop()
