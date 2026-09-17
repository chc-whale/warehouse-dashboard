import os
import json
import requests

# 从GitHub Secrets中读取密钥（不要直接写在代码里！）
WEBHOOK_URL = os.environ.get("WPS_WEBHOOK_URL")
API_TOKEN = os.environ.get("WPS_API_TOKEN")

if not WEBHOOK_URL or not API_TOKEN:
    print("❌ 错误：缺少环境变量 WPS_WEBHOOK_URL 或 WPS_API_TOKEN")
    exit(1)

headers = {
    "AirScript-Token": API_TOKEN
}

# 1. 调用 WPS AirScript，获取表格数据
try:
    response = requests.post(WEBHOOK_URL, headers=headers)
    response.raise_for_status()
    raw_data = response.json()
    print("✅ WPS 数据拉取成功")
except Exception as e:
    print(f"❌ 请求 WPS 失败: {e}")
    exit(1)

# 2. 把 WPS 返回的二维数组，转换成 HTML 需要的结构
# WPS 返回格式类似：[["抖音仓","爆品拣货区",36,22,2,1.6,800,20,45], ...]
records = raw_data if isinstance(raw_data, list) else raw_data.get('data', [])

warehouses = {}
for row in records:
    if not row or len(row) < 9:
        continue
    
    wh_name = str(row[0]).strip()      # 仓库
    zone_name = str(row[1]).strip()    # 区域
    rows = int(row[2]) if row[2] else 0      # 排
    cols = int(row[3]) if row[3] else 0      # 列
    layers = int(row[4]) if row[4] else 1    # 层
    slot_vol = float(row[5]) if row[5] else 0  # 单库位容积
    occupied = int(row[6]) if row[6] else 0    # 已用
    overdue = int(row[7]) if row[7] else 0     # 超期数
    avg_age = float(row[8]) if row[8] else 0   # 平均库龄

    total_slots = rows * cols * layers
    fill = occupied / total_slots if total_slots > 0 else 0

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

# 3. 输出成 data.json
output = list(warehouses.values())
with open('data.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"✅ data.json 生成成功，共 {len(output)} 个仓库")
