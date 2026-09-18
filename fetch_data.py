import os
import json
import requests

WEBHOOK_URL = os.environ.get("WPS_WEBHOOK_URL")
API_TOKEN = os.environ.get("WPS_API_TOKEN")

if not WEBHOOK_URL or not API_TOKEN:
    print("❌ 缺少环境变量")
    exit(1)

headers = {
    "AirScript-Token": API_TOKEN,
    "Content-Type": "application/json"
}

body = {"Context": {"argv": {}}}

# ========== 1. 请求 WPS ==========
try:
    response = requests.post(WEBHOOK_URL, headers=headers, json=body, timeout=60)
    response.raise_for_status()
    print("WPS 原始返回:", response.text[:2000])
except Exception as e:
    print(f"❌ 请求失败: {e}")
    if 'response' in locals():
        print(f"返回内容: {response.text[:1000]}")
    exit(1)

# ========== 2. 解析返回 ==========
parsed = response.json()
records = []

if isinstance(parsed, dict):
    data_obj = parsed.get("data", {})
    if isinstance(data_obj, dict):
        result_str = data_obj.get("result", "")
        if result_str and result_str != "[Undefined]":
            if isinstance(result_str, str):
                try:
                    records = json.loads(result_str)
                except Exception as e:
                    print(f"❌ result 不是有效 JSON: {e}")
                    records = []
            elif isinstance(result_str, list):
                records = result_str
elif isinstance(parsed, list):
    records = parsed

print(f"✅ 解析到 {len(records)} 行原始数据")

# ========== 3. 过滤表头 ==========
if records and str(records[0][0]).strip() in ['仓库', '区域']:
    records = records[1:]
    print(f"✅ 跳过表头后剩余 {len(records)} 行")

# ========== 4. 工具函数 ==========
def to_int(v, d=0):
    try: return int(float(v))
    except: return d

def to_float(v, d=0.0):
    try: return float(v)
    except: return d

# ========== 5. 组装数据 ==========
warehouses = {}

for row in records:
    if not row or len(row) < 9:
        continue
    
    wh_name    = str(row[0]).strip()
    zone_name  = str(row[1]).strip()
    rows       = to_int(row[2])
    cols       = to_int(row[3])
    layers     = to_int(row[4], 1)
    slot_vol   = to_float(row[5])
    occupied   = to_int(row[6])
    overdue    = to_int(row[7])
    avg_age    = to_float(row[8])
    
    total = rows * cols * layers
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
        "rows": rows,
        "cols": cols,
        "layers": layers,
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
