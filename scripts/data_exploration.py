import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Load dataset
data_path = os.path.join("..", "data", "PS_20174392719_1491204439457_log.csv")
df = pd.read_csv(data_path)

# Basic info
print("Dataset Shape:", df.shape)
print("Columns:", df.columns.tolist())
print("Missing Values:\n", df.isnull().sum())
print("\nFraud distribution:")
print(df['isFraud'].value_counts())

# Fraud percentage
fraud_cases = df['isFraud'].value_counts()
fraud_percentage = (fraud_cases[1] / fraud_cases.sum()) * 100
print(f"\nFraud cases percentage: {fraud_percentage:.4f}%")

# Plot Fraud vs Non-Fraud distribution
plt.figure(figsize=(6,4))
sns.countplot(x='isFraud', data=df)
plt.title
