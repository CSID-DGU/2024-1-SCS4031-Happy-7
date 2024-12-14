# Description: Upbit API 호출을 위한 access, secret key 정보를 읽어오는 스크립트

class Info:

    upbit_access_key = ""
    upbit_secret_key = ""

    def __init__(self):
        # 키 파일에서 Upbit API 키 읽어오기
        with open("/home/ubuntu/project/data/key.txt", "r") as f:
            lines = f.readlines()

        # API 키 추출 및 변수에 할당
        self.upbit_access_key = lines[0].split(":")[1].strip()
        self.upbit_secret_key = lines[1].split(":")[1].strip()

    # Upbit 액세스 키 반환
    def get_upbit_access_key(self):
        return self.upbit_access_key

    # Upbit 시크릿 키 반환
    def get_upbit_secret_key(self):
        return self.upbit_secret_key
