import os
import json
import pandas as pd
from google import genai
from google.genai import types
from pydantic import BaseModel
from dotenv import load_dotenv

# 讀取 .env 檔案中的環境變數
load_dotenv()

# 定義輸出的資料結構
class CompetitionContent(BaseModel):
    question_number: int
    question: str
    answer: str

def get_analyzed_links(csv_filename):
    """讀取已經分析過的 YouTube 連結（包含本地 CSV 與 Hugging Face 基準）"""
    analyzed_links = set()
    
    # 1. 從本地已有的結果檔案讀取
    if os.path.exists(csv_filename):
        try:
            # 讀取現有檔案，不假設有 header
            df = pd.read_csv(csv_filename, header=None)
            # 根據新的格式，youtube_link 可能在第 1 欄 (舊格式) 或 第 3 欄 (新格式)
            # 我們檢查所有欄位，只要網址出現在裡面就視為已處理
            for col in df.columns:
                analyzed_links.update(df[col].astype(str).unique())
        except Exception:
            pass
            
    # 2. 從 Hugging Face 基準檔讀取
    if os.path.exists("processed_links.txt"):
        try:
            with open("processed_links.txt", "r") as f:
                for line in f:
                    analyzed_links.add(line.strip())
        except Exception:
            pass
            
    return analyzed_links

def analyze_video_competition(video_info, youtube_index, csv_filename="competition_results.csv"):
    """
    使用 Gemini 2.5 Flash 分析影片並格式化為指定的欄位格式。
    video_info 包含: date, title, url, id
    """
    youtube_link = video_info['url']
    
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("錯誤：請先在 .env 檔案中設定 GEMINI_API_KEY")
        return

    client = genai.Client(api_key=api_key)
    model = "gemini-2.5-flash"

    prompt = """
    請根據畫面中的內容，擷取比賽題目與正確答案，並以 JSON 格式輸出。

    JSON 結構規範如下：
    - 僅包含 3 個欄位：question_number(題目編號), question（題目）與 answer（答案）。
    - 每筆資料為一組題目與答案。
    - 若答案中含有代號（如「A:」「B:」等），請移除代號，僅保留純文字答案。

    文字格式要求：
    1. 所有標點符號須使用全形符號，不得出現 '[', ']', '{', '}' 等符號。
    2. 英文和數字須使用半形字元。
    3. 中文與英文之間須保留一個空格。
    4. question 與 answer 欄位內容僅可包含繁體中文與英文。

    請僅輸出 JSON，不要加入任何解釋、註解或額外文字。
    """

    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part(file_data=types.FileData(file_uri=youtube_link)),
                types.Part.from_text(text=prompt),
            ],
        ),
    ]

    generate_content_config = types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=list[CompetitionContent],
    )

    print(f"正在分析新影片：{video_info['title'][:20]}... (Index: {youtube_index})")
    
    try:
        response = client.models.generate_content(
            model=model,
            contents=contents,
            config=generate_content_config,
        )
        
        data = json.loads(response.text)
        if not data:
            print("影片中未找到資料。")
            return

        # 格式化資料：date, title, youtube_link, youtube_id, question_number, question, answer, conversation
        formatted_data = []
        for item in data:
            conv = [
                {"from": "human", "value": item['question']},
                {"from": "gpt", "value": item['answer']}
            ]
            formatted_data.append({
                'date': video_info['date'],
                'title': video_info['title'],
                'youtube_link': youtube_link,
                'youtube_id': video_info['id'],
                'question_number': item['question_number'],
                'question': item['question'],
                'answer': item['answer'],
                'conversation': json.dumps(conv, ensure_ascii=False)
            })

        df = pd.DataFrame(formatted_data)
        
        # 指定欄位順序
        cols = ['date', 'title', 'youtube_link', 'youtube_id', 'question_number', 'question', 'answer', 'conversation']
        df = df[cols]

        if os.path.exists(csv_filename):
            df.to_csv(csv_filename, mode='a', header=False, index=False, encoding='utf-8-sig')
        else:
            # 第一次建立時，我們加上 Header
            df.to_csv(csv_filename, mode='w', header=True, index=False, encoding='utf-8-sig')

        print(f"成功處理影片 Index {youtube_index}")

    except Exception as e:
        print(f"分析失敗: {e}")

if __name__ == "__main__":
    if os.path.exists("latest_videos.csv"):
        df_videos = pd.read_csv("latest_videos.csv")
        analyzed = get_analyzed_links("competition_results.csv")
        
        print(f"總影片清單數: {len(df_videos)}")
        
        # 逐一處理未分析過的影片
        for idx, row in df_videos.iterrows():
            youtube_index = idx + 1
            video_info = {
                'date': row['date'],
                'title': row['title'],
                'url': row['url'],
                'id': row['id']
            }
            if video_info['url'] not in analyzed:
                analyze_video_competition(video_info, youtube_index)
            # else:
            #     print(f"跳過已存在影片: {video_info['url']}")
    else:
        print("未找到影片清單。")
