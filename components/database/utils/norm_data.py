import time
from ast import literal_eval
import os

from aicore.components.retrieval.embedding import *

norm = device_info = {
    "bandwidth": "Mbps",  # Total bandwidth in Mbps
    "bandwidth_6_ghz": "Mbps",  # Bandwidth for 6 GHz in Mbps
    "bandwidth_5_ghz": "Mbps",  # Bandwidth for 5 GHz in Mbps
    "bandwidth_2_4_ghz": "Mbps",  # Bandwidth for 2.4 GHz in Mbps
    "max_devices_supported": "devices",  # Number of devices supported (unit: devices)
    "coverage": "m^2",  # Coverage area in square meters (unit: m²)
    "power_consumption": "W",  # Power consumption in watts (unit: W)
    "latency": "second",  # Latency in seconds (unit: s)
    "price": "USD"
}

genai.configure(api_key=os.getenv('GEMINI_API'))

# Create the model
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "application/json",
}

model = genai.GenerativeModel(
    model_name="gemini-2.0-flash-exp",
    generation_config=generation_config,
    system_instruction="Chuẩn hóa dữ liệu sau theo cấu trúc bảng sau và chuyển đổi kết quả sang định dạng CSV:  \n \n**Bảng cấu trúc**:  \n- `id TEXT PRIMARY KEY`  \n- `name TEXT NOT NULL`  \n- `device_type TEXT NOT NULL`  \n- `ethernet_ports TEXT`  \n- `wifi_ports TEXT`  \n- `bandwidth NUMERIC(10, 5)` (đơn vị Mbps, tính bằng tổng: bandwidth_6_ghz + bandwidth_5_ghz + bandwidth_2_4_ghz)  \n- `bandwidth_6_ghz NUMERIC(10, 5)` (đơn vị Mbps)  \n- `bandwidth_5_ghz NUMERIC(10, 5)` (đơn vị Mbps)  \n- `bandwidth_2_4_ghz NUMERIC(10, 5)` (đơn vị Mbps)  \n- `supported_protocols TEXT`  \n- `max_devices_supported TEXT`  \n- `poe_support TEXT`  \n- `vlan_support TEXT`  \n- `security_features TEXT`  \n- `coverage TEXT` (đơn vị m²)  \n- `frequency TEXT`  \n- `power_consumption TEXT`  \n- `latency NUMERIC(10, 10)` (đơn vị giây)  \n- `manufacturer TEXT`  \n- `price NUMERIC(10, 2)` (đơn vị USD)  \n- `url TEXT` \n- `img_url TEXT`  \n- `embedding vector(768)`   \n **Yêu cầu cụ thể**:  \n1. Chuẩn hóa dữ liệu:  \n    - Kiểm tra và đảm bảo các giá trị thuộc đúng định dạng và ý nghĩa.  \n    - Trường `bandwidth` phải là tổng của `bandwidth_6_ghz`, `bandwidth_5_ghz`, và `bandwidth_2_4_ghz`.  \n2. Xuất dữ liệu đã chuẩn hóa thành file CSV, mỗi hàng tương ứng với một thiết bị.   \n Trả về dữ liệu dưới dạng file CSV hoặc nội dung CSV trực tiếp.",
)


def norm_data(sample):
    res = model.generate_content(sample).text
    norm_dt = literal_eval(res.replace("null", "'null'"))[0]
    doc = ''
    for key, val in norm_dt.items():
        if 'url' in key:
            continue
        if key in norm.keys():
            doc = doc + key + ": " + str(val) + " " + norm[key] + ",\n"
        else:
            doc += key + ": " + str(val) + ",\n"
    embed = get_embedding_doc(doc)
    norm_dt['embedding'] = embed
    time.sleep(2)
    return norm_dt
