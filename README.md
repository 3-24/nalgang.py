# 날갱

디스코드 채팅방에서 날짜갱신(출석체크)를 하고 점수를 관리하는 봇입니다.

## 사용 가능한 명령어
```
!날갱 : 날개
!날갱점수 : 내 점수 확인하기
!id : 나의 $id 확인하기
!날갱점수 $id : $id의 점수 확인하기
!점수보내기 $id $pt : $id를 가진 계정으로 $pt만큼의 점수 보내기
!날갱도움 : 도움말
```

## Setup
이 프로젝트는 Python3 기반입니다.
```bash
pip install -r requirements.txt
```
하여 필요한 라이브러리를 설치합니다.
또한, `main.py`에는
```python
TOKEN = os.environ["nalgang_TOKEN"]
```
을 요구하는데, 디스코드 개발자 포털에서 제공하는 토큰을 `nalgang_TOKEN`이라는 이름의 환경변수로 저장하거나 저 코드를 고치면 됩니다.
