
  
# 날갱 Nalgang :calendar:

![workflow](https://github.com/3-24/nalgang/actions/workflows/python-app.yml/badge.svg) ![Uptime Robot ratio (7 days)](https://img.shields.io/uptimerobot/ratio/7/m789126293-ee416185a54d15d7b5111c93)

디스코드 채팅방에서 출석체크를 하고 점수를 관리하는 봇입니다.
<div align="center">
  
### :robot: 봇을 초대하려면 [여기](https://discord.com/api/oauth2/authorize?client_id=692341237302165554&permissions=67584&scope=bot)를 눌러주세요 :robot:
  
</div>

<div align="center">
<img src="https://imgur.com/lhnqgbQ.png" width="576px">
</div>

## 사용 가능한 명령어
- `!등록` : 현재 계정을 날갱 시스템에 등록합니다.
- `!날갱 (인사말)` : 날갱합니다.
- `!점수` : 내 점수를 확인합니다.
- `!점수 @멘션` : 멘션한 계정의 점수를 확인합니다.
- `!보내기 @멘션 점수`: 멘션한 계정으로 점수를 보냅니다.
- `!순위표` : 점수의 순위를 해당 채널에서 10위까지 출력합니다.
- `!도움` : 도움말을 확인합니다.

## 점수 시스템

매일 날갱을 한 순위에 따라 차등적으로 점수가 지급됩니다. 날짜갱신의 기준은 KST 오전 6시입니다.

- 당일 1위 - 10점
- 당일 2위 - 5점
- 당일 3위 - 3점
- 기본 - 1점

또한, 날갱을 연속으로 한 횟수에 따라 보너스 점수를 지급합니다.

- 7일(주전근) - 20점
- 30일(달전근) - 100점
- 365일(연전근) - 1500점

## API

채널에서 날갱 점수를 이용해 봇을 만들 수 있도록 필요한 기능들을 제공 중입니다.

- REST GET 리퀘스트로 특정 유저의 날갱 점수를 확인할 수 있습니다.
  ```
  http://api.youngseok.dev/nalgang?id={id_value}&guild={guild_value}
  ```
  예를 들면, id 값이 527850031273869312이고, guild 값이 691566159853649920인 유저의 날갱점수는 http://api.youngseok.dev/nalgang?id=527850031273869312&guild=691566159853649920 를 통해 반환합니다.

- 해당 채널에서 `NalgangAPIClient`라는 이름의 역할을 갖고 있다면, 다음 명령어를 추가적으로 사용할 수 있습니다.
  - `!점수추가 @멘션 (점수값)` : 해당 계정의 점수에 (점수값) 만큼 더해줍니다. 이 점수값은 음수가 될 수도 있으며, 음수일 경우 현재 점수가 부족하다면 이 명령은 거부됩니다.

## 서버 설정
봇을 본인의 컴퓨팅 서버에서 굴리고 싶다면 지금부터 나오는 안내를 읽으시길 바랍니다.

### 초기 설정
이 프로젝트는 Python 3 기반입니다.
```bash
pip3 install -r requirements.txt
```
하여 필요한 라이브러리를 설치합니다.
또한, `main.py`에는
```python
TOKEN = os.environ["nalgang_TOKEN"]
```
을 요구하는데, 디스코드 개발자 포털에서 제공하는 토큰을 `nalgang_TOKEN`이라는 이름의 환경변수로 저장하거나 저 코드를 고치면 됩니다.

### 실행
```bash
python3 main.py
```
데이터베이스를 상대경로로 저장하기 때문에 반드시 `main.py`가 있는 경로에서 실행해야 합니다.

### 고급설정
`config.py`의 값들을 변경하여 필요한 설정을 할 수 있습니다. 현재 들어있는 값들은 하나의 예시입니다.
- `point_by_rank`: `!날갱` 명령어를 입력한 순서에 따라 점수를 설정하는 배열입니다. 순위가 배열의 크기를 넘어가게 되면 배열의 마지막 원소에 해당하는 점수를 설정합니다. 
- `week_bonus`, `month_bonus`: 주전근, 달전근 추가 점수입니다.
- `timezone`: 사용할 세계 시간을 선택할 수 있습니다.

## 기여

Issue를 자유롭게 써주시면 됩니다. PR도 좋고요!
