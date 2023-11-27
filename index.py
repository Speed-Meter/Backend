import RPi.GPIO as GPIO
import time
from flask import Flask, request, jsonify
import sqlite3

v = 0  # 속도
vmax = 0  # 최대 속도
Sigpin = 8  # GPIO.BOARD 기준으로 라즈베리 파이 14번 핀에 해당하는 번호 (물리적>인 핀 번호에 맞게 변경)

GPIO.setmode(GPIO.BOARD)
GPIO.setup(Sigpin, GPIO.IN)

def measure_speed():
    global v
    T = 0  # 주기
    f = 0.0  # 주파수

    while GPIO.input(Sigpin):
        pass    
    while not GPIO.input(Sigpin):
        pass

    t1 = time.time()
    while GPIO.input(Sigpin):
                pass
    t2 = time.time()

    T = (t2 - t1) * 1e6
    f = 1 / T
    v = int((f * 1e6) / 44.0)

    return v  # 현재 속도 반환

try:
    while True:
        current_speed = measure_speed()
        print(f"현재 속도: {current_speed} km/h")
        time.sleep(0.5)

except KeyboardInterrupt:
    GPIO.cleanup()
    

#ID 저장
@app.route('/main', methods=['POST'])
def main():
    try:
        # POST 요청에서 'value' 필드의 값을 받음
        received_value = request.json.get('value')

        # 데이터베이스에 받은 값을 'Sports' 테이블의 'value_received' 열에 저장
        cursor.execute("INSERT INTO Sports (Id) VALUES (?)", (received_value,))
        conn.commit()

        return jsonify({"message": "ID값이 성공적으로 저장되었습니다.", "received_value": received_value})

    except Exception as e:
        return jsonify({"ID error": str(e)})


#속도 보냄 // 원래 값과 비교해서 
@app.route('/measure', methods=['GET'])
def measure():
    try:
        # 3초 동안의 최대 속도 측정
        max_speed = 0
        start_time = time.time()

        while time.time() - start_time < 3:
            current_speed = measure_speed()
            max_speed = max(max_speed, current_speed)
            time.sleep(0.1)  # 0.1초 간격으로 속도를 측정

        # 프론트엔드에서 보낸 Id와 스포츠 이름 가져오기
        user_id = request.args.get('Id')
        sports_name = request.args.get('sports')

        # 현재 스포츠 값 가져오기
        cursor.execute(f"SELECT {sports_name} FROM Sports WHERE Id=?", (user_id,))
        current_sports_value = cursor.fetchone()[0]

        # 만약 max_speed가 현재 스포츠 값보다 크다면 업데이트
        if max_speed > current_sports_value:
            cursor.execute(f"UPDATE Sports SET {sports_name} = ? WHERE Id=?", (max_speed, user_id))
            conn.commit()

        # 프론트엔드에 최대 속도를 응답으로 전송
        return jsonify({"max_speed": max_speed, "sports_name": sports_name, "user_id": user_id})

    except Exception as e:
        return jsonify({"MESR error": str(e)})

#rank
@app.route('/rank', methods=['GET'])
def rank():
    try:
        # 프론트엔드에서 보낸 종목 이름 가져오기
        sports_name = request.args.get('sports')

        # 속도가 높은 순서로 정렬된 결과 가져오기
        cursor.execute(f"SELECT Id, {sports_name} FROM Sports ORDER BY {sports_name} DESC")
        high_to_low_data = cursor.fetchall()

        # 프론트엔드에 속도가 높은 순서로 정렬된 데이터를 응답으로 전송
        return jsonify({
            "high_to_low_data": high_to_low_data,
            "sports_name": sports_name
        })

    except Exception as e:
        return jsonify({"Rank error": str(e)})
