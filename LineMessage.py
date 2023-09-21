#!C:\Users\cody8\Anaconda3\envs\LineMessage\Scripts\python.exe

# 載入 Flask 以及 request 處理 HTTP 請求
from flask import Flask, request

import json # 載入 json 標準函式庫，處理回傳的資料格式
import os # 操作系統路徑和文件
from datetime import datetime # 獲取和格式化當前日期
import pyodbc # 與資料庫進行連接

# 載入 LINE Message API 相關函式庫
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

# 創建 Flask 應用實例
app = Flask(__name__)

# 全局變數，用於追踪當前日期和訊息計數器
current_day = None
message_counter = 0

# 定義網頁路由和相應的函數
@app.route("/", methods=['POST'])
def linebot():
    global current_day
    global message_counter

    body = request.get_data(as_text=True)                    # 取得從 LINE 來的 POST 請求內容
    try:
        json_data = json.loads(body)                         # 解析收到的 JSON 數據

        # 定義 LINE API 的 token 和 secret
        access_token = 'your_access_token'
        secret = 'your_secret'

        # 初始化 LINE API 的接口
        line_bot_api = LineBotApi(access_token)              # 確認 token 是否正確
        handler = WebhookHandler(secret)                     # 確認 secret 是否正確

        # 驗證訊息來源是否有效
        signature = request.headers['X-Line-Signature']      # 加入回傳的 headers
        handler.handle(body, signature)                      # 綁定訊息回傳的相關資訊

        tk = json_data['events'][0]['replyToken']            # 取得回傳訊息的 Token
        type = json_data['events'][0]['message']['type']     # 取得 LINe 收到的訊息類型

        if type=='text':
            # 處理文字訊息
            msg = json_data['events'][0]['message']['text']  # 取得 LINE 收到的文字訊息
            userId = json_data['events'][0]['source']['userId']  # 提取 userId

            # 檢查日期並更新訊息計數器
            today_str = datetime.now().strftime('%Y%m%d')
            if current_day != today_str:
                current_day = today_str
                message_counter = 1
            else:
                message_counter += 1

            # 儲存訊息到文件中
            save_to_txt(f"{current_day}{message_counter:04}/{msg}", userId)
            
            # 回復用戶訊息
            reply = f"{current_day}{message_counter:04}/{msg}"
            line_bot_api.reply_message(tk, TextSendMessage(reply))
        else:
            reply = '你傳的不是文字呦～'
            print(reply)
            line_bot_api.reply_message(tk,TextSendMessage(reply))# 回傳訊息
    except Exception as e:
        # 如果出現異常，則打印異常和收到的訊息內容
        print("Exception:", e)
        print(body)                                          # 如果發生錯誤，印出收到的內容
    return 'OK'                                              # 驗證 Webhook 使用，不能省略

# 將收到的訊息儲存到文件中
def save_to_txt(message, userId):
    directory = "D:\\LineMessage"
    if not os.path.exists(directory):
        os.makedirs(directory)  # 如果目錄不存在，創建它

    today_str = datetime.now().strftime('%Y%m%d')
    filename_base = os.path.join(directory, today_str)
    
    all_messages_filename = os.path.join(directory, f"ALL_{today_str}.txt")
    with open(all_messages_filename, "a", encoding="utf-8") as all_messages_file:
        all_messages_file.write(message + "/" + userId + "\n")

    while os.path.exists(f"{filename_base}.txt"):
        counter += 1
    
    final_filename = f"{filename_base}.txt"
    
    with open(final_filename, "a", encoding="utf-8") as f:  # 使用 "a" 模式，避免每次都覆蓋檔案
        f.write(message + "/" + userId + "\n")  # 加上換行符，確保每次存儲的訊息在新的一行

    execute_stored_procedure()


# 執行Stored Procedure，用於進一步處理訊息
def execute_stored_procedure():
    conn = pyodbc.connect('DRIVER={SQL Server};SERVER=127.0.0.1;DATABASE=your_database;UID=your_id;PWD=your_pwd')
    cursor = conn.cursor()
    cursor.execute("{CALL SP_LineMessage}")
    cursor.commit()
    cursor.close()
    conn.close()


# 啟動 Flask 應用
if __name__ == "__main__":
    app.run(host='0.0.0.0')
