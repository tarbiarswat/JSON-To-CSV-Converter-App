import os
import json
import csv
import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image

# Force dark mode early
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Load icon (must match your filename)
icon_img = ctk.CTkImage(Image.open("icon.png"), size=(20, 20))

class JSONTruncatorApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("🗂️ JSON Truncator & CSV Converter")
        self.geometry("500x600")
        self.resizable(False, False)

        self.file_paths = []
        self.limit_var = ctk.StringVar(value="100")

        # Title
        #ctk.CTkLabel(self, text="📂 JSON → CSV Converter", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=(25, 10))
        ctk.CTkLabel(
        self,
        text="JSON → CSV Converter",
        image=icon_img,
        compound="left",  # <-- image left, text right
        font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=(25, 10))

        # Dropdown
        ctk.CTkOptionMenu(self, values=["10", "50", "100", "500", "1000"], variable=self.limit_var).pack(pady=(10, 0))
        ctk.CTkLabel(self, text="Select max records").pack(pady=(5, 20))

        # File picker
        ctk.CTkButton(self, text="Select JSON Files", command=self.select_files).pack(pady=5)

        # Progress
        self.progress_bar = ctk.CTkProgressBar(self, width=360)
        self.progress_bar.set(0)
        self.progress_bar.pack(pady=(30, 5))

        # Status
        self.status = ctk.CTkLabel(self, text="Waiting for files...")
        self.status.pack(pady=(0, 10))

        # Logs (Textbox)
        ctk.CTkLabel(self, text="Logs:").pack()
        self.log_box = ctk.CTkTextbox(self, width=460, height=150, wrap="none")
        self.log_box.pack(pady=5)
        self.log_box.configure(state="disabled")

        # Convert button
        ctk.CTkButton(self, text="🚀 Convert", fg_color="green", command=self.convert).pack(pady=10)

        # Footer
        ctk.CTkLabel(self, text="Developed with ♡ by Md Tarbiar Swat", font=ctk.CTkFont(size=12)).pack(side="bottom", pady=10)

    def select_files(self):
        files = filedialog.askopenfilenames(filetypes=[("JSON Files", "*.json")])
        if files:
            self.file_paths = files
            self.status.configure(text=f"{len(files)} file(s) selected")
            self.progress_bar.set(0)
            self._log(f"📁 Selected {len(files)} file(s)")

    def convert(self):
        if not self.file_paths:
            messagebox.showwarning("No Files", "Please select one or more JSON files.")
            return

        limit = int(self.limit_var.get())
        os.makedirs("output", exist_ok=True)
        step = 1 / len(self.file_paths)

        for i, path in enumerate(self.file_paths):
            name = os.path.splitext(os.path.basename(path))[0]
            try:
                self._log(f"🔄 Processing '{name}'...")
                with open(path, 'r', encoding='utf-8') as f:
                    first = f.read(1)
                    f.seek(0)
                    if first == '[':
                        data = json.load(f)
                    else:
                        data = [json.loads(line) for line in f if line.strip()]

                data = data[:limit]
                flat = [self.flatten_json(d) for d in data]
                keys = sorted({k for row in flat for k in row})

                with open(f"output/{name}.json", 'w', encoding='utf-8') as jf:
                    json.dump(data, jf, indent=2)
                with open(f"output/{name}.csv", 'w', newline='', encoding='utf-8') as cf:
                    writer = csv.DictWriter(cf, fieldnames=keys)
                    writer.writeheader()
                    writer.writerows(flat)

                self._log(f"✅ Saved: output/{name}.json and .csv")

            except Exception as e:
                self._log(f"❌ Failed on {name}: {e}")
                messagebox.showerror("Error", f"Failed to process {name}:\n{e}")

            self.progress_bar.set(step * (i + 1))
            self.status.configure(text=f"{i + 1} of {len(self.file_paths)} converted")

        self.status.configure(text="✅ Done! Files saved to /output")

    def _log(self, msg):
        self.log_box.configure(state="normal")
        self.log_box.insert("end", msg + "\n")
        self.log_box.configure(state="disabled")
        self.log_box.yview("end")

    def flatten_json(self, y, prefix=''):
        out = {}
        if isinstance(y, dict):
            for k, v in y.items():
                out.update(self.flatten_json(v, f"{prefix}.{k}" if prefix else k))
        elif isinstance(y, list):
            for i, v in enumerate(y):
                out.update(self.flatten_json(v, f"{prefix}[{i}]"))
        else:
            out[prefix] = y
        return out

if __name__ == "__main__":
    app = JSONTruncatorApp()
    app.mainloop()
