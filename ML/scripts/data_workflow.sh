#!/bin/bash

# Description:
# This script automates the data workflow for cryptocurrency orderbook and ticks data.
# The workflow includes:
# 1. Creating directories for downloading, training, validation, and testing data.
# 2. Clearing existing files from the training, validation, and testing directories.
# 3. Downloading the latest available data from a remote server until failures occur.
# 4. Distributing the downloaded files into training, validation, and testing directories.
# 5. Logging all operations to a timestamped log file.

# Variables
BASE_URL_ORDERBOOK="https://observator-s3.s3.amazonaws.com/raw/orderbooks"
BASE_URL_TICKS="https://observator-s3.s3.amazonaws.com/raw/ticks"

DOWNLOAD_DIR_ORDERBOOK="/home/fairy/ml/crypto_maniac/orderbooks"
DOWNLOAD_DIR_TICKS="/home/fairy/ml/crypto_maniac/ticks"

TRAIN_DIR_ORDERBOOK="/home/fairy/ml/crypto_maniac/orderbooks/train"
VAL_DIR_ORDERBOOK="/home/fairy/ml/crypto_maniac/orderbooks/validation"
TEST_DIR_ORDERBOOK="/home/fairy/ml/crypto_maniac/orderbooks/test"

TRAIN_DIR_TICKS="/home/fairy/ml/crypto_maniac/ticks/train"
VAL_DIR_TICKS="/home/fairy/ml/crypto_maniac/ticks/validation"
TEST_DIR_TICKS="/home/fairy/ml/crypto_maniac/ticks/test"

LOG_DIR="/home/fairy/ml/crypto_maniac/logs"
DATE=$(date '+%Y-%m-%d_%H-%M-%S')
LOG_FILE="$LOG_DIR/workflow_$DATE.log"

# Create required directories
mkdir -p $DOWNLOAD_DIR_ORDERBOOK $DOWNLOAD_DIR_TICKS
mkdir -p $TRAIN_DIR_ORDERBOOK $VAL_DIR_ORDERBOOK $TEST_DIR_ORDERBOOK
mkdir -p $TRAIN_DIR_TICKS $VAL_DIR_TICKS $TEST_DIR_TICKS
mkdir -p $LOG_DIR

# Function: Clear all files in a directory
clear_directory() {
  TARGET_DIR=$1
  echo "Clearing files in directory: $TARGET_DIR" | tee -a $LOG_FILE
  find "$TARGET_DIR" -type f -exec rm -f {} \;
  if [ $? -eq 0 ]; then
    echo "Successfully cleared files in directory: $TARGET_DIR" | tee -a $LOG_FILE
  else
    echo "Failed to clear files in directory: $TARGET_DIR" | tee -a $LOG_FILE
    exit 1
  fi
}

# Function: Download data until failures occur
download_data_until_fail() {
  BASE_URL=$1
  DOWNLOAD_DIR=$2
  DATA_TYPE=$3
  
  echo "Downloading $DATA_TYPE data until failure..." | tee -a $LOG_FILE
  i=1
  while true; do
    FILE_DATE=$(date -d "-$i day" '+%Y%m%d')
    FILE_URL="$BASE_URL/$FILE_DATE.txt"
    OUTPUT_FILE="$DOWNLOAD_DIR/$FILE_DATE.txt"

    wget -O "$OUTPUT_FILE" "$FILE_URL" 2>> $LOG_FILE
    if [ $? -eq 0 ]; then
      echo "Downloaded $FILE_DATE.txt for $DATA_TYPE successfully." | tee -a $LOG_FILE
    else
      echo "Failed to download $FILE_DATE.txt for $DATA_TYPE. Stopping download." | tee -a $LOG_FILE
      break
    fi
    ((i++))
  done
}

# Function: Distribute data into train, validation, and test directories
distribute_data() {
  DOWNLOAD_DIR=$1
  TRAIN_DIR=$2
  VAL_DIR=$3
  TEST_DIR=$4
  DATA_TYPE=$5
  
  echo "Sorting and distributing $DATA_TYPE files..." | tee -a $LOG_FILE
  FILES=($(ls -1 $DOWNLOAD_DIR/*.txt | sort -r))  # Sort files in reverse order
  FILE_COUNT=${#FILES[@]}

  echo "Found $FILE_COUNT files for $DATA_TYPE distribution." | tee -a $LOG_FILE

  # Require at least one file for distribution
  if [ $FILE_COUNT -eq 0 ]; then
    echo "No files available for $DATA_TYPE distribution. Exiting." | tee -a $LOG_FILE
    exit 1
  fi

  # Latest file -> Test directory
  if [ $FILE_COUNT -ge 1 ]; then
    mv "${FILES[0]}" $TEST_DIR
    echo "Moved ${FILES[0]} to Test directory." | tee -a $LOG_FILE
  fi

  # Next file -> Validation directory
  if [ $FILE_COUNT -ge 2 ]; then
    mv "${FILES[1]}" $VAL_DIR
    echo "Moved ${FILES[1]} to Validation directory." | tee -a $LOG_FILE
  fi

  # Remaining files -> Train directory
  if [ $FILE_COUNT -ge 3 ]; then
    for ((i=2; i<$FILE_COUNT; i++)); do
      mv "${FILES[$i]}" $TRAIN_DIR
      echo "Moved ${FILES[$i]} to Train directory." | tee -a $LOG_FILE
    done
  fi

  echo "$DATA_TYPE files distributed successfully." | tee -a $LOG_FILE
}

# Clear existing files
clear_directory $TRAIN_DIR_ORDERBOOK
clear_directory $VAL_DIR_ORDERBOOK
clear_directory $TEST_DIR_ORDERBOOK
clear_directory $TRAIN_DIR_TICKS
clear_directory $VAL_DIR_TICKS
clear_directory $TEST_DIR_TICKS

# 1. Download and distribute orderbook data
download_data_until_fail $BASE_URL_ORDERBOOK $DOWNLOAD_DIR_ORDERBOOK "orderbook"
distribute_data $DOWNLOAD_DIR_ORDERBOOK $TRAIN_DIR_ORDERBOOK $VAL_DIR_ORDERBOOK $TEST_DIR_ORDERBOOK "orderbook"

# 2. Download and distribute ticks data
download_data_until_fail $BASE_URL_TICKS $DOWNLOAD_DIR_TICKS "ticks"
distribute_data $DOWNLOAD_DIR_TICKS $TRAIN_DIR_TICKS $VAL_DIR_TICKS $TEST_DIR_TICKS "ticks"

# Completion message
echo "Data workflow completed successfully." | tee -a $LOG_FILE
