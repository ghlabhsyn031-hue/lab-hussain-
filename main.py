"""
مختبرات حسين غلاب - نظام الفحوصات الطبية
تطبيق Android بلغة Python + KivyMD
"""
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDFlatButton, MDIconButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import MDList, TwoLineListItem, OneLineListItem
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.bottomnavigation import MDBottomNavigation, MDBottomNavigationItem
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.spinner import MDSpinner
from kivymd.uix.tab import MDTabsBase, MDTabs
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.menu import MDDropdownMenu
from kivy.uix.scrollview import ScrollView
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.utils import get_color_from_hex
from kivy.storage.jsonstore import JsonStore
from kivy.clock import Clock
import json, os, datetime

# ── PDF ──────────────────────────────────────────────────────
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_RIGHT, TA_CENTER, TA_LEFT
from io import BytesIO
import qrcode
import arabic_reshaper
from bidi.algorithm import get_display

# ── WhatsApp ─────────────────────────────────────────────────
try:
    from android.permissions import request_permissions, Permission
    from android import mActivity
    from jnius import autoclass
    ANDROID = True
except:
    ANDROID = False

def ar(t):
    try:
        return get_display(arabic_reshaper.reshape(str(t)))
    except:
        return str(t)

# ── SUBJECTS DATA ─────────────────────────────────────────────
SUBJECTS = [
  {"id":"blood","name":"تحاليل الدم","icon":"🩸",
   "tests":[
     {"id":"cbc","name":"صورة دم كاملة","nameEn":"CBC","price":50,"icon":"💉","fields":[
        {"n":"WBC","ar":"كريات الدم البيضاء","u":"×10³/μL","min":4.5,"max":11.0},
        {"n":"RBC","ar":"كريات الدم الحمراء","u":"×10⁶/μL","min":4.5,"max":5.9},
        {"n":"HGB","ar":"الهيموغلوبين","u":"g/dL","min":13.5,"max":17.5},
        {"n":"HCT","ar":"الهيماتوكريت","u":"%","min":41,"max":53},
        {"n":"MCV","ar":"متوسط حجم الكرية","u":"fL","min":80,"max":100},
        {"n":"MCH","ar":"متوسط هيموغلوبين الكرية","u":"pg","min":27,"max":33},
        {"n":"PLT","ar":"الصفائح الدموية","u":"×10³/μL","min":150,"max":400},
        {"n":"Neutrophil","ar":"المحببات المتعادلة","u":"%","min":55,"max":70},
        {"n":"Lymphocyte","ar":"الخلايا الليمفاوية","u":"%","min":20,"max":40},
     ]},
     {"id":"esr","name":"سرعة الترسيب","nameEn":"ESR","price":25,"icon":"⏱️","fields":[
        {"n":"ESR","ar":"سرعة ترسيب الدم","u":"mm/hr","min":0,"max":20},
     ]},
     {"id":"coag","name":"تخثر الدم","nameEn":"Coagulation","price":30,"icon":"🩹","fields":[
        {"n":"PT","ar":"وقت البروثرومبين","u":"sec","min":11,"max":13.5},
        {"n":"PTT","ar":"زمن الثرومبوبلاستين","u":"sec","min":25,"max":35},
        {"n":"INR","ar":"نسبة التطبيع الدولية","u":"","min":0.8,"max":1.2},
     ]},
   ]},
  {"id":"chem","name":"الكيمياء الحيوية","icon":"⚗️",
   "tests":[
     {"id":"glucose","name":"سكر الدم","nameEn":"Glucose","price":20,"icon":"🍭","fields":[
        {"n":"Fasting","ar":"سكر الصيام","u":"mg/dL","min":70,"max":100},
        {"n":"Random","ar":"سكر عشوائي","u":"mg/dL","min":70,"max":140},
        {"n":"HbA1c","ar":"السكر التراكمي","u":"%","min":4.0,"max":5.7},
     ]},
     {"id":"kidney","name":"وظائف الكلى","nameEn":"Kidney","price":60,"icon":"🫘","fields":[
        {"n":"Urea","ar":"اليوريا","u":"mg/dL","min":17,"max":43},
        {"n":"Creatinine","ar":"الكرياتينين","u":"mg/dL","min":0.6,"max":1.3},
        {"n":"Uric_Acid","ar":"حمض اليوريك","u":"mg/dL","min":3.5,"max":7.2},
        {"n":"eGFR","ar":"معدل الترشيح","u":"mL/min","min":90,"max":999},
     ]},
     {"id":"liver","name":"وظائف الكبد","nameEn":"Liver","price":80,"icon":"🫁","fields":[
        {"n":"Bilirubin_T","ar":"البيليروبين الكلي","u":"mg/dL","min":0.2,"max":1.2},
        {"n":"ALT","ar":"الناقلة ALT","u":"U/L","min":7,"max":40},
        {"n":"AST","ar":"الناقلة AST","u":"U/L","min":10,"max":40},
        {"n":"ALP","ar":"الفوسفاتاز","u":"U/L","min":44,"max":147},
        {"n":"Albumin","ar":"الألبومين","u":"g/dL","min":3.4,"max":5.4},
     ]},
     {"id":"lipid","name":"دهنيات الدم","nameEn":"Lipid Profile","price":70,"icon":"🫀","fields":[
        {"n":"Cholesterol","ar":"الكوليسترول الكلي","u":"mg/dL","min":0,"max":200},
        {"n":"TG","ar":"الدهون الثلاثية","u":"mg/dL","min":0,"max":150},
        {"n":"HDL","ar":"كوليسترول HDL","u":"mg/dL","min":40,"max":999},
        {"n":"LDL","ar":"كوليسترول LDL","u":"mg/dL","min":0,"max":100},
     ]},
   ]},
  {"id":"hormones","name":"الهرمونات","icon":"⚡",
   "tests":[
     {"id":"thyroid","name":"الغدة الدرقية","nameEn":"Thyroid","price":120,"icon":"🦋","fields":[
        {"n":"TSH","ar":"هرمون TSH","u":"mIU/L","min":0.4,"max":4.0},
        {"n":"FT4","ar":"ثيروكسين حر","u":"ng/dL","min":0.8,"max":1.8},
        {"n":"FT3","ar":"T3 الحر","u":"pg/mL","min":2.3,"max":4.2},
     ]},
     {"id":"repro","name":"هرمونات التكاثر","nameEn":"Reproductive","price":150,"icon":"🧬","fields":[
        {"n":"FSH","ar":"FSH","u":"mIU/mL","min":1.5,"max":12.4},
        {"n":"LH","ar":"LH","u":"mIU/mL","min":1.7,"max":8.6},
        {"n":"Prolactin","ar":"البرولاكتين","u":"ng/mL","min":2.0,"max":29.2},
        {"n":"Testosterone","ar":"التستوستيرون","u":"ng/dL","min":270,"max":1070},
     ]},
   ]},
  {"id":"urine","name":"تحليل البول","icon":"🧪",
   "tests":[
     {"id":"ua","name":"تحليل بول كامل","nameEn":"Urinalysis","price":30,"icon":"🔬","fields":[
        {"n":"pH","ar":"الحموضة","u":"","min":4.6,"max":8.0},
        {"n":"SG","ar":"الثقل النوعي","u":"","min":1.005,"max":1.030},
        {"n":"WBC_HPF","ar":"خلايا بيضاء","u":"HPF","min":0,"max":5},
        {"n":"RBC_HPF","ar":"خلايا حمراء","u":"HPF","min":0,"max":2},
        {"n":"Color","ar":"اللون","u":"","t":"txt","normal":"أصفر"},
        {"n":"Protein","ar":"البروتين","u":"","t":"txt","normal":"سلبي"},
        {"n":"Glucose_U","ar":"السكر","u":"","t":"txt","normal":"سلبي"},
     ]},
   ]},
  {"id":"sero","name":"المصلية والمناعة","icon":"🛡️",
   "tests":[
     {"id":"hep","name":"التهاب الكبد","nameEn":"Hepatitis","price":100,"icon":"🔴","fields":[
        {"n":"HBsAg","ar":"مستضد كبد ب","u":"","t":"txt","normal":"سلبي"},
        {"n":"Anti_HCV","ar":"أجسام كبد ج","u":"","t":"txt","normal":"سلبي"},
        {"n":"Anti_HBs","ar":"أجسام كبد ب","u":"IU/L","min":10,"max":999},
     ]},
     {"id":"crp","name":"بروتين CRP","nameEn":"CRP","price":30,"icon":"⚠️","fields":[
        {"n":"CRP","ar":"بروتين CRP","u":"mg/L","min":0,"max":10},
        {"n":"hsCRP","ar":"CRP عالي الحساسية","u":"mg/L","min":0,"max":3},
     ]},
     {"id":"widal","name":"فيدال","nameEn":"Widal","price":35,"icon":"🌡️","fields":[
        {"n":"Typhi_O","ar":"تيفويد O","u":"تيتر","t":"txt","normal":"1:80 أو أقل"},
        {"n":"Typhi_H","ar":"تيفويد H","u":"تيتر","t":"txt","normal":"1:80 أو أقل"},
     ]},
   ]},
  {"id":"vitamins","name":"الفيتامينات","icon":"💊",
   "tests":[
     {"id":"vit","name":"فيتامينات ومعادن","nameEn":"Vitamins","price":150,"icon":"🌞","fields":[
        {"n":"Vit_D","ar":"فيتامين د","u":"ng/mL","min":30,"max":100},
        {"n":"Vit_B12","ar":"فيتامين ب12","u":"pg/mL","min":200,"max":900},
        {"n":"Folic","ar":"حمض الفوليك","u":"ng/mL","min":2.7,"max":17.0},
        {"n":"Iron","ar":"الحديد","u":"μg/dL","min":60,"max":170},
        {"n":"Ferritin","ar":"الفريتين","u":"ng/mL","min":12,"max":300},
        {"n":"Calcium","ar":"الكالسيوم","u":"mg/dL","min":8.6,"max":10.0},
     ]},
   ]},
  {"id":"cardiac","name":"القلب","icon":"❤️",
   "tests":[
     {"id":"troponin","name":"علامات القلب","nameEn":"Cardiac Markers","price":200,"icon":"💗","fields":[
        {"n":"Troponin_I","ar":"تروبونين I","u":"ng/mL","min":0,"max":0.04},
        {"n":"CK_MB","ar":"كيناز القلب CK-MB","u":"U/L","min":0,"max":25},
        {"n":"LDH","ar":"LDH","u":"U/L","min":135,"max":225},
        {"n":"BNP","ar":"BNP","u":"pg/mL","min":0,"max":100},
     ]},
   ]},
  {"id":"micro","name":"الميكروبيولوجيا","icon":"🦠",
   "tests":[
     {"id":"culture","name":"زراعة وحساسية","nameEn":"Culture","price":120,"icon":"🧫","fields":[
        {"n":"Organism","ar":"الكائن الدقيق","u":"","t":"txt","normal":"لا نمو"},
        {"n":"Amox","ar":"أموكسيسيلين","u":"","t":"txt","normal":""},
        {"n":"Cipro","ar":"سيبروفلوكساسين","u":"","t":"txt","normal":""},
        {"n":"Gentamicin","ar":"جنتاميسين","u":"","t":"txt","normal":""},
        {"n":"Ceftriaxone","ar":"سيفترياكسون","u":"","t":"txt","normal":""},
     ]},
     {"id":"malaria","name":"فحص الملاريا","nameEn":"Malaria","price":40,"icon":"🦟","fields":[
        {"n":"Malaria","ar":"فحص الملاريا","u":"","t":"txt","normal":"سلبي"},
     ]},
   ]},
  {"id":"stool","name":"تحليل البراز","icon":"🫙",
   "tests":[
     {"id":"stool","name":"تحليل براز كامل","nameEn":"Stool","price":30,"icon":"🔬","fields":[
        {"n":"Stool_Color","ar":"اللون","u":"","t":"txt","normal":"بني"},
        {"n":"Consistency","ar":"القوام","u":"","t":"txt","normal":"متماسك"},
        {"n":"Blood","ar":"الدم الخفي","u":"","t":"txt","normal":"سلبي"},
        {"n":"Pus","ar":"خلايا صديدية","u":"HPF","min":0,"max":2},
        {"n":"Parasites","ar":"طفيليات","u":"","t":"txt","normal":"سلبي"},
     ]},
   ]},
]

LAB_PHONE = "352454545454"

KV = """
#:import get_color_from_hex kivy.utils.get_color_from_hex
#:import dp kivy.metrics.dp

<HomeScreen>:
    MDBoxLayout:
        orientation: 'vertical'
        md_bg_color: get_color_from_hex('#0a1628')

<NewTestScreen>:
    MDBoxLayout:
        orientation: 'vertical'
        md_bg_color: get_color_from_hex('#0a1628')

<RecordsScreen>:
    MDBoxLayout:
        orientation: 'vertical'
        md_bg_color: get_color_from_hex('#0a1628')

<SubjectsScreen>:
    MDBoxLayout:
        orientation: 'vertical'
        md_bg_color: get_color_from_hex('#0a1628')
"""

def get_flag(val, field):
    try:
        v = float(val)
        mn = field.get('min')
        mx = field.get('max')
        if mn is not None and v < mn: return 'LOW'
        if mx is not None and v > mx: return 'HIGH'
        return 'NORMAL'
    except:
        return 'TEXT'

def generate_pdf(rec, out_path):
    buf = BytesIO()
    C_DARK  = colors.HexColor('#0a1628')
    C_DARK2 = colors.HexColor('#0d1e38')
    C_DARK3 = colors.HexColor('#111f3a')
    C_ACCENT= colors.HexColor('#00d4ff')
    C_GREEN = colors.HexColor('#00c853')
    C_RED   = colors.HexColor('#ff3b5c')
    C_YELLOW= colors.HexColor('#ffab00')
    C_GOLD  = colors.HexColor('#ffd700')
    C_MUTED = colors.HexColor('#5a8ab8')
    C_TEXT  = colors.HexColor('#c8dff5')

    lab_name = rec.get('lab_name', 'مختبرات حسين غلاب')
    lab_phone= rec.get('lab_phone', LAB_PHONE)
    lab_addr = rec.get('lab_addr', 'المملكة العربية السعودية')

    sub = next((s for s in SUBJECTS if s['id']==rec['subject_id']), None)
    test= next((t for t in sub['tests'] if t['id']==rec['test_id']), None) if sub else None

    doc = SimpleDocTemplate(buf, pagesize=A4,
        rightMargin=12*mm, leftMargin=12*mm,
        topMargin=10*mm, bottomMargin=10*mm)
    styles = getSampleStyleSheet()

    def S(nm, **kw):
        s = ParagraphStyle(nm, parent=styles['Normal'])
        for k,v in kw.items(): setattr(s,k,v)
        return s

    S_LAB  = S('lab',  fontSize=17, textColor=C_ACCENT, alignment=TA_RIGHT, fontName='Helvetica-Bold')
    S_SUB  = S('sub',  fontSize=9,  textColor=C_MUTED,  alignment=TA_RIGHT)
    S_LBL  = S('lbl',  fontSize=8,  textColor=C_MUTED,  alignment=TA_RIGHT)
    S_VAL  = S('val',  fontSize=10, textColor=C_TEXT,   alignment=TA_RIGHT, fontName='Helvetica-Bold')
    S_TH   = S('th',   fontSize=9,  textColor=C_ACCENT, alignment=TA_RIGHT, fontName='Helvetica-Bold')
    S_TD   = S('td',   fontSize=9,  textColor=C_TEXT,   alignment=TA_RIGHT)
    S_RES  = S('res',  fontSize=12, textColor=C_ACCENT, alignment=TA_CENTER,fontName='Helvetica-Bold')
    S_FN   = S('fn',   fontSize=8,  textColor=C_GREEN,  alignment=TA_CENTER,fontName='Helvetica-Bold')
    S_FH   = S('fh',   fontSize=8,  textColor=C_RED,    alignment=TA_CENTER,fontName='Helvetica-Bold')
    S_FL   = S('fl',   fontSize=8,  textColor=C_YELLOW, alignment=TA_CENTER,fontName='Helvetica-Bold')
    S_FOOT = S('ft',   fontSize=7,  textColor=C_MUTED,  alignment=TA_RIGHT)
    S_PH   = S('ph',   fontSize=11, textColor=C_ACCENT, alignment=TA_RIGHT, fontName='Helvetica-Bold')
    S_SEC  = S('sec',  fontSize=11, textColor=C_ACCENT, alignment=TA_RIGHT, fontName='Helvetica-Bold')

    story = []
    W = A4[0] - 24*mm

    # QR
    from reportlab.platypus import Image as RLImage
    qr_buf = BytesIO()
    qr = qrcode.QRCode(box_size=3, border=2)
    qr.add_data(lab_phone); qr.make(fit=True)
    qr.make_image(fill_color='#00d4ff', back_color='#0a1628').save(qr_buf, 'PNG')
    qr_buf.seek(0)

    # Header
    h = Table([
        [Paragraph(ar(lab_name), S_LAB), RLImage(qr_buf, 52, 52)],
        [Paragraph(ar(f"📞 {lab_phone}  |  📍 {lab_addr}"), S_SUB), ''],
        [Paragraph(ar(f"مرخص: {rec.get('lab_lic','وزارة الصحة')}"), S_SUB), ''],
    ], colWidths=[W-58, 58])
    h.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,-1),C_DARK),
        ('SPAN',(1,0),(1,2)),('VALIGN',(1,0),(1,2),'MIDDLE'),('ALIGN',(1,0),(1,2),'LEFT'),
        ('LINEBELOW',(0,-1),(-1,-1),2,C_ACCENT),
        ('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),5),
        ('RIGHTPADDING',(0,0),(-1,-1),8),('LEFTPADDING',(0,0),(-1,-1),8),
    ]))
    story.append(h); story.append(Spacer(1,3*mm))

    # Patient info
    info = [
        ('رقم الطلب', rec['req_num']),('اسم المريض', rec['patient_name']),
        ('العمر / الجنس', f"{rec.get('age','-')} / {rec.get('gender','ذكر')}"),
        ('التاريخ', rec['date']),('الطبيب المحول', rec.get('doctor','-') or '-'),
        ('الفاحص', rec.get('tech','-') or '-'),('الهاتف', rec.get('phone','-') or '-'),
        ('السعر', f"{test['price'] if test else '-'} ريال"),
    ]
    cw = W/4
    rows=[]
    for i in range(0, len(info), 4):
        rl=[]; rv=[]
        for lbl,val in info[i:i+4]:
            rl.append(Paragraph(ar(lbl), S_LBL)); rv.append(Paragraph(ar(str(val)), S_VAL))
        while len(rl)<4: rl.append(Paragraph('',S_LBL)); rv.append(Paragraph('',S_VAL))
        rows.append(rl); rows.append(rv)
    pt = Table(rows, colWidths=[cw]*4)
    pt.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,-1),C_DARK2),
        ('BOX',(0,0),(-1,-1),1,C_ACCENT),
        ('INNERGRID',(0,0),(-1,-1),0.3,colors.HexColor('#1e3a5f')),
        ('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),4),
        ('RIGHTPADDING',(0,0),(-1,-1),7),('LEFTPADDING',(0,0),(-1,-1),7),
        ('ALIGN',(0,0),(-1,-1),'RIGHT'),('VALIGN',(0,0),(-1,-1),'MIDDLE'),
    ]))
    story.append(pt); story.append(Spacer(1,3*mm))

    # Test header
    if test:
        th2 = Table([[Paragraph(ar(f"{test.get('icon','')}  {test['name']}"), S_SEC),
                      Paragraph(test['nameEn'], S_TD)]], colWidths=[W*0.65, W*0.35])
        th2.setStyle(TableStyle([
            ('BACKGROUND',(0,0),(-1,-1),colors.HexColor('#0d2248')),
            ('LINEBELOW',(0,0),(-1,-1),2,C_ACCENT),
            ('TOPPADDING',(0,0),(-1,-1),9),('BOTTOMPADDING',(0,0),(-1,-1),9),
            ('RIGHTPADDING',(0,0),(-1,-1),10),('LEFTPADDING',(0,0),(-1,-1),10),
            ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
        ]))
        story.append(th2); story.append(Spacer(1,3*mm))

    # Results table
    if test:
        hdr=[ Paragraph(ar('الاختبار'),S_TH), Paragraph('Symbol',S_TH),
              Paragraph(ar('النتيجة'),S_TH), Paragraph(ar('الوحدة'),S_TH),
              Paragraph(ar('المرجع'),S_TH), Paragraph(ar('التقييم'),S_TH) ]
        res_rows=[hdr]; rstyle=[
            ('BACKGROUND',(0,0),(-1,0),colors.HexColor('#0d2248')),
            ('LINEBELOW',(0,0),(-1,0),2,C_ACCENT),
            ('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6),
            ('RIGHTPADDING',(0,0),(-1,-1),5),('LEFTPADDING',(0,0),(-1,-1),5),
            ('ALIGN',(0,0),(-1,-1),'RIGHT'),('VALIGN',(0,0),(-1,-1),'MIDDLE'),
            ('ALIGN',(1,0),(1,-1),'LEFT'),('ALIGN',(2,0),(2,-1),'CENTER'),('ALIGN',(5,0),(5,-1),'CENTER'),
            ('BOX',(0,0),(-1,-1),1,colors.HexColor('#1e3a5f')),
            ('INNERGRID',(0,0),(-1,-1),0.3,colors.HexColor('#1e3a5f')),
        ]
        results = rec.get('results', {})
        for i,f in enumerate(test['fields']):
            val = results.get(f['n'], '-')
            flag = get_flag(val, f)
            if flag=='NORMAL': fp=Paragraph(ar('✓ طبيعي'),S_FN)
            elif flag=='HIGH':  fp=Paragraph(ar('↑ مرتفع'),S_FH)
            elif flag=='LOW':   fp=Paragraph(ar('↓ منخفض'),S_FL)
            else: fp=Paragraph('-', S_TD)
            ref=f.get('normal','-') if f.get('t')=='txt' else (f"{f.get('min','-')} – {f.get('max','-')}" if f.get('min') is not None else '-')
            res_rows.append([
                Paragraph(ar(f['ar']),S_TD), Paragraph(f['n'],S_TD),
                Paragraph(str(val),S_RES), Paragraph(f.get('u',''),S_TD),
                Paragraph(ar(str(ref)),S_TD), fp
            ])
            bg = C_DARK2 if i%2==0 else C_DARK3
            rstyle.append(('BACKGROUND',(0,i+1),(-1,i+1),bg))
        cws=[W*0.26,W*0.16,W*0.13,W*0.12,W*0.18,W*0.15]
        rt=Table(res_rows, colWidths=cws, repeatRows=1)
        rt.setStyle(TableStyle(rstyle))
        story.append(rt); story.append(Spacer(1,4*mm))

    # Notes
    if rec.get('notes'):
        nt=Table([[Paragraph(ar('📋 ملاحظات'),S_SEC)],[Paragraph(ar(rec['notes']),S_TD)]],colWidths=[W])
        nt.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),colors.HexColor('#0c1e36')),
            ('BOX',(0,0),(-1,-1),1,C_GOLD),('TOPPADDING',(0,0),(-1,-1),7),
            ('BOTTOMPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),9),
            ('LEFTPADDING',(0,0),(-1,-1),9),('ALIGN',(0,0),(-1,-1),'RIGHT')]))
        story.append(nt); story.append(Spacer(1,3*mm))

    # Signatures
    sg=Table([[Paragraph(ar(f"توقيع الفاحص: {rec.get('tech','__________') or '__________'}"),S_TD),
               Paragraph(ar('توقيع مدير المختبر: __________'),S_TD)]],colWidths=[W/2,W/2])
    sg.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),C_DARK2),
        ('LINEABOVE',(0,0),(-1,-1),1,colors.HexColor('#1e3a5f')),
        ('TOPPADDING',(0,0),(-1,-1),10),('BOTTOMPADDING',(0,0),(-1,-1),10),
        ('RIGHTPADDING',(0,0),(-1,-1),9),('LEFTPADDING',(0,0),(-1,-1),9),
        ('ALIGN',(0,0),(-1,-1),'RIGHT')]))
    story.append(sg); story.append(Spacer(1,3*mm))

    # Footer QR
    fqr_buf=BytesIO()
    fqr=qrcode.QRCode(box_size=3,border=2)
    fqr.add_data(f"{rec['req_num']}|{lab_phone}")
    fqr.make(fit=True)
    fqr.make_image(fill_color='#00d4ff',back_color='#0a1628').save(fqr_buf,'PNG')
    fqr_buf.seek(0)
    ft=Table([
        [Paragraph(ar(lab_name),S_PH), RLImage(fqr_buf,48,48)],
        [Paragraph(ar(f"📞 {lab_phone}"),S_PH),''],
        [Paragraph(ar(f"هذه النتائج سرية • يرجى مراجعة الطبيب"),S_FOOT),''],
        [Paragraph(ar(f"طُبع: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}"),S_FOOT),''],
    ],colWidths=[W-54,54])
    ft.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,-1),colors.HexColor('#050f20')),
        ('LINEABOVE',(0,0),(-1,-1),2,colors.HexColor('#1e3a5f')),
        ('SPAN',(1,0),(1,3)),('VALIGN',(1,0),(1,3),'MIDDLE'),('ALIGN',(1,0),(1,3),'LEFT'),
        ('TOPPADDING',(0,0),(-1,-1),4),('BOTTOMPADDING',(0,0),(-1,-1),4),
        ('RIGHTPADDING',(0,0),(-1,-1),9),('LEFTPADDING',(0,0),(-1,-1),9),
        ('ALIGN',(0,0),(0,-1),'RIGHT'),('VALIGN',(0,0),(0,-1),'MIDDLE'),
    ]))
    story.append(ft)

    def dark_bg(c, d):
        c.saveState(); c.setFillColor(C_DARK)
        c.rect(0,0,A4[0],A4[1],fill=1,stroke=0); c.restoreState()

    doc.build(story, onFirstPage=dark_bg, onLaterPages=dark_bg)
    with open(out_path, 'wb') as f:
        f.write(buf.getvalue())
    return out_path


class LabApp(MDApp):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.records = []
        self.store = None
        self.sel_subject = None
        self.sel_test = None
        self.editing_id = None
        self.settings_data = {
            'lab_name': 'مختبرات حسين غلاب',
            'lab_phone': LAB_PHONE,
            'lab_addr': 'المملكة العربية السعودية',
            'lab_lic': 'وزارة الصحة',
        }

    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Cyan"
        self.theme_cls.primary_hue = "400"

        Builder.load_string(KV)

        # Load stored data
        try:
            self.store = JsonStore('lab_records.json')
            if self.store.exists('records'):
                self.records = self.store.get('records')['data']
            if self.store.exists('settings'):
                self.settings_data.update(self.store.get('settings')['data'])
        except:
            pass

        return self.build_ui()

    def build_ui(self):
        root = MDBoxLayout(orientation='vertical', md_bg_color=get_color_from_hex('#0a1628'))

        # Top bar
        tb = MDTopAppBar(
            title="مختبرات حسين غلاب",
            md_bg_color=get_color_from_hex('#0d2248'),
            specific_text_color=get_color_from_hex('#00d4ff'),
            elevation=4,
        )
        root.add_widget(tb)

        # Bottom nav
        bn = MDBottomNavigation(
            panel_color=get_color_from_hex('#050f20'),
            selected_color_background=get_color_from_hex('#00d4ff'),
            text_color_active=get_color_from_hex('#00d4ff'),
        )

        # HOME
        home = MDBottomNavigationItem(name='home', text='الرئيسية', icon='home')
        home.add_widget(self.build_home())
        bn.add_widget(home)

        # NEW TEST
        nt = MDBottomNavigationItem(name='new', text='فحص جديد', icon='plus-circle')
        nt.add_widget(self.build_new_test())
        bn.add_widget(nt)

        # RECORDS
        rc = MDBottomNavigationItem(name='records', text='السجلات', icon='clipboard-list')
        rc.add_widget(self.build_records())
        bn.add_widget(rc)

        # SUBJECTS
        sj = MDBottomNavigationItem(name='subjects', text='المواد', icon='microscope')
        sj.add_widget(self.build_subjects())
        bn.add_widget(sj)

        root.add_widget(bn)
        return root

    # ── HOME ─────────────────────────────────────────────────
    def build_home(self):
        sv = MDScrollView()
        box = MDBoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10),
                          size_hint_y=None, adaptive_height=True,
                          md_bg_color=get_color_from_hex('#0a1628'))
        sv.add_widget(box)

        # Stats grid
        stats_grid = MDGridLayout(cols=2, spacing=dp(8), size_hint_y=None, height=dp(160), padding=[0,0,0,0])
        self.stat_total = self._stat_card('📊', '0', 'إجمالي الفحوصات', '#00d4ff')
        self.stat_done  = self._stat_card('✅', '0', 'مكتملة', '#00c853')
        self.stat_rev   = self._stat_card('💰', '0', 'الإيرادات ريال', '#ffd700')
        self.stat_pnd   = self._stat_card('⏳', '0', 'قيد الانتظار', '#ff3b5c')
        for s in [self.stat_total, self.stat_done, self.stat_rev, self.stat_pnd]:
            stats_grid.add_widget(s)
        box.add_widget(stats_grid)

        # Subjects grid
        box.add_widget(self._section_label('🔬 أقسام الفحوصات'))
        sub_grid = MDGridLayout(cols=3, spacing=dp(8), size_hint_y=None, adaptive_height=True)
        for s in SUBJECTS:
            btn = MDRaisedButton(
                text=f"{s['icon']}\n{s['name']}\n{len(s['tests'])} فحص",
                md_bg_color=get_color_from_hex('#0d1e38'),
                line_color=get_color_from_hex('#1e3a5f'),
                size_hint_x=1,
                halign='center',
            )
            btn.bind(on_release=lambda x, sid=s['id']: self.go_subject(sid))
            sub_grid.add_widget(btn)
        box.add_widget(sub_grid)

        # Recent
        box.add_widget(self._section_label('🕐 آخر الفحوصات'))
        self.recent_box = MDBoxLayout(orientation='vertical', size_hint_y=None, adaptive_height=True, spacing=dp(5))
        box.add_widget(self.recent_box)
        self.refresh_home()
        return sv

    def refresh_home(self):
        total = len(self.records)
        done  = sum(1 for r in self.records if r.get('status')=='مكتمل')
        rev   = sum(r.get('test_price',0) for r in self.records)
        pnd   = sum(1 for r in self.records if r.get('status')=='منتظر')
        try:
            self.stat_total.children[0].children[0].text = str(total)
            self.stat_done.children[0].children[0].text  = str(done)
            self.stat_rev.children[0].children[0].text   = str(rev)
            self.stat_pnd.children[0].children[0].text   = str(pnd)
        except: pass

        self.recent_box.clear_widgets()
        for r in self.records[:5]:
            item = self._rec_list_item(r)
            self.recent_box.add_widget(item)

    def _stat_card(self, icon, val, label, color):
        card = MDCard(md_bg_color=get_color_from_hex('#0d1e38'),
                      radius=[dp(12)], elevation=2, padding=dp(10))
        box = MDBoxLayout(orientation='vertical', halign='center', spacing=dp(2))
        box.add_widget(MDLabel(text=icon, halign='center', font_style='H5'))
        vl = MDLabel(text=val, halign='center', font_style='H5',
                     theme_text_color='Custom', text_color=get_color_from_hex(color))
        box.add_widget(vl)
        box.add_widget(MDLabel(text=label, halign='center', font_style='Caption',
                               theme_text_color='Custom', text_color=get_color_from_hex('#5a8ab8')))
        card.add_widget(box)
        return card

    def _section_label(self, text):
        return MDLabel(text=text, font_style='H6',
                       theme_text_color='Custom', text_color=get_color_from_hex('#00d4ff'),
                       size_hint_y=None, height=dp(36), halign='right')

    def _rec_list_item(self, r):
        card = MDCard(md_bg_color=get_color_from_hex('#0d1e38'), radius=[dp(10)],
                      size_hint_y=None, height=dp(64), padding=dp(8))
        box = MDBoxLayout(orientation='horizontal', spacing=dp(8))
        box.add_widget(MDLabel(text=r.get('test_icon','🔬'), font_style='H5', size_hint_x=None, width=dp(40)))
        info = MDBoxLayout(orientation='vertical')
        info.add_widget(MDLabel(text=r.get('patient_name',''), font_style='Body1', halign='right',
                                theme_text_color='Custom', text_color=get_color_from_hex('#e8f4fd')))
        info.add_widget(MDLabel(text=f"{r.get('test_name','')} • {r.get('date','')}",
                                font_style='Caption', halign='right',
                                theme_text_color='Custom', text_color=get_color_from_hex('#5a8ab8')))
        box.add_widget(info)
        btn = MDIconButton(icon='file-pdf-box', theme_icon_color='Custom',
                           icon_color=get_color_from_hex('#ffd700'))
        btn.bind(on_release=lambda x, rid=r['id']: self.gen_pdf_share(rid))
        box.add_widget(btn)
        card.add_widget(box)
        card.bind(on_release=lambda x, rid=r['id']: self.view_record(rid))
        return card

    # ── NEW TEST ──────────────────────────────────────────────
    def build_new_test(self):
        sv = MDScrollView()
        box = MDBoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10),
                          size_hint_y=None, adaptive_height=True)
        sv.add_widget(box)

        # Patient fields
        box.add_widget(self._section_label('👤 بيانات المريض'))
        self.f_name   = MDTextField(hint_text='اسم المريض *', halign='right', text_color_normal=get_color_from_hex('#e8f4fd'))
        self.f_age    = MDTextField(hint_text='العمر', input_filter='int', halign='right')
        self.f_phone  = MDTextField(hint_text='رقم الهاتف', input_filter='int', halign='right')
        self.f_doctor = MDTextField(hint_text='الطبيب المحول', halign='right')
        self.f_date   = MDTextField(hint_text='التاريخ', text=datetime.date.today().isoformat(), halign='right')
        for w in [self.f_name, self.f_age, self.f_phone, self.f_doctor, self.f_date]:
            box.add_widget(w)

        # Gender
        self.gender_val = 'ذكر'
        gbox = MDBoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40), spacing=dp(10))
        gbox.add_widget(MDLabel(text='الجنس:', halign='right'))
        for g in ['ذكر','أنثى']:
            cb = MDCheckbox(group='gender', size_hint_x=None, width=dp(48), active=(g=='ذكر'))
            cb.bind(active=lambda inst,v,gv=g: setattr(self,'gender_val',gv) if v else None)
            gbox.add_widget(cb)
            gbox.add_widget(MDLabel(text=g, halign='right'))
        box.add_widget(gbox)

        # Subject selector
        box.add_widget(self._section_label('🔬 اختر الفحص'))
        self.sub_menu_btn = MDRaisedButton(text='-- اختر القسم --',
                                           md_bg_color=get_color_from_hex('#0d1e38'))
        self.sub_menu_btn.bind(on_release=self.open_sub_menu)
        box.add_widget(self.sub_menu_btn)

        self.test_box = MDBoxLayout(orientation='vertical', size_hint_y=None, adaptive_height=True, spacing=dp(5))
        box.add_widget(self.test_box)

        # Results
        box.add_widget(self._section_label('📋 النتائج'))
        self.result_box = MDBoxLayout(orientation='vertical', size_hint_y=None, adaptive_height=True, spacing=dp(5))
        box.add_widget(self.result_box)

        # Notes
        self.f_notes = MDTextField(hint_text='ملاحظات إضافية', multiline=True, halign='right')
        self.f_tech  = MDTextField(hint_text='اسم الفاحص', halign='right')
        box.add_widget(self.f_notes)
        box.add_widget(self.f_tech)

        # Save buttons
        brow = MDBoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50), spacing=dp(8))
        b1 = MDRaisedButton(text='💾 حفظ', md_bg_color=get_color_from_hex('#00c853'))
        b1.bind(on_release=lambda x: self.save_test())
        b2 = MDRaisedButton(text='🖨️ حفظ + PDF', md_bg_color=get_color_from_hex('#ffd700'),
                             theme_text_color='Custom', text_color=get_color_from_hex('#000'))
        b2.bind(on_release=lambda x: self.save_test(pdf=True))
        brow.add_widget(b1); brow.add_widget(b2)
        box.add_widget(brow)

        self.result_fields = {}
        return sv

    def open_sub_menu(self, btn):
        items = [{'text': f"{s['icon']} {s['name']}", 'viewclass': 'OneLineListItem',
                  'on_release': lambda x, sid=s['id']: self.select_subject(sid)}
                 for s in SUBJECTS]
        self._sub_menu = MDDropdownMenu(caller=btn, items=items, width_mult=4)
        self._sub_menu.open()

    def select_subject(self, sid):
        try: self._sub_menu.dismiss()
        except: pass
        self.sel_subject = next((s for s in SUBJECTS if s['id']==sid), None)
        if self.sel_subject:
            self.sub_menu_btn.text = f"{self.sel_subject['icon']} {self.sel_subject['name']}"
        self.test_box.clear_widgets()
        self.result_box.clear_widgets()
        self.result_fields.clear()
        self.sel_test = None
        for t in self.sel_subject['tests']:
            btn = MDRaisedButton(text=f"{t['icon']} {t['name']} — {t['price']} ر.س",
                                 md_bg_color=get_color_from_hex('#0d1e38'))
            btn.bind(on_release=lambda x, td=t: self.select_test(td))
            self.test_box.add_widget(btn)

    def select_test(self, test):
        self.sel_test = test
        self.result_box.clear_widgets()
        self.result_fields.clear()
        hdr = MDCard(md_bg_color=get_color_from_hex('#0d2248'), radius=[dp(10)],
                     padding=dp(10), size_hint_y=None, height=dp(56))
        hdr.add_widget(MDLabel(text=f"{test['icon']}  {test['name']} — {test['nameEn']}",
                               halign='right', theme_text_color='Custom',
                               text_color=get_color_from_hex('#00d4ff')))
        self.result_box.add_widget(hdr)
        for f in test['fields']:
            row = MDBoxLayout(orientation='horizontal', size_hint_y=None, height=dp(56), spacing=dp(6))
            row.add_widget(MDLabel(text=f['ar'], halign='right', size_hint_x=0.45,
                                   theme_text_color='Custom', text_color=get_color_from_hex('#c8dff5')))
            tf = MDTextField(hint_text=f.get('normal','') if f.get('t')=='txt' else f"({f.get('min')}-{f.get('max')})",
                             input_filter=None if f.get('t')=='txt' else 'float',
                             size_hint_x=0.35, halign='center')
            row.add_widget(tf)
            row.add_widget(MDLabel(text=f.get('u',''), halign='center', size_hint_x=0.2,
                                   theme_text_color='Custom', text_color=get_color_from_hex('#5a8ab8')))
            self.result_fields[f['n']] = tf
            self.result_box.add_widget(row)

    def save_test(self, pdf=False):
        name = self.f_name.text.strip()
        if not name:
            Snackbar(text='أدخل اسم المريض').open(); return
        if not self.sel_test:
            Snackbar(text='اختر الفحص').open(); return

        results = {k: v.text for k,v in self.result_fields.items()}
        rec = {
            'id': self.editing_id or str(int(datetime.datetime.now().timestamp()*1000)),
            'req_num': self._gen_req_num(),
            'date': self.f_date.text or datetime.date.today().isoformat(),
            'patient_name': name,
            'age': self.f_age.text,
            'gender': self.gender_val,
            'phone': self.f_phone.text,
            'doctor': self.f_doctor.text,
            'subject_id': self.sel_subject['id'],
            'subject_name': self.sel_subject['name'],
            'subject_icon': self.sel_subject['icon'],
            'test_id': self.sel_test['id'],
            'test_name': self.sel_test['name'],
            'test_icon': self.sel_test.get('icon','🔬'),
            'test_price': self.sel_test['price'],
            'results': results,
            'notes': self.f_notes.text,
            'tech': self.f_tech.text,
            'status': 'مكتمل',
            'lab_name': self.settings_data['lab_name'],
            'lab_phone': self.settings_data['lab_phone'],
            'lab_addr': self.settings_data['lab_addr'],
            'lab_lic': self.settings_data['lab_lic'],
        }
        if self.editing_id:
            idx = next((i for i,r in enumerate(self.records) if r['id']==self.editing_id), None)
            if idx is not None: self.records[idx] = rec
            self.editing_id = None
        else:
            self.records.insert(0, rec)
        self._save_records()
        Snackbar(text='✅ تم الحفظ').open()
        if pdf: self.gen_pdf_share(rec['id'])
        self.refresh_home()

    def _gen_req_num(self):
        d = datetime.date.today()
        n = len(self.records)+1
        return f"HG-{d.year}{d.month:02d}{d.day:02d}-{n:04d}"

    def _save_records(self):
        try: self.store.put('records', data=self.records)
        except: pass

    # ── RECORDS ───────────────────────────────────────────────
    def build_records(self):
        sv = MDScrollView()
        box = MDBoxLayout(orientation='vertical', padding=dp(10), spacing=dp(8),
                          size_hint_y=None, adaptive_height=True)
        sv.add_widget(box)
        box.add_widget(self._section_label('📋 سجل الفحوصات'))

        self.search_field = MDTextField(hint_text='بحث...', halign='right')
        self.search_field.bind(text=self.filter_records)
        box.add_widget(self.search_field)

        b_del = MDRaisedButton(text='🗑️ حذف الكل', md_bg_color=get_color_from_hex('#ff3b5c'))
        b_del.bind(on_release=lambda x: self.del_all_confirm())
        box.add_widget(b_del)

        self.records_list = MDBoxLayout(orientation='vertical', size_hint_y=None,
                                         adaptive_height=True, spacing=dp(6))
        box.add_widget(self.records_list)
        self.render_records_list()
        return sv

    def render_records_list(self, data=None):
        self.records_list.clear_widgets()
        recs = data or self.records
        for r in recs:
            card = MDCard(md_bg_color=get_color_from_hex('#0d1e38'), radius=[dp(10)],
                          size_hint_y=None, height=dp(80), padding=dp(8))
            outer = MDBoxLayout(orientation='vertical', spacing=dp(3))
            row1 = MDBoxLayout(orientation='horizontal', spacing=dp(6))
            row1.add_widget(MDLabel(text=f"{r.get('test_icon','🔬')} {r.get('patient_name','')}",
                                    halign='right', theme_text_color='Custom',
                                    text_color=get_color_from_hex('#e8f4fd'), font_style='Body1'))
            row1.add_widget(MDLabel(text=r.get('req_num',''), halign='left',
                                    theme_text_color='Custom', text_color=get_color_from_hex('#00d4ff'),
                                    font_style='Caption', size_hint_x=None, width=dp(120)))
            outer.add_widget(row1)
            row2 = MDBoxLayout(orientation='horizontal', spacing=dp(4))
            row2.add_widget(MDLabel(text=f"{r.get('test_name','')} • {r.get('date','')}",
                                    halign='right', font_style='Caption',
                                    theme_text_color='Custom', text_color=get_color_from_hex('#5a8ab8')))
            bp = MDRaisedButton(text='🖨️PDF', md_bg_color=get_color_from_hex('#ffd700'),
                                theme_text_color='Custom', text_color=get_color_from_hex('#000'),
                                size_hint_x=None, width=dp(72), height=dp(28))
            bp.bind(on_release=lambda x, rid=r['id']: self.gen_pdf_share(rid))
            bw = MDRaisedButton(text='📱واتس', md_bg_color=get_color_from_hex('#25d366'),
                                theme_text_color='Custom', text_color=get_color_from_hex('#fff'),
                                size_hint_x=None, width=dp(76), height=dp(28))
            bw.bind(on_release=lambda x, rid=r['id']: self.share_wa(rid))
            bd = MDIconButton(icon='delete', theme_icon_color='Custom',
                              icon_color=get_color_from_hex('#ff3b5c'),
                              size_hint_x=None, width=dp(36))
            bd.bind(on_release=lambda x, rid=r['id']: self.del_record(rid))
            row2.add_widget(bp); row2.add_widget(bw); row2.add_widget(bd)
            outer.add_widget(row2)
            card.add_widget(outer)
            self.records_list.add_widget(card)

    def filter_records(self, inst, val):
        q = val.lower()
        filtered = [r for r in self.records if q in r.get('patient_name','').lower() or q in r.get('req_num','').lower()]
        self.render_records_list(filtered)

    def del_record(self, rid):
        def do(*a):
            self.records = [r for r in self.records if r['id'] != rid]
            self._save_records(); self.render_records_list(); self.refresh_home()
            Snackbar(text='تم الحذف').open()
        dlg = MDDialog(title='تأكيد الحذف', text='هل تريد حذف هذا السجل؟',
                       buttons=[MDFlatButton(text='نعم', on_release=lambda x: (dlg.dismiss(), do())),
                                MDFlatButton(text='إلغاء', on_release=lambda x: dlg.dismiss())])
        dlg.open()

    def del_all_confirm(self):
        def do(*a):
            self.records = []; self._save_records(); self.render_records_list(); self.refresh_home()
            Snackbar(text='تم حذف الكل').open()
        dlg = MDDialog(title='حذف الكل', text='حذف جميع السجلات؟',
                       buttons=[MDFlatButton(text='نعم', on_release=lambda x: (dlg.dismiss(), do())),
                                MDFlatButton(text='إلغاء', on_release=lambda x: dlg.dismiss())])
        dlg.open()

    def view_record(self, rid):
        r = next((x for x in self.records if x['id']==rid), None)
        if not r: return
        sub = next((s for s in SUBJECTS if s['id']==r['subject_id']), None)
        test = next((t for t in sub['tests'] if t['id']==r['test_id']), None) if sub else None
        details = f"رقم: {r['req_num']}\nالمريض: {r['patient_name']}\nالتاريخ: {r['date']}\nالفحص: {r['test_name']}\n\nالنتائج:\n"
        if test and r.get('results'):
            for f in test['fields']:
                v = r['results'].get(f['n'],'-')
                details += f"  {f['ar']}: {v} {f.get('u','')}\n"
        dlg = MDDialog(title=f"{r['test_icon']} {r['test_name']}", text=details,
                       buttons=[
                           MDFlatButton(text='🖨️ PDF', on_release=lambda x: (dlg.dismiss(), self.gen_pdf_share(rid))),
                           MDFlatButton(text='📱 واتساب', on_release=lambda x: (dlg.dismiss(), self.share_wa(rid))),
                           MDFlatButton(text='إغلاق', on_release=lambda x: dlg.dismiss()),
                       ])
        dlg.open()

    # ── SUBJECTS ──────────────────────────────────────────────
    def build_subjects(self):
        sv = MDScrollView()
        box = MDBoxLayout(orientation='vertical', padding=dp(10), spacing=dp(8),
                          size_hint_y=None, adaptive_height=True)
        sv.add_widget(box)
        box.add_widget(self._section_label('🔬 جميع الأقسام والفحوصات'))
        for s in SUBJECTS:
            sh = MDCard(md_bg_color=get_color_from_hex('#0d2248'), radius=[dp(10)],
                        padding=dp(10), size_hint_y=None, height=dp(48))
            sh.add_widget(MDLabel(text=f"{s['icon']}  {s['name']}  ({len(s['tests'])} فحص)",
                                  halign='right', theme_text_color='Custom',
                                  text_color=get_color_from_hex('#00d4ff'), font_style='Body1'))
            box.add_widget(sh)
            for t in s['tests']:
                tc = MDCard(md_bg_color=get_color_from_hex('#0d1e38'), radius=[dp(8)],
                            padding=[dp(6), dp(6), dp(6), dp(6)], size_hint_y=None, height=dp(44))
                row = MDBoxLayout(orientation='horizontal')
                row.add_widget(MDLabel(text=f"  {t['icon']} {t['name']}", halign='right',
                                       theme_text_color='Custom', text_color=get_color_from_hex('#c8dff5')))
                row.add_widget(MDLabel(text=f"{t['price']} ر.س", halign='left',
                                       theme_text_color='Custom', text_color=get_color_from_hex('#ffd700'),
                                       size_hint_x=None, width=dp(80)))
                tc.add_widget(row)
                box.add_widget(tc)
        return sv

    def go_subject(self, sid):
        pass  # Navigate to subjects tab

    # ── PDF + SHARE ───────────────────────────────────────────
    def gen_pdf_share(self, rid):
        rec = next((r for r in self.records if r['id']==rid), None)
        if not rec: return
        try:
            import tempfile
            out = os.path.join(tempfile.gettempdir(), f"lab_{rid}.pdf")
            generate_pdf(rec, out)
            if ANDROID:
                self._share_file_android(out, rec)
            else:
                Snackbar(text=f'PDF محفوظ: {out}').open()
        except Exception as e:
            Snackbar(text=f'خطأ: {str(e)[:50]}').open()

    def _share_file_android(self, path, rec):
        try:
            Intent = autoclass('android.content.Intent')
            Uri = autoclass('android.net.Uri')
            File = autoclass('java.io.File')
            FileProvider = autoclass('androidx.core.content.FileProvider')
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            context = PythonActivity.mActivity
            f = File(path)
            uri = FileProvider.getUriForFile(context, context.getPackageName()+'.fileprovider', f)
            intent = Intent(Intent.ACTION_SEND)
            intent.setType('application/pdf')
            intent.putExtra(Intent.EXTRA_STREAM, uri)
            intent.putExtra(Intent.EXTRA_TEXT, self._wa_text(rec))
            intent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
            chooser = Intent.createChooser(intent, 'مشاركة نتيجة الفحص')
            context.startActivity(chooser)
        except Exception as e:
            Snackbar(text=f'خطأ مشاركة: {str(e)[:50]}').open()

    def share_wa(self, rid):
        rec = next((r for r in self.records if r['id']==rid), None)
        if not rec: return
        if ANDROID:
            self.gen_pdf_share(rid)
        else:
            import webbrowser
            phone = (rec.get('phone','') or '').replace(' ','').replace('-','')
            msg = self._wa_text(rec)
            webbrowser.open(f"https://wa.me/{phone}?text={msg}")

    def _wa_text(self, rec):
        from urllib.parse import quote
        sub = next((s for s in SUBJECTS if s['id']==rec['subject_id']), None)
        test = next((t for t in sub['tests'] if t['id']==rec['test_id']), None) if sub else None
        m = f"🧪 *{rec.get('lab_name','مختبرات حسين غلاب')}*\n"
        m += f"━━━━━━━━━━━━\n"
        m += f"📋 *رقم:* {rec['req_num']}\n👤 *المريض:* {rec['patient_name']}\n"
        m += f"🔬 *الفحص:* {rec.get('test_icon','')} {rec['test_name']}\n📅 *التاريخ:* {rec['date']}\n"
        m += f"━━━━━━━━━━━━\n📊 *النتائج:*\n"
        if test and rec.get('results'):
            for f in test['fields']:
                v = rec['results'].get(f['n'],'-')
                m += f"• {f['ar']}: *{v}* {f.get('u','')}\n"
        m += f"━━━━━━━━━━━━\n📞 {rec.get('lab_phone',LAB_PHONE)}"
        return quote(m)


if __name__ == '__main__':
    LabApp().run()
