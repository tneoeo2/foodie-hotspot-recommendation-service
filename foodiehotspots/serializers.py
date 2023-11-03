from .models import Restaurant, Rate
from rest_framework.serializers import ModelSerializer, PrimaryKeyRelatedField, SerializerMethodField

class EvalCreateSerializers(ModelSerializer):
    model = Rate
    field = ['score', 'content']
    
class FoodieDetailsSerializers(ModelSerializer):

    related_eval_ids = SerializerMethodField()
    
    
    def get_related_eval_ids(self, obj):
        # 해당 company_id로 지원한 지원공고인 recruit_id를 리스트로 반환
        related_evals = Rate.objects.filter(restaurant=obj.id).order_by('-created_at')
        #value_list를 사용하면 object에서 지정해준 field값을 tuple형태로 return 해줍니다.
        evals_ids = related_evals.values_list('score','content')
        return evals_ids
    
    class Meta:
        model = Restaurant
        fields = '__all__'

        