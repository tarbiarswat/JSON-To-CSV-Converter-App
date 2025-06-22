import json
import csv
import os
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk

def flatten_json(y, prefix=''):
    out = {}
    if isinstance(y, dict):
        for key, value in y.items():
            full_key = f"{prefix}.{key}" if prefix else key
            out.update(flatten_json(value, full_key))
    elif isinstance(y, list):
        for i, value in enumerate(y):
            full_key = f"{prefix}[{i}]"
            out.update(flatten_json(value, full_key))
    else:
        out[prefix] = y
    return out

def process_file(file_path, progress, status_label):
    try:
        # Setup output paths
        os.makedirs("output", exist_ok=True)
        base_name = os.path.splitext(os.path.basename(file_path))[0]
        json_output = os.path.join("output", f"{base_name}.json")
        csv_output = os.path.join("output", f"{base_name}.csv")

        # Read and parse JSON or NDJSON
        progress['value'] = 10
        status_label.config(text="Reading JSON...")
        root.update_idletasks()

        data = []
        with open(file_path, 'r', encoding='utf-8') as f:
            first_char = f.read(1)
            f.seek(0)
            if first_char == '[':
                data = json.load(f)
            else:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            data.append(json.loads(line))
                        except json.JSONDecodeError:
                            continue

        top100 = data[:100]

        # Save JSON output
        with open(json_output, 'w', encoding='utf-8') as jf:
            json.dump(top100, jf, indent=2)

        progress['value'] = 50
        status_label.config(text="Flattening JSON...")
        root.update_idletasks()

        # Flatten and write CSV
        flat_data = []
        all_keys = set()
        for item in top100:
            flat = flatten_json(item)
            flat_data.append(flat)
            all_keys.update(flat.keys())

        all_keys = sorted(all_keys)

        with open(csv_output, 'w', newline='', encoding='utf-8') as cf:
            writer = csv.DictWriter(cf, fieldnames=all_keys)
            writer.writeheader()
            writer.writerows(flat_data)

        progress['value'] = 100
        status_label.config(text="✅ Done: Files saved in /output")
        messagebox.showinfo("Success", f"Saved:\n{json_output}\n{csv_output}")

    except Exception as e:
        messagebox.showerror("Error", str(e))
        progress['value'] = 0
        status_label.config(text="⚠️ Failed")

def select_file():
    file_path = filedialog.askopenfilename(
        title="Select a JSON File",
        filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")]
    )
    if file_path:
        progress['value'] = 0
        status_label.config(text="Starting...")
        root.update_idletasks()
        process_file(file_path, progress, status_label)

# GUI setup
root = tk.Tk()
root.title("JSON to CSV Converter")
root.geometry("400x200")
root.resizable(False, False)

frame = ttk.Frame(root, padding=20)
frame.pack(fill=tk.BOTH, expand=True)

ttk.Label(frame, text="JSON to CSV (First 100 records)", font=("Arial", 14)).pack(pady=10)
ttk.Button(frame, text="Select JSON File", command=select_file).pack(pady=5)

progress = ttk.Progressbar(frame, orient=tk.HORIZONTAL, length=300, mode='determinate')
progress.pack(pady=10)

status_label = ttk.Label(frame, text="No file selected.")
status_label.pack(pady=5)

root.mainloop()
