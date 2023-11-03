from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()


class Restaurant(models.Model):
    # OPEN API
    sgg = models.CharField(max_length=50) # 시군구명
    sgg_code = models.CharField(max_length=205, null=True, blank=True) # 시군구 코드
    name = models.CharField(max_length=100) # 상호명
    start_date = models.CharField(max_length=100, null=True, blank=True) # 영업시작일
    business_state = models.CharField(max_length=100, null=True, blank=True) # 영업상태
    closed_date = models.CharField(max_length=100, null=True, blank=True) # 영업정지일
    local_area = models.CharField(max_length=100, null=True, blank=True) # 소재지면적
    water_facility = models.CharField(max_length=100, null=True, blank=True) # 급수시설구분명
    male_employee_cnt = models.CharField(max_length=100, null=True, blank=True) # 남성종업원수
    year = models.CharField(max_length=100, null=True, blank=True) # 연수
    multi_used = models.CharField(max_length=100, null=True, blank=True) # 다중이용업소구분
    grade_sep = models.CharField(max_length=100, null=True, blank=True) # 등급 구분명
    total_area = models.CharField(max_length=100, null=True, blank=True) # 총시설구분명
    female_employee_cnt = models.CharField(max_length=100, null=True, blank=True) #여성종업원수
    buisiness_site = models.CharField(max_length=100, null=True, blank=True) # 영업장 주변구분명
    sanitarity = models.CharField(max_length=100, null=True, blank=True) # 위생업종명
    food_category = models.CharField(max_length=100, null=True, blank=True) # 위생업태명
    employee_cnt = models.CharField(max_length=100, null=True, blank=True) # 총 종업원수
    address_lotno = models.CharField(max_length=200) # 지번주소
    address_roadnm = models.CharField(max_length=200) # 도로명주소
    zip_code = models.CharField(max_length=100, null=True, blank=True) # 우편번호
    longitude = models.CharField(max_length=100) # 경도
    latitude = models.CharField(max_length=100) # 위도
    
    name_address = models.CharField(max_length=255, unique=True) # name + address_roadnm
    score = models.FloatField(default=0, validators=[MinValueValidator(0.0), MaxValueValidator(5.0)])# 평가점수
    
    def save(self, *args, **kwagrs):
        if self.name_address:
            self.name_address = self.name + self.address_roadnm
        
        return super(Restaurant, self).save(*args, **kwagrs)
    
    def get_unique_field(self):
        return self.name_address
        

class Rate(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    score = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(5)])
    content = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

