import json
import os
import sys

# Define 52 clinical-grade formal medical terms with high-frequency colloquial counterparts across 6 languages
COLLOQUIAL_DATA = [
    {
        "english": "otitis media",
        "informal_english": ["middle ear infection", "ear infection"],
        "translations": {
            "Spanish": {"formal": "otitis media", "informal": ["infección del oído medio", "infección de oído"]},
            "Vietnamese": {"formal": "viêm tai giữa", "informal": ["nhiễm trùng tai giữa", "nhiễm trùng tai"]},
            "German": {"formal": "Mittelohrentzündung", "informal": ["Mittelohrentzündung", "Ohrenentzündung"]},
            "Arabic": {"formal": "التهاب الأذن الوسطى", "informal": ["التهاب الأذن الوسطى", "التهاب الأذن"]},
            "Japanese": {"formal": "中耳炎", "informal": ["中耳炎", "耳の感染症"]},
            "Hindi": {"formal": "मध्यकर्णशोथ", "informal": ["मध्य कान का संक्रमण", "कान का संक्रमण"]}
        },
        "description": "An inflammatory disease of the middle ear."
    },
    {
        "english": "gastroenteritis",
        "informal_english": ["stomach flu", "gastro", "stomach bug"],
        "translations": {
            "Spanish": {"formal": "gastroenteritis", "informal": ["gripe estomacal", "gastro", "bicho estomacal"]},
            "Vietnamese": {"formal": "viêm dạ dày ruột", "informal": ["cúm dạ dày", "bệnh đường ruột", "nhiễm trùng tiêu hóa"]},
            "German": {"formal": "Magen-Darm-Grippe (Gastroenteritis)", "informal": ["Magen-Darm-Grippe", "Magen-Darm-Infekt", "Magen-Darm"]},
            "Arabic": {"formal": "التهاب المعدة والأمعاء", "informal": ["أنفلونزا المعدة", "التهاب الأمعاء", "نزلة معوية"]},
            "Japanese": {"formal": "胃腸炎", "informal": ["お腹의風邪", "胃腸炎", "お腹の虫"]},
            "Hindi": {"formal": "गैस्ट्रोएंटेराइटिस", "informal": ["पेट का फ्लू", "पेट की खराबी", "पेट में इन्फेक्शन"]}
        },
        "description": "Inflammation of the stomach and intestines, typically resulting from bacterial toxins or viral infection."
    },
    {
        "english": "dyspnea",
        "informal_english": ["shortness of breath", "trouble breathing", "breathlessness"],
        "translations": {
            "Spanish": {"formal": "disnea", "informal": ["dificultad para respirar", "falta de aire", "ahogo"]},
            "Vietnamese": {"formal": "khó thở", "informal": ["hụt hơi", "khó thở", "thở dốc"]},
            "German": {"formal": "Dyspnoe", "informal": ["Kurzatmigkeit", "Atemnot", "Schweratmigkeit"]},
            "Arabic": {"formal": "ضيق التنفس", "informal": ["ضيق في التنفس", "صعوبة في التنفس", "كتمة"]},
            "Japanese": {"formal": "呼吸困難", "informal": ["息切れ", "息苦しさ", "息が荒い"]},
            "Hindi": {"formal": "डिस्पनिया", "informal": ["साँस फूलना", "साँस लेने में तकलीफ", "साँस की कमी"]}
        },
        "description": "Difficult or labored breathing."
    },
    {
        "english": "myocardial infarction",
        "informal_english": ["heart attack"],
        "translations": {
            "Spanish": {"formal": "infarto de miocardio", "informal": ["ataque al corazón"]},
            "Vietnamese": {"formal": "nhồi máu cơ tim", "informal": ["đột quỵ tim", "đau tim"]},
            "German": {"formal": "Myokardinfarkt", "informal": ["Herzinfarkt"]},
            "Arabic": {"formal": "احتشاء عضلة القلب", "informal": ["نوبة قلبية"]},
            "Japanese": {"formal": "心筋梗塞", "informal": ["心臓麻痺", "心臓発作"]},
            "Hindi": {"formal": "मायोकार्डियल इन्फार्क्शन", "informal": ["दिल का दौरा"]}
        },
        "description": "Another term for heart attack."
    },
    {
        "english": "syncope",
        "informal_english": ["fainting", "passed out", "blackout"],
        "translations": {
            "Spanish": {"formal": "síncope", "informal": ["desmayo", "desvanecimiento", "pérdida de conocimiento"]},
            "Vietnamese": {"formal": "ngất xỉu", "informal": ["ngất", "bất tỉnh", "xỉu"]},
            "German": {"formal": "Synkope", "informal": ["Ohnmacht", "Kreislaufkollaps", "Schwarzwerden vor den Augen"]},
            "Arabic": {"formal": "إغماء", "informal": ["إغماء", "فقدان الوعي", "غيبوبة خفيفة"]},
            "Japanese": {"formal": "失神", "informal": ["気絶", "意識を失う", "目の前が真っ暗になる"]},
            "Hindi": {"formal": "मूर्च्छा", "informal": ["बेहोश होना", "चक्कर खाकर गिरना", "अंधेरा छाना"]}
        },
        "description": "Temporary loss of consciousness caused by a fall in blood pressure."
    },
    {
        "english": "epistaxis",
        "informal_english": ["nosebleed", "bloody nose"],
        "translations": {
            "Spanish": {"formal": "epistaxis", "informal": ["sangrado de nariz", "hemorragia nasal"]},
            "Vietnamese": {"formal": "chảy máu cam", "informal": ["chảy máu mũi", "máu cam"]},
            "German": {"formal": "Epistaxis", "informal": ["Nasenbluten", "blutende Nase"]},
            "Arabic": {"formal": "رعاف", "informal": ["نزيف الأنف", "رعاف"]},
            "Japanese": {"formal": "鼻出血", "informal": ["鼻血", "鼻から血が出る"]},
            "Hindi": {"formal": "नकसीर", "informal": ["नाक से खून बहना", "नकसीर"]}
        },
        "description": "Bleeding from the nose."
    },
    {
        "english": "pharyngitis",
        "informal_english": ["sore throat", "strep throat"],
        "translations": {
            "Spanish": {"formal": "faringitis", "informal": ["dolor de garganta", "faringitis estreptocócica"]},
            "Vietnamese": {"formal": "viêm họng", "informal": ["đau họng", "viêm họng liên cầu khuẩn"]},
            "German": {"formal": "Pharyngitis", "informal": ["Halsschmerzen", "Halsentzündung"]},
            "Arabic": {"formal": "التهاب البلعوم", "informal": ["احتقان الحلق", "التهاب الحلق"]},
            "Japanese": {"formal": "咽頭炎", "informal": ["喉の痛み", "のどの腫れ"]},
            "Hindi": {"formal": "ग्रसनीशोथ", "informal": ["गले में खराश", "गला खराब होना"]}
        },
        "description": "Inflammation of the pharynx, causing a sore throat."
    },
    {
        "english": "pertussis",
        "informal_english": ["whooping cough"],
        "translations": {
            "Spanish": {"formal": "tos ferina", "informal": ["tos convulsa"]},
            "Vietnamese": {"formal": "bệnh ho gà", "informal": ["ho gà"]},
            "German": {"formal": "Pertussis", "informal": ["Keuchhusten"]},
            "Arabic": {"formal": "السعال الديكي", "informal": ["سعال ديكي"]},
            "Japanese": {"formal": "百日咳", "informal": ["百日ぜき"]},
            "Hindi": {"formal": "काली खांसी", "informal": ["कुकुर खांसी"]}
        },
        "description": "A highly contagious respiratory disease."
    },
    {
        "english": "varicella",
        "informal_english": ["chickenpox"],
        "translations": {
            "Spanish": {"formal": "varicela", "informal": ["lepra", "peste cristal"]},
            "Vietnamese": {"formal": "bệnh thủy đậu", "informal": ["trái rạ", "thủy đậu"]},
            "German": {"formal": "Varizellen", "informal": ["Windpocken"]},
            "Arabic": {"formal": "جدري الماء", "informal": ["جديري الماء"]},
            "Japanese": {"formal": "水痘", "informal": ["水疱瘡"]},
            "Hindi": {"formal": "वरिसेला", "informal": ["छोटी माता", "चेचक"]}
        },
        "description": "A highly contagious viral infection causing an itchy, blister-like rash on the skin."
    },
    {
        "english": "allergic rhinitis",
        "informal_english": ["hay fever"],
        "translations": {
            "Spanish": {"formal": "rinitis alérgica", "informal": ["fiebre del heno"]},
            "Vietnamese": {"formal": "viêm mũi dị ứng", "informal": ["dị ứng thời tiết"]},
            "German": {"formal": "allergische Rhinitis", "informal": ["Heuschnupfen"]},
            "Arabic": {"formal": "التهاب الأنف التحسسي", "informal": ["حمى القش"]},
            "Japanese": {"formal": "アレルギー性鼻炎", "informal": ["花粉症"]},
            "Hindi": {"formal": "एलर्जिक राइनाइटिस", "informal": ["हे फीवर", "पराग ज्वर"]}
        },
        "description": "Inflammation of the nose, most commonly caused by an allergy."
    },
    {
        "english": "fracture",
        "informal_english": ["broken bone", "crack"],
        "translations": {
            "Spanish": {"formal": "fractura", "informal": ["hueso roto", "fisura"]},
            "Vietnamese": {"formal": "gãy xương", "informal": ["bể xương", "nứt xương"]},
            "German": {"formal": "Fraktur", "informal": ["Knochenbruch", "Riss"]},
            "Arabic": {"formal": "كسر", "informal": ["عظم مكسور", "شرخ"]},
            "Japanese": {"formal": "骨折", "informal": ["骨折", "ひび"]},
            "Hindi": {"formal": "अस्थि-भंग", "informal": ["हड्डी टूटना", "दरार"]}
        },
        "description": "The cracking or breaking of a hard object or material, especially a bone."
    },
    {
        "english": "renal calculi",
        "informal_english": ["kidney stones"],
        "translations": {
            "Spanish": {"formal": "cálculos renales", "informal": ["piedras en los riñones"]},
            "Vietnamese": {"formal": "sỏi thận", "informal": ["đá trong thận"]},
            "German": {"formal": "Nierensteine", "informal": ["Nierensteine"]},
            "Arabic": {"formal": "حصى الكلى", "informal": ["حصوات الكلى"]},
            "Japanese": {"formal": "腎結石", "informal": ["尿路結石"]},
            "Hindi": {"formal": "गुर्दे की पथरी", "informal": ["किडनी की पथरी"]}
        },
        "description": "A hard mass formed in the kidneys."
    },
    {
        "english": "influenza",
        "informal_english": ["the flu", "flu"],
        "translations": {
            "Spanish": {"formal": "influenza", "informal": ["la gripe", "gripe"]},
            "Vietnamese": {"formal": "bệnh cúm", "informal": ["cảm cúm", "cúm"]},
            "German": {"formal": "Influenza", "informal": ["echte Grippe", "Grippe"]},
            "Arabic": {"formal": "الإنفلونزا", "informal": ["الإنفلونزا", "الرشح"]},
            "Japanese": {"formal": "インフルエンザ", "informal": ["インフル"]},
            "Hindi": {"formal": "इन्फ्लूएंजा", "informal": ["फ्लू"]}
        },
        "description": "A highly contagious viral infection of the respiratory passages."
    },
    {
        "english": "hyperpyrexia",
        "informal_english": ["high fever", "burning up"],
        "translations": {
            "Spanish": {"formal": "hiperpirexia", "informal": ["fiebre muy alta", "quemando de fiebre"]},
            "Vietnamese": {"formal": "sốt cao co giật", "informal": ["sốt cao", "nóng hầm hập"]},
            "German": {"formal": "Hyperpyrexie", "informal": ["hohes Fieber", "glühend heiß"]},
            "Arabic": {"formal": "فرط السخونة", "informal": ["حمى شديدة", "جسم حار جدا"]},
            "Japanese": {"formal": "超高熱", "informal": ["高熱", "体が燃えるように熱い"]},
            "Hindi": {"formal": "अतिताप", "informal": ["तेज बुखार", "तप रहा शरीर"]}
        },
        "description": "An exceptionally high fever."
    },
    {
        "english": "bronchitis",
        "informal_english": ["chest cold"],
        "translations": {
            "Spanish": {"formal": "bronquitis", "informal": ["resfriado de pecho"]},
            "Vietnamese": {"formal": "viêm phế quản", "informal": ["cảm lạnh phế quản"]},
            "German": {"formal": "Bronchitis", "informal": ["Brustverkältung"]},
            "Arabic": {"formal": "التهاب الشعب الهوائية", "informal": ["برد في الصدر"]},
            "Japanese": {"formal": "気管支炎", "informal": ["胸の風邪"]},
            "Hindi": {"formal": "ब्रोंकाइटिस", "informal": ["सीने में ठंड"]}
        },
        "description": "Inflammation of the mucous membrane in the bronchial tubes."
    },
    {
        "english": "conjunctivitis",
        "informal_english": ["pink eye", "red eye"],
        "translations": {
            "Spanish": {"formal": "conjuntivitis", "informal": ["ojo rosa", "ojo rojo"]},
            "Vietnamese": {"formal": "viêm kết mạc", "informal": ["đau mắt đỏ", "đỏ mắt"]},
            "German": {"formal": "Konjunktivitis", "informal": ["Bindehautentzündung", "rotes Auge"]},
            "Arabic": {"formal": "التهاب الملتحمة", "informal": ["الرمد الربيعي", "عين وردية"]},
            "Japanese": {"formal": "結膜炎", "informal": ["はやり目", "赤い目"]},
            "Hindi": {"formal": "नेत्रश्लेष्मलाशोथ", "informal": ["आँख आना", "लाल आँख"]}
        },
        "description": "Inflammation of the conjunctiva of the eye."
    },
    {
        "english": "dyspepsia",
        "informal_english": ["indigestion", "heartburn"],
        "translations": {
            "Spanish": {"formal": "dispepsia", "informal": ["indigestión", "acidez de estómago"]},
            "Vietnamese": {"formal": "khó tiêu", "informal": ["đầy bụng", "ợ chua"]},
            "German": {"formal": "Dyspepsie", "informal": ["Verdauungsstörung", "Sodbrennen"]},
            "Arabic": {"formal": "عسر الهضم", "informal": ["عسر الهضم", "حرقة المعدة"]},
            "Japanese": {"formal": "消化不良", "informal": ["消化不良", "胸焼け"]},
            "Hindi": {"formal": "अपच", "informal": ["बदहजमी", "सीने में जलन"]}
        },
        "description": "Indigestion."
    },
    {
        "english": "pruritus",
        "informal_english": ["itching", "itchy skin"],
        "translations": {
            "Spanish": {"formal": "prurito", "informal": ["picazón", "picor de piel"]},
            "Vietnamese": {"formal": "ngứa", "informal": ["ngứa da", "ngứa ngáy"]},
            "German": {"formal": "Pruritus", "informal": ["Juckreiz", "juckende Haut"]},
            "Arabic": {"formal": "حكة", "informal": ["حكة", "حكة جلدية"]},
            "Japanese": {"formal": "掻痒症", "informal": ["かゆみ", "皮膚のかゆみ"]},
            "Hindi": {"formal": "खुजली", "informal": ["खुजली", "खाज"]}
        },
        "description": "Severe itching of the skin."
    },
    {
        "english": "cephalalgia",
        "informal_english": ["headache"],
        "translations": {
            "Spanish": {"formal": "cefalalgia", "informal": ["dolor de cabeza"]},
            "Vietnamese": {"formal": "đau đầu", "informal": ["nhức đầu"]},
            "German": {"formal": "Cephalgie", "informal": ["Kopfschmerzen"]},
            "Arabic": {"formal": "صداع", "informal": ["وجع رأس"]},
            "Japanese": {"formal": "頭痛", "informal": ["頭痛"]},
            "Hindi": {"formal": "शिरःशूल", "informal": ["सिरदर्द"]}
        },
        "description": "Pain in the head."
    },
    {
        "english": "laceration",
        "informal_english": ["cut", "gash", "tear"],
        "translations": {
            "Spanish": {"formal": "laceración", "informal": ["corte", "brecha", "desgarro"]},
            "Vietnamese": {"formal": "vết rách", "informal": ["vết cắt", "vết chém", "vết rách"]},
            "German": {"formal": "Lazeration", "informal": ["Schnittwunde", "Klaffende Wunde", "Riss"]},
            "Arabic": {"formal": "تهتك", "informal": ["جرح", "شق عميق", "تمزق"]},
            "Japanese": {"formal": "裂傷", "informal": ["切り傷", "深い傷", "破れ傷"]},
            "Hindi": {"formal": "विदारण", "informal": ["घाव", "चीरा", "कटाव"]}
        },
        "description": "A deep cut or tear in skin or flesh."
    },
    {
        "english": "contusion",
        "informal_english": ["bruise"],
        "translations": {
            "Spanish": {"formal": "contusión", "informal": ["moretón", "hematoma"]},
            "Vietnamese": {"formal": "vết bầm tím", "informal": ["bầm tím"]},
            "German": {"formal": "Kontusion", "informal": ["Bluterguss", "blauer Fleck"]},
            "Arabic": {"formal": "كدمة", "informal": ["كدمة", "رضة"]},
            "Japanese": {"formal": "打撲傷", "informal": ["青あざ", "打ち身"]},
            "Hindi": {"formal": "भीतरी चोट", "informal": ["नील", "गुम चोट"]}
        },
        "description": "A region of injured tissue or skin in which blood capillaries have been ruptured."
    },
    {
        "english": "urticaria",
        "informal_english": ["hives", "skin rash"],
        "translations": {
            "Spanish": {"formal": "urticaria", "informal": ["ronchas", "erupción cutánea"]},
            "Vietnamese": {"formal": "mày đay", "informal": ["phát ban", "nổi mẩn đỏ"]},
            "German": {"formal": "Urtikaria", "informal": ["Nesselsucht", "Hautausschlag"]},
            "Arabic": {"formal": "شرى", "informal": ["خلايا النحل", "طفح جلدي"]},
            "Japanese": {"formal": "じんましん", "informal": ["蕁麻疹", "湿疹"]},
            "Hindi": {"formal": "शीतपित्त", "informal": ["पित्ती", "लाल चकत्ते"]}
        },
        "description": "A rash of round, red welts on the skin that itch intensely."
    },
    {
        "english": "alopecia",
        "informal_english": ["hair loss", "baldness"],
        "translations": {
            "Spanish": {"formal": "alopecia", "informal": ["caída del cabello", "calvicie"]},
            "Vietnamese": {"formal": "rụng tóc", "informal": ["hói đầu", "rụng tóc"]},
            "German": {"formal": "Alopezie", "informal": ["Haarausfall", "Glatzenbildung"]},
            "Arabic": {"formal": "ثعلبة", "informal": ["تساقط الشعر", "صلع"]},
            "Japanese": {"formal": "脱毛症", "informal": ["抜け毛", "ハゲ"]},
            "Hindi": {"formal": "खालित्य", "informal": ["बालों का झड़ना", "गंजापन"]}
        },
        "description": "Baldness; hair loss."
    },
    {
        "english": "insomnia",
        "informal_english": ["trouble sleeping", "sleeplessness"],
        "translations": {
            "Spanish": {"formal": "insomnio", "informal": ["problemas para dormir", "falta de sueño"]},
            "Vietnamese": {"formal": "mất ngủ", "informal": ["khó ngủ", "thiếu ngủ"]},
            "German": {"formal": "Insomnie", "informal": ["Schlafstörungen", "Schlaflosigkeit"]},
            "Arabic": {"formal": "أرق", "informal": ["صعوبة في النوم", "عدم القدرة على النوم"]},
            "Japanese": {"formal": "不眠症", "informal": ["眠れないこと", "寝不足"]},
            "Hindi": {"formal": "अनिद्रा", "informal": ["नींद न आना", "बेचैनी"]}
        },
        "description": "Habitual sleeplessness."
    },
    {
        "english": "gingivitis",
        "informal_english": ["gum disease", "swollen gums"],
        "translations": {
            "Spanish": {"formal": "gingivitis", "informal": ["enfermedad de las encías", "encías inflamadas"]},
            "Vietnamese": {"formal": "viêm nướu", "informal": ["sưng nướu", "chảy máu chân răng"]},
            "German": {"formal": "Gingivitis", "informal": ["Zahnfleischentzündung", "geschwollenes Zahnfleisch"]},
            "Arabic": {"formal": "التهاب اللثة", "informal": ["مرض اللثة", "لثة منتفخة"]},
            "Japanese": {"formal": "歯肉炎", "informal": ["歯周病", "歯茎の腫れ"]},
            "Hindi": {"formal": "मसूड़े की सूजन", "informal": ["मसूड़ों की बीमारी", "सूजे हुए मसूड़े"]}
        },
        "description": "Inflammation of the gums."
    },
    {
        "english": "edema",
        "informal_english": ["swelling", "fluid retention"],
        "translations": {
            "Spanish": {"formal": "edema", "informal": ["hinchazón", "retención de líquidos"]},
            "Vietnamese": {"formal": "phù nề", "informal": ["sưng phù", "tích nước"]},
            "German": {"formal": "Ödem", "informal": ["Schwellung", "Wasseransammlung"]},
            "Arabic": {"formal": "وذمة", "informal": ["تورم", "احتباس السوائل"]},
            "Japanese": {"formal": "浮腫", "informal": ["むくみ", "水がたまる"]},
            "Hindi": {"formal": "सूजन", "informal": ["सूजन", "द्रव प्रतिधारण"]}
        },
        "description": "A condition characterized by an excess of watery fluid collecting in the cavities or tissues of the body."
    },
    {
        "english": "vomiting",
        "informal_english": ["throwing up", "vomiting", "sick to stomach"],
        "translations": {
            "Spanish": {"formal": "vómitos", "informal": ["vomitar", "devolver", "malo del estómago"]},
            "Vietnamese": {"formal": "nôn mửa", "informal": ["ói", "nôn", "mắc ói"]},
            "German": {"formal": "Erbrechen", "informal": ["Übergeben", "Kotzen", "schlecht im Magen"]},
            "Arabic": {"formal": "قيء", "informal": ["استفراغ", "ترجيع", "تعبان في المعدة"]},
            "Japanese": {"formal": "嘔吐", "informal": ["吐くこと", "戻すこと", "お腹が気持ち悪い"]},
            "Hindi": {"formal": "वमन", "informal": ["उल्टी होना", "उल्टी", "जी मिचलाना"]}
        },
        "description": "Ejecting matter from the stomach through the mouth."
    },
    {
        "english": "nausea",
        "informal_english": ["feeling sick", "sick to my stomach"],
        "translations": {
            "Spanish": {"formal": "náuseas", "informal": ["ganas de vomitar", "revuelto del estómago"]},
            "Vietnamese": {"formal": "buồn nôn", "informal": ["nôn nao", "mắc ói"]},
            "German": {"formal": "Übelkeit", "informal": ["Unwohlsein", "Flaues Gefühl im Magen"]},
            "Arabic": {"formal": "غثيان", "informal": ["لوعة", "غثيان في المعدة"]},
            "Japanese": {"formal": "吐き気", "informal": ["気持ち悪さ", "吐き気がする"]},
            "Hindi": {"formal": "मतली", "informal": ["उबकाई आना", "जी घबराना"]}
        },
        "description": "A feeling of loathing; temporary stomach distress."
    },
    {
        "english": "haematuria",
        "informal_english": ["blood in urine"],
        "translations": {
            "Spanish": {"formal": "hematuria", "informal": ["sangre en la orina"]},
            "Vietnamese": {"formal": "tiểu máu", "informal": ["máu trong nước tiểu"]},
            "German": {"formal": "Hämaturie", "informal": ["Blut im Urin"]},
            "Arabic": {"formal": "بيلة دموية", "informal": ["دم في البول"]},
            "Japanese": {"formal": "血尿", "informal": ["尿に血が混じる"]},
            "Hindi": {"formal": "रक्तमूत्रता", "informal": ["पेशाब में खून आना"]}
        },
        "description": "The presence of blood in urine."
    },
    {
        "english": "diarrhoea",
        "informal_english": ["the runs", "runny tummy", "loose stools"],
        "translations": {
            "Spanish": {"formal": "diarrea", "informal": ["cagalera", "flojera de estómago", "heces sueltas"]},
            "Vietnamese": {"formal": "tiêu chảy", "informal": ["tào tháo đuổi", "đi ngoài", "phân lỏng"]},
            "German": {"formal": "Diarrhö", "informal": ["Flitzekacke", "Dünnpfiff", "flüssiger Stuhl"]},
            "Arabic": {"formal": "إسهال", "informal": ["إسهال", "مغص مع إسهال", "براز سائل"]},
            "Japanese": {"formal": "下痢", "informal": ["お腹がゆるい", "下痢", "軟便"]},
            "Hindi": {"formal": "अतिसार", "informal": ["दस्त", "पेट चलना", "ढीला मल"]}
        },
        "description": "A condition in which feces are discharged from the bowels frequently and in a liquid form."
    },
    {
        "english": "dysphagia",
        "informal_english": ["trouble swallowing", "difficulty swallowing"],
        "translations": {
            "Spanish": {"formal": "disfagia", "informal": ["problemas para tragar", "dificultad para tragar"]},
            "Vietnamese": {"formal": "khó nuốt", "informal": ["nghẹn", "vướng họng"]},
            "German": {"formal": "Dysphagie", "informal": ["Schluckbeschwerden", "Schluckprobleme"]},
            "Arabic": {"formal": "عسر البلع", "informal": ["صعوبة في البلع", "مشاكل في البلع"]},
            "Japanese": {"formal": "嚥下障害", "informal": ["飲み込みにくさ", "喉がつまること"]},
            "Hindi": {"formal": "निगलने में कठिनाई", "informal": ["निगलने में तकलीफ", "गले में अटकना"]}
        },
        "description": "Difficulty or discomfort in swallowing."
    },
    {
        "english": "hypertension",
        "informal_english": ["high blood pressure"],
        "translations": {
            "Spanish": {"formal": "hipertensión", "informal": ["presión alta"]},
            "Vietnamese": {"formal": "cao huyết áp", "informal": ["huyết áp cao"]},
            "German": {"formal": "Hypertonie", "informal": ["Bluthochdruck"]},
            "Arabic": {"formal": "ارتفاع ضغط الدم", "informal": ["ضغط دم مرتفع"]},
            "Japanese": {"formal": "高血圧", "informal": ["血圧が高いこと"]},
            "Hindi": {"formal": "उच्च रक्तचाप", "informal": ["हाई ब्लड प्रेशर"]}
        },
        "description": "Abnormally high blood pressure."
    },
    {
        "english": "hypotension",
        "informal_english": ["low blood pressure"],
        "translations": {
            "Spanish": {"formal": "hipotensión", "informal": ["presión baja"]},
            "Vietnamese": {"formal": "huyết áp thấp", "informal": ["huyết áp thấp"]},
            "German": {"formal": "Hypotonie", "informal": ["niedriger Blutdruck"]},
            "Arabic": {"formal": "انخفاض ضغط الدم", "informal": ["ضغط دم منخفض"]},
            "Japanese": {"formal": "低血圧", "informal": ["血圧が低いこと"]},
            "Hindi": {"formal": "निम्न रक्तचाप", "informal": ["लो ब्लड प्रेशर"]}
        },
        "description": "Abnormally low blood pressure."
    },
    {
        "english": "vertigo",
        "informal_english": ["dizziness", "spinning sensation"],
        "translations": {
            "Spanish": {"formal": "vértigo", "informal": ["mareo", "sensación de que todo da vueltas"]},
            "Vietnamese": {"formal": "chóng mặt", "informal": ["chóng mặt", "quay cuồng"]},
            "German": {"formal": "Vertigo", "informal": ["Schwindel", "Drehschwindel"]},
            "Arabic": {"formal": "دوار", "informal": ["دوخة", "احساس بالدوران"]},
            "Japanese": {"formal": "めまい", "informal": ["めまい", "目が回ること"]},
            "Hindi": {"formal": "चक्कर आना", "informal": ["चक्कर", "घूमने की अनुभूति"]}
        },
        "description": "A sensation of whirling and loss of balance."
    },
    {
        "english": "tinnitus",
        "informal_english": ["ringing in ears", "ringing noise"],
        "translations": {
            "Spanish": {"formal": "tinnitus", "informal": ["zumbido en los oídos", "pitido en el oído"]},
            "Vietnamese": {"formal": "ù tai", "informal": ["tiếng ve kêu trong tai", "tiếng ù tai"]},
            "German": {"formal": "Tinnitus", "informal": ["Ohrensausen", "Pfeifen im Ohr"]},
            "Arabic": {"formal": "طنين", "informal": ["طنين في الأذن", "وش في الأذن"]},
            "Japanese": {"formal": "耳鳴り", "informal": ["耳鳴り", "キーンとする音"]},
            "Hindi": {"formal": "कर्णक्ष्वेड", "informal": ["कान बजना", "कानों में सायं-सायं होना"]}
        },
        "description": "Ringing or buzzing in the ears."
    },
    {
        "english": "tremor",
        "informal_english": ["shaking", "shakes"],
        "translations": {
            "Spanish": {"formal": "temblor", "informal": ["tembleque", "tirones"]},
            "Vietnamese": {"formal": "run", "informal": ["bị run", "co giật nhẹ"]},
            "German": {"formal": "Tremor", "informal": ["Zittern", "Zittern der Hände"]},
            "Arabic": {"formal": "رعشة", "informal": ["رجفة", "ارتعاش"]},
            "Japanese": {"formal": "震え", "informal": ["手足の震え", "震え"]},
            "Hindi": {"formal": "कंपन", "informal": ["कंपकंपी", "कांपना"]}
        },
        "description": "An involuntary quivering movement."
    },
    {
        "english": "fatigue",
        "informal_english": ["exhaustion", "tiredness", "feeling run down"],
        "translations": {
            "Spanish": {"formal": "fatiga", "informal": ["agotamiento", "cansancio", "estar derrengado"]},
            "Vietnamese": {"formal": "mệt mỏi", "informal": ["kiệt sức", "mệt rã rời", "đuối sức"]},
            "German": {"formal": "Fatigue", "informal": ["Erschöpfung", "Müdigkeit", "Abgeschlagenheit"]},
            "Arabic": {"formal": "إعياء", "informal": ["إرهاق شديد", "تعب", "خمول"]},
            "Japanese": {"formal": "疲労", "informal": ["倦態感", "お疲れ", "体がだるいこと"]},
            "Hindi": {"formal": "थकान", "informal": ["थकावट", "कमजोरी", "सुस्ती"]}
        },
        "description": "Extreme tiredness resulting from mental or physical exertion or illness."
    },
    {
        "english": "spasm",
        "informal_english": ["cramp", "muscle twitch"],
        "translations": {
            "Spanish": {"formal": "espasmo", "informal": ["calambre", "tirón muscular"]},
            "Vietnamese": {"formal": "co thắt", "informal": ["chuột rút", "co giật cơ"]},
            "German": {"formal": "Spasmus", "informal": ["Krampf", "Muskelzucken"]},
            "Arabic": {"formal": "تشنج", "informal": ["تشنج عضلي", "تقلص عضلي"]},
            "Japanese": {"formal": "痙攣", "informal": ["けいれん", "つること"]},
            "Hindi": {"formal": "ऐंठन", "informal": ["ऐंठन", "मांसपेशियों का खिंचाव"]}
        },
        "description": "A sudden involuntary muscular contraction or convulsive movement."
    },
    {
        "english": "dysuria",
        "informal_english": ["painful urination", "burning when peeing"],
        "translations": {
            "Spanish": {"formal": "disuria", "informal": ["dolor al orinar", "ardor al hacer pis"]},
            "Vietnamese": {"formal": "tiểu buốt", "informal": ["tiểu rát", "buốt khi đi tiểu"]},
            "German": {"formal": "Dysurie", "informal": ["schmerzhaftes Wasserlassen", "Brennen beim Urinieren"]},
            "Arabic": {"formal": "عسر البول", "informal": ["ألم أثناء التبول", "حرقان عند التبول"]},
            "Japanese": {"formal": "排尿困難", "informal": ["排尿時の痛み", "おしっこするときの痛み"]},
            "Hindi": {"formal": "मूत्रकृच्छ्र", "informal": ["पेशाब में दर्द", "पेशाब में जलन"]}
        },
        "description": "Painful or difficult urination."
    },
    {
        "english": "clavicle",
        "informal_english": ["collarbone"],
        "translations": {
            "Spanish": {"formal": "clavícula", "informal": ["clavícula"]},
            "Vietnamese": {"formal": "xương đòn", "informal": ["xương quai xanh"]},
            "German": {"formal": "Klavikula", "informal": ["Schlüsselbein"]},
            "Arabic": {"formal": "ترقوة", "informal": ["عظمة الترقوة"]},
            "Japanese": {"formal": "鎖骨", "informal": ["鎖骨"]},
            "Hindi": {"formal": "हंसली", "informal": ["कॉलर की हड्डी"]}
        },
        "description": "Technical term for collarbone."
    },
    {
        "english": "patella",
        "informal_english": ["kneecap"],
        "translations": {
            "Spanish": {"formal": "rótula", "informal": ["rótula", "tapa de la rodilla"]},
            "Vietnamese": {"formal": "xương bánh chè", "informal": ["bánh chè"]},
            "German": {"formal": "Patella", "informal": ["Kniescheibe"]},
            "Arabic": {"formal": "رضفة", "informal": ["صابونة الركبة"]},
            "Japanese": {"formal": "膝蓋骨", "informal": ["膝の皿"]},
            "Hindi": {"formal": "पटैला", "informal": ["घुटने की हड्डी", "कटोरी"]}
        },
        "description": "The kneecap."
    },
    {
        "english": "sternum",
        "informal_english": ["breastbone"],
        "translations": {
            "Spanish": {"formal": "esternón", "informal": ["hueso del pecho"]},
            "Vietnamese": {"formal": "xương ức", "informal": ["xương lồng ngực"]},
            "German": {"formal": "Sternum", "informal": ["Brustbein"]},
            "Arabic": {"formal": "قص", "informal": ["عظمة القص"]},
            "Japanese": {"formal": "胸骨", "informal": ["胸の骨"]},
            "Hindi": {"formal": "उरोस्थि", "informal": ["छाती की हड्डी"]}
        },
        "description": "The breastbone."
    },
    {
        "english": "trachea",
        "informal_english": ["windpipe"],
        "translations": {
            "Spanish": {"formal": "tráquea", "informal": ["tráquea", "tubo de la respiración"]},
            "Vietnamese": {"formal": "khí quản", "informal": ["đường thở chính"]},
            "German": {"formal": "Trachea", "informal": ["Luftröhre"]},
            "Arabic": {"formal": "رغامي", "informal": ["القصبة الهوائية"]},
            "Japanese": {"formal": "気管", "informal": ["気管"]},
            "Hindi": {"formal": "श्वासनली", "informal": ["सांस की नली"]}
        },
        "description": "The windpipe."
    },
    {
        "english": "phlegm",
        "informal_english": ["mucus", "snot"],
        "translations": {
            "Spanish": {"formal": "flema", "informal": ["moco", "mocos"]},
            "Vietnamese": {"formal": "đờm", "informal": ["đờm dãi", "nhớt"]},
            "German": {"formal": "Phlegma", "informal": ["Schleim", "Rotz"]},
            "Arabic": {"formal": "بلغم", "informal": ["مخاط", "مخاط الأنف"]},
            "Japanese": {"formal": "痰", "informal": ["鼻水", "鼻汁"]},
            "Hindi": {"formal": "कफ", "informal": ["बलगम", "बलगम"]}
        },
        "description": "The thick viscous substance secreted by the mucous membranes."
    },
    {
        "english": "abrasion",
        "informal_english": ["scrape", "scratch"],
        "translations": {
            "Spanish": {"formal": "abrasión", "informal": ["raspón", "rasguño"]},
            "Vietnamese": {"formal": "vết trầy xước", "informal": ["vết xước", "trầy da"]},
            "German": {"formal": "Abrasion", "informal": ["Schürfwunde", "Kratzer"]},
            "Arabic": {"formal": "سحج", "informal": ["خدش", "جرح سطحي"]},
            "Japanese": {"formal": "擦過傷", "informal": ["擦り傷", "かき傷"]},
            "Hindi": {"formal": "अपघर्षण", "informal": ["खरोंच", "रगड़"]}
        },
        "description": "An area damaged by scraping or wearing away."
    },
    {
        "english": "pyrexia",
        "informal_english": ["fever", "high temperature"],
        "translations": {
            "Spanish": {"formal": "pirexia", "informal": ["fiebre", "temperatura alta"]},
            "Vietnamese": {"formal": "sốt", "informal": ["sốt", "nhiệt độ cao"]},
            "German": {"formal": "Pyrexie", "informal": ["Fieber", "hohe Temperatur"]},
            "Arabic": {"formal": "حمى", "informal": ["حرارة مرتفعة", "سخونة"]},
            "Japanese": {"formal": "発熱", "informal": ["熱", "高熱"]},
            "Hindi": {"formal": "ज्वर", "informal": ["बुखार", "तेज तापमान"]}
        },
        "description": "Fever."
    },
    {
        "english": "obstipation",
        "informal_english": ["severe constipation"],
        "translations": {
            "Spanish": {"formal": "obstipación", "informal": ["estreñimiento severo"]},
            "Vietnamese": {"formal": "táo bón nặng", "informal": ["táo bón nghiêm trọng"]},
            "German": {"formal": "Obstipation", "informal": ["schwere Verstopfung"]},
            "Arabic": {"formal": "إمساك شديد", "informal": ["إمساك حاد"]},
            "Japanese": {"formal": "重度便秘", "informal": ["ひどい便秘"]},
            "Hindi": {"formal": "कब्ज", "informal": ["गंभीर कब्ज"]}
        },
        "description": "Severe or complete constipation."
    },
    {
        "english": "dysphonia",
        "informal_english": ["hoarseness", "lost voice"],
        "translations": {
            "Spanish": {"formal": "disfonía", "informal": ["ronquera", "voz ronca"]},
            "Vietnamese": {"formal": "khàn giọng", "informal": ["mất giọng", "giọng khàn"]},
            "German": {"formal": "Dysphonie", "informal": ["Heiserkeit", "Stimmverlust"]},
            "Arabic": {"formal": "بحة الصوت", "informal": ["بحة", "فقدان الصوت"]},
            "Japanese": {"formal": "発声障害", "informal": ["声がれ", "声が出ないこと"]},
            "Hindi": {"formal": "स्वरभंग", "informal": ["गला बैठना", "आवाज खोना"]}
        },
        "description": "Difficulty in speaking due to a physical disorder of the mouth, tongue, throat, or vocal cords."
    },
    {
        "english": "erythema",
        "informal_english": ["redness", "skin flushing"],
        "translations": {
            "Spanish": {"formal": "eritema", "informal": ["enrojecimiento", "rubor de piel"]},
            "Vietnamese": {"formal": "ban đỏ", "informal": ["ửng đỏ", "ửng đỏ da"]},
            "German": {"formal": "Erythem", "informal": ["Rötung", "Hautrötung"]},
            "Arabic": {"formal": "حمامي", "informal": ["احمرار", "احمرار الجلد"]},
            "Japanese": {"formal": "紅斑", "informal": ["赤み", "皮膚の赤み"]},
            "Hindi": {"formal": "लालिमा", "informal": ["लालपन", "त्वचा का लाल होना"]}
        },
        "description": "Superficial redness of the skin."
    },
    {
        "english": "stridor",
        "informal_english": ["noisy breathing", "wheezing"],
        "translations": {
            "Spanish": {"formal": "estridor", "informal": ["respiración ruidosa", "silbido al respirar"]},
            "Vietnamese": {"formal": "thở rít", "informal": ["thở khò khè", "tiếng thở rít"]},
            "German": {"formal": "Stridor", "informal": ["pfeifendes Atemgeräusch", "Keuchen"]},
            "Arabic": {"formal": "صرير", "informal": ["صوت صفير عند التنفس", "خرخرة"]},
            "Japanese": {"formal": "喘鳴", "informal": ["ぜーぜーいう呼吸音", "呼吸の雑音"]},
            "Hindi": {"formal": "स्ट्रिडोर", "informal": ["घरघराहट", "साँस से आवाज़ आना"]}
        },
        "description": "A harsh or grating sound in inhalation."
    },
    {
        "english": "hyperhidrosis",
        "informal_english": ["excessive sweating", "sweaty palms"],
        "translations": {
            "Spanish": {"formal": "hiperhidrosis", "informal": ["sudoración excesiva", "manos sudorosas"]},
            "Vietnamese": {"formal": "tăng tiết mồ hôi", "informal": ["đổ mồ hôi nhiều", "mồ hôi trộm"]},
            "German": {"formal": "Hyperhidrose", "informal": ["übermäßiges Schwitzen", "schwitzige Hände"]},
            "Arabic": {"formal": "فرط التعرق", "informal": ["تعرق مفرط", "تعرق اليدين"]},
            "Japanese": {"formal": "多汗症", "informal": ["異常な発汗", "手汗"]},
            "Hindi": {"formal": "अतिस्वेद", "informal": ["बहुत अधिक पसीना आना", "पसीने से तर हाथ"]}
        },
        "description": "Abnormally excessive sweating."
    },
    {
        "english": "dental caries",
        "informal_english": ["tooth decay", "cavity", "rotten tooth"],
        "translations": {
            "Spanish": {"formal": "caries dentales", "informal": ["caries", "diente picado", "diente podrido"]},
            "Vietnamese": {"formal": "sâu răng", "informal": ["sâu răng", "lỗ hổng răng", "răng sún"]},
            "German": {"formal": "Zahnkaries", "informal": ["Karies", "Zahnfäule", "Zahnloch"]},
            "Arabic": {"formal": "تسوس الأسنان", "informal": ["تسوس", "حفرة في السن", "ضرس مسوس"]},
            "Japanese": {"formal": "う蝕", "informal": ["虫歯", "虫歯の穴"]},
            "Hindi": {"formal": "दंत क्षय", "informal": ["दांतों की सड़न", "कैविटी", "सड़ा हुआ दांत"]}
        },
        "description": "Tooth decay or cavities."
    }
]

def main():
    json_path = "dictionary/glossary.json"
    csv_path = "dictionary/glossary.csv"
    
    if not os.path.exists(json_path):
        print(f"[ERROR] glossary.json not found at {json_path}")
        sys.exit(1)
        
    print(f"Loading glossary database from '{json_path}'...")
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    glossary_list = data.get("glossary", [])
    print(f"  Loaded {len(glossary_list)} existing terminology entries.")
    
    # Create lookup map
    lookup = {entry["english"].lower().strip(): entry for entry in glossary_list}
    
    enriched_count = 0
    added_count = 0
    
    for item in COLLOQUIAL_DATA:
        term_key = item["english"].lower().strip()
        if term_key in lookup:
            # Enrich existing entry in place
            entry = lookup[term_key]
            entry["informal_english"] = item["informal_english"]
            
            # Merge/override translations
            existing_trans = entry.get("translations", {})
            for lang, val in item["translations"].items():
                existing_trans[lang] = val
            entry["translations"] = existing_trans
            
            # Update description if empty or generic
            if not entry.get("description") or len(entry.get("description")) < len(item["description"]):
                entry["description"] = item["description"]
                
            enriched_count += 1
        else:
            # Create a completely new entry
            new_entry = {
                "english": item["english"],
                "informal_english": item["informal_english"],
                "translations": item["translations"],
                "description": item["description"]
            }
            glossary_list.append(new_entry)
            lookup[term_key] = new_entry
            added_count += 1
            
    print(f"Enrichment Summary:")
    print(f"  - Enriched existing entries: {enriched_count}")
    print(f"  - Added brand-new entries: {added_count}")
    print(f"  - Total glossary entries: {len(glossary_list)}")
    
    # Save the updated glossary.json
    print(f"Saving updated glossary database to '{json_path}'...")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump({"glossary": glossary_list}, f, indent=2, ensure_ascii=False)
    print("  Save complete.")
    
    # Import export_to_csv to compile the 7-column CSV
    print(f"Compiling 7-column CSV '{csv_path}'...")
    try:
        from demo.import_glossary import load_glossary_json, export_to_csv
        flat_glossary = load_glossary_json(json_path)
        exported_rows = export_to_csv(flat_glossary, csv_path)
        print(f"  Successfully compiled and wrote {exported_rows} multi-lingual translation rows to CSV.")
    except Exception as e:
        print(f"[ERROR] Failed to compile CSV: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
