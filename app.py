import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io
import requests
import random
import os

# --- 1. Page Configuration ---
st.set_page_config(page_title="T4 Pro Studio", layout="wide", page_icon="🎨")

# --- 2. Helper Functions ---
def generate_image(prompt, negative_prompt, width, height, seed):
    """Advanced Image Generation"""
    # Prompt နှင့် Negative Prompt ကို ပေါင်းစပ်ခြင်း
    full_prompt = f"{prompt} --no {negative_prompt}"
    formatted_prompt = full_prompt.replace(" ", "%20")
    
    # Model = flux (အကောင်းဆုံး quality)
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
    st.header("⚙️ Setting ချိန်ညှိရန်")
    
    # A. Size
    st.subheader("၁။ Size & Layout")
    ratio_choice = st.selectbox("Size", ("Square (1:1)", "Portrait (9:16)", "Landscape (16:9)"))
    
    if "Square" in ratio_choice: img_w, img_h = 1080, 1080
    elif "Portrait" in ratio_choice: img_w, img_h = 768, 1344 
    else: img_w, img_h = 1280, 720

    # B. Text
    st.subheader("၂။ မြန်မာစာသား")
    font_size = st.slider("Font Size", 30, 200, 80)
    text_color = st.color_picker("Text Color", "#FFFFFF")
    text_x = st.slider("Move X (Left/Right)", -500, 500, 0)
    text_y = st.slider("Move Y (Up/Down)", -500, 500, 0)

    st.divider()

    # C. Advanced AI Control (Feature အသစ်)
    with st.expander("🛠️ Advanced AI Settings (အဆင့်မြင့်)", expanded=False):
        st.caption("ပုံစံတူကို ပြန်လိုချင်ရင် Seed နံပါတ်ကို မှတ်ထားပါ")
        # Random Seed သို့မဟုတ် Fixed Seed
        use_random_seed = st.checkbox("Random Seed (ပုံစံအသစ်ချည်း ထုတ်မည်)", value=True)
        if use_random_seed:
            seed_input = random.randint(1, 99999)
        else:
            seed_input = st.number_input("Seed Number (ပုံစံတူ ထိန်းရန်)", value=42, step=1)
            
        st.caption("မပါစေချင်သော အရာများ (Negative Prompt)")
        neg_prompt = st.text_area("Negative Prompt", "blur, ugly, deformed, text, logo, watermark, low quality, bad hands", height=70)

    st.divider()

    # D. Logo
    logo_file = st.file_uploader("Logo (PNG)", type=['png', 'jpg'])
    if logo_file:
        logo_size = st.slider("Logo Size", 50, 400, 150)
        logo_x = st.slider("Logo X", 0, img_w, int(img_w - 200)) 
        logo_y = st.slider("Logo Y", 0, img_h, 50)

# --- 4. MAIN PAGE ---
st.title("🛍️ T4 Pro AI Design Studio")

col1, col2 = st.columns([1, 1.5])

with col1:
    st.info("အဆင့် (၁) - ပုံစံကြမ်း ရွေးချယ်ပါ")
    
    # Category Selection
    category = st.selectbox(
        "Product Category:",
        ("Cosmetic (အလှကုန်)", "Food (အစားအသောက်)", "Fashion (ဖက်ရှင်)", "Gadget (နည်းပညာ)", "Furniture (ပရိဘောဂ)")
    )
    
    # Auto-Prompt Logic
    base_prompt = ""
    if category == "Cosmetic (အလှကုန်)":
        item = st.text_input("Item Name", "Luxury Perfume")
        theme = st.selectbox("Theme", ("Floral Garden", "Water Splash", "Minimal Studio", "Golden Luxury"))
        if theme == "Floral Garden": base_prompt = f"Professional product photo of {item}, surrounded by soft pink flowers, bokeh nature background, sunlight, 8k"
        elif theme == "Water Splash": base_prompt = f"Fresh {item}, dynamic water splash, blue background, refreshing, high speed photography"
        elif theme == "Minimal Studio": base_prompt = f"Clean studio shot of {item}, pastel background, soft shadows, minimalist"
        else: base_prompt = f"Luxurious {item} on black podium, gold dust, elegant lighting, premium ad"

    elif category == "Food (အစားအသောက်)":
        item = st.text_input("Item Name", "Burger")
        base_prompt = f"Delicious {item} on wooden table, restaurant lighting, steam rising, mouth watering, 8k food photography"

    elif category == "Fashion (ဖက်ရှင်)":
        item = st.text_input("Item Name", "Silk Dress")
        base_prompt = f"Fashion model wearing {item}, street style, city background, golden hour lighting, magazine quality"
        
    else:
        item = st.text_input("Item Name", "Modern Chair")
        base_prompt = f"Interior design shot of {item}, modern living room, soft sunlight, architectural digest style"

    # --- THE EDITABLE PROMPT FIELD (အဓိက ပြင်ဆင်ချက်) ---
    st.warning("အဆင့် (၂) - AI ကို ခိုင်းမည့်စာ (စိတ်ကြိုက် ပြင်နိုင်သည်)")
    final_prompt = st.text_area("Prompt Editor (လိုချင်သလို ပြင်ရေးပါ)", base_prompt, height=120)
    
    st.success("အဆင့် (၃) - မြန်မာစာသား ထည့်ပါ")
    overlay_text = st.text_area("Overlay Text", "သဘာဝအလှ\nအကောင်းဆုံးရွေးချယ်မှု")
    
    generate_btn = st.button("🚀 Generate Design", type="primary", use_container_width=True)
    
    # Seed ကို ပြသပေးခြင်း (မှတ်ထားလို့ရအောင်)
    if not use_random_seed:
        st.caption(f"Current Seed: {seed_input}")

with col2:
    if generate_btn:
        with st.spinner("Creating your masterpiece..."):
            
            # Use the edited 'final_prompt' and 'seed_input'
            base_image = generate_image(final_prompt, neg_prompt, img_w, img_h, seed_input)
            
            if base_image:
                draw = ImageDraw.Draw(base_image)
                W, H = base_image.size
                
                # Logo
                if logo_file:
                    try:
                        logo = Image.open(logo_file).convert("RGBA")
                        aspect = logo.width / logo.height
                        new_h = int(logo_size / aspect)
                        logo = logo.resize((logo_size, new_h))
                        base_image.paste(logo, (logo_x, logo_y), logo)
                    except: pass

                # Text
                try:
                    if os.path.exists("mmrtext.ttf"): font = ImageFont.truetype("mmrtext.ttf", font_size)
                    else: font = ImageFont.truetype("C:/Windows/Fonts/mmrtext.ttf", font_size)
                except: font = ImageFont.load_default()

                lines = overlay_text.split('\n')
                try: line_h = font.getbbox("hg")[3] - font.getbbox("hg")[1] + (font_size * 0.4)
                except: line_h = font_size + 10
                
                total_h = line_h * len(lines)
                start_y = ((H - total_h) / 2) + text_y

                for line in lines:
                    try: line_w = font.getlength(line)
                    except: line_w = len(line) * (font_size/2)
                    start_x = ((W - line_w) / 2) + text_x
                    
                    # Shadow
                    draw.text((start_x+4, start_y+4), line, font=font, fill="black")
                    # Main
                    hex_c = text_color.lstrip('#')
                    rgb_c = tuple(int(hex_c[i:i+2], 16) for i in (0, 2, 4))
                    draw.text((start_x, start_y), line, font=font, fill=rgb_c)
                    start_y += line_h

                st.image(base_image, caption=f"Result (Seed: {seed_input})")
                
                # Download
                buf = io.BytesIO()
                base_image.save(buf, format="PNG")
                st.download_button("⬇️ Download Image", buf.getvalue(), "t4_design.png", "image/png", type="primary")
            else:
                st.error("Error generating image. Try again.")