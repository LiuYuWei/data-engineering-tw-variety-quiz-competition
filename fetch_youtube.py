import yt_dlp
import csv
import os
import time
import random
from datetime import datetime

def fetch_latest_playlist_videos(playlist_url, count=700):
    """
    抓取整個播放清單的影片。
    """
    # 使用 ios/android 客戶端模擬行動裝置，較不容易被標記為機器人
    ydl_opts_flat = {
        'extract_flat': True,
        'quiet': True,
        'playlist_items': f'1-{count}',
        'extractor_args': {
            'youtube': {
                'player_client': ['ios', 'android', 'web']
            }
        }
    }
    
    # 關鍵：如果本地有 cookies.txt，就在第一階段讀取清單時也使用它
    if os.path.exists('cookies.txt'):
        print("偵測到 cookies.txt，將使用 Cookie 進行認證...")
        ydl_opts_flat['cookiefile'] = 'cookies.txt'

    videos = []
    with yt_dlp.YoutubeDL(ydl_opts_flat) as ydl:
        try:
            print(f"正在讀取播放清單資訊...")
            playlist_result = ydl.extract_info(playlist_url, download=False)
            if 'entries' in playlist_result:
                entries = playlist_result['entries']
                total_found = len(entries)
                print(f"找到共 {total_found} 個項目。開始逐一提取詳細資訊...")
                
                # 先讀取已有的 ID 以避免重複抓取詳細資訊，減少請求次數
                existing_ids = set()
                if os.path.exists('latest_videos.csv'):
                    try:
                        with open('latest_videos.csv', 'r', encoding='utf-8-sig') as f:
                            reader = csv.DictReader(f)
                            for row in reader:
                                existing_ids.add(row['id'])
                    except Exception:
                        pass

                for i, entry in enumerate(entries, 1):
                    if not entry:
                        continue
                    
                    video_id = entry.get('id')
                    if video_id in existing_ids:
                        continue

                    video_url = f"https://www.youtube.com/watch?v={video_id}"
                    
                    # 抓取詳細資訊
                    ydl_opts_video = {
                        'quiet': True,
                        'no_warnings': True,
                        'extractor_args': {
                            'youtube': {
                                'player_client': ['ios', 'android']
                            }
                        }
                    }
                    if os.path.exists('cookies.txt'):
                        ydl_opts_video['cookiefile'] = 'cookies.txt'
                    
                    try:
                        print(f"進度: {i}/{total_found} - 正在抓取: {video_id}")
                        with yt_dlp.YoutubeDL(ydl_opts_video) as ydl_v:
                            v_info = ydl_v.extract_info(video_url, download=False)
                            
                            title = v_info.get('title')
                            if not title or title in ['[Private video]', '[Deleted video]']:
                                continue

                            raw_date = v_info.get('upload_date')
                            formatted_date = ""
                            if raw_date:
                                try:
                                    formatted_date = datetime.strptime(raw_date, '%Y%m%d').strftime('%Y-%m-%d')
                                except:
                                    formatted_date = raw_date

                            videos.append({
                                'date': formatted_date,
                                'title': title,
                                'url': video_url,
                                'id': video_id,
                                'uploader': v_info.get('uploader'),
                            })
                            
                            # 隨機休息 1~3 秒模擬真人行為
                            time.sleep(random.uniform(1, 3))

                    except Exception as e:
                        print(f"抓取影片 {video_id} 失敗: {e}")
                        continue

        except Exception as e:
            print(f"播放清單抓取錯誤: {e}")
    
    return videos

def save_to_csv(videos, filename='latest_videos.csv'):
    if not videos:
        print("沒有找到新影片資料。")
        return

    existing_ids = set()
    file_exists = os.path.exists(filename)
    if file_exists:
        try:
            with open(filename, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    existing_ids.add(row['id'])
        except Exception as e:
            print(f"讀取舊檔案時發生錯誤: {e}")

    new_videos = [v for v in videos if v['id'] not in existing_ids]

    if not new_videos:
        print("所有影片均已在清單中。")
        return

    keys = videos[0].keys()
    mode = 'a' if file_exists else 'w'
    with open(filename, mode, newline='', encoding='utf-8-sig') as output_file:
        dict_writer = csv.DictWriter(output_file, fieldnames=keys)
        if not file_exists:
            dict_writer.writeheader()
        dict_writer.writerows(new_videos)
    
    print(f"成功將 {len(new_videos)} 筆新資料整理進 {filename}")

if __name__ == "__main__":
    PLAYLIST_URL = 'https://www.youtube.com/playlist?list=PLgPBJbB-rmNJjMuBzqgfmwQEYhSFu0AT3'
    # 設定為 700 或更大的數字來抓取完整清單
    FETCH_COUNT = 750 
    print(f"開始完整整理影片清單 (預計約 689 部)...")
    videos_list = fetch_latest_playlist_videos(PLAYLIST_URL, count=FETCH_COUNT)
    save_to_csv(videos_list)
