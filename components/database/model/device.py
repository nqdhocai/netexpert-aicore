from dataclasses import dataclass, asdict

@dataclass
class Device:
    id: str
    name: str
    device_type: str
    ethernet_ports: str
    wifi_ports: str
    bandwidth: float
    bandwidth_6_ghz: float
    bandwidth_5_ghz: float
    bandwidth_2_4_ghz: float
    supported_protocols: str
    max_devices_supported: str
    poe_support: str
    vlan_support: str
    security_features: str
    coverage: float
    frequency: float
    power_consumption: str
    latency: float
    manufacturer: str
    price: float
    url: str
    img_url: str
    embedding: list[float]

    def __post_init__(self):
        self.id = self.id.lower()
        self.device_type = self.device_type.lower()
    def to_dict(self) -> dict:
        return asdict(self)
