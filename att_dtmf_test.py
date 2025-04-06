import os
import sys
import time
from dotenv import load_dotenv
from twilio.rest import Client
import traceback

# 환경변수 로드
load_dotenv()

# Twilio 설정
account_sid = os.getenv('TWILIO_ACCOUNT_SID')
auth_token = os.getenv('TWILIO_AUTH_TOKEN')
twilio_phone_number = os.getenv('TWILIO_PHONE_NUMBER')

def test_att_with_dtmf_audio(target_phone=None, dtmf_url=None):
    """
    AT&T 국제 콜렉트콜 서비스를 직접 이용한 테스트 (DTMF 오디오 파일 사용)
    
    미국의 AT&T 국제 콜렉트콜 접속번호(1-800-822-8256)에 직접 전화를 걸고
    DTMF 4번 오디오 파일을 재생하여 콜렉트콜 서비스를 이용합니다.
    """
    # 기본 테스트 번호
    if not target_phone:
        target_phone = "01033650654"  # 기본 테스트 번호
    
    # 기본 DTMF URL (공개 접근 가능)
    if not dtmf_url:
        dtmf_url = "https://raw.githubusercontent.com/Twilio-org/sound-sets/master/touch-tones/key4.mp3"
    
    # + 기호가 있으면 제거
    if target_phone.startswith('+'):
        target_phone = target_phone[1:]
    
    # 82로 시작하면 010으로 변환
    if target_phone.startswith('82'):
        target_phone = '0' + target_phone[2:]
    
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
    
    print(f"\n===== AT&T 국제 콜렉트콜 DTMF 오디오 테스트: {target_phone} =====")
    
    try:
        # AT&T 국제 콜렉트콜 접속 번호
        att_collect_call = "+18008228256"  # 1-800-822-8256
        service_number = "1-800-822-8256"
        
        print(f"AT&T 국제 콜렉트콜 서비스({service_number})에 직접 연결합니다.")
        print(f"DTMF 4번 오디오 파일({dtmf_url})을 재생하여 콜렉트콜 메뉴를 선택합니다.")
        print(f"그런 다음 {target_phone} 번호로 연결을 시도합니다.")
        
        # 대상 번호 (0 제거) - 국제 형식에 맞게 조정
        target_dial = target_phone.replace('0', '', 1) if target_phone.startswith('0') else target_phone
        
        # TwiML 작성 (DTMF 오디오 파일 사용)
        twiml = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <!-- AT&T 국제 콜렉트콜 서비스 직접 연결 -->
    <Dial timeout="8">{0}</Dial>

    <Play>{1}</Play>
    <Pause length="2"/>
    <Play>{1}</Play> <!-- 한 번 더 재생 -->

    <!-- 번호 입력 안내 대기 -->
    <Pause length="10"/>
    
    <!-- 대상 전화번호 입력 (국가 코드 포함, #으로 종료) -->
    <Say voice="woman" language="en-US">Now entering the phone number with country code: 82 {2}</Say>
    <Pause length="5"/>
    <Play digits="82{2}#"/>
    <Pause length="15"/>
    
    <!-- 연결 대기 및 녹음 -->
    <Say voice="woman" language="en-US">Waiting for connection. Recording for analysis.</Say>
    <Record timeout="180" playBeep="false"/>
    <Say voice="woman" language="en-US">Test completed. Hanging up now.</Say>
</Response>""".format(att_collect_call, dtmf_url, target_dial)
        
        # 테스트용 일반 전화번호 (Twilio 검증된 번호)
        test_number = "+821033650654"  
        
        # 통화 시작
        call = client.calls.create(
            to=test_number,  # 테스트용 번호로 연결
            from_=twilio_phone_number,
            twiml=twiml,
            timeout=180  # 최대 3분
        )
        
        print(f"통화 시작: SID={call.sid}")
        print(f"전체 과정이 녹음됩니다.")
        
        # 통화 진행 상황 모니터링
        print("\n통화 진행 상황 확인 중...")
        for i in range(36):  # 3분(180초) 동안 5초마다 확인
            time.sleep(5)
            
            # 통화 상태 확인
            call_status = client.calls(call.sid).fetch()
            status = call_status.status
            duration = call_status.duration
            
            print(f"\r상태: {status}, 통화 시간: {duration}초", end="")
            
            # 통화가 완료되었으면 루프 종료
            if status in ["completed", "failed", "busy", "no-answer"]:
                break
        
        # 최종 통화 결과 확인
        final_call = client.calls(call.sid).fetch()
        print(f"\n\n통화 결과:")
        print(f"  상태: {final_call.status}")
        print(f"  시작 시간: {final_call.start_time}")
        print(f"  종료 시간: {final_call.end_time}")
        print(f"  통화 시간: {final_call.duration}초")
        
        # 녹음 파일 확인
        recordings = client.recordings.list(call_sid=call.sid)
        for recording in recordings:
            print(f"\n녹음 파일:")
            print(f"  SID: {recording.sid}")
            print(f"  길이: {recording.duration}초")
            print(f"  URL: https://api.twilio.com{recording.uri.replace('.json','')}")
        
        print("\n테스트가 완료되었습니다.")
        print("DTMF 오디오 파일이 AT&T IVR에서 인식되었는지 녹음 결과를 확인하세요.")
        
    except Exception as e:
        print(f"\n오류 발생: {e}")
        traceback.print_exc()
    
    print("\n===== 테스트 종료 =====")

if __name__ == "__main__":
    # 명령행 인수로 전화번호 받기
    if len(sys.argv) > 1:
        phone_number = sys.argv[1]
        # 선택적으로 DTMF URL 지정
        dtmf_url = sys.argv[2] if len(sys.argv) > 2 else None
        test_att_with_dtmf_audio(phone_number, dtmf_url)
    else:
        print("사용법: python att_dtmf_test.py [전화번호] [DTMF_오디오_URL]")
        print("예시: python att_dtmf_test.py 01033650654")
        print("      python att_dtmf_test.py 821033650654 http://example.com/dtmf4.wav")
        print("참고: 국가 코드(82)나 +기호는 있어도 되고 없어도 됩니다.")
        # 기본 번호로 테스트
        test_att_with_dtmf_audio() 