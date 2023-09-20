from flask import Flask, request

# 載入 json 標準函式庫，處理回傳的資料格式
import json
import os
from datetime import datetime
import pyodbc

# 載入 LINE Message API 相關函式庫
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

app = Flask(__name__)

# 全局變數
current_day = None
message_counter = 0

@app.route("/", methods=['POST'])
def linebot():
    global current_day
    global message_counter

    body = request.get_data(as_text=True)                    # 取得收到的訊息內容
    try:
        json_data = json.loads(body)                         # json 格式化訊息內容
        access_token = 'gdnhmbUovozyOzvdX1zxxWJTLBcFsijKXYI7nTe0pZHIPRpAY5EEvrNZkbGM/ubvykXhkba+s41g4RuPtUrx/to0YASQo5zr0VplwJBb00Eoi/Sebuj8g/AB7Y+Z+YeaCW4gyVEuo66xKnbGqQ5ZXwdB04t89/1O/w1cDnyilFU='
        secret = '289f626e24c847c3abfeeeacf1ac7d0b'
        line_bot_api = LineBotApi(access_token)              # 確認 token 是否正確
        handler = WebhookHandler(secret)                     # 確認 secret 是否正確
        signature = request.headers['X-Line-Signature']      # 加入回傳的 headers
        handler.handle(body, signature)                      # 綁定訊息回傳的相關資訊
        tk = json_data['events'][0]['replyToken']            # 取得回傳訊息的 Token
        type = json_data['events'][0]['message']['type']     # 取得 LINe 收到的訊息類型

        if type=='text':
            msg = json_data['events'][0]['message']['text']  # 取得 LINE 收到的文字訊息
            userId = json_data['events'][0]['source']['userId']  # 提取 userId

            # 檢查日期
            today_str = datetime.now().strftime('%Y%m%d')
            if current_day != today_str:
                current_day = today_str
                message_counter = 1
            else:
                message_counter += 1

            # 儲存訊息
            save_to_txt(f"{current_day}{message_counter:04}/{msg}", userId)
            
            # 回覆的訊息
            reply = f"{current_day}{message_counter:04}/{msg}"
            line_bot_api.reply_message(tk, TextSendMessage(reply))
        else:
            reply = '你傳的不是文字呦～'
            print(reply)
            line_bot_api.reply_message(tk,TextSendMessage(reply))# 回傳訊息
    except:
        print(body)                                          # 如果發生錯誤，印出收到的內容
    return 'OK'                                              # 驗證 Webhook 使用，不能省略


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


def execute_stored_procedure():
    conn = pyodbc.connect('DRIVER={SQL Server};SERVER=127.0.0.1;DATABASE=dbDATABASE;UID=sa;PWD=db111022')
    cursor = conn.cursor()
    cursor.execute("{CALL SP_LineMessage}")
    cursor.commit()
    cursor.close()
    conn.close()


    

if __name__ == "__main__":
    app.run(host='0.0.0.0')