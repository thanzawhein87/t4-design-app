import streamlit as st
import google.generativeai as genai
from PIL import Image
import io

# --- CONFIG & SETUP ---
st.set_page_config(page_title="AdGenius AI (Streamlit)", layout="wide")

# Initialize Session State
if "history" not in st.session_state:
    st.session_state.history = []
if "page" not in st.session_state:
    st.session_state.page = "dashboard"
if "scoping" not in st.session_state:
    st.session_state.scoping = {}
if "assets" not in st.session_state:
    st.session_state.assets = {}

# --- SIDEBAR API KEY ---
with st.sidebar:
    st.title("⚙️ Configuration")
    api_key = st.text_input("Gemini API Key", type="password")
    if api_key:
        genai.configure(api_key=api_key)
    else:
        st.warning("Please enter your API Key to generate images.")

# --- HELPER FUNCTIONS ---

def get_image_bytes(uploaded_file):
    if uploaded_file is None:
        return None
    return Image.open(uploaded_file)

def build_prompt(scoping, assets, variant):
    # Determine flags
    has_model = scoping.get('modelRole') != 'None' and assets.get('model_img')
    has_product = scoping.get('productRole') != 'None' and assets.get('product_img')
    has_building = scoping.get('buildingRole') != 'None' and assets.get('building_img')
    has_fantasy = scoping.get('fantasyRole') != 'None' and assets.get('fantasy_img')
    has_main_ref = assets.get('main_ref') is not None

    # 1. Scene Construction
    scene_desc = f"Create a professional advertising image for the topic: '{scoping.get('topic', 'Ad')}'.\n\nKEY ELEMENTS TO INCLUDE:\n"
    
    if scoping.get('modelRole') != 'None':
        scene_desc += f"- MODEL: {scoping.get('modelCount')} {scoping.get('modelGender')} model(s) ({scoping.get('modelRole')} role).{ ' (Reference image provided)' if has_model else ''}\n"
    if scoping.get('productRole') != 'None':
        scene_desc += f"- PRODUCT: {scoping.get('productCount')} item(s) ({scoping.get('productRole')} role).{ ' (Reference image provided)' if has_product else ''}\n"
    if scoping.get('buildingRole') != 'None':
        scene_desc += f"- ARCHITECTURE: {scoping.get('buildingCount')} structure(s) ({scoping.get('buildingRole')} role).{ ' (Reference image provided)' if has_building else ''}\n"
    if scoping.get('fantasyRole') != 'None':
        scene_desc += f"- FANTASY/BG: {scoping.get('fantasyCount')} element(s) ({scoping.get('fantasyRole')} role).{ ' (Reference image provided)' if has_fantasy else ''}\n"

    if scoping.get('textRole') != 'None':
        scene_desc += f"- TEXT LAYOUT: Leave space for {scoping.get('textLineCount')} lines of text. Primary focus on line {scoping.get('textPrimaryLineIdx') + 1}.\n"

    # 2. Style Instruction
    style_instruction = ""
    if variant == 'Standard':
        style_instruction = "STYLE: Standard Commercial Photography. High-key lighting, clean background, eye-level perspective, sharp focus on the product/subject."
    elif variant == 'Uncommon':
        style_instruction = "STYLE: Dynamic Creative. Use a Dutch Angle, low angle, or unexpected framing. Dramatic lighting, high contrast."
    elif variant == 'Distance':
        style_instruction = "STYLE: Wide Establishing Shot. The subject is small in frame, showing the vast environment. Cinematic landscape composition."
    elif variant == 'Abstract':
        style_instruction = "STYLE: Surreal/Abstract Art. Dreamlike quality, floating elements, exaggerated colors, artistic interpretation."

    # 3. Final Assembly
    prompt = f"""
    {scene_desc}
    
    { "VISUAL REFERENCE: Please loosely follow the composition and vibe of the provided Style Reference image." if has_main_ref else ""}
    
    {style_instruction}
    
    {f"ADDITIONAL NOTES: {assets.get('specialInstructions')}" if assets.get('specialInstructions') else ""}
    
    REQUIREMENTS: Photorealistic, High Resolution (4k), Advertising Standard.
    """
    return prompt

def generate_image(scoping, assets, variant):
    try:
        model = genai.GenerativeModel('gemini-2.5-flash-image')
        prompt = build_prompt(scoping, assets, variant)
        
        # Prepare inputs (Prompt + Images)
        inputs = [prompt]
        
        # Attach Images if they exist
        if scoping.get('modelRole') != 'None' and assets.get('model_img'): inputs.append(assets['model_img'])
        if scoping.get('productRole') != 'None' and assets.get('product_img'): inputs.append(assets['product_img'])
        if scoping.get('buildingRole') != 'None' and assets.get('building_img'): inputs.append(assets['building_img'])
        if scoping.get('fantasyRole') != 'None' and assets.get('fantasy_img'): inputs.append(assets['fantasy_img'])
        if assets.get('main_ref'): inputs.append(assets['main_ref'])

        # Aspect Ratio Map
        ratio_map = {
            '1:1': '1:1',
            '9:16': '9:16',
            '16:9': '16:9',
            '3:4': '3:4'
        }
        
        response = model.generate_content(
            inputs,
            generation_config=genai.types.GenerationConfig(
                candidate_count=1,
            )
            # Note: Aspect ratio param in Python SDK might vary slightly depending on version, 
            # usually handled via prompt or specific config param if supported by 2.5 flash.
        )
        
        return response.parts[0].image
    except Exception as e:
        st.error(f"Error generating {variant}: {e}")
        return None

# --- PAGES ---

def render_dashboard():
    st.title("AdGenius AI - Dashboard")
    st.write("Review your past campaigns.")
    
    if st.button("+ Create New Ad", type="primary"):
        st.session_state.page = "wizard_1"
        st.rerun()

    if not st.session_state.history:
        st.info("No campaigns yet. Start creating magic!")
    else:
        cols = st.columns(4)
        for idx, project in enumerate(st.session_state.history):
            with cols[idx % 4]:
                with st.container(border=True):
                    if project['thumbnail']:
                        st.image(project['thumbnail'], use_container_width=True)
                    st.subheader(project['topic'])
                    st.caption(project['date'])

def render_wizard_phase_1():
    st.title("Phase 1: Project Scoping")
    
    with st.form("scoping_form"):
        col1, col2 = st.columns(2)
        with col1:
            topic = st.text_input("Campaign Topic", value=st.session_state.scoping.get('topic', ''))
        with col2:
            ratio = st.selectbox("Aspect Ratio", ['1:1', '9:16', '16:9', '3:4'], index=0)

        st.divider()

        # Model
        st.subheader("👤 Human Model")
        c1, c2, c3 = st.columns(3)
        model_role = c1.selectbox("Role", ['None', 'Main', 'Supporting'], key="mr")
        model_count = c2.selectbox("Quantity", ['1', '2', '3', 'Group'], key="mc")
        model_gender = c3.selectbox("Gender", ['Female', 'Male', 'Mixed'], key="mg")

        # Product
        st.subheader("📦 Product")
        c1, c2 = st.columns(2)
        product_role = c1.selectbox("Role", ['None', 'Main', 'Supporting'], key="pr")
        product_count = c2.selectbox("Quantity", ['1', '2', '3', 'Group'], key="pc")

        # Building
        st.subheader("🏢 Architecture")
        c1, c2 = st.columns(2)
        building_role = c1.selectbox("Role", ['None', 'Main', 'Supporting'], key="br")
        building_count = c2.selectbox("Quantity", ['1', '2', '3', 'Group'], key="bc")

        # Fantasy
        st.subheader("✨ Fantasy World")
        c1, c2 = st.columns(2)
        fantasy_role = c1.selectbox("Role", ['None', 'Main', 'Supporting'], key="fr")
        fantasy_count = c2.selectbox("Quantity", ['1', '2', '3', 'Group'], key="fc")

        # Text
        st.subheader("📝 Text Layout")
        c1, c2 = st.columns(2)
        text_role = c1.selectbox("Role", ['None', 'Main', 'Supporting'], key="tr")
        text_lines = c2.slider("Line Count", 1, 4, 1)
        text_focus = st.selectbox("Primary Focus Line", [f"Line {i+1}" for i in range(text_lines)])

        submitted = st.form_submit_button("Next Step →")
        if submitted:
            if not topic:
                st.error("Please enter a topic.")
            else:
                st.session_state.scoping = {
                    'topic': topic, 'ratio': ratio,
                    'modelRole': model_role, 'modelCount': model_count, 'modelGender': model_gender,
                    'productRole': product_role, 'productCount': product_count,
                    'buildingRole': building_role, 'buildingCount': building_count,
                    'fantasyRole': fantasy_role, 'fantasyCount': fantasy_count,
                    'textRole': text_role, 'textLineCount': text_lines, 
                    'textPrimaryLineIdx': int(text_focus.split(' ')[1]) - 1
                }
                st.session_state.page = "wizard_2"
                st.rerun()

def render_wizard_phase_2():
    st.title("Phase 2: Asset Upload")
    scoping = st.session_state.scoping
    assets = {}

    st.info("Upload **one main reference image** per category for best results.")

    if scoping['modelRole'] != 'None':
        st.subheader("👤 Model Reference")
        assets['model_img'] = get_image_bytes(st.file_uploader("Upload Model Ref", type=['png', 'jpg', 'jpeg'], key="u_model"))

    if scoping['productRole'] != 'None':
        st.subheader("📦 Product Reference")
        assets['product_img'] = get_image_bytes(st.file_uploader("Upload Product Ref", type=['png', 'jpg', 'jpeg'], key="u_prod"))

    if scoping['buildingRole'] != 'None':
        st.subheader("🏢 Building Reference")
        assets['building_img'] = get_image_bytes(st.file_uploader("Upload Building Ref", type=['png', 'jpg', 'jpeg'], key="u_build"))

    if scoping['fantasyRole'] != 'None':
        st.subheader("✨ Fantasy Reference")
        assets['fantasy_img'] = get_image_bytes(st.file_uploader("Upload Fantasy Ref", type=['png', 'jpg', 'jpeg'], key="u_fant"))

    st.subheader("🎨 Main Style Reference (Important)")
    assets['main_ref'] = get_image_bytes(st.file_uploader("Upload Style/Vibe Ref", type=['png', 'jpg', 'jpeg'], key="u_main"))

    st.subheader("Instructions")
    assets['specialInstructions'] = st.text_area("Special Instructions (Optional)")

    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("← Back"):
            st.session_state.page = "wizard_1"
            st.rerun()
    with col2:
        if st.button("Generate 4 Styles ✨", type="primary"):
            st.session_state.assets = assets
            st.session_state.page = "results"
            st.rerun()

def render_results():
    st.title("Generation Results")
    
    if not api_key:
        st.error("API Key missing. Please configure in sidebar.")
        if st.button("Back"): st.session_state.page = "wizard_2"; st.rerun()
        return

    scoping = st.session_state.scoping
    assets = st.session_state.assets

    with st.status("Designing 4 Perspectives...", expanded=True) as status:
        st.write("Generating Standard View...")
        img_std = generate_image(scoping, assets, 'Standard')
        st.write("Generating Creative View...")
        img_cre = generate_image(scoping, assets, 'Uncommon')
        st.write("Generating Distance View...")
        img_dis = generate_image(scoping, assets, 'Distance')
        st.write("Generating Abstract View...")
        img_abs = generate_image(scoping, assets, 'Abstract')
        status.update(label="Generation Complete!", state="complete", expanded=False)

    # Save to history (Simple Mock)
    thumbnail = img_std or img_cre or img_dis or img_abs
    if thumbnail:
        st.session_state.history.append({
            'topic': scoping['topic'],
            'date': 'Just Now',
            'thumbnail': thumbnail
        })

    # Display Grid
    c1, c2 = st.columns(2)
    c3, c4 = st.columns(2)

    with c1: 
        st.subheader("Standard")
        if img_std: st.image(img_std)
    with c2: 
        st.subheader("Creative")
        if img_cre: st.image(img_cre)
    with c3: 
        st.subheader("Distance")
        if img_dis: st.image(img_dis)
    with c4: 
        st.subheader("Abstract")
        if img_abs: st.image(img_abs)

    if st.button("Start New Project"):
        st.session_state.page = "dashboard"
        st.session_state.scoping = {}
        st.session_state.assets = {}
        st.rerun()

# --- MAIN ROUTER ---

if st.session_state.page == "dashboard":
    render_dashboard()
elif st.session_state.page == "wizard_1":
    render_wizard_phase_1()
elif st.session_state.page == "wizard_2":
    render_wizard_phase_2()
elif st.session_state.page == "results":
    render_results()