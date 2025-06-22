import os
import json
import csv
import customtkinter as ctk
from tkinter import filedialog, messagebox
from tqdm import tqdm

# Flatten helper
def flatten_json(y, prefix=''):
    out = {}
    if isinstance(y, dict):
        for k, v in y.items():
            full_key = f"{prefix}.{k}" if prefix else k
            out.update(flatten_json(v, full_key))
    elif isinstance(y, list):
        for i, v in enumerate(y):
            full_key = f"{prefix}[{i}]"
            out.update(flatten_json(v, full_key))
    else:
        out[prefix] = y
    return out

# Process a single file
def process_file(filepath, limit, progress_bar, status_label):
    base = os.path.basename(filepath)
    name = os.path.splitext(base)[0]
    os.makedirs("output", exist_ok=True)
    json_out = f"output/{name}.json"
    csv_out = f"output/{name}.csv"

    try:
        progress_bar.set(0.1)
        status_label.configure(text=f"Reading {base}...")

        data = []
        with open(filepath, 'r', encoding='utf-8') as f:
            first_char = f.read(1)
            f.seek(0)
            if first_char == '[':
                data = json.load(f)
            else:
                for line in f:
                    if line.strip():
                        try:
                            data.append(json.loads(line))
                        except:
                            continue

        top_data = data[:limit]

        with open(json_out, 'w', encoding='utf-8') as jf:
            json.dump(top_data, jf, indent=2)

        progress_bar.set(0.5)
        status_label.configure(text=f"Flattening {base}...")

        flat_data = []
        keys = set()
        for item in top_data:
            flat = flatten_json(item)
            flat_data.append(flat)
            keys.update(flat.keys())

        keys = sorted(keys)
        with open(csv_out, 'w', newline='', encoding='utf-8') as cf:
            writer = csv.DictWriter(cf, fieldnames=keys)
            writer.writeheader()
            writer.writerows(flat_data)

        progress_bar.set(1)
        status_label.configure(text=f"✅ {base} done!")

    except Exception as e:
        messagebox.showerror("Error", str(e))
        progress_bar.set(0)
        status_label.configure(text=f"❌ Failed: {base}")

# GUI action
def choose_files():
    files = filedialog.askopenfilenames(filetypes=[("JSON Files", "*.json")])
    if not files:
        return

    try:
        limit = int(record_limit_var.get())
    except:
        messagebox.showwarning("Invalid Input", "Please select a valid record limit.")
        return

    for file in files:
        process_file(file, limit, progress_bar, status_label)
    messagebox.showinfo("Done", "All files processed!")

# ---------- GUI Setup ----------
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.geometry("480x360")
app.title("🧩 JSON Truncator & CSV Converter")

title = ctk.CTkLabel(app, text="📂 JSON → CSV Converter", font=ctk.CTkFont(size=20, weight="bold"))
title.pack(pady=15)

record_limit_var = ctk.StringVar(value="100")
dropdown = ctk.CTkOptionMenu(app, values=["10", "50", "100", "500", "1000"], variable=record_limit_var)
dropdown.pack(pady=10)
ctk.CTkLabel(app, text="Select max records").pack()

button = ctk.CTkButton(app, text="Select JSON Files", command=choose_files)
button.pack(pady=20)

progress_bar = ctk.CTkProgressBar(app, width=300)
progress_bar.set(0)
progress_bar.pack(pady=10)

status_label = ctk.CTkLabel(app, text="Waiting for file...", text_color="#AAAAAA")
status_label.pack(pady=5)

footer = ctk.CTkLabel(app, text="Developed with 💙 by Md Tarbiar Swat", font=ctk.CTkFont(size=12))
footer.pack(side="bottom", pady=8)

app.mainloop()
