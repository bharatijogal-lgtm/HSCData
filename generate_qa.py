import os
import json
import time
from google import genai

# API Key ચેક કરવી
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    print("❌ Error: GEMINI_API_KEY મળી નથી! GitHub Secrets ચેક કરો.", flush=True)
    exit(1)

client = genai.Client(api_key=api_key)

# Progress Tracker વાંચવું (જો ફાઈલમાં ભૂલ હોય તો આપમેળે રીસેટ કરશે)
tracker_path = 'system/progress_tracker.json'
try:
    with open(tracker_path, 'r', encoding='utf-8') as f:
        tracker = json.load(f)
except Exception as e:
    print(f"⚠️ ટ્રેકર ફાઈલ વાંચવામાં સમસ્યા ({e}), ડિફોલ્ટ સેટ કરી રહ્યા છીએ...", flush=True)
    tracker = {
        "current_subject_index": 0,
        "current_type_index": 0,
        "current_chapter": 1,
        "status": "in_progress"
    }

if tracker.get('status') == "completed":
    print("🎉 ઓટોમેશન પૂર્ણ થઈ ગયું છે. ધોરણ 12 સાયન્સના તમામ વિષયોના ડેટા બની ગયા છે!", flush=True)
    exit(0)

# ==========================================
# ધોરણ 12 સાયન્સ (નવો સિલેબસ NCERT) - તમામ વિષયો
# ==========================================
science_subjects = [
    {
        "id": "Biology",
        "prefix": "bio",
        "guj_name": "બાયોલોજી (જીવવિજ્ઞાન)",
        "chapters": {
            1: "સપુષ્પી વનસ્પતિઓમાં લિંગી પ્રજનન",
            2: "માનવ પ્રજનન",
            3: "પ્રજનન સ્વાસ્થ્ય",
            4: "આનુવંશિકતા અને ભિન્નતાના સિદ્ધાંતો",
            5: "આનુવંશિકતાનો આણ્વીય આધાર",
            6: "ઉદ્વિકાસ",
            7: "માનવ સ્વાસ્થ્ય અને રોગો",
            8: "માનવ કલ્યાણમાં સૂક્ષ્મજીવો",
            9: "બાયોટેકનોલોજી : સિદ્ધાંતો અને પ્રક્રિયાઓ",
            10: "બાયોટેકનોલોજી અને તેના પ્રયોજનો",
            11: "સજીવો અને વસ્તી",
            12: "નિવસનતંત્ર",
            13: "જૈવ-વિવિધતા અને સંરક્ષણ"
        }
    },
    {
        "id": "Physics",
        "prefix": "physics",
        "guj_name": "ભૌતિકવિજ્ઞાન (Physics)",
        "chapters": {
            1: "વિદ્યુતભારો અને ક્ષેત્રો",
            2: "સ્થિત વિદ્યુત સ્થિતિમાન અને કેપેસિટન્સ",
            3: "પ્રવાહ વિદ્યુત",
            4: "ગતિમાન વિદ્યુતભારો અને ચુંબકત્વ",
            5: "ચુંબકત્વ અને દ્રવ્ય",
            6: "વિદ્યુતચુંબકીય પ્રેરણ",
            7: "પ્રત્યાવર્તી પ્રવાહ",
            8: "વિદ્યુતચુંબકીય તરંગો",
            9: "કિરણ પ્રકાશશાસ્ત્ર અને પ્રકાશીય ઉપકરણો",
            10: "તરંગ પ્રકાશશાસ્ત્ર",
            11: "વિકિરણ અને દ્રવ્યની દ્વૈત પ્રકૃતિ",
            12: "પરમાણુઓ",
            13: "ન્યુક્લિયસ",
            14: "સેમિકન્ડક્ટર ઇલેક્ટ્રોનિક્સ : દ્રવ્યો, રચનાઓ અને સાદા પરિપથો"
        }
    },
    {
        "id": "Chemistry",
        "prefix": "chem",
        "guj_name": "રસાયણવિજ્ઞાન (Chemistry)",
        "chapters": {
            1: "દ્રાવણો",
            2: "વિદ્યુતરસાયણ",
            3: "રાસાયણિક ગતિકી",
            4: "d અને f-વિભાગનાં તત્ત્વો",
            5: "સવર્ગ સંયોજનો",
            6: "હેલોઆલ્કેન અને હેલોએરીન સંયોજનો",
            7: "આલ્કોહોલ, ફિનોલ અને ઇથર સંયોજનો",
            8: "આલ્ડિહાઇડ, કીટોન અને કાર્બોક્સિલિક એસિડ સંયોજનો",
            9: "એમાઇન સંયોજનો",
            10: "જૈવિક અણુઓ"
        }
    },
    {
        "id": "Maths",
        "prefix": "math",
        "guj_name": "ગણિત (Mathematics)",
        "chapters": {
            1: "સંબંધ અને વિધેય",
            2: "ત્રિકોણમિતિય પ્રતિવિધેયો",
            3: "શ્રેણિક",
            4: "નિશ્ચાયક",
            5: "સાતત્ય અને વિકલનીયતા",
            6: "વિકલિતના ઉપયોગો",
            7: "સંકલન",
            8: "સંકલનના ઉપયોગો",
            9: "વિકલ સમીકરણો",
            10: "સદિશ બીજગણિત",
            11: "ત્રિપરિમાણીય ભૂમિતિ",
            12: "સુરેખ આયોજન",
            13: "સંભાવના"
        }
    }
]

# પ્રશ્નોના પ્રકાર: પહેલા 5 પ્રકાર સ્ક્રીનશોટ મુજબ (array_format) અને બાકીના 3 જૂના ફોર્મેટ મુજબ (object_format)
question_types = [
    {"id": "MCQ", "file_name": "MCQ.js", "var_suffix": "questionsdatabase_std12", "name": "બહુવિકલ્પી પ્રશ્નો (MCQ)", "marks": 1, "min_count": 50, "format_type": "array_format"},
    {"id": "Blanks", "file_name": "Blanks.js", "var_suffix": "fillintheblankss_std12", "name": "ખાલી જગ્યા પૂરો", "marks": 1, "min_count": 40, "format_type": "array_format"},
    {"id": "1MarkQ", "file_name": "1MarkQ.js", "var_suffix": "onelines_std12", "name": "એક વાક્યમાં ઉત્તર (1 ગુણ)", "marks": 1, "min_count": 40, "format_type": "array_format"},
    {"id": "TrueFalse", "file_name": "TrueFalse.js", "var_suffix": "truefalse_std12", "name": "ખરા-ખોટા વિધાનો", "marks": 1, "min_count": 35, "format_type": "array_format"},
    {"id": "Jodaka", "file_name": "Jodaka.js", "var_suffix": "matchss_std12", "name": "જોડકાં જોડો", "marks": 2, "min_count": 15, "format_type": "array_format"},
    {"id": "2_Marks", "file_name": "2_Marks.js", "var_suffix": "2_Marks", "name": "ટૂંક જવાબી પ્રશ્નો (2 ગુણ)", "marks": 2, "min_count": 20, "format_type": "object_format"},
    {"id": "3_Marks", "file_name": "3_Marks.js", "var_suffix": "3_Marks", "name": "મુદ્દાસર પ્રશ્નો (3 ગુણ)", "marks": 3, "min_count": 15, "format_type": "object_format"},
    {"id": "4_Marks", "file_name": "4_Marks.js", "var_suffix": "4_Marks", "name": "વિસ્તૃત પ્રશ્નો (4 ગુણ)", "marks": 4, "min_count": 12, "format_type": "object_format"}
]

# ટ્રેકરમાંથી હાલની સ્થિતિ મેળવવી (જો ઇન્ડેક્સ આઉટ ઓફ રેન્જ હોય તો સેફ્ટી રાખવી)
sub_idx = int(tracker.get('current_subject_index', 0))
type_idx = int(tracker.get('current_type_index', 0))
ch_num = int(tracker.get('current_chapter', 1))

if sub_idx >= len(science_subjects):
    sub_idx = 0
if type_idx >= len(question_types):
    type_idx = 0

current_subject = science_subjects[sub_idx]
current_q_type = question_types[type_idx]
max_chapters = len(current_subject["chapters"])

if ch_num > max_chapters or ch_num < 1:
    ch_num = 1

ch_name = current_subject["chapters"].get(ch_num, "અન્ય")

print(f"🚀 Generating {current_q_type['name']} for Std 12 {current_subject['id']} Chapter {ch_num} ({ch_name})...", flush=True)

# ==========================================
# સ્ક્રીનશોટ મુજબ પ્રોમ્પ્ટ અને ફોર્મેટ સેટિંગ
# ==========================================
if current_q_type['format_type'] == "array_format":
    if current_q_type['id'] == "MCQ":
        format_instruction = (
            'કોઈપણ વધારાના લખાણ કે માર્કડાઉન વગર માત્ર નીચેના ફોર્મેટમાં જ દરેક લાઈનમાં એક ઓબ્જેક્ટ (છેલ્લે અલ્પવિરામ સાથે) આપવો:\n'
            f'  {{ chapter: {ch_num}, q: "અહીં પ્રશ્ન લખવો?", options: ["વિકલ્પ A", "વિકલ્પ B", "વિકલ્પ C", "વિકલ્પ D"], ans: 0 }},\n'
            '(નોંધ: ans માં સાચા વિકલ્પનો ઇન્ડેક્સ નંબર 0, 1, 2, અથવા 3 જ લખવો.)'
        )
    elif current_q_type['id'] == "Blanks":
        format_instruction = (
            'દરેક ખાલી જગ્યાના વાક્યને અંતે કૌંસમાં 3 વિકલ્પો ફરજિયાત આપવા. માત્ર નીચેના ફોર્મેટમાં જ દરેક લાઈનમાં એક ઓબ્જેક્ટ આપવો:\n'
            f'  {{ chapter: {ch_num}, marks: 1, q: "અહીં ખાલી જગ્યા વાળું વાક્ય ________ છે. (વિકલ્પ1, વિકલ્પ2, વિકલ્પ3)", ans: "સાચો જવાબ" }},'
        )
    elif current_q_type['id'] == "1MarkQ":
        format_instruction = (
            'કોઈપણ વધારાના લખાણ વગર માત્ર નીચેના ફોર્મેટમાં જ દરેક લાઈનમાં એક ઓબ્જેક્ટ આપવો:\n'
            f'  {{ chapter: {ch_num}, marks: 1, q: "અહીં એક ગુણનો પ્રશ્ન લખવો?", ans: "અહીં ટૂંકો અને સચોટ જવાબ લખવો" }},'
        )
    elif current_q_type['id'] == "TrueFalse":
        format_instruction = (
            'કોઈપણ વધારાના લખાણ વગર માત્ર નીચેના ફોર્મેટમાં જ દરેક લાઈનમાં એક ખરા-ખોટાનું વિધાન આપવું:\n'
            f'  {{ chapter: {ch_num}, marks: 1, q: "અહીં વિધાન લખવું.", ans: "સાચું" }},\n'
            '(નોંધ: ans માં માત્ર "સાચું" અથવા "ખોટું" લખવું.)'
        )
    elif current_q_type['id'] == "Jodaka":
        format_instruction = (
            'કોઈપણ વધારાના લખાણ વગર માત્ર નીચેના ફોર્મેટમાં જ જોડકાંના ઓબ્જેક્ટ્સ આપવા:\n'
            '  {\n'
            f'    chapter: {ch_num}, marks: 2,\n'
            '    q: "નીચેના જોડકાં યોગ્ય રીતે જોડો.",\n'
            '    colA: ["(1) પ્રથમ બાબત", "(2) બીજી બાબત"],\n'
            '    colB: ["(a) પ્રથમ વિકલ્પ", "(b) બીજો વિકલ્પ", "(c) ત્રીજો વધારાનો વિકલ્પ"],\n'
            '    ans: "(1) - (b), (2) - (a)"\n'
            '  },'
        )

    prompt = (
        f"તમે ગુજરાત બોર્ડ (GSEB) ધોરણ 12 સાયન્સના નિષ્ણાત શિક્ષક છો.\n"
        f"વિષય: {current_subject['guj_name']}\n"
        f"પ્રકરણ {ch_num}: {ch_name}\n"
        f"પ્રશ્નનો પ્રકાર: {current_q_type['name']}\n\n"
        f"નિયમો:\n"
        f"1. પ્રશ્નો માત્ર ધોરણ 12 સાયન્સના '{current_subject['guj_name']}' ના પ્રકરણ '{ch_name}' (નવા NCERT સિલેબસ) માંથી જ હોવા જોઈએ.\n"
        f"2. ઓછામાં ઓછા {current_q_type['min_count']} પ્રશ્નો ફરજિયાત બનાવવાના છે.\n"
        f"3. કોઈ પ્રશ્ન રીપીટ ન થવો જોઈએ.\n"
        f"4. {format_instruction}\n"
        f"5. શરૂઆતમાં કે અંતમાં [ કે ] કે var કશું જ લખવું નહીં, માત્ર કૌંસ {{ થી શરૂ થતા અને }}, થી પૂરા થતા ઓબ્જેક્ટ્સ જ આપવા."
    )

else:
    # 2, 3 અને 4 ગુણના પ્રશ્નો માટે તમારું જૂનું ફોર્મેટ
    prompt = f"""તમે ગુજરાત બોર્ડ (GSEB) ના એક્સપર્ટ શિક્ષક છો. 
તમારે ધોરણ 12 સાયન્સ, વિષય: {current_subject['guj_name']}, પ્રકરણ: {ch_num} ({ch_name}) ના નવા NCERT સિલેબસ મુજબ પ્રશ્નો બનાવવાના છે.

પ્રશ્નનો પ્રકાર: {current_q_type['name']} ({current_q_type['marks']} માર્ક)

અત્યંત કડક નિયમો:
1. શુદ્ધતા: પ્રશ્નો માત્ર અને માત્ર '{current_subject['guj_name']}' ના પ્રકરણ '{ch_name}' માંથી જ હોવા જોઈએ.
2. પ્રશ્નોની સંખ્યા (TARGET): ઓછામાં ઓછા {current_q_type['min_count']} પ્રશ્નો ફરજિયાત બનાવવાના છે.
3. સંપૂર્ણ જવાબ અને ટ્રીક: દરેક પ્રશ્નની સાથે તેનો સચોટ જવાબ અને તેને યાદ રાખવા માટે '💡 નિતેશ સરની શોર્ટકટ ટ્રીક (NJ Classes)' ફરજિયાત હોવી જોઈએ.

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

# ==========================================
# ભવિષ્યમાં કોઈ મોડલ બંધ થાય તો ઓટોમેટિક નવું મોડલ શોધવાની સિસ્ટમ
# ==========================================
def get_available_models():
    discovered = []
    try:
        for model in client.models.list():
            actions = getattr(model, 'supported_actions', None) or []
            if "generateContent" in actions:
                m_name = model.name.lower()
                skip_keywords = ['video', 'audio', 'tts', 'vision', 'image', 'embedding', 'aqa', 'veo', 'imagen', 'learnlm', 'robotics', 'computer-use']
                if not any(kw in m_name for kw in skip_keywords):
                    discovered.append(model.name)
    except Exception as e:
        print(f"⚠️ મોડલ લિસ્ટ મેળવવામાં ક્ષતિ: {e}", flush=True)

    def model_priority(name):
        n = name.lower()
        if '2.5-flash' in n and 'lite' not in n:
            return 0
        elif '3-flash' in n:
            return 1
        elif '2.0-flash' in n and 'lite' not in n:
            return 2
        elif 'flash' in n and 'lite' not in n:
            return 3
        elif 'pro' in n:
            return 4
        return 5

    discovered.sort(key=model_priority)

    backup_models = [
        "gemini-2.5-flash",
        "gemini-3-flash-preview",
        "gemini-2.0-flash",
        "gemini-2.5-pro",
        "gemini-1.5-flash"
    ]
    for bm in backup_models:
        if bm not in discovered and f"models/{bm}" not in discovered:
            discovered.append(bm)

    return discovered

valid_models = get_available_models()
print(f"✅ ઉપલબ્ધ મોડલ્સની યાદી: {valid_models[:6]}", flush=True)

output_data = ""

for m in valid_models[:6]:
    print(f"⏳ મોડલ '{m}' દ્વારા પ્રશ્નો જનરેટ થઈ રહ્યા છે...", flush=True)
    success = False

    for attempt in range(1, 4):
        try:
            response = client.models.generate_content(model=m, contents=prompt)
            if not response or not response.text:
                raise ValueError("મોડલ તરફથી ખાલી રિસ્પોન્સ મળ્યો છે.")
                
            raw_output = response.text.strip()
            raw_output = raw_output.replace("```json", "").replace("```javascript", "").replace("```js", "").replace("```", "").strip()

            if current_q_type['format_type'] == "object_format":
                if "{" in raw_output and "}" in raw_output:
                    raw_output = raw_output[raw_output.find("{") : raw_output.rfind("}") + 1]
            else:
                if raw_output.startswith("["):
                    raw_output = raw_output[1:].strip()
                if raw_output.endswith("]"):
                    raw_output = raw_output[:-1].strip()
                if "{" in raw_output and "}" in raw_output:
                    raw_output = raw_output[raw_output.find("{") : raw_output.rfind("}") + 1]
                if raw_output.endswith("}"):
                    raw_output += ","

            output_data = raw_output.strip()
            print(f"✅ સફળતા! '{m}' મોડલ દ્વારા ડેટા બની ગયો છે.", flush=True)
            success = True
            break

        except Exception as e:
            err_msg = str(e)
            print(f"⚠️ પ્રયાસ {attempt}/3 નિષ્ફળ ({m}): {err_msg}", flush=True)
            if any(err_code in err_msg.upper() for err_code in ["NOT_FOUND", "404", "DEPRECATED", "NO LONGER AVAILABLE", "INVALID_ARGUMENT", "PERMISSION_DENIED"]):
                print(f"🔄 મોડલ '{m}' ઉપલબ્ધ નથી, ઓટોમેટિક બીજા મોડલ પર શિફ્ટ થઈ રહ્યા છીએ...", flush=True)
                break
            time.sleep(6)

    if success:
        break

if not output_data:
    print("❌ Error: તમામ મોડલ્સ પર પ્રયાસ નિષ્ફળ ગયો છે.", flush=True)
    exit(1)

# ==========================================
# ફાઈલ સેવ કરવાનું લોજીક (ધોરણ 12 સાયન્સ)
# ==========================================
folder_path = f"Science/Std12/{current_subject['id']}"
os.makedirs(folder_path, exist_ok=True)

if current_q_type['format_type'] == "array_format":
    file_path = f"{folder_path}/{current_q_type['file_name']}"
    var_name = f"{current_subject['prefix']}{current_q_type['var_suffix']}"
    
    if ch_num == 1 or not os.path.exists(file_path):
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(f"var {var_name} = [\n\n")
            f.write(f"  // ---------------- પ્રકરણ {ch_num}: {ch_name} ----------------\n")
            f.write("  " + output_data + "\n")
    else:
        with open(file_path, 'r', encoding='utf-8') as f:
            existing_content = f.read().rstrip()
        if existing_content.endswith("];"):
            existing_content = existing_content[:-2].rstrip()
            
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(existing_content + "\n\n")
            f.write(f"  // ---------------- પ્રકરણ {ch_num}: {ch_name} ----------------\n")
            f.write("  " + output_data + "\n")

    if ch_num == max_chapters:
        with open(file_path, 'a', encoding='utf-8') as f:
            f.write("\n];\n")

else:
    q_id = current_q_type['id']
    file_path = f"{folder_path}/{current_subject['id']}_{q_id}.js"
    
    if ch_num == 1 or not os.path.exists(file_path):
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(f"var Std12_{current_subject['id']}_{q_id} = {{\n")
            f.write(f'"{ch_num}": ' + output_data + '\n')
    else:
        with open(file_path, 'r', encoding='utf-8') as f:
            existing_content = f.read().rstrip()
        if existing_content.endswith("};"):
            existing_content = existing_content[:-2].rstrip()
            
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(existing_content + f',\n"{ch_num}": ' + output_data + '\n')

    if ch_num == max_chapters:
        with open(file_path, 'a', encoding='utf-8') as f:
            f.write("\n};\n")

# ==========================================
# ટ્રાન્ઝિશન લોજીક (પ્રકરણ -> પ્રશ્ન પ્રકાર -> વિષય)
# ==========================================
tracker['current_chapter'] = ch_num + 1
tracker['current_type_index'] = type_idx
tracker['current_subject_index'] = sub_idx
tracker['status'] = "in_progress"

if tracker['current_chapter'] > max_chapters:
    tracker['current_chapter'] = 1
    tracker['current_type_index'] += 1

if tracker['current_type_index'] >= len(question_types):
    print(f"🎉 ધોરણ 12 {current_subject['guj_name']} વિષય પૂર્ણ થયો!", flush=True)
    tracker['current_type_index'] = 0
    tracker['current_subject_index'] += 1
    
    if tracker['current_subject_index'] >= len(science_subjects):
        print("🎉 ધોરણ 12 સાયન્સના તમામ વિષયોનું ઓટોમેશન પૂર્ણ થયું!", flush=True)
        tracker['status'] = "completed"
        tracker['current_subject_index'] -= 1

os.makedirs('system', exist_ok=True)
with open(tracker_path, 'w', encoding='utf-8') as f:
    json.dump(tracker, f, indent=4)

print("🎉 Task Completed Successfully!", flush=True)
