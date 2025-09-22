import time

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.model_selection import train_test_split

import joblib

# Load the trained model
model = joblib.load('models/ddos_model.pkl')
# Define the chunk size
chunk_size = 100000

# Initialize an empty list to store the sample
sample_list = []

# Read the CSV in chunks without early termination
for chunk in pd.read_csv('datasets/ddos-dataset/ddos_balanced/final_dataset.csv', chunksize=chunk_size):
    # Sample from the current chunk
    sample = chunk.sample(frac=0.1, random_state=42)
    sample_list.append(sample)

# Concatenate all sampled chunks
df = pd.concat(sample_list, ignore_index=True)
print(df['Label'].value_counts())
df = df.drop(['Unnamed: 0', 'Flow ID', 'Src IP', 'Dst IP', 'Timestamp'], axis=1)
df = df.dropna()
print(df.info())
print(df.columns)
print(len(df.columns))
quit()
# Check for infinite values
inf_mask = np.isinf(df.select_dtypes(include=[np.number]))
inf_columns = inf_mask.any()
print("Columns with inf values:\n", inf_columns[inf_columns].index.tolist())
df_clean = df.replace([np.inf, -np.inf], np.nan).dropna()
print("Remaining inf:", np.isinf(df_clean.select_dtypes(include=[np.number])).any().any())
print("Remaining NaN:", df_clean.isna().any().any())



X = df_clean.drop('Label', axis=1)
y = df_clean['Label']

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y, test_size=0.2, random_state=42, stratify=y
)
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)
y_pred = model.predict(X_test)
print(classification_report(y_test, y_pred))
print("Confusion Matrix:\n", confusion_matrix(y_test, y_pred))
print("Accuracy:",accuracy_score(y_test, y_pred))
time_suffix = time.strftime("%Y%m%d_%H%M")
joblib.dump(model, f'models/ddos_model_{time_suffix}.pkl')