# API Server

## 참고사항

- 우분투 16.04.6 LTS, 파이썬 3.8 환경에서 작동하는 것을 확인함. 다른 환경에서는 작동을 보장할 수 없음
- 다음 디렉토리 혹은 파일은 누락되어 있음. 이를 채워야 작동함
    - `assets/`
    - `model/keyext/*.pkl`
    - `model/keyext/*.pkl.back`
    - `model/keyext/ner/*.bin`
- 기본적으로 7002번 포트에서 동작함 (수정하고 싶다면 `config/config.py` 파일과 `run` 파일을 수정해야 함)

## How to Use

파이썬 가상환경을 만들어 그 안에서 작업하는 것을 추천함.

1. 필요 패키지 설치

```
$ pip install -r requirements.txt
```

2. 누락된 파일들을 채워 넣는다.

3. 다음 명령어로 실행한다.

```
$ ./run
```