from agents.planner import get_action
from agents import device_rcm, normal_chat, technical_expert, network_builder

functions = {
    "normal_chat": normal_chat.normal_chat,
    "technical_chat": technical_expert.technical_chat,
    "rcm_devices": device_rcm.rcm_devices,
    "get_more_req": network_builder.get_more_req,
    "household_network_build": network_builder.household_network_build,
    "business_network_build": network_builder.business_network_build,
}

def get_response(history):
    res = {
        "status": "success",
        "response": "",
        "devices": [],
        "networks": [],
        "blogs": []
    }
    function = get_action(history)
    function_dict = {
        'name': function[0],
        'args': function[1]
    }
    print(function_dict)
    result = functions[function_dict['name']](**function_dict['args'])
    for key in res.keys():
        if key in result.keys():
            res[key] = result[key]
    return res

history=[
    {
      "role": "user",
      "parts": [
        "tôi muốn hệ thống mạng",
      ],
    },
    {
      "role": "model",
      "parts": [
        "```Function call\n{\n  \"name\": \"get_more_req\",\n  \"args\": {\n    \"recommend_question\": \"Bạn muốn xây dựng hệ thống mạng cho mục đích gì? (ví dụ: gia đình, văn phòng, doanh nghiệp) và bạn có yêu cầu đặc biệt nào không?\"\n  }\n}\n```",
      ],
    },
    {
      "role": "user",
      "parts": [
        "cho mục đích xem phim",
      ],
    },
    {
      "role": "model",
      "parts": [
        "```Function call\n{\n  \"name\": \"rcm_devices\",\n  \"args\": {}\n}\n```",
      ],
    },
    {
      "role": "user",
      "parts": [
        "đề xuất mạng cho gia đình với ngân sách 100 usd\n",
      ],
    },
    {
      "role": "model",
      "parts": [
        "```Function call\n{\n  \"name\": \"get_more_req\",\n  \"args\": {\n    \"recommend_question\": \"Bạn có thể cho biết thêm về số lượng thiết bị cần kết nối vào mạng và tần số mạng ưa thích của bạn không?\"\n  }\n}\n```",
      ],
    },
    {
      "role": "user",
      "parts": [
        "100 thiết bị\n",
      ],
    },
    {
      "role": "model",
      "parts": [
        "```Function call\n{\n  \"name\": \"get_more_req\",\n  \"args\": {\n    \"recommend_question\": \"Tần số mạng ưa thích của bạn là bao nhiêu? (2.4GHz hoặc 5GHz)\"\n  }\n}\n```",
      ],
    },
    {
      "role": "user",
      "parts": [
        "2.4",
      ],
    },
    {
      "role": "model",
      "parts": [
        "```Function call\n{\n  \"name\": \"household_network_build\",\n  \"args\": {\n    \"brand_preference\": \"any\",\n    \"budget\": 100.0,\n    \"number_of_devices\": 100.0,\n    \"preferred_frequency\": 2.4\n  }\n}\n```",
      ],
    },
    {
      "role": "user",
      "parts": [
        "xây dựng mạng cho doanh nghiệp cỡ vừa\n",
      ],
    },
    {
      "role": "model",
      "parts": [
        "```Function call\n{\n  \"name\": \"get_more_req\",\n  \"args\": {\n    \"recommend_question\": \"Bạn có thể cung cấp thêm thông tin về số lượng thiết bị, băng thông ước tính, các ứng dụng quan trọng cần ưu tiên, số lượng thiết bị PoE và yêu cầu về VLAN và mức độ bảo mật mong muốn của bạn không?\"\n  }\n}\n```",
      ],
    },
    {
      "role": "user",
      "parts": [
        "khoảng 1000 thiết bị, băng thông cao có kết nối Vlan và mức độ bảo mật cao\n",
      ],
    },
    {
      "role": "model",
      "parts": [
        "```Function call\n{\n  \"name\": \"get_more_req\",\n  \"args\": {\n    \"recommend_question\": \"Bạn có thể cho biết thêm về băng thông ước tính (ví dụ: 1Gbps, 10Gbps,...), số lượng thiết bị PoE và ngân sách của bạn là bao nhiêu không?\"\n  }\n}\n```",
      ],
    },
    {
      "role": "user",
      "parts": [
        "10 gbps\n",
      ],
    },
    {
      "role": "model",
      "parts": [
        "```Function call\n{\n  \"name\": \"get_more_req\",\n  \"args\": {\n    \"recommend_question\": \"Bạn có thể cho biết thêm về số lượng thiết bị PoE và ngân sách của bạn là bao nhiêu không?\"\n  }\n}\n```",
      ],
    },
    {
      "role": "user",
      "parts": [
        "100",
      ],
    },
    {
      "role": "model",
      "parts": [
        "```Function call\n{\n  \"name\": \"get_more_req\",\n  \"args\": {\n    \"recommend_question\": \"Ngân sách bạn dự kiến cho việc xây dựng hệ thống mạng này là bao nhiêu?\"\n  }\n}\n```",
      ],
    },
    {
      "role": "user",
      "parts": [
        "10",
      ],
    },
  ]

