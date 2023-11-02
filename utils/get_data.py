import time
import json
import requests
import environ
import xmltodict
from custom_logger import CustomLogger

logging = CustomLogger("DEBUG").get_logger()  # 테스트용 추후변경

env = environ.Env(DEBUG=(bool, True))

DB_FIELD = {   # DB 필드명 매핑용
  'SIGUN_NM'                    :       'sgg'                  
  ,'SIGUN_CD'                   :       'sgg_code'             
  ,'BIZPLC_NM'                  :       'name'                 
  ,'LICENSG_DE'                 :       'start_date'           
  ,'BSN_STATE_NM'               :       'business_state'       
  ,'CLSBIZ_DE'                  :       'closed_date'           
  ,'LOCPLC_AR'                  :       'local_area'       
  ,'GRAD_FACLT_DIV_NM'          :       'water_facility'    
  ,'MALE_ENFLPSN_CNT'           :       'male_employee_cnt'    
  ,'YY'                         :       'year'                 
  ,'MULTI_USE_BIZESTBL_YN'      :       'multi_used'           
  ,'GRAD_DIV_NM'                :       'grade_sep'            
  ,'TOT_FACLT_SCALE'            :       'total_area'           
  ,'FEMALE_ENFLPSN_CNT'         :       'female_employee_cnt'  
  ,'BSNSITE_CIRCUMFR_DIV_NM'    :       'buisiness_site'       
  ,'SANITTN_INDUTYPE_NM'        :       'sanitarity'           
  ,'SANITTN_BIZCOND_NM'         :       'food_category'        
  ,'TOT_EMPLY_CNT'              :       'employee_cnt'         
  ,'REFINE_LOTNO_ADDR'          :       'address_lotno'        
  ,'REFINE_ROADNM_ADDR'         :       'address_roadnm'       
  ,'REFINE_ZIP_CD'              :       'zip_code'             
  ,'REFINE_WGS84_LOGT'          :       'logitude'             
  ,'REFINE_WGS84_LAT'           :       'latitude'             
     
}

API_URL = {
    "LUNCH" : "https://openapi.gg.go.kr/Genrestrtlunch", # 깁밥
    "JPTFOOD" : "https://openapi.gg.go.kr/Genrestrtjpnfood", # 일식
    "CHIFOOD" : "https://openapi.gg.go.kr/Genrestrtchifood", # 중식
    "FASTFOOD" : "https://openapi.gg.go.kr/Genrestrtfastfood", # 패스트푸드
}

API_KEY= env('API_KEY') 


def get_restaurant(api_url, api_key, page_index:int, page_size:int)->dict:   # API 요청 
    '''
    :param api_url: 요청할 api 주소
    :param api_key: api 인증 키
    :param page_index: 페이지 번호
    :param page_size:  한 페이지에 담길 데이터의 양
    :return: dict 형식의 데이터 
    '''
    # API 요청을 위한 파라미터 설정
    params = {
        "Key": api_key,
        "pIndex" : page_index,
        "pSize": str(page_size),
    }

    # API 요청 보내기
    response = requests.get(api_url, params=params)


    if response.status_code == 200:
        root = response.text
        jsondata = json.dumps(xmltodict.parse(root), indent=4)
        
        dict = json.loads(jsondata)
        # logging.debug("dict: ", dict)
        

    return dict


def get_mapping_data(raw_data:dict, field:dict) -> dict:
    '''
    :param raw_data:  원본데이터
    :param field:  기존필드명, 변경할 필드명이 담긴 dict
    :return: 매핑된 데이터 
    '''
    result = {}
    if len(raw_data) != 1:
    # 기존 데이터의 키를 DB_FIELD 딕셔너리를 참조하여 교체
        for el in raw_data:
            for key, value in el.items():
                new_key = field[key]  
                result[new_key] = value
    else: 
        for key, value in raw_data.items():
            new_key = field[key]  
            result[new_key] = value

    return result


try:
    start_time1 = time.time()
    new_data = [] #결과 데이터
     
    for key in API_URL.keys(): # 모든 url에 요청
        start_time2 = time.time()
        unprocessed_data = -1 #전체 데이터 숫자 확인용
        #* 아래 두 변수는 필요에 따라 수정하여 사용합니다.
        page_index = 1  # 페이지 번호
        page_size = 1000  # 페이지에 담긴 정보 수 
        
        logging.info(f'----------{key} : {API_URL[key]} API 요청 시작----------')
        
        while unprocessed_data > 0 or unprocessed_data == -1:
            raw_data = get_restaurant(API_URL[key], API_KEY, page_index,  page_size)  #? API 요청
            try:
                status = raw_data[API_URL[key].split('/')[-1]]['head']['RESULT']['CODE'] #* CODE:INFO-000시 정상, 그 외 API 요청 실패처리 
                status_code = status.split('-')[-1]
                if status_code == '000' :   # 요청 성공
                    tot_cnt = int(raw_data[API_URL[key].split('/')[-1]]['head']['list_total_count'])
                    unprocessed_data =  tot_cnt
                    unprocessed_data -= page_size*page_index
                    unprocessed_data = max(unprocessed_data, 0)
                    logging.debug(f'남은 데이터 수 : {unprocessed_data}')
                    page_index += 1
                    new_data.append(get_mapping_data(raw_data[API_URL[key].split('/')[-1]]['row'], DB_FIELD)) #? 데이터 매핑
            except Exception as e:
                logging.error(f'API 요청 실패 --- {status}\n {e}')
                logging.info(f'time_check: {time.time()-start_time2}')
                # status = raw_data['RESULT']['CODE']   #* 에러코드 반환시 형식
                # status_code = status.split('-')[-1]
                # if status_code != '000' :
            # if page_index == 5:   #! 테스트용 제한
        logging.debug(f'new_data : {new_data}  리스트 길이 :  {len(new_data)}, 전체 데이터 수 : {tot_cnt}')
        logging.info(f'{key}_time_check: {time.time()-start_time2}')
        logging.debug('==========*****==========\n')
    logging.debug(f'new_data : {new_data}  리스트 길이 :  {len(new_data)}, 전체 데이터 수 : {tot_cnt}')
    logging.info(f'total_time_check: {time.time()-start_time1}')

except Exception as e:
        logging.info(f'{key}_time_check: {time.time()-start_time2}')
        logging.error(f'ERROR : {e}')    

