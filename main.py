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

# Files
input_file = 'UserRoleMaps.json'
output_file = 'output.csv'

# Load NDJSON or array-based JSON
data = []
with open(input_file, 'r', encoding='utf-8') as f:
    first_char = f.read(1)
    f.seek(0)
    if first_char == '[':
        # It's a JSON array
        data = json.load(f)
    else:
        # It's NDJSON
        for line in tqdm(f, desc="Reading JSON lines"):
            line = line.strip()
            if line:
                try:
                    data.append(json.loads(line))
                except json.JSONDecodeError as e:
                    print(f"⚠️ Skipped bad line: {e}")

# Flatten all records
flat_data = []
all_keys = set()

for item in tqdm(data, desc="Flattening entries"):
    flat_item = flatten_json(item)
    flat_data.append(flat_item)
    all_keys.update(flat_item.keys())

all_keys = sorted(all_keys)

# Write to CSV
with open(output_file, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=all_keys)
    writer.writeheader()
    for row in flat_data:
        writer.writerow(row)

print(f"\n✅ Exported {len(flat_data)} records with {len(all_keys)} fields to '{output_file}'")
