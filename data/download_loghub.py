import os
import urllib.request

def download_hdfs_log():
    # Target directory and file path
    target_dir = os.path.join("data", "raw_logs")
    os.makedirs(target_dir, exist_ok=True)
    target_file = os.path.join(target_dir, "HDFS_2k.log")
    
    # URL for HDFS 2k log sample from Loghub
    url = "https://raw.githubusercontent.com/logpai/loghub/master/HDFS/HDFS_2k.log"
    
    print(f"Attempting to download sample HDFS dataset (2k log entries) from Loghub...")
    print(f"Source: {url}")
    print(f"Destination: {target_file}")
    
    try:
        urllib.request.urlretrieve(url, target_file)
        print("Success! Sample HDFS log file downloaded successfully.")
        print(f"File size: {os.path.getsize(target_file)} bytes")
    except Exception as e:
        print("\n[ERROR] Failed to download the sample dataset automatically:")
        print(str(e))
        print("\nManual Instructions:")
        print("1. Open your browser and navigate to: https://github.com/logpai/loghub/blob/master/HDFS/HDFS_2k.log")
        print(f"2. Download the raw file and save it as 'HDFS_2k.log' in the folder '{target_dir}'.")

    print("\n--- Note on the Full HDFS Dataset ---")
    print("If you need the full HDFS dataset (1.58 GB containing 11,175,629 logs):")
    print("1. Download it from Zenodo: https://zenodo.org/record/3227177/files/HDFS_1.tar.gz")
    print("2. Extract the file and place the 'HDFS.log' in the 'data/raw_logs/' directory.")

if __name__ == "__main__":
    download_hdfs_log()
