# OBservator 실행 방법 (로컬호스트 버전)

## ❗주의❗

> **본 프로젝트는 프로젝트의 특성상, 그리고 서비스의 실제 상용화를 위해 고정 IP 및 도메인 상에서 진행하였으며, 로컬에서 임의로 실행할 경우 다음과 같은 제약사항이 있음을 알려드립니다.**

**1. 휘발성 데이터베이스**

* 하단의 지침에 따라 로컬호스트에서 프로젝트를 실행하게 되면, 기존의 AWS RDS에 반영구적으로 저장되는 형태가 아닌, Spring Framework에서 기본으로 제공하는 H2를 사용하게 됩니다.
* 이 H2는 프로그램 종료시 해당 내용이 자동으로 삭제되는 휘발성 데이터베이스이므로 회원가입부터 프로필 페이지에 입력 시 저장되는 API 키를 매번 입력해야 하는 번거로움이 발생합니다.

**2. 자동매매 기능 지원 불가**

* 기존 프로젝트는 서비스 서버의 고정 IP 및 이에 할당된 도메인을 기준으로 ML 서버와 통신을 하여 가상화폐의 실시간 시세 및 거래 명령을 송수신 받는 구조로 설계되었습니다.
* 하지만 로컬에서 실행하게 되면 사용자마다, 그리고 사용 위치에 따라 IP가 고정되지 않고, 매번 IP가 바뀌기 때문에 ML 서버에서도 매번 해당 IP 및 포트를 지정해주어야 합니다.

**3. 업비트 API 키 발급**
* 프로필 페이지의 "발급받는 방법" 버튼을 누르면, 사용자의 편의를 위해 서비스 서버의 IP를 입력해야 한다고 설명란에 공시가 되어있습니다.
* 하지만 로컬에서 실행할 경우 사용자의 현재 IP를 입력하여 API 키 발급을 해주어야 합니다.

## 실행 방법
> 업비트에 이미 회원가입이 되어있는 상태라고 가정합니다.
1. 본 레포지토리를 clone받습니다.
```
git clone https://github.com/CSID-DGU/2024-2-SCS4031-Happy-7.git OBservator
```

2. clone받은 폴더로 경로를 이동합니다.
```
cd OBservator
```

3. **Backend/observator/src/main/resources** 경로에 있는 **_application.properties_** 파일을 아래 내용을 복사하여 변경해줍니다.
```
# Application Name
spring.application.name=observator

# Reset cache
spring.thymeleaf.cache=false

# Security-related configuration
spring.security.user.name=admin
spring.security.user.password=admin

# OAuth2 configuration
spring.security.oauth2.client.registration.google.client-id=1052925642956-2550ukjm4u2qms261ukbl189hncdngfd.apps.googleusercontent.com
spring.security.oauth2.client.registration.google.client-secret=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
spring.security.oauth2.client.registration.google.redirect-uri=https://observator.co.kr/home

# SMTP configuration
spring.mail.host=smtp.gmail.com
spring.mail.port=587
spring.mail.username=observatoremail@gmail.com
spring.mail.password=cozrwsvjxrmghgtv
spring.mail.properties.mail.smtp.auth=true
spring.mail.properties.mail.smtp.starttls.enable=true

# H2 configuration
spring.datasource.url=jdbc:h2:mem:testdb
spring.datasource.driverClassName=org.h2.Driver
spring.datasource.username=sa
spring.datasource.password=password
spring.h2.console.enabled=true
spring.h2.console.path=/h2-console
```

4. **Backend/observator/src/main/java/com/happy/observator** 경로에 있는 **_ObseravtorApplication.java_** 파일도 아래와 같이 변경해줍니다.
```
package com.happy.observator;

import org.springframework.boot.CommandLineRunner;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.Bean;

import com.happy.observator.service.UserService;
import com.happy.observator.model.TradingOrderProcessor;

@SpringBootApplication
public class ObservatorApplication {

    public static void main(String[] args) {
        SpringApplication.run(ObservatorApplication.class, args);
    }

    @Bean
    CommandLineRunner run(UserService userService, TradingOrderProcessor tradingOrderProcessor) {
        return args -> {
        };
    }
}
```

5. 변경을 완료했다면 **_ObseravtorApplication.java_** 를 실행시켜준 후 로컬호스트의 8080포트로 접속합니다.

    [localhost 바로가기](http://localhost:8080)

6. 회원가입 및 로그인 후 프로필 페이지로 들어가서 "발급받는 방법" 버튼을 눌러 나오는 키 발급받기 링크로 접속합니다.
    
    [Open API 키 발급받기](https://upbit.com/mypage/open_api_management)

7. (중요) 프로필 페이지의 팝업창에 안내되어있는 순으로 키 발급을 진행하되, IP는 설명란에 명시된 서버의 IP가 아닌, 사용자 본인의 현재 IP를 입력하여 발급받아야 합니다.

    [내 IP 조회하기](https://www.findip.kr/)

8. 발급받은 Access key와 Secret key를 프로필 페이지에 입력 후 저장해줍니다.
* 단, Secret key의 경우 발급했을 당시에만 볼 수 있으므로, 개인의 안전한 저장소에 백업해두는 것을 추천합니다.
* 저장이 정상적으로 완료되면, 이메일 전송버튼 하단에 보유 자산에 대한 정보 표가 나타나게 됩니다.

9. 각 페이지 상단의 네비게이션 바를 이용하거나 홈 페이지로 돌아가 거래 페이지(대시보드)로 이동합니다.
* 웹소켓 연결의 특성상 경우에 따라 초반 몇 초동안 안정적인 연결을 위해 로딩 시간이 소요될 수 있습니다.
* 앞서 언급하였듯이 로컬호스트에서는 자동매매기능에 제한이 있어 이점 참고해주세요!

[👉***README로 돌아가기***](/README.md)