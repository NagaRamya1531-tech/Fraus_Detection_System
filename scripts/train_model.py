import pandas as pd
import xgboost as xgb
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score, accuracy_score, precision_score, recall_score, f1_score
import pickle
import os

# Load preprocessed data
X_train = pd.read_csv("data/X_train.csv")
X_test = pd.read_csv("data/X_test.csv")
y_train = pd.read_csv("data/y_train.csv")
y_test = pd.read_csv("data/y_test.csv")

# Convert y to 1D arrays
y_train = y_train.values.ravel()
y_test = y_test.values.ravel()

print("Training data loaded successfully.")

# Define and train XGBoost model
model = xgb.XGBClassifier(
    n_estimators=200,
    max_depth=6,
    learning_rate=0.1,
    subsample=0.8,
    colsample_bytree=0.8,
    scale_pos_weight=1,
    eval_metric='logloss'
)

print("Training model...")
model.fit(X_train, y_train)

# Predictions
y_pred = model.predict(X_test)
y_pred_proba = model.predict_proba(X_test)[:, 1]

# Metrics
accuracy = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred)
recall = recall_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred)
roc_auc = roc_auc_score(y_test, y_pred_proba)

# Confusion Matrix
cm = confusion_matrix(y_test, y_pred)
tn, fp, fn, tp = cm.ravel()
false_positive_rate = fp / (fp + tn)

# Print Results
print("\n📌 Model Performance Metrics:")
print(f"✅ Accuracy: {accuracy:.4f}")
print(f"✅ Precision: {precision:.4f}")
print(f"✅ Recall: {recall:.4f}")
print(f"✅ F1-Score: {f1:.4f}")
print(f"✅ ROC-AUC Score: {roc_auc:.4f}")
print(f"✅ False Positive Rate: {false_positive_rate:.6f}")
print("\n📌 Classification Report:\n", classification_report(y_test, y_pred))
print("📌 Confusion Matrix:\n", cm)

# Save model
model_path = os.path.join( "models", "fraud_model.pkl")
with open(model_path, 'wb') as file:
    pickle.dump(model, file)

print(f"\n✅ Model trained and saved as {model_path}")
