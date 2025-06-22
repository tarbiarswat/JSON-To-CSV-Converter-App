import os
import json
import csv
import customtkinter as ctk
from tkinter import filedialog, messagebox

# Setup dark mode before any widgets
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class JSONTruncatorApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("🗂️ JSON Truncator & CSV Converter")
        self.geometry("440x530")
        self.resizable(False, False)

        self.file_paths = []
        self.limit_var = ctk.StringVar(value="100")

        # UI Layout
        ctk.CTkLabel(self, text="📂 JSON → CSV Converter", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=(25, 10))

        ctk.CTkOptionMenu(self, values=["10", "50", "100", "500", "1000"], variable=self.limit_var).pack(pady=(10, 0))
        ctk.CTkLabel(self, text="Select max records").pack(pady=(5, 20))

        ctk.CTkButton(self, text="Select JSON Files", command=self.select_files).pack(pady=5)

        self.progress_bar = ctk.CTkProgressBar(self, width=300)
        self.progress_bar.set(0)
        self.progress_bar.pack(pady=(30, 5))

        self.status = ctk.CTkLabel(self, text="Waiting for files...")
        self.status.pack(pady=(0, 20))

        ctk.CTkButton(self, text="🚀 Convert", fg_color="green", command=self.convert).pack(pady=10)

        ctk.CTkLabel(self, text="Developed with ♡ by Md Tarbiar Swat", font=ctk.CTkFont(size=12)).pack(side="bottom", pady=10)

    def select_files(self):
        files = filedialog.askopenfilenames(filetypes=[("JSON Files", "*.json")])
        if files:
            self.file_paths = files
            self.status.configure(text=f"{len(files)} file(s) selected")
            self.progress_bar.set(0)

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

            except Exception as e:
                messagebox.showerror("Error", f"Failed to process {name}:\n{e}")

            self.progress_bar.set(step * (i + 1))
            self.status.configure(text=f"{i + 1} of {len(self.file_paths)} converted")

        self.status.configure(text=f"✅ Done! Saved to /output")

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
