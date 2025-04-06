import os
import sys
from dotenv import load_dotenv
from twilio.rest import Client
import time

# 환경변수 로드
load_dotenv()

# Twilio 설정
account_sid = os.getenv('TWILIO_ACCOUNT_SID')
auth_token = os.getenv('TWILIO_AUTH_TOKEN')
twilio_phone_number = os.getenv('TWILIO_PHONE_NUMBER')

def test_dtmf_playback(phone_number, dtmf_url=None):
    """
    DTMF 오디오 파일이 전화에서 제대로 재생되는지 테스트
    """
    # DTMF URL 설정
    if not dtmf_url:
        dtmf_url = "https://raw.githubusercontent.com/Twilio-org/sound-sets/master/touch-tones/key4.mp3"
    
    # Twilio 클라이언트 초기화
    client = None
    if account_sid and auth_token:
        try:
            client = Client(account_sid, auth_token)
            print(f"Twilio 클라이언트 초기화 성공!")
        except Exception as e:
            print(f"Twilio 클라이언트 초기화 실패: {e}")
            sys.exit(1)
    else:
        print("Twilio 인증 정보가 없습니다. .env 파일을 확인하세요.")
        sys.exit(1)
    
    print(f"\n===== DTMF 오디오 재생 테스트 =====")
    print(f"대상 전화번호: {phone_number}")
    print(f"DTMF 오디오 URL: {dtmf_url}")
    
    # TwiML 생성 - 오디오 파일 반복 재생
    twiml = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="woman" language="ko-KR">안녕하세요, DTMF 오디오 재생 테스트를 시작합니다.</Say>
    <Pause length="1"/>
    
    <Say voice="woman" language="ko-KR">이제 DTMF 4번 오디오 파일을 재생합니다.</Say>
    <Pause length="1"/>
    
    <!-- DTMF 오디오 파일 재생 (5번 반복) -->
    <Say voice="woman" language="ko-KR">1번째 재생</Say>
    <Play>{0}</Play>
    <Pause length="1"/>
    
    <Say voice="woman" language="ko-KR">2번째 재생</Say>
    <Play>{0}</Play>
    <Pause length="1"/>
    
    <Say voice="woman" language="ko-KR">3번째 재생, 볼륨 주의</Say>
    <Play>{0}</Play>
    <Play>{0}</Play>
    <Play>{0}</Play>
    <Pause length="1"/>
    
    <Say voice="woman" language="ko-KR">이어서 Twilio의 기본 DTMF 4번 톤을 재생합니다.</Say>
    <Play digits="4"/>
    <Pause length="1"/>
    <Play digits="4"/>
    <Pause length="1"/>
    <Play digits="444"/>
    
    <Say voice="woman" language="ko-KR">테스트가 완료되었습니다. 감사합니다.</Say>
</Response>""".format(dtmf_url)
    
    try:
        # 전화 걸기
        call = client.calls.create(
            to=phone_number,
            from_=twilio_phone_number,
            twiml=twiml,
            timeout=60
        )
        
        print(f"통화 시작: SID={call.sid}")
        
        # 통화 상태 모니터링
        print("통화 진행 상황 확인 중...")
        for i in range(12):  # 1분 동안 5초마다 확인
            time.sleep(5)
            
            call_status = client.calls(call.sid).fetch()
            status = call_status.status
            duration = call_status.duration
            
            print(f"\r상태: {status}, 통화 시간: {duration}초", end="")
            
            if status in ["completed", "failed", "busy", "no-answer"]:
                break
        
        # 최종 결과
        final_call = client.calls(call.sid).fetch()
        print(f"\n\n통화 결과:")
        print(f"  상태: {final_call.status}")
        print(f"  통화 시간: {final_call.duration}초")
        
    except Exception as e:
        print(f"\n오류 발생: {e}")
    
    print("\n===== 테스트 종료 =====")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        phone_number = sys.argv[1]
        dtmf_url = sys.argv[2] if len(sys.argv) > 2 else None
        test_dtmf_playback(phone_number, dtmf_url)
    else:
        print("사용법: python test_dtmf_playback.py [전화번호] [DTMF_오디오_URL]")
        print("예시: python test_dtmf_playback.py +821033650654")
        print("      python test_dtmf_playback.py +821033650654 http://example.com/dtmf4.wav")
        sys.exit(1) 