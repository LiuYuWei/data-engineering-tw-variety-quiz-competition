import os
import argparse
import pandas as pd
from datasets import load_dataset, Dataset, concatenate_datasets
from dotenv import load_dotenv

load_dotenv()

def push_new_data_to_hf(local_csv="competition_results.csv", repo_id="Simon-Liu/tw-variety-quiz-competition", mode="append"):
    if not os.path.exists(local_csv):
        print(f"錯誤：找不到本地結果檔案 {local_csv}")
        return

    # 1. 讀取本地資料
    print(f"正在讀取本地資料 {local_csv}...")
    df_local = pd.read_csv(local_csv)
    if df_local.empty:
        print("本地資料為空，停止操作。")
        return

    ds_local = Dataset.from_pandas(df_local)
    if '__index_level_0__' in ds_local.column_names:
        ds_local = ds_local.remove_columns(['__index_level_0__'])

    final_dataset = None

    if mode == "append":
        # 2. 下載 HF 現有的資料集並合併
        print(f"正在下載現有數據集 {repo_id} 並進行合併 (Append 模式)...")
        try:
            ds_old = load_dataset(repo_id, split='train')
            final_dataset = concatenate_datasets([ds_old, ds_local])
            print(f"合併完成。總筆數: {len(final_dataset)}")
        except Exception as e:
            print(f"無法取得現有數據集，將改以 Overwrite 模式建立新數據集。錯誤原因: {e}")
            final_dataset = ds_local
    else:
        # Overwrite 模式：只使用本地資料
        print(f"正在使用 Overwrite 模式 (僅上傳本地資料)...")
        final_dataset = ds_local

    # 4. 推送到 Hugging Face
    token = os.environ.get("HF_TOKEN")
    print(f"正在推送到 Hugging Face (Repo: {repo_id})...")
    try:
        final_dataset.push_to_hub(repo_id, token=token)
        print(f"🎉 成功以 {mode} 模式更新 Hugging Face 資料集！")
    except Exception as e:
        print(f"推送失敗：{e}")
        print("請確保您已在 .env 中設定 HF_TOKEN 或執行 huggingface-cli login")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="將資料推送到 Hugging Face 數據集")
    parser.add_argument("--mode", choices=["append", "overwrite"], default="append", 
                        help="模式：append (附加到現有資料，預設) 或 overwrite (取代所有資料)")
    parser.add_argument("--csv", default="competition_results.csv", help="要上傳的本地 CSV 檔案路徑")
    
    args = parser.parse_args()
    
    push_new_data_to_hf(local_csv=args.csv, mode=args.mode)