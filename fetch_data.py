import json
import csv

# 从仓库里的 data.csv 读取数据
with open('data.csv', 'r', encoding='utf-8-sig') as f:
    rows = list(csv.reader(f))

# 跳过表头
if rows and rows[0] and str(rows[0][0]).strip() in ['仓库', '区域']:
    rows = rows[1:]

def to_int(v, d=0):
    try: return int(float(v))
    except: return d

def to_float(v, d=0.0):
    try: return float(v)
    except: return d

warehouses = {}

for row in rows:
    if not row or len(row) < 9:
        continue
    
    wh_name = str(row[0]).strip()
    if not wh_name:
        continue
    
    zone_name = str(row[1]).strip()
    rows_n    = to_int(row[2])
    cols_n    = to_int(row[3])
    layers_n  = to_int(row[4], 1)
    slot_vol  = to_float(row[5])
    occupied  = to_int(row[6])
    overdue   = to_int(row[7])
    avg_age   = to_float(row[8])
    
    total = rows_n * cols_n * layers_n
    fill = occupied / total if total > 0 else 0
    
    if wh_name not in warehouses:
        warehouses[wh_name] = {
            "id": wh_name,
            "name": wh_name,
            "meta": "WPS 自动同步",
            "zones": []
        }
    
    warehouses[wh_name]["zones"].append({
        "key": zone_name,
        "name": zone_name,
        "rows": rows_n,
        "cols": cols_n,
        "layers": layers_n,
        "slotVol": slot_vol,
        "fill": fill,
        "occupied": occupied,
        "overdue": overdue,
        "avgAge": avg_age
    })

output = list(warehouses.values())

with open('data.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"✅ data.json 生成成功，共 {len(output)} 个仓库")
