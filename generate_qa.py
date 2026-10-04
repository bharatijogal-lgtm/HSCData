import os
import json
import time
from google import genai

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

with open('system/progress_tracker.json', 'r', encoding='utf-8') as f:
    tracker = json.load(f)

if tracker.get('status') == "completed":
    print("🎉 ઓટોમેશન પૂર્ણ થઈ ગયું છે. ધોરણ 11 સાયન્સના તમામ વિષયોના ડેટા બની ગયા છે!", flush=True)
    exit(0)

# ==========================================
# ધોરણ 11 સાયન્સ (નવો સિલેબસ 2024+) - તમામ વિષયો
# ==========================================
science_subjects = [
    {
        "id": "Biology",
        "guj_name": "બાયોલોજી (જીવવિજ્ઞાન)",
        "chapters": {
            1: "સજીવ વિશ્વ", 2: "જૈવિક વર્ગીકરણ", 3: "વનસ્પતિ સૃષ્ટિ", 4: "પ્રાણી સૃષ્ટિ",
            5: "સપુષ્પી વનસ્પતિઓની બાહ્યાકાર વિદ્યા", 6: "સપુષ્પી વનસ્પતિઓની અંતઃસ્થ રચના",
            7: "પ્રાણીઓમાં રચનાકીય આયોજન", 8: "કોષ: જીવનનો એકમ", 9: "જૈવ અણુઓ",
            10: "કોષચક્ર અને કોષવિભાજન", 11: "ઉચ્ચ કક્ષાની વનસ્પતિઓમાં પ્રકાશસંશ્લેષણ",
            12: "વનસ્પતિઓમાં શ્વસન", 13: "વનસ્પતિ વૃદ્ધિ અને વિકાસ", 14: "શ્વાસોચ્છવાસ અને વાયુઓનું વિનિમય",
            15: "દેહજળ અને પરિવહન", 16: "ઉત્સર્ગ પેદાશો અને તેનો નિકાલ", 17: "પ્રચલન અને હલનચલન",
            18: "ચેતાકીય નિયંત્રણ અને સહનિયમન", 19: "રાસાયણિક સહનિયમન અને સંકલન"
        }
    },
    {
        "id": "Physics",
        "guj_name": "ભૌતિકવિજ્ઞાન (Physics)",
        "chapters": {
            1: "એકમ અને માપન", 2: "સુરેખ પથ પર ગતિ", 3: "સમતલમાં ગતિ", 4: "ગતિના નિયમો",
            5: "કાર્ય, ઊર્જા અને પાવર", 6: "કણોનાં તંત્રો અને ચાકગતિ", 7: "ગુરુત્વાકર્ષણ",
            8: "ઘન પદાર્થોના યાંત્રિક ગુણધર્મો", 9: "તરલના યાંત્રિક ગુણધર્મો", 10: "દ્રવ્યના ઉષ્મીય ગુણધર્મો",
            11: "થર્મોડાયનેમિક્સ", 12: "વાયુનો ગતિવાદ", 13: "દોલનો", 14: "તરંગો"
        }
    },
    {
        "id": "Chemistry",
        "guj_name": "રસાયણવિજ્ઞાન (Chemistry)",
        "chapters": {
            1: "રસાયણવિજ્ઞાનની કેટલીક પાયાની સંકલ્પનાઓ", 2: "પરમાણુનું બંધારણ",
            3: "તત્ત્વોનું વર્ગીકરણ અને ગુણધર્મોમાં આવર્તિતા", 4: "રાસાયણિક બંધન અને આણ્વીય રચના",
            5: "ઉષ્માગતિશાસ્ત્ર", 6: "સંતુલન", 7: "રેડોક્ષ પ્રક્રિયાઓ",
            8: "કાર્બનિક રસાયણવિજ્ઞાન - કેટલાક પાયાના સિદ્ધાંતો અને તકનીકો", 9: "હાઇડ્રોકાર્બન"
        }
    },
    {
        "id": "Maths",
        "guj_name": "ગણિત (Mathematics)",
        "chapters": {
            1: "ગણ", 2: "સંબંધ અને વિધેય", 3: "ત્રિકોણમિતિય વિધેયો", 
            4: "સંકર સંખ્યાઓ અને દ્વિઘાત સમીકરણો", 5: "સુરેખ અસમતાઓ", 
            6: "ક્રમચય અને સંચય", 7: "દ્વિપદી પ્રમેય", 8: "શ્રેણી અને શ્રેઢી", 
            9: "રેખાઓ", 10: "શાંકવો", 11: "ત્રિપરિમાણીય ભૂમિતિનો પરિચય", 
            12: "લક્ષ અને વિકલન", 13: "આંકડાશાસ્ત્ર", 14: "સંભાવના"
        }
    }
]

# પ્રશ્નોના પ્રકાર અને તેનો મિનિમમ ટાર્ગેટ
question_types = [
    {"id": "MCQs", "name": "બહુવિકલ્પી પ્રશ્નો (MCQ)", "marks": 1, "min_count": 70},
    {"id": "FillBlanks", "name": "ખાલી જગ્યા પૂરો (3 વિકલ્પો સાથે)", "marks": 1, "min_count": 70},
    {"id": "OneWord", "name": "એક વાક્યમાં ઉત્તર", "marks": 1, "min_count": 70},
    {"id": "MatchPairs", "name": "જોડકાં જોડો", "marks": 1, "min_count": 70},
    {"id": "2_Marks", "name": "ટૂંક જવાબી પ્રશ્નો", "marks": 2, "min_count": 20},
    {"id": "3_Marks", "name": "મુદ્દાસર પ્રશ્નો", "marks": 3, "min_count": 20},
    {"id": "4_Marks", "name": "વિસ્તૃત પ્રશ્નો", "marks": 4, "min_count": 20}
]

# ટ્રેકરમાંથી હાલની સ્થિતિ મેળવવી
sub_idx = tracker.get('current_subject_index', 0)
type_idx = tracker.get('current_type_index', 0)
ch_num = tracker.get('current_chapter', 1)

current_subject = science_subjects[sub_idx]
current_q_type = question_types[type_idx]
ch_name = current_subject["chapters"].get(ch_num, "અન્ય")
max_chapters = len(current_subject["chapters"])

print(f"Generating {current_q_type['name']} for Std 11 {current_subject['id']} Chapter {ch_num} ({ch_name})...", flush=True)

# પ્રકાર મુજબ ખાસ નિયમો
type_specific_rules = ""
if current_q_type['id'] == "MCQs":
    type_specific_rules = "દરેક પ્રશ્ન સાથે 4 વિકલ્પો (A, B, C, D) ફરજિયાત આપવા."
elif current_q_type['id'] == "FillBlanks":
    type_specific_rules = "દરેક ખાલી જગ્યાના અંતે કૌંસમાં 3 વિકલ્પો ફરજિયાત આપવા. દા.ત. _____ (વિકલ્પ1, વિકલ્પ2, વિકલ્પ3)."
elif current_q_type['id'] == "MatchPairs":
    type_specific_rules = "વિભાગ A અને વિભાગ B ના જોડકાં આપવા અને જવાબમાં સાચી જોડ આપવી."

prompt = f"""
તમે ગુજરાત બોર્ડ (GSEB) ના એક્સપર્ટ શિક્ષક છો. 
તમારે ધોરણ 11 સાયન્સ, વિષય: {current_subject['guj_name']}, પ્રકરણ: {ch_num} ({ch_name}) ના નવા ઘટાડેલા NCERT સિલેબસ મુજબ પ્રશ્નો બનાવવાના છે.

પ્રશ્નનો પ્રકાર: {current_q_type['name']} ({current_q_type['marks']} માર્ક)

અત્યંત કડક નિયમો (STRICT QUALITY CONTROL & ZERO MIXING):
1. શુદ્ધતા: પ્રશ્નો માત્ર અને માત્ર '{current_subject['guj_name']}' ના પ્રકરણ '{ch_name}' માંથી જ હોવા જોઈએ. ભૂલથી પણ અન્ય વિષયના પ્રશ્નો ન આવવા જોઈએ.
2. પ્રશ્નોની સંખ્યા (TARGET): ઓછામાં ઓછા {current_q_type['min_count']} પ્રશ્નો ફરજિયાત બનાવવાના છે. {current_q_type['min_count']} થી વધુ પ્રશ્નો બની શકતા હોય તો ફરજિયાત બનાવવાના જ છે. આખા ચેપ્ટરની દરેક લાઈન કવર થઈ જવી જોઈએ.
3. પ્રકાર મુજબ શરત: {type_specific_rules}
4. નો-રીપીટેશન: અગાઉના કોઈ પ્રશ્ન રીપીટ ન થવા જોઈએ. 
5. સંપૂર્ણ જવાબ અને ટ્રીક: દરેક પ્રશ્નની સાથે તેનો સચોટ જવાબ અને તેને યાદ રાખવા માટે '💡 નિતેશ સરની શોર્ટકટ ટ્રીક (NJ Classes)' ફરજિયાત હોવી જોઈએ. ગણિત કે વિજ્ઞાનના સમીકરણો સ્પષ્ટ લખવા.

ફોર્મેટ (STRICT JSON FORMAT ONLY):
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
            invalid_words = ['video', 'audio', 'tts', 'vision', 'image', 'exp', 'learnlm', 'embedding', 'aqa', '2.5-flash']
            if not any(word in name for word in invalid_words):
                valid_models.append(model.name)
except Exception as e:
    print(f"Error fetching models: {e}", flush=True)

if not valid_models:
    valid_models = ["models/gemini-3-flash-preview"]

valid_models.sort(key=lambda x: ('flash' not in x.lower(), x))
print(f"Active Models to use: {valid_models}", flush=True)

output_data = ""

for m in valid_models[:3]:
    print(f"⏳ Pending: {m} મોડલ દ્વારા ઓછામાં ઓછા {current_q_type['min_count']} પ્રશ્નો બની રહ્યા છે...", flush=True)
    success = False
    
    for attempt in range(1, 4):
        try:
            response = client.models.generate_content(model=m, contents=prompt)
            raw_output = response.text.strip()
            
            if "{" in raw_output and "}" in raw_output:
                raw_output = raw_output[raw_output.find("{") : raw_output.rfind("}") + 1]
                
            output_data = raw_output.strip()
            print(f"✅ Success! ડેટા બની ગયો છે.", flush=True)
            success = True
            break
        except Exception as e:
            err_msg = str(e)
            print(f"⚠️ પ્રયાસ {attempt}/3 નિષ્ફળ ({m}): {err_msg}", flush=True)
            if "NOT_FOUND" in err_msg or "no longer available" in err_msg:
                break
            time.sleep(6)
            
    if success:
        break

if not output_data:
    print("Error: બધી જ ટ્રાય ફેલ ગઈ છે.", flush=True)
    exit(1)

# ફોલ્ડર સ્ટ્રક્ચર: Science/Std11/Physics (તે વિષય મુજબ બનશે)
folder_path = f"Science/Std11/{current_subject['id']}"
os.makedirs(folder_path, exist_ok=True)

q_id = current_q_type['id']
file_path = f"{folder_path}/{current_subject['id']}_{q_id}.js"

mode = 'a' if os.path.exists(file_path) else 'w'
with open(file_path, mode, encoding='utf-8') as f:
    if mode == 'w':
        f.write(f"var Std11_{current_subject['id']}_{q_id} = {{\n")
        f.write(f'"{ch_num}": ' + output_data + '\n')
    else:
        f.write(f',\n"{ch_num}": ' + output_data + '\n')

# ==========================================
# ટ્રાન્ઝિશન લોજીક (પ્રકરણ -> પ્રશ્ન પ્રકાર -> વિષય)
# ==========================================
tracker['current_chapter'] += 1

# જો બધા ચેપ્ટર પૂરા થાય તો નવો પ્રશ્ન પ્રકાર શરૂ કરો
if tracker['current_chapter'] > max_chapters:
    tracker['current_chapter'] = 1
    tracker['current_type_index'] += 1

# જો બધા પ્રશ્ન પ્રકાર પૂરા થાય તો નવો વિષય શરૂ કરો
if tracker['current_type_index'] >= len(question_types):
    print(f"🎉 {current_subject['guj_name']} વિષય પૂર્ણ થયો!", flush=True)
    tracker['current_type_index'] = 0
    tracker['current_subject_index'] += 1
    
    # જો ચારેય વિષયો પૂરા થઈ જાય તો
    if tracker['current_subject_index'] >= len(science_subjects):
        print("🎉 ધોરણ 11 સાયન્સના તમામ વિષયોનું ઓટોમેશન પૂર્ણ થયું!", flush=True)
        tracker['status'] = "completed"
        tracker['current_subject_index'] -= 1  # એરર અટકાવવા

with open('system/progress_tracker.json', 'w', encoding='utf-8') as f:
    json.dump(tracker, f, indent=4)

print("Task Completed Successfully!", flush=True)
