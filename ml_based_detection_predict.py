import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
import joblib

# Load the trained model (replace with your model file path)
model = joblib.load('models/ddos_model_20250902_1133.pkl')

# Sample data: This is an example of what a single row might look like
# Assuming the model was trained on these features:
sample_data = {
    'Src Port': np.random.randint(1024, 65535),
    'Dst Port': np.random.randint(80, 443),
    'Protocol': np.random.choice([1, 6, 17]),  # 1: ICMP, 6: TCP, 17: UDP
    'Flow Duration': np.random.randint(50, 1000),
    'Tot Fwd Pkts': np.random.randint(1, 2000),
    'Tot Bwd Pkts': np.random.randint(1, 2000),
    'TotLen Fwd Pkts': np.random.randint(500, 50000),
    'TotLen Bwd Pkts': np.random.randint(500, 50000),
    'Fwd Pkt Len Max': np.random.randint(50, 1500),
    'Fwd Pkt Len Min': np.random.randint(50, 1500),
    'Fwd Pkt Len Mean': np.random.randint(50, 1500),
    'Fwd Pkt Len Std': np.random.uniform(0, 500),
    'Bwd Pkt Len Max': np.random.randint(50, 1500),
    'Bwd Pkt Len Min': np.random.randint(50, 1500),
    'Bwd Pkt Len Mean': np.random.randint(50, 1500),
    'Bwd Pkt Len Std': np.random.uniform(0, 500),
    'Flow Byts/s': np.random.randint(500, 100000),
    'Flow Pkts/s': np.random.randint(1, 1000),
    'Flow IAT Mean': np.random.uniform(0, 1000),
    'Flow IAT Std': np.random.uniform(0, 1000),
    'Flow IAT Max': np.random.uniform(0, 1000),
    'Flow IAT Min': np.random.uniform(0, 1000),
    'Fwd IAT Tot': np.random.uniform(0, 1000),
    'Fwd IAT Mean': np.random.uniform(0, 1000),
    'Fwd IAT Std': np.random.uniform(0, 1000),
    'Fwd IAT Max': np.random.uniform(0, 1000),
    'Fwd IAT Min': np.random.uniform(0, 1000),
    'Bwd IAT Tot': np.random.uniform(0, 1000),
    'Bwd IAT Mean': np.random.uniform(0, 1000),
    'Bwd IAT Std': np.random.uniform(0, 1000),
    'Bwd IAT Max': np.random.uniform(0, 1000),
    'Bwd IAT Min': np.random.uniform(0, 1000),
    'Fwd PSH Flags': np.random.randint(0, 2),
    'Bwd PSH Flags': np.random.randint(0, 2),
    'Fwd URG Flags': np.random.randint(0, 2),
    'Bwd URG Flags': np.random.randint(0, 2),
    'Fwd Header Len': np.random.randint(0, 100),
    'Bwd Header Len': np.random.randint(0, 100),
    'Fwd Pkts/s': np.random.randint(1, 1000),
    'Bwd Pkts/s': np.random.randint(1, 1000),
    'Pkt Len Min': np.random.randint(50, 1500),
    'Pkt Len Max': np.random.randint(50, 1500),
    'Pkt Len Mean': np.random.randint(50, 1500),
    'Pkt Len Std': np.random.uniform(0, 500),
    'Pkt Len Var': np.random.uniform(0, 500),
    'FIN Flag Cnt': np.random.randint(0, 10),
    'SYN Flag Cnt': np.random.randint(0, 10),
    'RST Flag Cnt': np.random.randint(0, 10),
    'PSH Flag Cnt': np.random.randint(0, 10),
    'ACK Flag Cnt': np.random.randint(0, 10),
    'URG Flag Cnt': np.random.randint(0, 10),
    'CWE Flag Count': np.random.randint(0, 10),
    'ECE Flag Cnt': np.random.randint(0, 10),
    'Down/Up Ratio': np.random.uniform(0.1, 1),
    'Pkt Size Avg': np.random.randint(50, 1500),
    'Fwd Seg Size Avg': np.random.randint(50, 1500),
    'Bwd Seg Size Avg': np.random.randint(50, 1500),
    'Fwd Byts/b Avg': np.random.uniform(0, 100),
    'Fwd Pkts/b Avg': np.random.uniform(0, 100),
    'Fwd Blk Rate Avg': np.random.uniform(0, 100),
    'Bwd Byts/b Avg': np.random.uniform(0, 100),
    'Bwd Pkts/b Avg': np.random.uniform(0, 100),
    'Bwd Blk Rate Avg': np.random.uniform(0, 100),
    'Subflow Fwd Pkts': np.random.randint(1, 1000),
    'Subflow Fwd Byts': np.random.randint(1, 10000),
    'Subflow Bwd Pkts': np.random.randint(1, 1000),
    'Subflow Bwd Byts': np.random.randint(1, 10000),
    'Init Fwd Win Byts': np.random.randint(1, 10000),
    'Init Bwd Win Byts': np.random.randint(1, 10000),
    'Fwd Act Data Pkts': np.random.randint(1, 1000),
    'Fwd Seg Size Min': np.random.randint(50, 1500),
    'Active Mean': np.random.uniform(0, 1000),
    'Active Std': np.random.uniform(0, 1000),
    'Active Max': np.random.uniform(0, 1000),
    'Active Min': np.random.uniform(0, 1000),
    'Idle Mean': np.random.uniform(0, 1000),
    'Idle Std': np.random.uniform(0, 1000),
    'Idle Max': np.random.uniform(0, 1000),
    'Idle Min': np.random.uniform(0, 1000)
}

sample_ddos_data = {
    'Src Port': np.random.randint(4000, 5000),  # Source port is random
    'Dst Port': 80,  # Common port for DDoS (HTTP)
    'Protocol': 6,  # TCP Protocol
    'Flow Duration': np.random.randint(1000000, 5000000),  # High flow duration typical of DDoS
    'Tot Fwd Pkts': np.random.randint(25, 50),  # High packet count (flood)
    'Tot Bwd Pkts': np.random.randint(25, 50),  # High packet count (flood)
    'TotLen Fwd Pkts': np.random.randint(70, 100),  # High byte size
    'TotLen Bwd Pkts': np.random.randint(50000, 100000),  # High byte size
    'Fwd Pkt Len Max': np.random.randint(70, 100),  # Packet length varies, but could be smaller in DDoS
    'Fwd Pkt Len Min': np.random.randint(0, 1),  # Packet length is unpredictable in DDoS
    'Fwd Pkt Len Mean': np.random.randint(25, 50),  # Often smaller packet sizes
    'Fwd Pkt Len Std': np.random.uniform(50, 100),  # High variation in packet length
    'Bwd Pkt Len Max': np.random.randint(1200, 5000),  # Backward packet length is also random
    'Bwd Pkt Len Min': np.random.randint(0, 1),  # Backward packet length
    'Bwd Pkt Len Mean': np.random.randint(1000, 1500),  # Likely smaller packets during flood
    'Bwd Pkt Len Std': np.random.uniform(300, 1000),  # High packet length variation in DDoS
    'Flow Byts/s': np.random.randint(10000, 20000),  # Very high flow of bytes per second
    'Flow Pkts/s': np.random.randint(10000, 30000),  # High packet rate in DDoS
    'Flow IAT Mean': np.random.uniform(50000.1, 100000),  # Shorter inter-arrival time between packets
    'Flow IAT Std': np.random.uniform(100000, 300000),  # DDoS has a high variation in inter-arrival times
    'Flow IAT Max': np.random.uniform(1000000, 5000000),  # Higher max IAT could be seen in some DDoS traffic
    'Flow IAT Min': np.random.uniform(100, 500),  # Short IAT between packets
    'Fwd IAT Tot': np.random.uniform(2000000, 5000000),  # Flooding activity may cause short IAT times
    'Fwd IAT Mean': np.random.uniform(100000, 300000),  # Rapid send rates of packets
    'Fwd IAT Std': np.random.uniform(100000, 300000),  # Variation due to attack pattern
    'Fwd IAT Max': np.random.uniform(2000000, 5000000),  # High max IAT during attack
    'Fwd IAT Min': np.random.uniform(150, 200),  # Small IAT indicating constant flood
    'Bwd IAT Tot': np.random.uniform(200000, 500000),  # Large amount of backward packets in the flood
    'Bwd IAT Mean': np.random.uniform(200000, 500000),  # Short time intervals in the flood
    'Bwd IAT Std': np.random.uniform(200000, 500000),  # Large variation in IAT
    'Bwd IAT Max': np.random.uniform(200000, 500000),  # Max IAT during flood
    'Bwd IAT Min': np.random.uniform(0.1, 1),  # Short IAT in some DDoS patterns
    'Fwd PSH Flags': np.random.randint(0, 2),  # PSH flags are unlikely to be frequent in DDoS
    'Bwd PSH Flags': np.random.randint(0, 2),  # PSH flags in BWD traffic could be lower
    'Fwd URG Flags': np.random.randint(0, 2),  # URG flags will be rare in a DDoS attack
    'Bwd URG Flags': np.random.randint(0, 2),  # Rarely used during DDoS
    'Fwd Header Len': np.random.randint(40, 100),  # Small headers for small packets
    'Bwd Header Len': np.random.randint(40, 100),  # Small headers for backward traffic
    'Fwd Pkts/s': np.random.randint(10000, 50000),  # DDoS increases packets per second
    'Bwd Pkts/s': np.random.randint(10000, 50000),  # Increased backward traffic rate
    'Pkt Len Min': np.random.randint(0, 1),  # Packet length is quite random in DDoS
    'Pkt Len Max': np.random.randint(1200, 1500),  # High variability in packet length
    'Pkt Len Mean': np.random.randint(600, 1000),  # Mean packet size is often small
    'Pkt Len Std': np.random.uniform(1000, 1500),  # High variation in packet size
    'Pkt Len Var': np.random.uniform(100000, 5000000),  # DDoS often generates packets of varying sizes
    'FIN Flag Cnt': np.random.randint(0, 1),  # FIN flags are low in DDoS traffic
    'SYN Flag Cnt': np.random.randint(0, 1),  # SYN flags might be frequent in SYN flood
    'RST Flag Cnt': np.random.randint(0, 1),  # RST flags are rare in DDoS
    'PSH Flag Cnt': np.random.randint(0, 1),  # PSH flags will be low in DDoS
    'ACK Flag Cnt': np.random.randint(0, 1),  # ACK flags may be frequent
    'URG Flag Cnt': np.random.randint(0, 1),  # URG flags are rare in DDoS
    'CWE Flag Count': np.random.randint(0, 1),  # Rarely used during DDoS
    'ECE Flag Cnt': np.random.randint(0, 1),  # Low during a flood
    'Down/Up Ratio': np.random.uniform(0, 1),  # DDoS may have a higher down-to-up ratio
    'Pkt Size Avg': np.random.randint(700, 1000),  # Packets in DDoS can vary in size
    'Fwd Seg Size Avg': np.random.randint(1, 5),  # Forward segment size may be small
    'Bwd Seg Size Avg': np.random.randint(1500, 5000),  # Similar for backward segments
    'Fwd Byts/b Avg': np.random.uniform(100000, 1),  # Floods generate higher byte rates
    'Fwd Pkts/b Avg': np.random.uniform(0, 1),  # Increased packets per byte in flood
    'Fwd Blk Rate Avg': np.random.uniform(0, 1),  # Block rate varies in DDoS
    'Bwd Byts/b Avg': np.random.uniform(0, 1),  # Increased backward byte rate
    'Bwd Pkts/b Avg': np.random.uniform(0, 1),  # Increased backward packets per byte
    'Bwd Blk Rate Avg': np.random.uniform(0, 1),  # Block rate for backward traffic
    'Subflow Fwd Pkts': np.random.randint(50, 100),  # High number of forward packets
    'Subflow Fwd Byts': np.random.randint(70, 100),  # High number of bytes in forward packets
    'Subflow Bwd Pkts': np.random.randint(50, 100),  # High number of backward packets
    'Subflow Bwd Byts': np.random.randint(60000, 100000),  # High backward byte count
    'Init Fwd Win Byts': np.random.randint(-1, 1),  # High initial forward window size
    'Init Bwd Win Byts': np.random.randint(50000, 100000),  # High initial backward window size
    'Fwd Act Data Pkts': np.random.randint(1000, 5000),  # Active data in the flood
    'Fwd Seg Size Min': np.random.randint(0, 1),  # Smallest forward segment size
    'Active Mean': np.random.uniform(0, 1),  # DDoS attacks can have high activity levels
    'Active Std': np.random.uniform(0, 1),  # High activity variation
    'Active Max': np.random.uniform(0, 1),  # Peak activity during DDoS
    'Active Min': np.random.uniform(0, 1),  # DDoS will have a lower activity during pause phases
    'Idle Mean': np.random.uniform(0, 1),  # Short idle times for DDoS
    'Idle Std': np.random.uniform(0, 1),  # Higher variation in idle times
    'Idle Max': np.random.uniform(0, 1),  # Max idle time might be seen during attack pauses
    'Idle Min': np.random.uniform(0, 1)   # Short idle time expected during DDoS
}
print(sample_ddos_data)

# Convert sample data into a pandas DataFrame
sample_df = pd.DataFrame(sample_ddos_data,index=[0])

# Optionally, scale the data if the model was trained with normalization (e.g., StandardScaler)
scaler = StandardScaler()
sample_df_scaled = scaler.fit_transform(sample_df)

# Make a prediction using the trained model
prediction = model.predict(sample_df_scaled)

# Output prediction (0 = Normal, 1 = DDoS)
result = "DDoS" if prediction[0] == 1 else "Normal"
print(f"Prediction: {result}")
