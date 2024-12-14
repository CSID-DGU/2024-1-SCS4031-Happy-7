#!/bin/bash

# Description:
# This script automates the full workflow for processing cryptocurrency trading data, training a model,
# and saving the best model. It consists of the following steps:
# 1. Download and distribute data using `data_workflow.sh`.
# 2. Perform feature engineering using `feature_engineering.py`.
# 3. Reduce the processed data using `data_reduction.py`.
# 4. Train the model using `model.py` for the specified date.
# 5. Save the best model based on test losses using `save_best.py`.
# 6. Log all outputs and errors into a timestamped log file for easier debugging.

# Set the date to yesterday in YYYYMMDD format
DATE=$(date -d "yesterday" '+%Y%m%d')

# Set the log directory and file
LOG_DIR="/home/fairy/ml/crypto_maniac/logs"
LOG_FILE="$LOG_DIR/full_workflow_$DATE.log"
mkdir -p $LOG_DIR

# Step 1: Data Download and Distribution
echo "Step 1: Running data_workflow.sh..." | tee -a $LOG_FILE
bash /home/fairy/ml/crypto_maniac/scripts/data_workflow.sh >> $LOG_FILE 2>&1
if [ $? -ne 0 ]; then
    echo "Error during data_workflow.sh execution. Exiting." | tee -a $LOG_FILE
    exit 1
fi
echo "data_workflow.sh completed successfully." | tee -a $LOG_FILE

# Step 2: Feature Engineering
echo "Step 2: Running feature_engineering.py with date=$DATE..." | tee -a $LOG_FILE
python /home/fairy/ml/crypto_maniac/feature_engineering.py --date $DATE >> $LOG_FILE 2>&1
if [ $? -ne 0 ]; then
    echo "Error during feature_engineering.py execution. Exiting." | tee -a $LOG_FILE
    exit 1
fi
echo "feature_engineering.py completed successfully." | tee -a $LOG_FILE

# Step 3: Data Reduction
echo "Step 3: Running data_reduction.py with date=$DATE..." | tee -a $LOG_FILE
python /home/fairy/ml/crypto_maniac/data_reduction.py --date $DATE >> $LOG_FILE 2>&1
if [ $? -ne 0 ]; then
    echo "Error during data_reduction.py execution. Exiting." | tee -a $LOG_FILE
    exit 1
fi
echo "data_reduction.py completed successfully." | tee -a $LOG_FILE

# Step 4: Model Training
echo "Step 4: Running model.py with date=$DATE..." | tee -a $LOG_FILE
python /home/fairy/ml/crypto_maniac/model.py --date $DATE >> $LOG_FILE 2>&1
if [ $? -ne 0 ]; then
    echo "Error during model.py execution. Exiting." | tee -a $LOG_FILE
    exit 1
fi
echo "model.py completed successfully." | tee -a $LOG_FILE

# Step 5: Save Best Model
echo "Step 5: Running save_best.py with date=$DATE..." | tee -a $LOG_FILE
python /home/fairy/ml/crypto_maniac/save_best.py --date $DATE >> $LOG_FILE 2>&1
if [ $? -ne 0 ]; then
    echo "Error during save_best.py execution. Exiting." | tee -a $LOG_FILE
    exit 1
fi
echo "save_best.py completed successfully." | tee -a $LOG_FILE

# Completion message
echo "Full workflow completed successfully for date=$DATE." | tee -a $LOG_FILE
