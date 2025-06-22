import json
import csv
import os
from tqdm import tqdm

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

# === Configuration ===
input_file = 'EmployeeHrYearInfos.json'  # <-- your original file
output_dir = 'output'

# Make sure output directory exists
os.makedirs(output_dir, exist_ok=True)

# Derive filename without extension
base_name = os.path.splitext(os.path.basename(input_file))[0]
json_output = os.path.join(output_dir, f"{base_name}.json")
csv_output = os.path.join(output_dir, f"{base_name}.csv")

# === Load Data ===
data = []
with open(input_file, 'r', encoding='utf-8') as f:
    first_char = f.read(1)
    f.seek(0)
    if first_char == '[':
        data = json.load(f)
    else:
        for line in tqdm(f, desc="Reading NDJSON"):
            line = line.strip()
            if line:
                try:
                    data.append(json.loads(line))
                except json.JSONDecodeError as e:
                    print(f"⚠️ Skipping malformed line: {e}")

# === Truncate and Save JSON ===
top100 = data[:100]

with open(json_output, 'w', encoding='utf-8') as jf:
    json.dump(top100, jf, indent=2)
print(f"✅ Saved first 100 entries to JSON: {json_output}")

# === Flatten and Save CSV ===
flat_data = []
all_keys = set()

for item in tqdm(top100, desc="Flattening"):
    flat_item = flatten_json(item)
    flat_data.append(flat_item)
    all_keys.update(flat_item.keys())

all_keys = sorted(all_keys)

with open(csv_output, 'w', newline='', encoding='utf-8') as cf:
    writer = csv.DictWriter(cf, fieldnames=all_keys)
    writer.writeheader()
    writer.writerows(flat_data)

print(f"✅ Saved CSV with {len(flat_data)} rows and {len(all_keys)} columns: {csv_output}")
