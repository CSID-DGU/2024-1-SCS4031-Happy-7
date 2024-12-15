# OBservator 🚀

**OBservator**에 오신 것을 환영합니다!  
이 서비스는 머신러닝 모델을 기반으로 가상화폐 가격 변동을 예측하고, 자동으로 거래를 실행합니다.  
**LSTM 신경망**을 활용하여 시장 데이터를 분석하고 실시간으로 유용한 매매 통찰을 제공합니다.

👉[**_서비스 바로가기_**](https://observator.co.kr/login) (2024년 12월 24일까지 임시 오픈 예정)

## 📜 **주요 기능**

### End-to-End 워크플로우

- **데이터 수집**: Upbit API를 통해 오더북(Orderbook) 및 거래(Ticks) 데이터를 자동으로 가져와 전처리.
- **특성 추출**: 가격 스프레드, 중간 가격, 오더북 불균형, 가격 변동성, 매수/매도 비율 등 핵심 특성 추출.
- **모델 학습**: 하이퍼파라미터 튜닝과 조기 종료를 적용하여 LSTM 모델을 학습.
- **자동 매매**: 모델의 예측 결과와 사용자가 설정한 임계값에 따라 실시간으로 BUY/SELL 명령 실행.

### 사용자 맞춤 기능

- **회원가입 및 로그인**: 사용자들은 웹사이트에서 간편하게 회원가입과 로그인을 할 수 있으며, Upbit API 키를 등록해 시스템과 연동 가능.
- **실시간 대시보드**: 웹사이트 대시보드를 통해 가상화폐의 실시간 정보(현재 가격, 호가창, 체결 정보 등)와 관련 뉴스를 한눈에 확인 가능.
- **임계값 설정**: 대시보드에서 사용자 지정 임계값을 설정해 자동 매매 전략을 세부적으로 조정 가능.
- **자동매매 제어**: 대시보드에서 **자동매매 시작/중지 버튼**을 통해 간단히 거래 실행 여부를 제어할 수 있음.
- **24시간 모델 업데이트**: 시스템은 매일 24시간마다 수집된 새로운 데이터를 기반으로 기존 모델을 재학습하며, 가장 성능이 우수한 모델로 자동 업데이트하여 실시간 예측 정확도를 지속적으로 향상시킴.

### 모듈화 및 확장 가능

- 각 구성 요소를 독립적으로 실행할 수 있도록 설계.
- 거래 매개변수, 데이터 입력, 모델 설정 등을 동적으로 구성 가능.

### 실시간 실행

- 지속적인 소켓 연결을 통해 실시간 데이터 스트림 처리.
- 효과적인 거래 전략을 위한 실시간 임계값 변경 지원.

### 로깅 및 디버깅

- 모든 스크립트에서의 상세 로깅으로 추적 및 디버깅 용이.
- 테스트 손실 및 성능 지표 저장으로 향후 분석 가능.

## 구현결과

### 1. 로그인 화면  

<img src="Doc/imgs/login_1.png" height=300> <img src="Doc/imgs/login_2.png" height=300>  

### 2. 회원가입 화면 & 이용약관 팝업  

<img src="Doc/imgs/signup_1.png" height=300>  <img src="Doc/imgs/signup_2.png" height=300>  

### 3. 홈 화면 & 네비게이션 바  

<img src="Doc/imgs/home.png" height=300>  

### 4. 프로필 화면 & Upbit API 발급방법 팝업

<img src="Doc/imgs/profile_1.png" height=300> <img src="Doc/imgs/profile_2.png" height=300> <img src="Doc/imgs/profile_3.png" height=300>  

### 5. 대시보드 화면

<img src="Doc/imgs/dashboard_1.png" height=300> <img src="Doc/imgs/dashboard_2.png" height=300>  

## 개발 환경

### OS

![windows](https://img.shields.io/badge/Windows-0078D6?style=for-the-badge&logo=windows&logoColor=white)![mac]( https://img.shields.io/badge/mac%20os-000000?style=for-the-badge&logo=apple&logoColor=white)![Ubuntu](https://img.shields.io/badge/Ubuntu-E95420?style=for-the-badge&logo=ubuntu&logoColor=white)

### Code Editor

![vsCode](https://img.shields.io/badge/Visual_Studio_Code-0078D4?style=for-the-badge&logo=visual%20studio%20code&logoColor=white)

### Collaboration Tool

![notion](https://img.shields.io/badge/Notion-000000?style=for-the-badge&logo=notion&logoColor=white)![google Cloud](https://img.shields.io/badge/Google_Cloud-4285F4?style=for-the-badge&logo=google-cloud&logoColor=white)![github](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)![slack](https://img.shields.io/badge/Slack-4A154B?style=for-the-badge&logo=slack&logoColor=white)![naver mybox](https://img.shields.io/badge/Naver%20Mybox-6079F6?style=for-the-badge&logo=naver&logoColor=white)

## 프로그래밍 언어 & 프레임워크

### FE

![html5](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white)![JavaScript](https://img.shields.io/badge/javascript-%23323330.svg?style=for-the-badge&logo=javascript&logoColor=%23F7DF1E)![css](https://img.shields.io/badge/CSS-239120?&style=for-the-badge&logo=css3&logoColor=white)

### BE

![java](https://img.shields.io/badge/Java-ED8B00?style=for-the-badge&logo=openjdk&logoColor=white)![python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)![Bash Script](https://img.shields.io/badge/bash_script-%23121011.svg?style=for-the-badge&logo=gnu-bash&logoColor=white)  
![Spring](https://img.shields.io/badge/spring-%236DB33F.svg?style=for-the-badge&logo=spring&logoColor=white)![Amazon EC2](https://img.shields.io/badge/Amazon%20EC2-FF9900?style=for-the-badge&logo=amazonec2&logoColor=white)![Amazone Route 53](https://img.shields.io/badge/Amazone%20Route%2053-8C4FFF?style=for-the-badge&logo=amazonroute53&logoColor=white)![Apache Maven](https://img.shields.io/badge/Apache%20Maven-C71A36?style=for-the-badge&logo=Apache%20Maven&logoColor=white)![Apache Freemarker](https://img.shields.io/badge/Apache%20Freemarker-326CAC?style=for-the-badge&logo=apachefreemarker&logoColor=white)  
![Amazon S3](https://img.shields.io/badge/Amazon%20S3-FF9900?style=for-the-badge&logo=amazons3&logoColor=white)![Amazon RDS](https://img.shields.io/badge/Amazon%20RDS-527FFF?style=for-the-badge&logo=amazonrds&logoColor=white)![MySQL](https://img.shields.io/badge/mysql-4479A1.svg?style=for-the-badge&logo=mysql&logoColor=white)  

### ML

![python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)![Bash Script](https://img.shields.io/badge/bash_script-%23121011.svg?style=for-the-badge&logo=gnu-bash&logoColor=white)  
![Anaconda](https://img.shields.io/badge/Anaconda-%2344A833.svg?style=for-the-badge&logo=anaconda&logoColor=white)![PyTorch](https://img.shields.io/badge/PyTorch-%23EE4C2C.svg?style=for-the-badge&logo=PyTorch&logoColor=white)![nVIDIA](https://img.shields.io/badge/cuda-000000.svg?style=for-the-badge&logo=nVIDIA&logoColor=green)![nVIDIA](https://img.shields.io/badge/cuDNN-000000.svg?style=for-the-badge&logo=nVIDIA&logoColor=green)

## 시스템 구성도

![SystemDiagram](./Doc/Diagrams/시스템구성도.png)

이 시스템 구성도는 **OBservator**의 전체 아키텍처를 나타냅니다. 시스템은 크게 **Client**, **AWS Cloud**, **WSL**, 그리고 **Upbit 거래소**로 구성됩니다.

### **_Client_**

- **회원가입 및 로그인**: 사용자들은 웹 또는 앱 클라이언트를 통해 계정을 생성하고 로그인할 수 있습니다.
- **실시간 가상화폐 정보 조회**: 대시보드에서 현재 가격, 호가창, 체결 정보 등 실시간 데이터를 확인할 수 있습니다.
- **가상화폐 자동거래 시작/중지**: 버튼 클릭만으로 자동 매매를 시작하거나 중지할 수 있습니다.
- **가상화폐 수동/예약 거래**: 원하는 가격과 시간에 맞춰 매매를 예약할 수 있습니다.
- **자산 정보 확인**: 사용자는 보유 자산, 거래 내역, 실시간 수익률 등을 확인할 수 있습니다.

---

### **_AWS Cloud (거래 서버)_**

- **거래 서버**:
  - **데이터 수집 및 전처리**: Upbit 거래소 API로부터 실시간 오더북과 체결 데이터를 수신하여 필요한 전처리를 수행합니다.
  - **데이터 저장**:
    - **데이터 DB(S3)**: 모델 학습 및 예측에 필요한 데이터(오더북, 체결 정보 등)를 저장합니다.
    - **사용자 DB(RDS)**: 사용자 정보, 예약 거래 정보, 설정된 임계값 등을 저장합니다.
  - **WSL 서버와 통신**:
    - 전처리된 데이터를 WSL의 머신러닝 서버로 실시간 전달합니다.
    - WSL 머신러닝 서버로부터 거래 명령과 예측값을 수신하여 Upbit 거래소로 전달합니다.

---

### **_WSL (ML 서버)_**

- **머신러닝 서버**:
  - AWS Cloud에서 전처리된 데이터를 수신하여 학습된 LSTM 모델을 통해 예측값을 생성합니다.
  - 예측값과 함께 생성된 거래 명령을 AWS Cloud의 거래 서버로 전송합니다.
- **모델 학습 및 업데이트**:
  - 데이터 DB(S3)에 저장된 데이터를 주기적으로 학습하여 모델 성능을 유지하고 개선합니다.
  - 24시간마다 새로운 데이터를 사용해 모델을 업데이트하며, 성능이 가장 좋은 모델을 실시간 예측에 사용합니다.

---

### **_Upbit 거래소_**

- **데이터 제공**: API를 통해 실시간 오더북 및 체결 정보를 AWS Cloud의 거래 서버에 제공합니다.
- **거래 실행**: AWS Cloud의 거래 서버로부터 수신된 매매 명령을 수행합니다.

## 기대효과

<img src="Doc/imgs/기대효과.png" height=300>

1. **투자 진입장벽 감소:** 복잡한 가상화폐 시장의 데이터를 분석하고 자동 매매 서비스를 제공하여 초보 투자자도 쉽게 접근할 수 있도록 지원합니다. 사용자 친화적인 대시보드와 간단한 설정만으로 투자 관리를 시작할 수 있습니다.

2. **낮은 투자 손실률:** 실시간 데이터 분석과 머신러닝 모델을 통해 투자 의사결정을 자동화함으로써 감정에 의존한 투자에서 벗어나 손실률을 줄이고 안정적인 수익률을 기대할 수 있습니다.

3. **자동화된 매매:** 사용자가 설정한 임계값에 따라 24시간 자동으로 매매를 수행하므로, 시장의 변동성을 놓치지 않고 항상 최적의 타이밍에 대응할 수 있습니다.

4. **확장성:** 다양한 가상화폐 시장 및 새로운 거래소와의 통합이 가능하도록 설계되었습니다. 또한, 정기적인 모델 업데이트를 통해 새로운 데이터와 시장 상황에 맞는 예측 성능을 유지합니다.  

## 프로젝트 산출물

| 분류 |  산출물  |
| :---: | :---: |
| 보고서 | [수행계획서](/Doc/Reports/수행계획서_S7_행복해조.pdf)🔹[중간보고서](Doc/1_2_OSSProj_01_버스태워조_수행계획발표자료%20.pdf)🔹[최종보고서](Doc/1_2_OSSProj_01_버스태워조_수행계획발표자료%20.pdf) |
| 발표자료 | [제안발표자료](/Doc/Presentation/제안발표_S7_행복해조.pdf)🔹[중간발표자료](/Doc/Presentation/중간발표_S7_행복해조.pdf)🔹[최종발표자료](/Doc/Presentation/최종발표_S7_행복해조.pdf)|
| 다이어그램 | [유스케이스](/Doc/useCaseDiagramExplain.md)🔹[시퀀스](/Doc/sequenceDiagramExplain.md)🔹[시스템블록](/Doc/systemBlockDiagramExplain.md)🔹[회의록](Doc/4_2_OSSProj_01_버스태워조_회의록.md) |

## 🤝 **Team&Members**

> 팀명: S7_행복해조

  | 성명 | 역할 |
  | :---: | :---: |
  | **진대한** | 👨🏻‍🏫멘토👨🏻‍🏫 |
  | **김민재** | 👑Machine Learning & 팀장👑 |
  | **이보성** | 📈Frontend📈 |
  | **권일준** | 🖥️Backend🖥️ |
  | **이승호** | 🌐Cloud Server & FE,BE보조🌐 |

## 라이선스

이 프로젝트는 MIT 라이선스에 따라 라이선스가 부여됩니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.
