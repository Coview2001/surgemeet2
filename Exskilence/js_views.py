import json
import re
from django.http import JsonResponse, HttpResponse
from rest_framework.decorators import api_view
import jsbeautifier
from Exskilencebackend160924.Blob_service import  get_blob_container_client
from .models import *
from .frontend_views import add_daysQN_db

@api_view(['POST'])
def run_test_js(request):
    try:
        data = json.loads(request.body.decode('utf-8'))
        js_code = data['Ans']
        beautified_js1 = jsbeautifier.beautify(js_code)
        d1 = beautified_js1.split('\n')
        sam = data['KEYS']
        ans = [a.replace(' ','') for key in sam for a in d1 if str(a.replace(' ','')).__contains__(key.replace(' ',''))]
        common_keywords = [i for i in sam if any(str(j).__contains__(i.replace(' ','')) for j in ans)]
        output = {
            "valid": len(common_keywords) == len(sam),
            "message": "JS code is valid." if len(common_keywords) == len(sam) else "JS code is Not valid.",
            "common":common_keywords,
        }
        score = f'{len(common_keywords) }/{len(sam) }'
        data.update({"Score": score,"Result":score})
        res= add_daysQN_db(data)
        # print('database',res)
        output.update({"score": score,"Res":res})
        return HttpResponse(json.dumps(output), content_type='application/json')
    
    except Exception as e:
        return HttpResponse(f"An error occurred: {e}", status=500)

