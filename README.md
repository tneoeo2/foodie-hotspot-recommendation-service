# (2차 과제) foodie hotspot recommendation service based geography

## 목차
- [개요](#개요)
- [요구사항](#요구사항)
- [개발환경세팅](#개발환경세팅)
- [Installation & Run](#Installation)
- [ER-Diagram](#ER-Diagram)
- [API Documentation](#API)
- [프로젝트 진행 및 이슈 관리](#프로젝트)
- [구현과정(설계 및 의도)](#구현과정)
- [TIL 및 회고](#TIL)
- [Authors](#Authors)



## 개요
본 서비스는 공공데이터를 활용하여, 지역 음식점 목록을 자동으로 업데이트 하고 이를 활용합니다. 사용자 위치와 가까운 맛집을 추천하여 더 나은 다양한 음식 경험을 제공하고, 음식을 좋아하는 사람들 간의 소통과 공유를 촉진하려 합니다.

**(내 위치 또는 지정한 위치 기반으로 식당 및 해당 맛집의 메뉴 를 추천한다)**

### 유저히스토리
- 유저는 본 사이트에 들어와 회원가입 및 내 위치를 지정한다.
- **A. 내 위치 기반 맛집추천 = (`내 주변보기`)**
    - `도보` 기준 `1km` 이내의 맛집을 추천한다.
    - `교통수단` 기준 `5km` 이내의 맛집을 추천한다.
- **B. 지역명 기준 맛집추천(`특정 지역 보기`)**
    - 지정한 `지명(시군구)` 중심위치 기준 `10km` 이내의 맛집을 추천한다.
- (선택구현 **C. 점심 추천 서비스)**
    - 점심 추천 서비스 이용을 승락한 대상에게 점심시간 30분 전 가게 (또는 가게+메뉴)추천 을 해준다.
- A, B를 다양한 검색기준 (정렬, 필터링 등)으로 조회 가능하며 (`거리순`, `평점순` , `양식`, `중식`)
- 해당 맛집의 상세정보를 확인할 수 있다.


## 요구사항 및 구현사항

### 1. 유저
#### 사용자 회원가입(API)
- 본 서비스에서는 유저 고유 정보가 크게 사용되지 않아 간단히 구현합니다.
- `계정명` , `패스워드` 입력하여 회원가입

#### 사용자 로그인(API)
- `계정`, `비밀번호` 로 로그시 `JWT` 가 발급됩니다.
- 이후 모든 API 요청 Header 에 `JWT` 가 항시 포함되며, `JWT` 유효성을 검증합니다.

#### 사용자 설정 업데이트(API)
- 사용자의 위치 인 `위도`, `경도` 를 업데이트 합니다.
    - 시구군 API로 제공되는 위치 정보 이용
- `점심 추천 기능 사용 여부` 를 업데이트 합니다.
    - 하위 점심추천 기능을 받을지 설정합니다.

#### 사용자 정보 (API)
- `패스워드` 를 제외한 모든 사용자 정보를 반환합니다.
- 클라이언트에서 사용자 위, 경도 / 점심추천 기능 사용여부 를 사용하기 위해서 입니다.


### 2. 데이터 파이프라인
- API호출로 동작되는 기능이 아닌 스케쥴러를 통해 매 시간 실행되는 기능들입니다. 클래스, 함수 등 자유롭게 구조하세요.

#### 데이터 수집
- [공공데이터포털](https://www.data.go.kr/tcs/dss/selectDataSetList.do?dType=API&keyword=%EA%B2%BD%EA%B8%B0%EB%8F%84+%EC%9D%BC%EB%B0%98%EC%9D%8C%EC%8B%9D%EC%A0%90&operator=AND&detailKeyword=&publicDataPk=&recmSe=&detailText=&relatedKeyword=&commaNotInData=&commaAndData=&commaOrData=&must_not=&tabId=&dataSetCoreTf=&coreDataNm=&sort=_score&relRadio=&orgFullName=&orgFilter=&org=&orgSearch=&currentPage=1&perPage=10&brm=&instt=&svcType=&kwrdArray=&extsn=&coreDataNmArray=&pblonsipScopeCode=) 로 접속하여 연동할 Open API 규격을 확인합니다.
- 규격 및 예시
```xml
<row>
    <SIGUN_NM>수원시</SIGUN_NM>
    <SIGUN_CD/>
    <BIZPLC_NM>강스피자(since 2000)</BIZPLC_NM>
    <LICENSG_DE>20030107</LICENSG_DE>
    <BSN_STATE_NM>영업</BSN_STATE_NM>
    <CLSBIZ_DE/>
    <LOCPLC_AR/>
    <GRAD_FACLT_DIV_NM/>
    <MALE_ENFLPSN_CNT>0</MALE_ENFLPSN_CNT>
    <YY/>
    <MULTI_USE_BIZESTBL_YN/>
    <GRAD_DIV_NM/>
    <TOT_FACLT_SCALE/>
    <FEMALE_ENFLPSN_CNT>0</FEMALE_ENFLPSN_CNT>
    <BSNSITE_CIRCUMFR_DIV_NM/>
    <SANITTN_INDUTYPE_NM/>
    <SANITTN_BIZCOND_NM>패스트푸드</SANITTN_BIZCOND_NM>
    <TOT_EMPLY_CNT/>
    <REFINE_LOTNO_ADDR>경기도 수원시 장안구 송죽동 440-7 코너스톤빌 101호</REFINE_LOTNO_ADDR>
    <REFINE_ROADNM_ADDR>경기도 수원시 장안구 경수대로1007번길 10, 101호 (송죽동, 코너스톤빌)</REFINE_ROADNM_ADDR>
    <REFINE_ZIP_CD>16300</REFINE_ZIP_CD>
    <REFINE_WGS84_LOGT>127.0009971016</REFINE_WGS84_LOGT>
    <REFINE_WGS84_LAT>37.3058511104</REFINE_WGS84_LAT>
  </row>
  ```

- 개발자 키 발급 
    > .env 에 환경번수로 등록하여 사용
- 경기도_일반음식점(xx) 에 해당하는 OpenAPI 중 3가지 이상 수집에 사용합니다.(한식, 중식, 일식 등)
    > 본 서비스에서는 중식, 일식, 패스트푸드, 분식 API 사용

#### 데이터 전처리
- 데이터를 내부에서 사용될 형태로 변경합니다.
    - 변경이 불필요한 경우 그대로 사용하셔도 됩니다.
- 누락 되거나 이상값을 가질 경우 처리 방침을 정하고 구현합니다.
    - ex) 누락, null 등 이오면 어떤 값으로 채울지 등
    - **멘토: 제가 요구하는 어떤 케이스가 존재하지는 않습니다. 개발 중 데이터 이상값이 확인되면, API단이 아닌 이곳에서 전처리되어야 합니다.**

#### 데이터 저장
- 식당 마다 하나의 데이터가(레코드) 존재해야하며, 정보들은 업데이트 되어야 합니다.
- **유일키인** 사업자 코드가 없기에, 현재 사업자는 사업장마다 내야하는 규칙에 따라 `가게명` + `지번주소`로 유일하게 유지합니다.
    - 실제 데이터에는 중복될수도 있는 부분은 예외처리하여 무시했습니다.
    - **`어떻게던 하나의 상호가 중복 생성되지 않는다`**


#### 자동화
- 스케쥴러로 자주 사용되는 라이브러리
    ```markdown
    1. Django (파이썬 프레임워크):
    
    Django-Celery: 비동기 작업 처리를 위한 라이브러리로, 주기적인 작업과 예약 작업을 스케줄링할 수 있습니다.
    APScheduler: Python에서 주기적인 작업을 실행할 수 있게 해주는 라이브러리로, Django와 함께 사용할 수 있습니다.
    django-background-tasks: Django 프로젝트에서 주기적인 백그라운드 작업을 스케줄링하고 실행하는 데 도움을 주는 라이브러리입니다.
    ```
    
- `스케쥴러`를 설정하여 위 데이터 파이프라인 로직을 지정한 시간마다 실행시킵니다.
- 자유롭게 시간과 횟수 등을 설정하세요.
- 스케쥴러 > 매 6시에 뭘 한다,  6시 28분


#### 기타 - csv 업로드   
- 자주 변하지 않는 데이터 들은 파일업로드를 통해 구현합니다.
- 필드 (명칭 변경 가능)
    - `do-si` : 도, 시(특별시 등)
    - `sgg` : 시군구
    - `lat`: 위도
    - `lon`: 경도
- 서비스 시작시 로드 하여도 되고, 직접 함수 실행하여 업로드 해도 좋습니다.
> Location 테이블을 생성하여 시작시 로드하고, 스케쥴러를 이용하여 주기적으로 update하도록 설정했습니다.

### 3. REST API - 맛집조회
#### 시군구 목록 (API)

- 위 업로드한 모든 목록을 반환합니다.
- 추후 첨부 된 예시(야놀자) 처럼 `시도` , `시군구` 로 지역 조회 기능에 사용됩니다.

#### 맛집 (추가 필드 관리)
- `평점`
    - `double` 타입입니다.
    - 초기 값은 0.0 이며, 맛집이 받은 모든 평가의 평균입니다.
    - 하위 `맛집 평가 API` 에서 업데이트 됩니다.

#### 맛집 목록(API)

- 아래 `쿼리 파라미터`를 사용 가능합니다.

| query | 속성 | default(미입력 시 값) | 설명 |
| --- | --- | --- | --- |
| lat | string | 필수값 | 지구 y축 원점 기준 거리 |
| lon | string | 필수값 | 주기 x축 원점 기준 거리 |
| range | double | 필수값 | km 를 소숫점으로 나타냅니다. 0.5 = 500m / 1.0 = 1000km |
| 정렬기능 | string | 거리순 | 정렬기능 파라메터 구조는 자유롭게 구현하되, 위에서 계산된 요청 좌표와 식당 사이의 거리인 거리순 과 평점순을 지원해야합니다. |
| 기타 |  |  |  |

- `lat`, `lon` : 각각 위, 경도를 나타내며 필수값 입니다.(없을 시 code 400)
    - **`내 주변보기`** 또는 **`특정 지역 보기`**  기능을 하지만 이는 클라이언트에서 구현합니다.
        - 내 주변보기: 클라이언트에서 유저 lat, lon 을 파라메터로 넣어줌.
        - 시군구에서 선택한 항목의 위경도로 요청, 범위는 사용자 필수 입력.
- `range` Km 를 의미하며, 사용자 요청 주소(`lat`, `lon` 과의 거리를 의미합니다.)
    - 1.0 지정시 요청 `lat`, `lon` 에서 1km 이내의 가게만 노출 됩니다.
               
- 기타 `page`, `search` , `filter` 등은 선택사항입니다.
- 이해를 돕기위한
    > **Note!**
    
    내 주변보기, 특정 지역 보기 등은 유저가 사용하는 기능 명칭입니다. 
    이는 사용자가 클라이언트에서 클릭하는 값들에 따라 결정되기에,
    
    **API 에서는 API 요청된 `lat`, `lon`, `range` 를 토대로 조회된 내용만 반환하면 됩니다.**
    
    ex)
    내 주변 보기 - 도보 > 클라이언트가 `유저 정보` lat, lon 참조 및 range = 1.0(km) 파라메터를 던집니다.
    내 주변 보기 - 교통수단 > 클라이언트가 `선택된 시군구` lat, lon 참조 및 range = 5.0(km) 파라메터를 던집니다.
    특정 지역 보기 > 클라이언트가 `선택된 시군구` lat, lon 참조 및 range = 10.0(km) 파라메터를 던집니다.
    > 
    - 이는 결국 같은 동작을 하는 API 를 분리하여 관리하지 않고, 하나의 API 로 지원하여 자유도와 유지보수를 돕게 됩니다.

#### 맛집 상세정보(API)
- `맛집 모든필드` 를 포함합니다.
- `평가` 상세 리스트도 포함됩니다.
    - (`평가` 는 아래 참조.)
    - 모든 내역을 생성시간 역순(최신순) 으로 반환합니다.
    - 추가 요구사항 없습니다.


### 4. REST API - 평가

#### 평가 (모델링)
- 점수 : 0~5점
- 내용 : 255자이내

#### 맛집 평가 생성 (API)
- `유저` 가 특정 `맛집` 에 평가를 한다.
- `평가` 가 생성되면, 해당 맛집의 `평점` 을 업데이트 한다.
    - 해당 맛집 모든 평가 기록 조회 및 평균 계산하여 업데이트


### 5.대규모 트래픽 대비 캐싱
- Redis 를 연동합니다.

#### 시군구 목록 고도화(API)
- 모든 유저가 사용하지만, 긴시간 변동이 없는 성격을 지닌 데이터 이기에, 캐싱을 진행한다.
- 데이터 특성상 만료 기간은 없거나 일반 API 보다 길어도 됩니다.

#### 맛집 상세정보 고도화(API)
- 1단계
```plain text
1. 캐시에 저장되었는지 확인.
	1. 저장되어 있으면, 캐싱 데이터 반환한다.
	2. 저장되어 있지 않으면, DB를 통해 데이터 불러온다.
		2-1. 캐시에 저장 하고(600초 등 자율적으로 삭제 deadline 설정)
    2-3. 연산된 데이터를 반환한다.
```
- 2단계
```plain text
2-1. 단계에서 모든 데이터를 캐싱하는것이 아닌
 2-1-1. N개 이상의 평가가 존재하는(=인기있는)맛집만 캐싱
 2-1-2. "조회 수" 필드를 신설하여 관리하고, 조회수 N 이상만 캐싱
 2-1-3. 기타 맛집의 인기 또는 추천율이 높음을 증명하는 지표.(자유롭게 구상)

위 1~3 중 적용
```

### 6. Notification
#### Discord Webhook 을 활용한 점심 추천 서비스
- `유저` 중 `점심 추천 서비스` 사용여부를 체크한 유저에 한해, 점심시간 30분전 주변 맛집 리스트를 제공합니다.
- Webhook 을 이용하여 채널에 맞집 목록이 보여지도록 구현했습니다.
    - 점심시간을 12시로 정하고 30분 전인 11:30 분에 `유저` 모델의 `lat`, `lon` 기반으로
    - 500 미터 이내의 맛집을 카테고리별로 5개씩 제공한다.



## 개발환경세팅
가상환경: ![pyenv](https://img.shields.io/badge/pyenv-virtualenv-red)

언어 및 프레임워크: ![Python](https://img.shields.io/badge/python-3670A0?&logo=python&logoColor=ffdd54) ![DjangoREST](https://img.shields.io/badge/DJANGO-REST-ff1709?&logo=django&logoColor=white&color=ff1709&labelColor=gray)

데이터 베이스: ![MySQL](https://img.shields.io/badge/mysql-%2300f.svg?&logo=mysql&logoColor=white)
![Redis](https://img.shields.io/badge/redis-%2300f.svg?&logo=redis&logoColor=#DC382D)


## Installation & Run
### MySQL DB 세팅
- DATABASE생성
    - DB_NAME=foodie
    - DB_HOST=localhost
    - DB_PORT=3306
- USER생성
    - DB_USER=wanted
    - 유저에게 db권한주기

### 환경 세팅

## 2️⃣ 애플리케이션의 실행 방법 (엔드포인트 호출 방법 포함)
(전제) `python >= 3.10` 과 `mysql >= 8.0` 은 설치되어 있습니다.

#### 1. pyenv와 poetry를 이용해서 가상환경을 세팅해줍니다.
1. pip를 이용해서 pyenv와 poetry를 설치해줍니다.
```
pip install pyenv poetry
```
2. 가상환경을 만드는 명령어
```
pyenv virtualenv (python-version) <environment_name>
(EX. pyenv virtualenv 3.10 foodie)
```
3. (선택) 가상환경이 만들어졌는지 확인 명령어
```
pyenv versions
```
4. 가상환경 활성화 
```
pyenv activate <가상환경이름>
```
- windows os는 pyenv를 지원하지 않아 pyenv-win을 설치해야 합니다.
- 또는 windows 상에서 ubuntu를 사용할 수 있도록 해주는 wsl2를 이용하여 리눅스 상에 pyenv와 poetry를 설치 할 수 있습니다.

#### 2. `pyproject.toml` 을 통해 동일한 환경을 만들어줍니다.
```
poetry install
```
- 위의 명령어 입력시, 현 폴더 위치에 `poetry.lock` 파일 생성 or 업데이트

#### 3. `manage.py` 가 있는 위치에서 모델 migration을 해줍니다.
```
(pyenv run) python manage.py migrate
```
[참고]
- `python manage.py makemigrations` : 아직 데이터베이스에 적용되지 않음, 데이터베이스 스키마 변경사항을 기록하는 용
- `python manage.py migrate` : 위의 명령어에서 생성된 마이그레이션 파일들을 데이터베이스에 적용
(지금은 두번째 명령어만 작성하는게 맞습니다. 변경사항 없이 DB에 적용하기 위함이기 때문입니다.)

#### 4. `manage.py` 가 있는 위치에서 서버를 실행합니다.
```
(pyenv run) python manage.py runserver [port_num]
```
- 필요에 따라 위의 명령어 뒤에 포트번호를 붙입니다.

#### 5. End-point 호출 방법 
[참고] Django REST Framework는 admin 패널을 제공합니다. Postman을 사용하지 않아도 (header인증 제외) 웹 상으로 request/response가 가능합니다.


<br>

### 초기 설정 : 데이터
- Restaurant 테이블과 Location 테이블에 대한 더미 데이터는 csv 파일로 제공합니다.
- Contributer : 김수현, 유진수
- 위치 기준(Location) 데이터 : utils/location/location_data.csv
- 음식점(Restaurant) 더미 데이터 : utils/dummy_restaurant.csv
	- [참고]
    - Restaurant 데이터는 am 2:00 기준으로 업데이트됩니다. 
    - (utils 안에 넣어둔 Restaurant 데이터는 스케줄링이 이루어지기 전 api 테스트를 위한 데이터 입니다.)

<br>

## ER-Diagram
<img width="800" alt="ER-Diagram" src="https://user-images.githubusercontent.com/51039577/281304757-83cb5ed2-afed-4277-aae5-353e4cc4eaa9.png">

<br>

## API Documentation
<img width="800" alt="API-Documentation" src="https://user-images.githubusercontent.com/51039577/281304702-60ff0191-1b6d-4637-aff9-7db70d47af6e.png">

<!-- [TODO]
아래의 details 태그 안에 각자 구현한 부분 Request/Response 작성하기 -->

<details>
<summary>1. 회원가입 API - click</summary>

#### Request
```plain
  POST /api/auth/signup
```
- Auth Required: False

| Body Parameter | Type     | Description    |
| :------------- | :------- | :------------- |
| `username`     | `string` | **Required**.  |
| `password`     | `string` | **Required**.  |
```
EX)
{
    "username": "user1",
    "password": "devpassword1"
}
```

#### Response
```http
HTTP 201 Created
Allow: POST, OPTIONS
Content-Type: application/json
Vary: Accept

{
    "username": "user1"
}
```
</details>

<details>
<summary>2. JWT로그인 API - click</summary>

#### Request
```plain
  POST /api/auth/jwt-login
```
- Auth Required: False

| Body Parameter | Type     | Description    |
| :------------- | :------- | :------------- |
| `username`     | `string` | **Required**.  |
| `password`     | `string` | **Required**.  |

```
EX)
{
    "username": "user1",
    "password": "devpassword1"
}
```

#### Response
```http
HTTP 200 OK
Allow: POST, OPTIONS
Content-Type: application/json
Vary: Accept

{
    "username": "user1",
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpVXCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjk5NDM2NTA3LCJpYXQiOjE2OTk0MzI5MDcsImp0aSI6Ijc4Y2E1NzI3NDZkMDQzYzA4ZWZlNWM3NGNjMDFkNDNiIiwidXNlcl9pZCI6MX0.W-z5wAg0zNJWlaLA6mb0xEMPeEdOqenKeKrCsenWCNs"
}
```
</details>

<details>
<summary>3. 사용자정보 API - click</summary>

#### Request
```plain
  GET /api/account
```
- Auth Required: True

#### Rquest Header

| Parameter       | Type     | Description                             |
| :-------------- | :------- | :-------------------------------------- |
| `Authorization` | `string` | **Required**. 'Bearer eyJhbGciOiJIU...' |
| `Content-Type`  | `string` | **Required**. `application/json`        |

#### Response
```
{
    "latitude": "37.555536126421906",
    "longitude": "127.04743100959513",
    "is_recommend": true
}    
```
이거랑 똑같으면 복붙해도 될 것 같습니다.

</details>
<details>
<summary>4. 사용자 설정 (전체) 업데이트 - click</summary>

#### Request
```plain
  PUT /api/account
```
- Auth Required: True

| Body Parameter | Type     | Description                 |
| :------------- | :------- | :-------------------------- |
| `latitude`     | `string` | **Required**. 위도           |
| `longitude`    | `string` | **Required**. 경도           |
| `is_recommend` | `string` | **Required**. 웹훅 추천 여부   |

#### Request Header
| Parameter       | Type     | Description                             |
| :-------------- | :------- | :-------------------------------------- |
| `Authorization` | `string` | **Required**. 'Bearer eyJhbGciOiJIU...' |
| `Content-Type`  | `string` | **Required**. `application/json`        |



#### Response
```http

{
    "latitude": "36.555536126421906",
    "longitude": "114.04743100959513",
    "is_recommend": true
}

```
</details>
<details>
<summary>5. 사용자 설정 (일부분) 업데이트 - click</summary>

#### Request
```plain text
  PATCH /api/account
```
| Body Parameter | Type     | Description                 |
| :------------- | :------- | :-------------------------- |
| `latitude`     | `string` | **Required**. 위도           |
| `longitude`    | `string` | **Required**. 경도           |
| `is_recommend` | `string` | **Required**. 웹훅 추천 여부   |

#### Request Header
| Parameter       | Type     | Description                             |
| :-------------- | :------- | :-------------------------------------- |
| `Authorization` | `string` | **Required**. 'Bearer eyJhbGciOiJIU...' |
| `Content-Type`  | `string` | **Required**. `application/json`        |



#### Response
```
{
    "latitude": "36.555536126421906",
    "longitude": "114.04743100959513",
    "is_recommend": true
}
```
</details>

<details>
<summary>6. 시구군 목록 API - click</summary>

#### Request
```plain
  GET /api/account/locations
  GET /api/account/locations?do_si=서울&sgg=강서구
```
- Auth Required: True

| Query Parameter | Type     | Description                   |
| :-------------- | :------- | :---------------------------- |
| `do_si`         | `string` | 없으면 전체 목록               |
| `sgg`           | `string` | 없으면 전체 목록               |

```
EX)
http://127.0.0.1:8000/api/account/locations/?do_si=서울&sgg=강서구
```
#### Response
```http
HTTP 200 OK
Allow: GET, HEAD, OPTIONS
Content-Type: application/json
Vary: Accept

{
    "count": 1,
    "next": null,
    "previous": null,
    "results": [
        {
            "dosi": "서울",
            "sgg": "강서구",
            "longitude": "126.851675",
            "latitude": "37.54815556"
        }
    ]
}

```
</details>

<details>
<summary>7. 맛집 목록 조회 API - click</summary>

#### Request
```plain
  GET /api/restaurant?lat=37.4&lon=127.08
  GET /api/restaurant?lat=37.4&lon=127.08&radius=3.0&sorting=score
```
- Auth Required: True

#### Request Header
| Parameter       | Type     | Description                             |
| :-------------- | :------- | :-------------------------------------- |
| `Authorization` | `string` | **Required**. 'Bearer eyJhbGciOiJIU...' |
| `Content-Type`  | `string` | **Required**. `application/json`        |


#### Response
```http
HTTP 200 OK
Allow: GET, HEAD, OPTIONS
Content-Type: application/json
Vary: Accept

{
    "count": 199,
    "next": "http://127.0.0.1:8000/api/restaurant/?lat=37.4&lon=127.08&page=2",
    "previous": null,
    "results": [
        {
            "id": 103,
            "longitude": "127.3675277",
            "latitude": "38.03622017",
            "score": 0.0
        },
        {
            "id": 76,
            "longitude": "127.3699406",
            "latitude": "38.01851261",
            "score": 0.0
        },
        {
            "id": 186,
            "longitude": "127.2733923",
            "latitude": "38.09082909",
            "score": 0.0
        },
        {
            "id": 108,
            "longitude": "127.2707932",
            "latitude": "38.09052662",
            "score": 0.0
        },
        {
            "id": 114,
            "longitude": "127.2422105",
            "latitude": "38.00082601",
            "score": 0.0
        },
        {
            "id": 116,
            "longitude": "127.1782146",
            "latitude": "38.02067685",
            "score": 0.0
        },
        {
            "id": 30,
            "longitude": "127.2121505",
            "latitude": "37.90504782",
            "score": 0.0
        },
        {
            "id": 60,
            "longitude": "127.2028686",
            "latitude": "37.89932853",
            "score": 0.0
        },
        {
            "id": 170,
            "longitude": "127.0567061",
            "latitude": "37.91549459",
            "score": 0.0
        },
        {
            "id": 172,
            "longitude": "127.0567061",
            "latitude": "37.91549459",
            "score": 0.0
        },
        {
            "id": 93,
            "longitude": "127.0568232",
            "latitude": "37.8973641",
            "score": 0.0
        },
        {
            "id": 55,
            "longitude": "127.1412779",
            "latitude": "37.83108128",
            "score": 0.0
        },
        {
            "id": 102,
            "longitude": "127.0972596",
            "latitude": "37.84688314",
            "score": 0.0
        },
        {
            "id": 35,
            "longitude": "127.3542435",
            "latitude": "37.62459177",
            "score": 0.0
        },
        {
            "id": 66,
            "longitude": "127.0651398",
            "latitude": "37.83507895",
            "score": 0.0
        },
        {
            "id": 64,
            "longitude": "127.068746",
            "latitude": "37.8305406",
            "score": 0.0
        },
        {
            "id": 160,
            "longitude": "126.9742539",
            "latitude": "37.89660966",
            "score": 0.0
        },
        {
            "id": 178,
            "longitude": "126.9737509",
            "latitude": "37.89696793",
            "score": 0.0
        },
        {
            "id": 123,
            "longitude": "126.9736615",
            "latitude": "37.8967332",
            "score": 0.0
        },
        {
            "id": 41,
            "longitude": "127.4924777",
            "latitude": "37.4885134",
            "score": 0.0
        }
    ]
}
```
</details>

<details>
<summary>8. 맛집 상세정보 API - click</summary>

#### Request
```plain
  GET /api/restaurant/<int:id>
```
- Auth Required: True

#### Rquest Header
| Parameter       | Type     | Description                             |
| :-------------- | :------- | :-------------------------------------- |
| `Authorization` | `string` | **Required**. 'Bearer eyJhbGciOiJIU...' |
| `Content-Type`  | `string` | **Required**. `application/json`        |

#### Response
```http
    HTTP 201 Created
    Allow: POST, OPTIONS
    Content-Type: application/json
    Vary: Accept

    [
        {"id":2,
        "related_eval_ids":[[5,"맛있어요,","2023-11-04T00:17:27.201854"],[5,"맛있어요,","2023-11-03T23:57:45.216180"],[5,"맛있어요,","2023-11-03T23:53:00.197081"],[5,"맛있어요,","2023-11-03T23:48:00.736289"],[5,"맛있어요,","2023-11-03T23:45:17.670956"],[5,"맛있어요,","2023-11-03T23:40:02.202311"],[4,"맛있어요","2023-11-03T23:39:46.219627"],[4,"맛있어요","2023-11-03T23:39:38.475735"],[4,"맛있어요","2023-11-03T23:36:49.422382"],[4,"맛있어요","2023-11-03T23:33:20.444661"],[4,"맛있어요","2023-11-03T23:32:27.959105"],[2,"좋","2023-11-03T23:18:52.790050"],[2,"좋","2023-11-03T23:18:29.857828"],[2,"좋","2023-11-03T23:11:50.142872"],[2,"좋","2023-11-03T22:55:32.197530"]],
        "sgg":"용인시",
        "sgg_code":"",
        "name":"한솥도시락 오토허브점",
        "start_date":"20180409",
        "business_state":"영업",
        "closed_date":"",
        "local_area":"",
        "water_facility":"",
        "male_employee_cnt":"",
        "year":"",
        "multi_used":"",
        "grade_sep":"",
        "total_area":"",
        "female_employee_cnt":"",
        "buisiness_site":"",
        "sanitarity":"",
        "food_category":"김밥(도시락)",
        "employee_cnt":"",
        "address_lotno":"경기도 용인시 기흥구 영덕동 21-1 NS오토허브 2F19호, 2F20호",
        "address_roadnm":"경기도 용인시 기흥구 중부대로 242, NS오토허브 2F19호, 2F20호 (영덕동)",
        "zip_code":"17095",
        "longitude":"127.0931485",
        "latitude":"37.26942696",
        "name_address":"한솥도시락 오토허브점경기도 용인시 기흥구 중부대로 242, NS오토허브 2F19호, 2F20호 (영덕동)",
        "score":4.984283447265625}
    ]
```
</details>
<details>
<summary>9. 맛집 평가 API - click</summary>

#### Request
```plain
  POST /api/restaurant/<int:id>/evaluation
```
- Auth Required: True

#### Rquest Header
| Parameter       | Type     | Description                             |
| :-------------- | :------- | :-------------------------------------- |
| `Authorization` | `string` | **Required**. 'Bearer eyJhbGciOiJIU...' |
| `Content-Type`  | `string` | **Required**. `application/json`        |

#### Request Body
| Body Parameter | Type      | Description                   |
| :------------- | :-------- | :---------------------------- |
| `score`        | `integer` | **Required**. 0 ~ 5 정수      |
| `content`      | `string`  | **Required**. 255자 이내      |


#### Response
```http
    {"avg_score":3.9921417236328125,
    "eval_ids":[[3,"그냥 평범 하네","2023-11-08T18:18:57.157338"],[5,"맛있어요,","2023-11-04T00:17:27.201854"],[5,"맛있어요,","2023-11-03T23:57:45.216180"],[5,"맛있어요,","2023-11-03T23:53:00.197081"],[5,"맛있어요,","2023-11-03T23:48:00.736289"],[5,"맛있어요,","2023-11-03T23:45:17.670956"],[5,"맛있어요,","2023-11-03T23:40:02.202311"],[4,"맛있어요","2023-11-03T23:39:46.219627"],[4,"맛있어요","2023-11-03T23:39:38.475735"],[4,"맛있어요","2023-11-03T23:36:49.422382"],[4,"맛있어요","2023-11-03T23:33:20.444661"],[4,"맛있어요","2023-11-03T23:32:27.959105"],[2,"좋","2023-11-03T23:18:52.790050"],[2,"좋","2023-11-03T23:18:29.857828"],[2,"좋","2023-11-03T23:11:50.142872"],[2,"좋","2023-11-03T22:55:32.197530"]]}

```
</details>

<br>

## Webhook 기능 구현

- 서버에서 알림을 주는 기능 구현을 위해 `Webhook`을 사용했습니다.
- 개인 채널 혹은 팀 채널로 알림 메시지를 보낸다는 가정으로 정해진 시간에 **discord 채널**에 메시지를 전달합니다.
- 정해진 시간에 기능을 동작시키기 위해 스케쥴러(APScheduler)를 사용했습니다.
- 메시지는 추천 기능을 활성화한 유저들의 위치에서 가까운 음식점 정보를 포함합니다.
    - 유저가 알림받기(is_recommend=True)로 설정하면 정해진 시간에 디스코드를 이용해서 알림해줍니다.
    - 유저 이름을 포함시켜 유저를 구분하도록 했습니다.
- 결과화면
![결과화면](https://user-images.githubusercontent.com/120071955/281346269-9a073173-76e1-4e7c-aa12-693117e942d9.png)


## 프로젝트 진행 및 이슈 관리
- ![GitHub의 `ISSUE`](https://github.com/I-deul-of-zoo/foodie-hotspot-recommendation-service/issues)로 등록해서 관리했습니다.

<br>

## 구현과정(설계 및 의도)

1. 환경설정
    - 공통의 환경을 구축하는 것이 중요하다고 생각해서 아래와 같이 환경설정을 진행하였습니다.
        - window os: wsl2 + Ubuntu 22.04을 세팅  
        - linux(mac) os: brew & pip 사용
    - 아래와 같이 로컬의 개발환경을 세팅하는 것으로 결정했습니다.
        - Pyenv 로 python 버전 통일 3.11.6 및 가상환경 생성
        - Poetry 로 패키지 관리

2. RESTful API 설계
    - 리소스 간 계층 구조를 나타내는 URI로 구현했습니다.
    - 각 API의 Response에 맞는 HTTP status code를 적절하게 사용하였고, 발생할 수 있는 에러 상황에 대한 예외처리를 진행하였습니다.

3. Scheduler 설계
    - 주기적인 데이터 로드 및 전처리 또한 webhook을 구현 위해 APscheduler를 사용하고자 하였습니다.
    - `Celery`를 사용하기 위해서는 message Broker인 Redis와 함께 사용해야하는데 둘다 리눅스에서 정식 지원할 뿐만아니라, 해당 라이브러리의 환경을 구축하는데 있어 시간이 걸리는 반면, `APscheduler`는 `Celery`보다 구현이 쉬우며 python을 사용하여 DJango에 바로 구현할 수 있다는 장점이 있고 남은 기한이 얼마 남지않아 요구사항부터 충족하고자 `APscheduler`를 우선적으로 사용하는 것으로 결정했습니다.
    - 이후, 추가적으로 Docker 환경을 생성하여 Redis와 Celery-beat를 이용한 자동화를 구축 할 예정입니다.

4. Redis를 통해 Caching을 진행
    - 자주 불러오는 '시군구 목록' 및 '맛집 상세 정보'에 대해서 caching 하였습니다.
    - 데이터 일관성을 위해 데이터를 업데이트하거나 일정 시간 이후 조회할 때 캐시가 업데이트 되도록 하였습니다.
    - 데이터 병목 현상을 피하기 위해 TTL(Time to Live)을 사용하여 캐시가 만료되도록 하였습니다.
    - 로컬에서 캐싱이 잘 진행되는지 확인하고, test code로 검증하였습니다.

5. Docker로 Redis 서버 동작
    - redis 서버를 Docker 환경에서 동작하도록 구성해봤습니다.
    - redis를 안정적으로 운영하기 위한 volume 설정과 redis.conf를 생성하고 docker를 이용해 redis 이미지를 다운받고 container를 실행했습니다.
    - 편리한 실행 및 종료를위해 `redis_exec.sh`를 통해 컨테이너를 실행하고, `redis_delete.sh`를 통해 종료시킬 수 있습니다.
    - 로컬에 redis를 설치한 것과 동일하게 동작하는 것을 확인할 수 있었고, 단순 DB Table 조회 시 10배 정도의 시간 단축을 확인했습니다.
    - 레코드 1개를 불러오는 동작에 대한 성능을 비교하기 위해 시간을 측정해보았습니다.
        - 1행은 DB에서 불러오는 시간 : 0.039016 초
        - 2, 3, 4행은 cache에서 불러오는 시간 : 0.002002 초, 0.000980초, 0.001053초
        - 10배 이상 빠른 속도임을 확인할 수 있었습니다.
    - 결과화면<br>
    ![결과화면](https://user-images.githubusercontent.com/120071955/281397882-778dac69-699a-41ae-a0d4-b201b6814246.png)

<br>

## TIL 및 회고
- Discord로 모여 매일 9:00, 14:00 에 모여 진행상황과 공부한 것을 공유했습니다.
- TIL 노션 페이지 [링크](https://sprinkle-piccolo-9fc.notion.site/TIL-677e52f238c0442697a3e03cc6f3edd9?pvs=4)

## 일정 관리
- 요구사항 분석 이후 작업 가능한 최소 단위의 task로 업무를 나누었습니다.
- 각 task에 대한 우선순위를 설정하고, 노션의 Timeline 기능을 사용하여 주어진 기간 동안 필수 기능과 선택 기능을 모두 구현할 수 있도록 일정 관리를 진행하였습니다.
- 일정 관리 노션 페이지 [링크](https://sprinkle-piccolo-9fc.notion.site/a13c436918eb44c79b6834dbc8ae0977?pvs=4)


<br>

## Authors

|이름|github주소|
|---|---------|
|강석영|https://github.com/mathtkang|
|김수현|https://github.com/tneoeo2|
|오동혁|https://github.com/airhac|
|유진수|https://github.com/YuJinsoo|
