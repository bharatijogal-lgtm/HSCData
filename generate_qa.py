import os
import json
from google import genai

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

with open('system/progress_tracker.json', 'r') as f:
    tracker = json.load(f)

# ધોરણ 11 બાયોલોજી (નવો સિલેબસ 2024+)
std11_bio_chapters = {
    1: "સજીવ વિશ્વ", 2: "જૈવિક વર્ગીકરણ", 3: "વનસ્પતિ સૃષ્ટિ", 4: "પ્રાણી સૃષ્ટિ",
    5: "સપુષ્પી વનસ્પતિઓની બાહ્યાકાર વિદ્યા", 6: "સપુષ્પી વનસ્પતિઓની અંતઃસ્થ રચના",
    7: "પ્રાણીઓમાં રચનાકીય આયોજન", 8: "કોષ: જીવનનો એકમ", 9: "જૈવ અણુઓ",
    10: "કોષચક્ર અને કોષવિભાજન", 11: "ઉચ્ચ કક્ષાની વનસ્પતિઓમાં પ્રકાશસંશ્લેષણ",
    12: "વનસ્પતિઓમાં શ્વસન", 13: "વનસ્પતિ વૃદ્ધિ અને વિકાસ", 14: "શ્વાસોચ્છવાસ અને વાયુઓનું વિનિમય",
    15: "દેહજળ અને પરિવહન", 16: "ઉત્સર્ગ પેદાશો અને તેનો નિકાલ", 17: "પ્રચલન અને હલનચલન",
    18: "ચેતાકીય નિયંત્રણ અને સહનિયમન", 19: "રાસાયણિક સહનિયમન અને સંકલન"
}

# પ્રશ્નોના પ્રકાર અને તેનો ક્રમ
question_types = [
    {"id": "MCQ", "name": "બહુવિકલ્પી પ્રશ્નો (MCQ)", "marks": 1, "min_count": 30},
    {"id": "FillBlanks", "name": "ખાલી જગ્યા પૂરો (3 વિકલ્પો સાથે)", "marks": 1, "min_count": 30},
    {"id": "OneWord", "name": "એક વાક્યમાં ઉત્તર", "marks": 1, "min_count": 30},
    {"id": "MatchPairs", "name": "જોડકાં જોડો", "marks": 1, "min_count": 30},
    {"id": "2Marks", "name": "ટૂંક જવાબી પ્રશ્નો", "marks": 2, "min_count": 20},
    {"id": "3Marks", "name": "મુદ્દાસર પ્રશ્નો", "marks": 3, "min_count": 20},
    {"id": "4Marks", "name": "વિસ્તૃત પ્રશ્નો", "marks": 4, "min_count": 20}
]

ch_num = tracker['current_chapter']
type_idx = tracker['current_type_index']
ch_name = std11_bio_chapters.get(ch_num, "અન્ય")
current_q_type = question_types[type_idx]

print(f"Generating {current_q_type['name']} for Std 11 Biology Chapter {ch_num} ({ch_name})...", flush=True)

# પ્રકાર મુજબ ખાસ નિયમો
type_specific_rules = ""
if current_q_type['id'] == "MCQ":
    type_specific_rules = "દરેક પ્રશ્ન સાથે 4 વિકલ્પો (A, B, C, D) ફરજિયાત આપવા."
elif current_q_type['id'] == "FillBlanks":
    type_specific_rules = "દરેક ખાલી જગ્યાના અંતે કૌંસમાં 3 વિકલ્પો ફરજિયાત આપવા. દા.ત. _____ (વિકલ્પ1, વિકલ્પ2, વિકલ્પ3)."
elif current_q_type['id'] == "MatchPairs":
    type_specific_rules = "વિભાગ A અને વિભાગ B ના જોડકાં આપવા અને જવાબમાં સાચી જોડ આપવી."

prompt = f"""
તમે ગુજરાત બોર્ડ (GSEB) ના એક્સપર્ટ Biology શિક્ષક છો. 
તમારે ધોરણ 11 સાયન્સ, વિષય: બાયોલોજી (જીવવિજ્ઞાન), પ્રકરણ: {ch_num} ({ch_name}) ના નવા NCERT સિલેબસ મુજબ પ્રશ્નો બનાવવાના છે.

પ્રશ્નનો પ્રકાર: {current_q_type['name']} ({current_q_type['marks']} માર્ક)

અત્યંત કડક નિયમો (STRICT QUALITY CONTROL):
1. પ્રશ્નોની સંખ્યા: ઓછામાં ઓછા {current_q_type['min_count']} પ્રશ્નો ફરજિયાત બનાવવાના છે. પ્રકરણ મોટું હોય તો વધુ બની શકે, પણ {current_q_type['min_count']} થી ઓછા નહિ. (આખા ચેપ્ટરનો ખૂણેખૂણો કવર થવો જોઈએ).
2. પ્રકાર મુજબ શરત: {type_specific_rules}
3. નો-રીપીટેશન: અગાઉના કોઈ પ્રશ્ન રીપીટ ન થવા જોઈએ. 
4. સંપૂર્ણ જવાબ અને ટ્રીક: દરેક પ્રશ્નની સાથે તેનો સચોટ જવાબ અને તેને યાદ રાખવા માટે '💡 નિતેશ સરની શોર્ટકટ ટ્રીક' ફરજિયાત હોવી જોઈએ.

ફોર્મેટ (STRICT JSON FORMAT):
કોઈપણ જાતના વેરીએબલ વગર માત્ર નીચે મુજબનું JSON Object આપવું:
{{
  "chapterName": "પ્રકરણ {ch_num}",
  "chapterTitle": "{ch_name}",
  "questionType": "{current_q_type['name']}",
  "qa_list": [
    {{
      "questionNumber": "પ્રશ્ન 1",
      "question": "અહીં પ્રશ્ન લખવો...",
      "answer": "<div style='background-color:#f0f8ff; padding:15px; border-left:5px solid #16a085; border-radius:8px;'><p><strong>ઉકેલ/જવાબ:</strong> અહીં સાચો જવાબ કે સંપૂર્ણ સમજૂતી લખવી.</p><hr><p style='color:#d32f2f; font-weight:bold;'>💡 નિતેશ સરની શોર્ટકટ ટ્રીક: અહીં યાદ રાખવાની ટ્રીક લખવી...</p></div>"
    }}
  ]
}}
"""

print("Searching for live text models from your API account...", flush=True)
valid_models = []
try:
    for model in client.models.list():
        if hasattr(model, 'supported_actions') and "generateContent" in model.supported_actions:
            name = model.name.lower()
            if not any(word in name for word in ['video', 'audio', 'tts', 'vision', 'image', 'exp', 'learnlm', 'embedding', 'aqa']):
                valid_models.append(model.name)
except Exception as e:
    print(f"Error fetching models: {e}", flush=True)

valid_models.sort(key=lambda x: ('flash' not in x.lower(), x))
output_data = ""

for m in valid_models[:3]:
    try:
        print(f"⏳ Pending: {m} મોડલ દ્વારા {current_q_type['min_count']} પ્રશ્નો બની રહ્યા છે...", flush=True)
        response = client.models.generate_content(model=m, contents=prompt)
        raw_output = response.text.strip()
        
        if "{" in raw_output and "}" in raw_output:
            raw_output = raw_output[raw_output.find("{") : raw_output.rfind("}") + 1]
            
        output_data = raw_output.strip()
        print(f"✅ Success! ડેટા બની ગયો છે.", flush=True)
        break
    except Exception as e:
        print(f"❌ Failed with {m}. Error: {e}", flush=True)

if not output_data:
    print("Error: બધી જ ટ્રાય ફેલ ગઈ છે.", flush=True)
    exit(1)

# તમારા કહ્યા મુજબનું નવું ફોલ્ડર સ્ટ્રક્ચર: Science/Std11/Biology
folder_path = f"Science/Std11/Biology/Ch_{ch_num}_{ch_name.replace(' ', '_')}"
os.makedirs(folder_path, exist_ok=True)
file_path = f"{folder_path}/{current_q_type['id']}.js"

mode = 'a' if os.path.exists(file_path) else 'w'
with open(file_path, mode, encoding='utf-8') as f:
    if mode == 'w':
        f.write(f"var Ch{ch_num}_{current_q_type['id']} = {{\n")
        f.write(f'"{current_q_type['id']}": ' + output_data + '\n')
    else:
        f.write(f',\n"{current_q_type['id']}": ' + output_data + '\n')

# ટ્રેકર અપડેટ લોજીક (MCQ -> ખાલી જગ્યા -> ... 4 માર્ક્સ -> નવું ચેપ્ટર)
tracker['current_type_index'] += 1
if tracker['current_type_index'] >= len(question_types):
    tracker['current_type_index'] = 0
    tracker['current_chapter'] += 1

if tracker['current_chapter'] > len(std11_bio_chapters):
    print("🎉 ધોરણ 11 બાયોલોજીના તમામ ચેપ્ટર પૂર્ણ થયા!", flush=True)
    tracker['status'] = "completed"

with open('system/progress_tracker.json', 'w') as f:
    json.dump(tracker, f, indent=4)

print("Task Completed Successfully!", flush=True)
