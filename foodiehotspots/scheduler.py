from .models import Restaurant, Rate
from accounts.models import User
import requests
import json
import math

#discord-webhook으로도 사용
class DiscordWebHooksScheduler:
    
    def send_lunch_notification(self, user, rest_infos):
        #for all params, see https://discordapp.com/developers/docs/resources/webhook#execute-webhook
        headers = {
            'Content-Type': 'application/json',
            'Cookie': '__cfruid=b861bcb43f0e3e066010c80bbda0f4685b31ef00-1698971327; __dcfduid=4e92bafe772611eeafed66025b66c56b; __sdcfduid=4e92bafe772611eeafed66025b66c56bb9116c38b61ecd811cf74f8dd52d6bed962e9d6126195927285a8f19cf4d3584; _cfuvid=IbG2yMM4vRp1X3cRolIUmKgcDlRjIwnsrhuGQu1m3Ok-1698971327328-0-604800000'
                    }
        data = {
            "username": "LunchHere",
            "avatar_url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRN9lF93jsUSQ2J5jX4f4OcOvJf4I37mCdrfg&usqp=CAU",
            "content" : "Your LunchHere! {}님 오늘의 점심 추천 맛집은~".format(user.username),
            "embeds" : [
                
            ]
        }
        
        for rest_info in rest_infos[:5]:
            #leave this out if you dont want an embed
            #for all params, see https://discordapp.com/developers/docs/resources/channel#embed-object
            data["embeds"].append(
                {
                "author": {
                    "name": rest_info[1].name,
                    },
                "description":rest_info[1].food_category,
                "fields": [
                        {
                            "name": "지번",
                            "value": rest_info[1].address_lotno
                        },
                        {
                            "name": "도로명",
                            "value": rest_info[1].address_roadnm
                        },
                    ],
                "footer": {
                    "text": "언제나 당신을 위한 맛집과 함께 돌아올게요, Enjoy your LunchHere :)",
                    "icon_url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRN9lF93jsUSQ2J5jX4f4OcOvJf4I37mCdrfg&usqp=CAU"
                    }  
                }
            )
        data["embeds"].append(
                {
                "author": {
                    "name": "Webhook Information",
                    "icon_url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRkkqaddbEgITDj4ScVsIi1wRND2Z4g1nUm_w&usqp=CAU"
                },
                "color": 6815584,
                "fields": [
                    {
                        "name": "여러분 팀의 Webhook URL",
                        "value": "https://discord.com/api/webhooks/1168538153775280138/kIRP6uWMpvlN1cpv-RXKH69ZmiCtPK1hkVpsp7K12rAZAqQ0lgqyetPjDfAOTP3S3Iko"
                    },
                    {
                        "name": "discord-webhooks-guide",
                        "value": "https://birdie0.github.io/discord-webhooks-guide/index.html"
                    },
                    {
                        "name": "get decimal color",
                        "value": "https://html-color.org/67ff60 , Discord Webhook color use '\''Decimal'\'' value, search your color in this site\n ex) #67ff60 > 6815584"
                    }
                ]
            }
        )
        
        url = "https://discord.com/api/webhooks/1169806092138717267/57BBLDa6dr6GgE3p9U2humk-xHQmz1mJQNWUktYDIqUIsqmu5TH8ViQcF7HzcGaD-GQx" #webhook url, from here: https://i.imgur.com/f9XnAew.png
        
        # print(json.dumps(data))
        result = requests.post(url,  headers=headers,  data=json.dumps(data))

        try:
            result.raise_for_status()
        except requests.exceptions.HTTPError as err:
            print(err)
        else:
            print("Payload delivered successfully, code {}.".format(result.status_code))
    
    def get_lunch_list(self, user, radius=0.5):
        user_point = (float(user.longitude),  float(user.latitude))
        
        restaurants = Restaurant.objects.all().order_by('-score')
        rest_infos = set()
        
        while len(rest_infos) <= 5:
            for restaurant in restaurants:
                rest_point = (float(restaurant.longitude), float(restaurant.latitude))
                distance = self.lat_lon_to_km(user_point, rest_point)
                if distance <= radius and (distance, restaurant) not in rest_infos:
                    rest_infos.add((distance, restaurant))
            radius += 0.5
            
        rest_infos = list(rest_infos)
        rest_infos.sort(key=lambda x : x[0])
        
        return rest_infos
    
    def recommend_lunch(self):
        #현재 추천 시스템을 받는 모든 사용자의 onject를 return 
        user_instance = User.objects.all().filter(is_recommend=True)
        
        
        #현재 사용자 반경 안에 있는 식당 중에 평점이 넢은 순서대로 나열
        
        #5개가 안되면 계속해서 반경을 늘려가도록 합니다.
        #제공 하고자하는 메뉴의 종류는 분식, 일식, 중식, 패스트푸드
        for obj in user_instance:
            rest_infos = self.get_lunch_list(obj)
            self.send_lunch_notification(obj, rest_infos)
            
                
    #해당 user의 일정 범위에 있는 맛집을 return 해줍니다.
    def lat_lon_to_km(self, point_1, point_2):
        lat1 = point_1[1]
        lon1 = point_1[0]
        lat2 = point_2[1]
        lon2 = point_2[0]

        # R = 6371  # km
        R = 1  # km
        dLat = math.radians(lat2-lat1)
        dLon = math.radians(lon2-lon1)

        lat1 = math.radians(lat1)
        lat2 = math.radians(lat2)

        a = math.sin(dLat/2) * math.sin(dLat/2) + \
            math.sin(dLon/2) * math.sin(dLon/2) * math.cos(lat1) * math.cos(lat2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

        return R * c 
