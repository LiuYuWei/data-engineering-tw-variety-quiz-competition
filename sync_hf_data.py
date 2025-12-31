from datasets import load_dataset
import pandas as pd
import os

def download_huggingface_data(repo_id="Simon-Liu/tw-variety-quiz-competition"):
    print(f"正在從 Hugging Face 下載數據集 {repo_id}...")
    try:
        dataset = load_dataset(repo_id)
        # 假設資料在 'train' 分片中
        df = dataset['train'].to_pandas()
        
        # 提取唯一的影片連結作為基準
        existing_links = set(df['youtube_link'].unique())
        print(f"下載完成。現有數據集包含 {len(df)} 筆題目，涉及 {len(existing_links)} 部影片。")
        
        # 存成一個簡單的基準檔
        with open("processed_links.txt", "w") as f:
            for link in existing_links:
                f.write(f"{link}\n")
        
        return existing_links
    except Exception as e:
        print(f"下載失敗: {e}")
        return set()

if __name__ == "__main__":
    download_huggingface_data()

