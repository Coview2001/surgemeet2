import json
from bs4 import BeautifulSoup
from django.http import HttpResponse
from rest_framework.decorators import api_view
import cssutils
from Exskilencebackend160924.Blob_service import download_blob

# from .internship import addCodeToDb, css_to_tuples, jsonToTuple
from Exskilence.models import *
from .frontend_views import add_daysQN_db
  

def css_to_tuples(css_code,KEYS):
    parser = cssutils.CSSParser()
    if KEYS :
        tuple_format_css = []

        for style in KEYS:
            if "media_query" in style:
                media_query = style["media_query"]
                rules = style["rules"]
                media_rules = [(rule["selector"], [(prop["property"], prop["value"]) for prop in rule["properties"]]) for rule in rules]
                tuple_format_css.append((media_query, media_rules))
            elif "keyframes_name" in style:
                keyframes_name = style["keyframes_name"]
                keyframes_steps = style["keyframes_steps"]
                keyframes = [(step["selector"], [(prop["property"], prop["value"]) for prop in step["properties"]]) for step in keyframes_steps]
                tuple_format_css.append((keyframes_name, keyframes))
            else:
                    selector = style["selector"]
                    properties = style["properties"]
                    prop_list = [(prop["property"], prop["value"]) for prop in properties]
                    tuple_format_css.append((selector, prop_list))
        return tuple_format_css
    else:
        stylesheet = parser.parseString(css_code)
    
        css_tuples = []

        for rule in stylesheet:
            if rule.type == rule.STYLE_RULE:
                selector = rule.selectorText
                properties = []
                for property in rule.style:
                    properties.append((property.name, property.value))
                css_tuples.append((selector, properties))
            elif rule.type == rule.MEDIA_RULE:
                media_query = rule.media.mediaText.strip()
                media_rules = []

                for media_rule in rule.cssRules:
                    if media_rule.type == media_rule.STYLE_RULE:
                        selector = media_rule.selectorText
                        properties = [(property.name, property.value) for property in media_rule.style]
                        media_rules.append((selector, properties))

                css_tuples.append((media_query, media_rules))
            elif rule.type == rule.KEYFRAMES_RULE:
                keyframes_name = rule.name.strip()
                keyframes_steps = []

                for keyframe in rule.cssRules:
                    if keyframe.type == keyframe.KEYFRAME_RULE:
                        keyframe_selector = keyframe.keyText.strip()
                        keyframe_properties = [(property.name, property.value) for property in keyframe.style]
                        keyframes_steps.append((keyframe_selector, keyframe_properties))

                css_tuples.append((keyframes_name, keyframes_steps))

    
    return css_tuples
 
@api_view(['POST'])
def css_compare(req    ):
    try:
        data = json.loads(req.body)
        css_code = data['Ans']
        keys=data['KEYS']
        css_tuples_a = css_to_tuples("",keys)
        css_tuples_b = css_to_tuples(css_code,'')
        common_keywords = [i for i in css_tuples_a if i in css_tuples_b]
        output={}
        if common_keywords == css_tuples_a:
           output.update({"valid": True,"message": "CSS code is valid."})
        else:
            output.update({"valid": False,"message": "CSS code is Not valid."})
        score = f'{len(common_keywords) }/{len(css_tuples_a) }'
        data.update({"Score": score,"Result":score})
        res= add_daysQN_db(data)#add_QnsToDb(data,len(common_keywords),score)
        output.update({"score": score,"Res":res})
        return HttpResponse(json.dumps(output), content_type='application/json')
    except Exception as e:
        return HttpResponse(f"An error occurred: {e}", status=500)

def jsonToTuple(code):
    tuple_format = []

    for element in code:
       tag = element["tag"]
       attributes = element["attributes"]
       for attr, value in attributes.items():
           tuple_format.append((tag, attr, value))
    return tuple_format

@api_view(['POST'])
def html_page(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            htmlcode = data.get('Ans')
            keys=data.get('KEYS')
            if not htmlcode:
                return HttpResponse("No HTML data provided", status=400)
            
            user_soup = BeautifulSoup(htmlcode, 'html.parser')
            def extract_tags_and_attributes(soup):
                elements = soup.find_all(True)  
                tag_attr_list = []
                for element in elements:
                    tag = element.name
                    attrs = element.attrs
                    for attr_name, attr_value in attrs.items():
                        tag_attr_list.append((tag, attr_name, attr_value))
                return tag_attr_list
            sample_elements=(jsonToTuple(keys))
            user_elements = extract_tags_and_attributes(user_soup)
            common_keywords = [i for i in sample_elements if i in user_elements]
            output = {}
            if len(common_keywords) == len(sample_elements):
                output.update({"valid": True,"message": "HTML code is valid."})
            else:
                output.update({"valid": False,"message": "HTML code is Not valid."})

            score = f'{len(common_keywords) }/{len(sample_elements) }'
            data.update({"Score": score,"Result":score})
            res= add_daysQN_db(data)#add_QnsToDb(data,len(common_keywords),score)
            output.update({"score": score,"Res":res})
            return HttpResponse(json.dumps(output), content_type='application/json')

        except Exception as e:
            return HttpResponse(f"An error occurred: {e}", status=500)
    else:
        return HttpResponse("Method Not Allowed", status=405)
    
# def add_QnsToDb(data ,score,result):
#     try:
#         user = FrontendDetails.objects.filter(Student_id=data['Student_id']).first()
    #     if user is None:
    #         user = FrontendDetails.objects.create(Student_id=data['Student_id'],
    #             HTML_Code={},
    #             CSS_Code={},
    #             JS_Code={})
    #     score=scoring_logic(score,data['Qn_name'])
    #     if data['File_name']=='html':
    #         old_score=user.HTML_Score.get(data['Qn_name'],0)
    #         user.HTML_Code.update({data['Qn_name']:data['data']}) 
    #         user.HTML_Score.update({data['Qn_name']:score})
    #         user.HTML_Result.update({data['Qn_name']:result})
    #     if data['File_name']=='css':
    #         old_score=user.CSS_Score.get(data['Qn_name'],0)
    #         user.CSS_Code.update({data['Qn_name']:data['data']}) 
    #         user.CSS_Score.update({data['Qn_name']:score})
    #         user.CSS_Result.update({data['Qn_name']:result})
    #     if data['File_name']=='js':
    #         old_score=user.JS_Score.get(data['Qn_name'],0)
    #         user.JS_Code.update({data['Qn_name']:data['data']}) 
    #         user.JS_Score.update({data['Qn_name']:score})
    #         user.JS_Result.update({data['Qn_name']:result})
    #     user.Score = user.Score + int(score) - int(old_score)
    #     user.save()
    #     return 'data saved'   
    # except Exception as e:
    #     return f"An error occurred: {e}"

   
def scoring_logic(Score,QN):
        if str(QN)[-4]=='E':
            return Score*5
        elif str(QN)[-4]=='M':
            return Score*10
        elif str(QN)[-4]=='H':
            return Score*15
        else:
            return Score 