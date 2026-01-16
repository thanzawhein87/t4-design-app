import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io
import requests
import random
import os

# --- 1. Page Configuration ---
st.set_page_config(page_title="T4 Smart Design AI", layout="wide", page_icon="🎨")

# --- 2. Helper Functions ---
def generate_image(prompt, width, height):
    """Pollinations AI မှ ပုံထုတ်ပေးမည့် Function"""
    formatted_prompt = prompt.replace(" ", "%20")
    seed = random.randint(1, 10000)
    # Model = flux (Quality ကောင်းသည်), nologo=true (AI logo မပါစေရန်)
    url = f"https://image.pollinations.ai/prompt/{formatted_prompt}?width={width}&height={height}&model=flux&seed={seed}&nologo=true"
    
    try:
        response = requests.get(url, timeout=60)
        if response.status_code == 200:
            return Image.open(io.BytesIO(response.content))
        return None
    except:
        return None

# --- 3. SIDEBAR CONTROLS ---
with st.sidebar:
    st.header("⚙️ ဒီဇိုင်း ဆက်တင်များ")
    
    # A. Image Size
    st.subheader("၁။ ပုံအရွယ်အစား")
    ratio_choice = st.selectbox(
        "Size ရွေးချယ်ပါ",
        ("Square (1:1) - FB/Insta", "Portrait (9:16) - Story/TikTok", "Landscape (16:9) - Video/Cover"),
        index=0
    )
    
    if "Square" in ratio_choice:
        img_w, img_h = 1080, 1080
    elif "Portrait" in ratio_choice:
        img_w, img_h = 768, 1344 
    else:
        img_w, img_h = 1280, 720

    st.divider()

    # B. Text Settings
    st.subheader("၂။ စာသား ဒီဇိုင်း")
    font_size = st.slider("စာလုံးအရွယ်အစား", 30, 200, 80)
    text_color = st.color_picker("စာလုံးအရောင်", "#FFFFFF")
    
    st.caption("စာသား နေရာရွှေ့ရန်")
    text_x_offset = st.slider("ဘယ် - ညာ", -500, 500, 0)
    text_y_offset = st.slider("အပေါ် - အောက်", -500, 500, 0)

    st.divider()

    # C. Logo Settings
    st.subheader("၃။ လုပ်ငန်း Logo")
    logo_file = st.file_uploader("Logo ဖိုင် (PNG အကြည်)", type=['png', 'jpg', 'jpeg'])
    
    if logo_file:
        logo_size = st.slider("Logo Size", 50, 400, 150)
        logo_x = st.slider("Logo (ဘယ်-ညာ)", 0, img_w, int(img_w - 200)) 
        logo_y = st.slider("Logo (အပေါ်-အောက်)", 0, img_h, 50)

# --- 4. MAIN PAGE ---
st.title("🛍️ T4 AI Design Studio")
st.write("ကုန်ပစ္စည်း ကြော်ငြာဒီဇိုင်းများကို Template စနစ်ဖြင့် လွယ်ကူစွာ ဖန်တီးပါ။")

col1, col2 = st.columns([1, 1.5])

# --- ဘယ်ဘက်ခြမ်း (Template ရွေးရန်) ---
with col1:
    st.success("အဆင့် (၁) - ဒီဇိုင်းပုံစံ ရွေးပါ")
    
    category = st.radio(
        "ကုန်ပစ္စည်း အမျိုးအစား:",
        ("အလှကုန် (Cosmetic)", "အစားအသောက် (Food/Drink)", "ဖက်ရှင် (Fashion)", "နည်းပညာ (Gadget)", "Custom (မိမိစိတ်ကြိုက်)")
    )
    
    real_prompt = ""
    
    # --- Template Logic ---
    if category == "အလှကုန် (Cosmetic)":
        product_name = st.text_input("ထုတ်ကုန်အမည် (ဥပမာ - Nivea)", "Luxury Perfume")
        theme = st.selectbox("နောက်ခံ Mood", ("ပန်းဥယျာဉ် (Floral)", "ရေစက်များ (Water Splash)", "ရွှေရောင် (Golden Luxury)", "စတူဒီယို (Clean Studio)"))
        
        if theme == "ပန်းဥယျာဉ် (Floral)":
            real_prompt = f"Professional product photography of {product_name}, surrounded by soft pink and white flowers, nature sunlight, bokeh background, 8k resolution, cinematic lighting"
        elif theme == "ရေစက်များ (Water Splash)":
            real_prompt = f"Fresh {product_name} product shot, dynamic water splash, blue background, refreshing vibe, high speed photography, advertising style, 4k"
        elif theme == "ရွှေရောင် (Golden Luxury)":
            real_prompt = f"Luxurious {product_name} bottle on a black podium, gold dust floating, elegant lighting, premium advertisement standard, sharp focus"
        else:
            real_prompt = f"Clean minimalist studio shot of {product_name}, pastel color background, soft shadows, high end commercial photography"
            
    elif category == "အစားအသောက် (Food/Drink)":
        food_name = st.text_input("အစားအစာအမည်", "Delicious Burger")
        style = st.selectbox("စတိုင်", ("စားသောက်ဆိုင် (Restaurant)", "အနက်ရောင်နောက်ခံ (Dark Moody)", "လတ်ဆတ်သော (Fresh & Bright)"))
        
        if style == "စားသောက်ဆိုင် (Restaurant)":
            real_prompt = f"Gourmet {food_name} on a wooden table, restaurant background blur, warm lighting, steam rising, delicious, 8k"
        elif style == "အနက်ရောင်နောက်ခံ (Dark Moody)":
            real_prompt = f"Professional food photography of {food_name}, dark background, dramatic rim lighting, cinematic, 4k"
        else:
            real_prompt = f"Fresh {food_name}, bright natural lighting, fruits and ingredients around, colorful, advertising style"

    elif category == "ဖက်ရှင် (Fashion)":
        item_name = st.text_input("ဝတ်စုံ/ပစ္စည်း", "Silk Dress")
        real_prompt = f"Fashion photography of a model wearing {item_name}, street style, city background, golden hour sunlight, magazine quality"

    elif category == "နည်းပညာ (Gadget)":
        item_name = st.text_input("ပစ္စည်းအမည်", "Smartphone")
        real_prompt = f"Futuristic product shot of {item_name}, neon lighting, cyberpunk style background, high tech vibe, 3d render style"

    elif category == "Custom (မိမိစိတ်ကြိုက်)":
        real_prompt = st.text_