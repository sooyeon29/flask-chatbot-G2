from flask import Flask, request, jsonify, send_from_directory, session
import openai
import sqlite3
import os
from datetime import datetime
import pytz

# Flask 앱 설정
app = Flask(__name__, static_folder=".", static_url_path="")
app.secret_key = os.urandom(24)
KST = pytz.timezone('Asia/Seoul')

# OpenAI API 키 설정
openai.api_key = os.getenv("OPENAI_API_KEY")

# 데이터베이스 초기화
def init_db():
    conn = sqlite3.connect('chatbot.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    dob TEXT,
                    gender TEXT,
                    start_time TEXT,
                    end_time TEXT,
                    chat_history TEXT,
                    status TEXT
                )''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    return send_from_directory(".", "index.html")

@app.route('/reset-session', methods=['POST'])
def reset_session():
    session.clear()
    return jsonify({"message": "새로운 사용자가 인식되었습니다."})

@app.route('/user-info', methods=['POST'])
def save_user_info():
    user_info = request.json
    session['user_info'] = user_info
    session['start_time'] = datetime.now(KST).strftime('%Y-%m-%d %H:%M:%S')
    session['chat_history'] = []

    # 챗봇 첫 메시지
    first_bot_message = f"안녕 {user_info['name']}~! 나는 사랑세포야. 오늘 사랑과 관련된 고민에 대해 이야기 나눠보자!"
    session['chat_history'].append({"user": None, "bot": first_bot_message})

    # 사용자 정보를 DB에 삽입
    conn = sqlite3.connect('chatbot.db')
    c = conn.cursor()
    # 중복 여부 확인
    c.execute("SELECT COUNT(*) FROM users WHERE name = ? AND start_time = ?",
              (user_info['name'], session['start_time']))
    if c.fetchone()[0] == 0:
        c.execute('''INSERT INTO users (name, dob, gender, start_time, chat_history, status)
                     VALUES (?, ?, ?, ?, ?, ?)''',
                  (user_info['name'], user_info['dob'], user_info['gender'], session['start_time'], '[]', 'incomplete'))
    conn.commit()
    conn.close()
    
    return jsonify({"message": "사용자 정보가 성공적으로 저장되었습니다."})

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_input = data.get("user_input", "")
    chat_history = session.get('chat_history', [])

    # 사용자의 첫 메시지 저장
    chat_history.append({"user": user_input, "bot": None})
    
    # GPT 호출을 통해 사랑세포 응답 생성
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",  # GPT-4o 모델 호출
            messages=[
                {
                    "role": "system",
                    "content": """
                    1. 이 챗봇은 사랑을 담당하는 세포인 사랑세포이다.
                    2. 사랑세포는 낙천적이고 긍정적인 성격을 가지고 있다.
                    3. 사랑세포는 항상 사랑에 대한 희망과 긍정을 잃지 않고 따뜻하고 다정한 어조로 말한다.
                    4. 사랑세포는 로맨틱한 이상을 추구하고 현실적인 문제보다 감정적인 위로에 집중한다.
                    5. 사랑세포는 부드럽고 귀여운 말투로 대화한다.
                    6. 사랑세포는 사용자가 전송하는 언어로 응답한다.
                    7. 사용자가 한국말로 하는 경우에는 반말로 대화를 하고 한국어가 아닌다른 언어를 하는 경우에는 친근한 어투로 이야기한다.
                    8. 사용자가 하는 말에 집중하여 이야기 흐름에 적절한 대답을 한다.
                    9. 이 챗봇은 사랑, 연애 관련 고민을 듣고 그에 따른 스트레스를 완화시키는데 도움을 주는 챗봇이다.
                    10. 사용자가 먼저 이야기하기 어려워 하는 경우에는 9번를 기억하고 이야기를 잘 이어나갈 수 있도록 대화를 이끌어 나간다.
                    """
                },
                {"role": "user", "content": user_input}
            ]
        )
        bot_reply = response['choices'][0]['message']['content']
    except Exception as e:
        bot_reply = "죄송해요, 오류가 발생했습니다."
    # except openai.error.OpenAIError as e:
    #     print(f"GPT API 호출 오류: {e}")
    #     bot_reply = "죄송해요, 요청을 처리하는 중 문제가 발생했습니다. 다시 시도해주세요."
    # except Exception as e:
    #     print(f"알 수 없는 오류: {e}")
    #     bot_reply = "죄송해요, 요청을 처리하는 중 문제가 발생했습니다. 다시 시도해주세요."

    # 응답 저장 및 반환
    chat_history.append({"user": user_input, "bot": bot_reply})
    session['chat_history'] = chat_history


    # 실시간 저장
    conn = sqlite3.connect('chatbot.db')
    c = conn.cursor()
    c.execute('UPDATE users SET chat_history = ? WHERE name = ? AND start_time = ?',
              (str(chat_history), session['user_info']['name'], session['start_time']))
    conn.commit()
    conn.close()
    
    return jsonify({"reply": bot_reply})

@app.route('/end-chat', methods=['POST'])
def end_chat():
    user_info = session.get('user_info', {})
    start_time = session.get('start_time')
    end_time = datetime.now(KST).strftime('%Y-%m-%d %H:%M:%S')
    chat_history = session.get('chat_history', [])

    # 진행 시간 계산 (분 단위)
    start_dt = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
    end_dt = datetime.now(KST)
    duration = (end_dt - start_dt).seconds // 60

    # 상태 결정: 대화 시간이 10분 이상이면 complete, 그렇지 않으면 incomplete
    status = 'complete' if duration >= 10 else 'incomplete'

    # 데이터베이스에 저장
    conn = sqlite3.connect('chatbot.db')
    c = conn.cursor()
    c.execute('''INSERT INTO users (name, dob, gender, start_time, end_time, chat_history, status)
                 VALUES (?, ?, ?, ?, ?, ?, ?)''',
              (user_info.get('name'), user_info.get('dob'), user_info.get('gender'),
               start_time, end_time, str(chat_history) if status == 'complete' else None, status))
    conn.commit()
    conn.close()

    session.clear()

    # 중간 종료 시와 정상 종료 시 다른 메시지 반환
    message = "안녕~! 다음에 또 이야기 하자!!" if status == 'complete' else "대화를 중간에 종료했어! 다음에 또 이야기하자!"
    return jsonify({"message": message})

@app.route('/complete-session', methods=['POST'])
def complete_session():
    user_info = session.get('user_info', {})
    start_time = session.get('start_time')

    if not user_info or not start_time:
        return jsonify({"error": "세션 정보가 없습니다."}), 400

    # 완료 시간 기록
    end_time = datetime.now(KST).strftime('%Y-%m-%d %H:%M:%S')

    # 완료 상태 업데이트
    conn = sqlite3.connect('chatbot.db')
    c = conn.cursor()
    c.execute('UPDATE users SET status = ?, end_time = ? WHERE name = ? AND start_time = ?',
              ('complete', end_time, user_info['name'], start_time))
    conn.commit()
    conn.close()

    return jsonify({"message": "대화 완료 상태가 저장되었습니다."})


@app.route('/view-data', methods=['GET'])
def view_data():
    conn = sqlite3.connect('chatbot.db')
    c = conn.cursor()
    c.execute("SELECT name, dob, gender, start_time, end_time, chat_history, status FROM users")
    users_data = c.fetchall()
    conn.close()

    html_content = """
    <html>
    <head>
        <title>Chat Data</title>
        <style>
            table { width: 100%; border-collapse: collapse; }
            th, td { border: 1px solid black; padding: 8px; text-align: left; }
            th { background-color: #f2f2f2; }
            td { word-wrap: break-word; white-space: pre-wrap; }
        </style>
    </head>
    <body>
        <h1>저장된 사용자 및 채팅 데이터</h1>
        <table>
            <tr>
                <th>이름</th>
                <th>생년월일</th>
                <th>성별</th>
                <th>시작 시간</th>
                <th>종료 시간</th>
                <th>채팅 내용</th>
                <th>상태</th>
            </tr>
    """

    for user in users_data:
        name, dob, gender, start_time, end_time, chat_history, status = user
        html_content += f"""
            <tr>
                <td>{name}</td>
                <td>{dob}</td>
                <td>{gender}</td>
                <td>{start_time}</td>
                <td>{end_time or ''}</td>
                <td>{chat_history}</td>
                <td>{status}</td>
            </tr>
        """

    html_content += """
        </table>
    </body>
    </html>
    """

    return html_content


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
