from components.database.model.device import Device
from components.retrieval.embedding import *
from ast import literal_eval
import psycopg2
import os

from dotenv import load_dotenv
load_dotenv()

# Fetch variables
USER = os.getenv("user")
PASSWORD = os.getenv("password")
HOST = os.getenv("host")
PORT = os.getenv("port")
DBNAME = os.getenv("dbname")

# Connect to the database
try:
    connection = psycopg2.connect(
        user=USER,
        password=PASSWORD,
        host=HOST,
        port=PORT,
        dbname=DBNAME
    )
    print("Connection successful!")

    # Create a cursor to execute SQL queries
    cursor = connection.cursor()

    # Example query
    cursor.execute("SELECT NOW();")
    result = cursor.fetchone()
    print("Current Time:", result)

    # Close the cursor and connection
    cursor.close()
    connection.close()

except Exception as e:
    print(f"Failed to connect: {e}")

def get_db_connection():
    connection = psycopg2.connect(
        user=USER,
        password=PASSWORD,
        host=HOST,
        port=PORT,
        dbname=DBNAME
    )
    return connection
def fetch_data_model(data_query):
    columns = "id, name, device_type, ethernet_ports, wifi_ports, bandwidth, bandwidth_6_ghz, bandwidth_5_ghz, bandwidth_2_4_ghz, supported_protocols, max_devices_supported, poe_support, vlan_support, security_features, coverage, frequency, power_consumption, latency, manufacturer, price, url, img_url, embedding"
    columns = columns.split(", ")
    data = {}
    for col, val in zip(columns, data_query):
        data[col] = val
    return data


def insert_device(device: Device):
    connection = get_db_connection()
    
    device_info = device.to_dict()
    cursor = connection.cursor()

    # Kiểm tra xem các trường có phải là 'null' hay không
    for col in ['bandwidth', 'bandwidth_6_ghz', 'bandwidth_5_ghz', 'bandwidth_2_4_ghz', 'price', 'latency']:
        if device_info[col] in ["'null'", 'null']:
            device_info[col] = 0

    try:
        # Kiểm tra xem sản phẩm đã tồn tại chưa
        cursor.execute('''SELECT id FROM devices WHERE id = %s''', (device_info['id'],))
        existing_device = cursor.fetchone()

        if existing_device:
            # Nếu sản phẩm đã tồn tại, in thông báo và không thêm vào
            print(f"Device with ID {device_info['id']} already exists.")
        else:
            # Nếu sản phẩm chưa tồn tại, thực hiện INSERT
            cursor.execute('''INSERT INTO devices (
                id, name, device_type, ethernet_ports, wifi_ports, bandwidth,
                bandwidth_6_ghz, bandwidth_5_ghz, bandwidth_2_4_ghz, supported_protocols,
                max_devices_supported, poe_support, vlan_support, security_features, coverage,
                frequency, power_consumption, latency, manufacturer, price, url, img_url, embedding
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)''', (
                device_info['id'], device_info['name'], device_info['device_type'], device_info['ethernet_ports'],
                device_info['wifi_ports'], float(device_info['bandwidth']), float(device_info['bandwidth_6_ghz']),
                float(device_info['bandwidth_5_ghz']), float(device_info['bandwidth_2_4_ghz']),
                device_info['supported_protocols'], device_info['max_devices_supported'], device_info['poe_support'],
                device_info['vlan_support'], device_info['security_features'], device_info['coverage'],
                device_info['frequency'],
                device_info['power_consumption'], float(device_info['latency']), device_info['manufacturer'],
                float(device_info['price']), device_info['url'], device_info['img_url'], device_info['embedding']
            ))

            # Commit transaction
            connection.commit()
            print(f"Device {device_info['id']} added")

    except psycopg2.errors.UniqueViolation as e:
        # Rollback in case of an error
        connection.rollback()
        print(f"Error: Device with ID {device_info['id']} already exists.")
    except Exception as e:
        # Rollback for any other errors
        connection.rollback()
        print(f"An error occurred: {e}")
    finally:
        # Close the cursor
        cursor.close()


def get_all_devices():
    connection = get_db_connection()
    
    cursor = connection.cursor()
    cursor.execute("select * from devices;")
    devices = cursor.fetchall()
    devices = [fetch_data_model(device) for device in devices]
    cursor.close()
    return devices

def get_device_by_location(nation="Global", province=""):
    connection = get_db_connection()
    cursor = connection.cursor()

    # Kiểm tra nếu nation tồn tại trong bảng retailers
    cursor.execute("SELECT COUNT(*) FROM retailers WHERE nation = %s;", (nation,))
    nation_exists = cursor.fetchone()[0] > 0

    if not nation_exists:
        nation = "Global"
    if not province:
        province = None

    # Truy vấn thiết bị dựa trên nation trước, rồi đến province
    query = """
        SELECT DISTINCT d.*
        FROM devices d
        JOIN device_retailers dr ON d.id = dr.device_id
        JOIN retailers r ON dr.retailer_id = r.id
        WHERE r.nation = %s
          AND (r.province = %s OR %s IS NULL);
    """
    cursor.execute(query, (nation, province, province))
    devices = cursor.fetchall()
    
    # Chuyển đổi dữ liệu sang định dạng mong muốn
    devices = [fetch_data_model(device) for device in devices]

    cursor.close()
    return devices


def get_device_by_id(id):
    connection = get_db_connection()
    
    cursor = connection.cursor()
    cursor.execute("select * from devices where id=%s ;", (id,))
    device = cursor.fetchone()
    if device:
        device = fetch_data_model(device)
    cursor.close()
    return device

def get_device_by_types(device_types):
    if not device_types:
        return []
    
    connection = get_db_connection()
    cursor = connection.cursor()

    placeholders = ', '.join(['%s'] * len(device_types))
    query = f"SELECT id FROM devices WHERE device_type IN ({placeholders})"

    cursor.execute(query, tuple(device_types))

    results = cursor.fetchall()

    cursor.close()

    return [row[0] for row in results]

def insert_blog_chunk(blog_id, content, embedding):
    connection = get_db_connection()
    
    cursor = connection.cursor()
    cursor.execute("""INSERT INTO blog_chunks (blog_id, content, embedding) VALUES (%s, %s, %s);""", (blog_id, content, embedding))
    connection.commit()
    cursor.close()

def query_by_vector(query):
    connection = get_db_connection()
    
    query_emb = get_embedding_query(query)
    cursor = connection.cursor()
    vector_str = f"[{','.join(map(str, query_emb))}]"

    # Thực hiện truy vấn tìm kiếm vector tương tự
    cursor.execute("""
        SELECT id, embedding <=> %s AS distance
        FROM devices
        ORDER BY distance
        LIMIT 10;
    """, (vector_str,))

    # In kết quả
    result = cursor.fetchall()
    return result

def get_device_by_price_range(budget):
    connection = get_db_connection()
    
    cursor = connection.cursor()
    min_budget = float(budget)*90/100
    max_budget = float(budget)*110/100
    cursor.execute("""
    select id from devices where price between %s and %s;
    """, (min_budget, max_budget))

    result = cursor.fetchall()
    return result

def get_all_blog():
    connection = get_db_connection()
    
    cursor = connection.cursor()
    cursor.execute("select id, title, content from blogs;")
    blogs = cursor.fetchall()
    cursor.close()
    return blogs

def get_blog_by_query(query, threshold=0.35):
    connection = get_db_connection()
    
    query_emb = get_embedding_query(query)
    cursor = connection.cursor()
    vector_str = f"[{','.join(map(str, query_emb))}]"

    # Thực hiện truy vấn tìm kiếm vector tương tự có ngưỡng threshold
    cursor.execute("""
            SELECT blog_id, content, embedding <=> %s AS distance
            FROM blog_chunks
            WHERE embedding <=> %s < %s  -- Thêm điều kiện lọc
            ORDER BY distance
            LIMIT 10;
        """, (vector_str, vector_str, threshold))

    result = cursor.fetchall()
    blog_ids = list(set([str(i[0]) for i in result]))
    chunk_contents = [i[1] for i in result]
    return blog_ids, chunk_contents

def get_blog_emb_by_id(blog_id):
    connection = get_db_connection()
    
    cursor = connection.cursor()
    cursor.execute("""
                SELECT embedding
                FROM blog_chunks
                WHERE id = %s;
            """, (blog_id,))
    embedding = cursor.fetchone()
    return literal_eval(embedding[0])

def get_related_blog(blog_id):
    connection = get_db_connection()
    
    blog_emb = get_blog_emb_by_id(blog_id)
    cursor = connection.cursor()
    vector_str = f"[{','.join(map(str, blog_emb))}]"

    # Thực hiện truy vấn tìm kiếm vector tương tự
    cursor.execute("""
                SELECT id, embedding <=> %s AS distance
                FROM blog_chunks
                ORDER BY distance
                LIMIT 3;
            """, (vector_str,))

    # In kết quả
    result = cursor.fetchall()
    related_blogs = {
        i[0]: i[1] for i in result
    }
    return related_blogs

def get_related_blogs(blog_ids):
    related_blogs = {}
    for blog_id in blog_ids:
        blogs = get_related_blog(blog_id)
        for key, val in blogs.items():
            if key in related_blogs.keys():
                related_blogs[key] += blogs[key]
            else:
                related_blogs[key] = blogs[key]
    related_blogs = sorted(related_blogs.items(), key=lambda item: item[1], reverse=True)
    return related_blogs

def get_device_retailer_by_id(device_id):
    connection = get_db_connection()
    
    cursor = connection.cursor()
    cursor.execute("""
                SELECT *
                FROM device_retailers
                WHERE device_id=%s;
            """, (device_id,))
    result = cursor.fetchone()
    retailers = result[-1]
    for retailer in retailers:
        retailer['retailer_url'] = retailer['retailer url']
        if "retailer url" in retailer.keys():
            del retailer['retailer url']
    return retailers