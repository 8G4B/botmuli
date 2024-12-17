# JEE6

## 명령어 일람

1. 급식 관련

   > NIES API를 이용했어요.

   - `!급식` 을 통해 다음 급식을 확인할 수 있어요.

   - `!급식.아침` 을 통해 오늘의 조식을 확인할 수 있어요.

   - `!급식.점심` 을 통해 오늘의 중식을 확인할 수 있어요.

   - `!급식.저녁` 을 통해 오늘의 석식을 확인할 수 있어요.

2. 도박 관련

   > 진짜 돈을 걸지 않아요!

   - `!도박.노동` 을 통해 정직하게 돈을 벌 수 있어요.

   - `!도박.지갑` 을 통해 재산을 확인할 수 있어요.

   - `!도박.동전 [예측] [베팅]` 을 통해 동전 던지기를 할 수 있어요.

     예측이 맞으면 베팅한 돈의 $1.5$배~$3$배를 얻을 수 있고, 틀리면 베팅한 돈을 잃어요. **(확률: $\frac{1}{2}$)**

   - `!도박.주사위 [예측] [베팅]` 을 통해 주사위 던지기를 할 수 있어요.

     예측이 맞으면 베팅한 돈의 5배~10배를 얻을 수 있고, 틀리면 베팅한 돈을 잃어요. **(확률: $\frac{1}{6}$)**

   - `!도박.잭팟 [베팅]` 을 통해 잭팟을 할 수 있어요.

     당첨되면 다른 사람들이 베팅한 돈을 모두 얻을 수 있고, 틀리면 베팅한 돈을 잃어요. **(확률: $\frac{1}{20}$)**

3. 기타

   - `!시간` 을 통해 현재 서버 시간을 확인할 수 있어요.

   - `!정보` 를 통해 JEE6의 정보를 확인할 수 있어요.

   - `!질문 [내용]` 을 통해 질문을 할 수 있어요.

## 로컬에서 실행

1. 패키지 설치

   `requirements.txt` 파일을 통해 패키지를 설치해주세요.

   ```shell
   pip install -r requirements.txt
   ```

   설치되는 패키지는 다음과 같아요.

   - python-dotenv
   - discord.py
   - requests
   - openai

2. 환경변수 설정

   `.env` 파일을 만들어서 환경변수를 설정해주세요. 이 파일은 보안상의 이유로 `.gitignore`에 포함되어 있어서 github에 올라가지 않아요.

   ```shell
   echo "DISCORD_TOKEN=[여기에 토큰 입력]" >> .env
   echo "MEAL_API_KEY=[여기에 키 입력]" >> .env
   echo "GPT_API_KEY=[여기에 키 입력]" >> .env
   ```

3. 실행

   `app.py` 파일을 실행해주세요.

## 도커로 실행

---