"""
OPTIMIZED TRAINING for 2.2 Million Lending Club Rows
Memory-efficient processing with chunking
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score, roc_auc_score, precision_score, recall_score
import joblib
import os
import gc
import time
import re

print("=" * 70)
print("🚀 LENDING CLUB FULL DATASET TRAINING (2.2 Million Rows)")
print("=" * 70)

start_time = time.time()

# ============================================
# CONFIGURATION
# ============================================
DATASET_PATH = "C:/Users/hemas/Downloads/archive/loan.csv"
CHUNK_SIZE = 100000  # Process 100k rows at a time
SAMPLE_FOR_TEST = 200000  # Use 200k for test set

print(f"\n📁 Dataset: {DATASET_PATH}")
print(f"📊 Chunk size: {CHUNK_SIZE:,} rows per batch")
print(f"🎯 Test set size: {SAMPLE_FOR_TEST:,} rows")

# ============================================
# FUNCTION: Process a chunk of data
# ============================================
def process_chunk(df_chunk):
    """Process one chunk of data to extract features and target"""
    
    # Map loan_status to default flag
    def map_loan_status(status):
        if pd.isna(status):
            return None
        status = str(status)
        bad_statuses = [
            'Charged Off', 'Default', 'Late (31-120 days)', 
            'Does not meet the credit policy. Status:Charged Off',
            'Late (16-30 days)'
        ]
        good_statuses = [
            'Fully Paid', 'Current', 'In Grace Period',
            'Does not meet the credit policy. Status:Fully Paid'
        ]
        if status in bad_statuses:
            return 1
        elif status in good_statuses:
            return 0
        return None
    
    # Convert employment length to years
    def emp_to_years(emp_str):
        if pd.isna(emp_str):
            return 0
        emp_str = str(emp_str)
        if '10+ years' in emp_str:
            return 10
        elif '< 1 year' in emp_str:
            return 0.5
        else:
            match = re.search(r'(\d+)', emp_str)
            return float(match.group(1)) if match else 0
    
    # Create features
    df_chunk['default_flag'] = df_chunk['loan_status'].apply(map_loan_status)
    
    # Remove rows with unknown status
    df_chunk = df_chunk.dropna(subset=['default_flag'])
    
    if len(df_chunk) == 0:
        return None
    
    # Feature engineering
    df_chunk['employment_years'] = df_chunk['emp_length'].apply(emp_to_years)
    
    # Term to months
    df_chunk['loan_term_months'] = df_chunk['term'].apply(
        lambda x: 36 if pd.isna(x) else (36 if '36' in str(x) else 60)
    )
    
    # Clean interest rate
    df_chunk['interest_rate'] = df_chunk['int_rate'].astype(str).str.replace('%', '').astype(float)
    
    # Clean revolving utilization
    df_chunk['revolving_utilization'] = df_chunk['revol_util'].astype(str).str.replace('%', '').astype(float) / 100
    df_chunk['revolving_utilization'] = df_chunk['revolving_utilization'].fillna(0.5)
    
    # Fill missing values
    df_chunk['employment_years'] = df_chunk['employment_years'].fillna(0)
    df_chunk['dti'] = df_chunk['dti'].fillna(0)
    df_chunk['delinq_2yrs'] = df_chunk['delinq_2yrs'].fillna(0)
    df_chunk['inq_last_6mths'] = df_chunk['inq_last_6mths'].fillna(0)
    df_chunk['open_acc'] = df_chunk['open_acc'].fillna(0)
    df_chunk['pub_rec'] = df_chunk['pub_rec'].fillna(0)
    
    # Estimate credit score
    df_chunk['estimated_credit_score'] = 700 - (df_chunk['dti'] * 2) - (df_chunk['delinq_2yrs'] * 10) - (df_chunk['inq_last_6mths'] * 5)
    df_chunk['estimated_credit_score'] = df_chunk['estimated_credit_score'].clip(300, 850).fillna(650)
    
    # Months since delinquency
    df_chunk['months_since_delinquency'] = df_chunk['mths_since_last_delinq'].fillna(999)
    df_chunk['months_since_delinquency'] = df_chunk['months_since_delinquency'].replace(999, 120)
    
    # Home ownership encoding
    home_map = {'MORTGAGE': 0, 'OWN': 1, 'RENT': 2, 'ANY': 3, 'NONE': 4}
    df_chunk['home_ownership_enc'] = df_chunk['home_ownership'].map(home_map).fillna(2)
    
    # Select features
    features_df = pd.DataFrame({
        'employment_years': df_chunk['employment_years'],
        'annual_income': df_chunk['annual_inc'],
        'credit_score': df_chunk['estimated_credit_score'],
        'loan_amount': df_chunk['loan_amnt'],
        'interest_rate': df_chunk['interest_rate'],
        'dti': df_chunk['dti'],
        'revolving_utilization': df_chunk['revolving_utilization'],
        'delinquencies_2yrs': df_chunk['delinq_2yrs'],
        'inquiries_last_6m': df_chunk['inq_last_6mths'],
        'open_accounts': df_chunk['open_acc'],
        'public_records': df_chunk['pub_rec'],
        'months_since_delinquency': df_chunk['months_since_delinquency'],
        'loan_term_months': df_chunk['loan_term_months'],
        'home_ownership': df_chunk['home_ownership_enc'],
        'default_flag': df_chunk['default_flag']
    })
    
    return features_df

# ============================================
# PROCESS DATA IN CHUNKS
# ============================================
print("\n📖 Processing data in chunks...")

all_features = []
total_rows = 0
default_count = 0
chunk_num = 0

# Read CSV in chunks
for chunk in pd.read_csv(DATASET_PATH, chunksize=CHUNK_SIZE, low_memory=False):
    chunk_num += 1
    print(f"   Processing chunk {chunk_num}...", end=" ")
    
    processed = process_chunk(chunk)
    if processed is not None:
        all_features.append(processed)
        total_rows += len(processed)
        default_count += processed['default_flag'].sum()
        print(f" ✅ {len(processed):,} rows (default rate: {processed['default_flag'].mean()*100:.1f}%)")
    else:
        print(f" ⚠️ No valid rows")
    
    # Clear memory
    del chunk
    gc.collect()

print(f"\n✅ Total valid rows: {total_rows:,}")
print(f"   Total defaults: {default_count:,}")
print(f"   Overall default rate: {default_count/total_rows*100:.2f}%")

# ============================================
# COMBINE ALL CHUNKS
# ============================================
print("\n🔗 Combining all chunks...")
full_df = pd.concat(all_features, ignore_index=True)
print(f"   Combined dataset: {len(full_df):,} rows")

# ============================================
# SPLIT DATA
# ============================================
print("\n✂️ Splitting train/test data...")

# Use last 200k rows for test (time-based split - more realistic)
test_size = min(SAMPLE_FOR_TEST, int(len(full_df) * 0.1))
X_test = full_df.tail(test_size).drop('default_flag', axis=1)
y_test = full_df.tail(test_size)['default_flag']

X_train = full_df.head(len(full_df) - test_size).drop('default_flag', axis=1)
y_train = full_df.head(len(full_df) - test_size)['default_flag']

print(f"   Training: {len(X_train):,} rows")
print(f"   Test: {len(X_test):,} rows")
print(f"   Train default rate: {y_train.mean()*100:.2f}%")
print(f"   Test default rate: {y_test.mean()*100:.2f}%")

# ============================================
# TRAIN XGBOOST MODEL
# ============================================
print("\n🎯 Training XGBoost model on real data...")
print("   (This will take 15-30 minutes)")

train_start = time.time()

# Calculate scale_pos_weight for imbalanced data
scale_pos_weight = len(y_train[y_train==0]) / len(y_train[y_train==1])

model = XGBClassifier(
    n_estimators=150,
    max_depth=6,
    learning_rate=0.1,
    random_state=42,
    scale_pos_weight=scale_pos_weight,
    use_label_encoder=False,
    eval_metric='logloss',
    n_jobs=-1,
    tree_method='hist'
)

print("   Training in progress...")
model.fit(X_train, y_train, verbose=False)

train_time = time.time() - train_start
print(f"   Training completed in {train_time/60:.1f} minutes")

# ============================================
# EVALUATE
# ============================================
print("\n📊 Evaluating model...")

y_pred = model.predict(X_test)
y_pred_proba = model.predict_proba(X_test)[:, 1]

print("\n" + "=" * 70)
print("🎯 MODEL PERFORMANCE ON REAL LENDING CLUB DATA")
print("=" * 70)
print(f"📈 Accuracy:  {accuracy_score(y_test, y_pred)*100:.2f}%")
print(f"📈 ROC-AUC:   {roc_auc_score(y_test, y_pred_proba):.4f}")
print(f"📈 Precision: {precision_score(y_test, y_pred):.4f}")
print(f"📈 Recall:    {recall_score(y_test, y_pred):.4f}")

# Feature importance
print("\n📊 TOP 10 FEATURE IMPORTANCE:")
importance_df = pd.DataFrame({
    'feature': X_train.columns,
    'importance': model.feature_importances_
}).sort_values('importance', ascending=False)

for i, row in importance_df.head(10).iterrows():
    bar = "█" * int(row['importance'] * 50)
    print(f"   {row['feature']:<25} {bar} {row['importance']*100:.1f}%")

# ============================================
# SAVE MODEL
# ============================================
print("\n💾 Saving model for production...")

os.makedirs('models', exist_ok=True)

# Save model
joblib.dump(model, 'models/lendingclub_full_xgboost.pkl')

# Save feature columns
feature_columns = X_train.columns.tolist()
joblib.dump(feature_columns, 'models/feature_columns.pkl')

# Save model info
model_info = {
    'training_rows': len(X_train),
    'test_rows': len(X_test),
    'default_rate': float(y_train.mean()),
    'roc_auc': float(roc_auc_score(y_test, y_pred_proba)),
    'accuracy': float(accuracy_score(y_test, y_pred)),
    'feature_importance': importance_df.to_dict()
}
joblib.dump(model_info, 'models/model_info.pkl')

print("   ✅ Model saved to: models/lendingclub_full_xgboost.pkl")
print("   ✅ Feature columns saved to: models/feature_columns.pkl")
print("   ✅ Model info saved to: models/model_info.pkl")

# ============================================
# SUMMARY
# ============================================
total_time = time.time() - start_time

print("\n" + "=" * 70)
print("✅ TRAINING COMPLETE!")
print("=" * 70)
print(f"⏱️  Total time: {total_time/60:.1f} minutes")
print(f"📊 Training data: {len(X_train):,} rows")
print(f"🎯 ROC-AUC Score: {roc_auc_score(y_test, y_pred_proba):.4f}")
print("\n🚀 Your model is now ready for production!")
print("   Update your API to use: models/lendingclub_full_xgboost.pkl")
