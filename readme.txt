mysql 설치 mysql connect 설치 환경 변수 편집. docker desktop 설치 wsl 다운

프로젝트의 k8s폴더의 각각 secret 폴더 deploymet 폴더의

kubectl apply -f mysql mysql-mysql-secret.yaml

kubectl apply -f mysql mysql-deployment.yaml

MySQL 파드와 연결하기 위해 포트 포워딩

kubectl port-forward service/mysql 3306:3306

터미널에

\web-project 위치에서

.\myenv\Scripts\activate 명령어로 가상환경 구성.

올리고자 하는 서비스만큼 터미널 추가 .\myenv\Scripts\activate 입력.

서비스 폴더 위치에서 pip install -r .\requirements.txt 입력.

ex.)python .\api_gateway.py

파이썬으로 py 실행.

    'login': os.getenv('LOGIN_SERVICE_URL', 'http://localhost:5006'),
    'course': os.getenv('COURSE_SERVICE_URL', 'http://localhost:5001'),
    'festival': os.getenv('FESTIVAL_SERVICE_URL', 'http://localhost:5002'),
    'notice': os.getenv('NOTICE_SERVICE_URL', 'http://localhost:5004'),
    'main': os.getenv('MAIN_SERVICE_URL', 'http://localhost:5003')

각 서비스의 url.

로그인으로 접근하여 회원가입을 하고 로그인.

