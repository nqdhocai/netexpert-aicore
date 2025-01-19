from components.database.database import *

def rcm_devices(query, budget=0):
    device_ids = [i[0] for i in query_by_vector(query)]
    result = []
    if budget != 0:
        satisfied_device_ids = get_device_by_price_range(budget)
        results = []
        for device_id in device_ids:
            if device_id in satisfied_device_ids:
                results.append(device_id)
        if len(results) == 0:
            result = device_ids[:3]
        elif len(results) >= 5:
            result = results[:5]
    else:
        result = device_ids[:5]
    return {
        "devices": result
    }
