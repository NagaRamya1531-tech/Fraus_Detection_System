import pandas as pd
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split
from imblearn.over_sampling import SMOTE
import os

# Load dataset
data_path = os.path.join("..", "data", "PS_20174392719_1491204439457_log.csv")
df = pd.read_csv(data_path)

print("Original Shape:", df.shape)

# Drop non-essential columns
df = df.drop(['nameOrig', 'nameDest', 'isFlaggedFraud'], axis=1)

# Encode 'type' column (CASH-IN, CASH-OUT, etc.)
le = LabelEncoder()
df['type'] = le.fit_transform(df['type'])

# Define features and target
X = df.drop('isFraud', axis=1)
y = df['isFraud']

# Handle imbalance using SMOTE
print("Before SMOTE:", y.value_counts())
sm = SMOTE(random_state=42)
X_res, y_res = sm.fit_resample(X, y)
print("After SMOTE:", y_res.value_counts())

# Scale features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X_res)

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y_res, test_size=0.2, random_state=42, stratify=y_res
)

print("Train set:", X_train.shape)
print("Test set:", X_test.shape)

# Save preprocessed data
pd.DataFrame(X_train).to_csv("../data/X_train.csv", index=False)
pd.DataFrame(X_test).to_csv("../data/X_test.csv", index=False)
pd.DataFrame(y_train).to_csv("../data/y_train.csv", index=False)
pd.DataFrame(y_test).to_csv("../data/y_test.csv", index=False)

print("✅ Preprocessing complete. Files saved in data folder.")
