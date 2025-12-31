.PHONY: setup sync fetch analyze push clean help

# 預設動作顯示幫助
help:
	@echo "YouTube 知識競賽資料集工具"
	@echo "用法:"
	@echo "  make setup    - 安裝必要 Python 套件"
	@echo "  make sync     - 從 Hugging Face 同步現有資料作為基準"
	@echo "  make fetch    - 抓取 YouTube 播放清單中的最新影片清單"
	@echo "  make analyze  - 呼叫 Gemini 分析新影片並產生 CSV"
	@echo "  make push     - 將新分析的資料合併並上推至 Hugging Face"
	@echo "  make clean    - 清除本地暫存的結果檔"

# 安裝套件
setup:
	pip install -r requirements.txt

# 同步 HF 資料
sync:
	python sync_hf_data.py

# 抓取播放清單
fetch:
	python fetch_youtube.py

# 執行分析
analyze:
	python analyze_competition.py

# 推送至 HF (可使用 make push MODE=overwrite)
MODE ?= append
push:
	python push_to_hf.py --mode $(MODE)

# 清除結果
clean:
	rm -f competition_results.csv processed_links.txt
