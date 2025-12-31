# YouTube 知識競賽資料擷取工具

這是一個自動化工具，用於從 YouTube 播放清單（例如《百變智多星》）中擷取比賽題目與答案，並將其格式化為對話式 AI 訓練用的數據集，最後同步至 Hugging Face。

## 流程架構

1. **同步基準**：從 Hugging Face 下載已處理過的影片網址，避免重複分析。
2. **抓取清單**：讀取 YouTube 播放清單，整理出影片的日期、標題與連結。
3. **Gemini 分析**：使用 Gemini 2.5 Flash 模型，針對「新出現」的影片內容進行視覺分析，擷取 JSON 格式的題庫。
4. **數據推送**：合併新舊資料，並推送到 Hugging Face 數據集。

## 快速開始

### 1. 環境設定
建立 `.env` 檔案並填入您的 API Keys：
```text
GEMINI_API_KEY=您的_Google_AI_API_KEY
HF_TOKEN=您的_Hugging_Face_Write_Token
```

### 2. 安裝套件
```bash
make setup
```

### 3. 執行完整流程
```bash
make sync     # 同步現有資料庫基準
make fetch    # 抓取 YouTube 最新影片
make analyze  # 執行分析 (會花費較長時間)
make push     # 上傳成果
```

## 檔案說明
- `fetch_youtube.py`: 負責與 YouTube 互動，抓取影片元數據。
- `analyze_competition.py`: 核心分析程式，呼叫 Gemini 並處理資料去重。
- `push_to_hf.py`: 數據集上傳工具。
- `latest_videos.csv`: 暫存的影片清單。
- `competition_results.csv`: 本地產生的分析結果。

## 數據格式
產出的 CSV 包含以下欄位：
`date, title, youtube_link, youtube_id, question_number, question, answer, conversation`
