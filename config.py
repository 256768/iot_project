"""Configuration for parking system"""
import BG77

# Mobile network
OPERATOR = BG77.Operator.CZ_VODAFONE
APN = "lpwa.vodafone.iot"
RADIO_INFO_PERIOD = 20  # [s]

# Connection
IPV4 = "127.0.1.10"
PORT = "65525"

# Capacity
CAPACITY = 10
