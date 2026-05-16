import streamlit as st
import pandas as pd
from PIL import Image
import zipfile
import os
import random
import time

# =====================================================
# CONFIG
# =====================================================

st.set_page_config(
    page_title="Property Guessr",
    page_icon="🏡",
    layout="wide"
)

# =====================================================
# LOAD DATA
# =====================================================
@st.cache_data
def load_data():

    df = pd.read_csv("data.csv")

    df = df[df["is_train"] == False].reset_index(drop=True)

    df["huisnummer"] = (
        df["huisnummer"]
        .fillna("")
        .astype(str)
        .str.replace(".0", "", regex=False)
    )

    return df


df = load_data()

# =====================================================
# HELPERS
# =====================================================

def euro(x):

    try:

        x = float(x)

        rounded = round(x / 10000) * 10000

        return f"€ {int(rounded / 1000)}K"

    except:

        return "-"


def safe(x):

    if pd.isna(x):
        return "-"

    return str(x)

def get_images(idx):

    folder = f"images/{idx}"

    imgs = []

    if os.path.exists(folder):

        for file in sorted(os.listdir(folder)):

            if file.endswith(".jpg") or file.endswith(".png"):

                path = os.path.join(folder, file)

                try:

                    img = Image.open(path)
                    img.verify()

                    imgs.append(path)

                except:
                    continue
    if len(imgs) > 0:
        return imgs[:5]
    else:
        st.rerun()



def calc_points(error):

    if error < 10001:
        return 100

    elif error < 30001:
        return 80

    elif error < 50001:
        return 50

    elif error < 100001:
        return 20

    return 0


# =====================================================
# SESSION STATE
# =====================================================

if "round" not in st.session_state:
    st.session_state.round = 1

if "max_rounds" not in st.session_state:
    st.session_state.max_rounds = 5

if "revealed" not in st.session_state:
    st.session_state.revealed = False

if "player_score" not in st.session_state:
    st.session_state.player_score = 0

if "ai_score" not in st.session_state:
    st.session_state.ai_score = 0

if "rules_open" not in st.session_state:
    st.session_state.rules_open = True

if "used_indices" not in st.session_state:

    st.session_state.used_indices = random.sample(
        range(len(df)),
        st.session_state.max_rounds
    )

current_idx = st.session_state.used_indices[
    st.session_state.round - 1
]

house = df.iloc[current_idx]

game_finished = (
    st.session_state.round == st.session_state.max_rounds
    and st.session_state.revealed
)

# =====================================================
# CSS
# =====================================================

st.markdown("""
<style>

#MainMenu {
    visibility: hidden;
}

header {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>

html, body, [class*="css"] {
    background-color: #08111f;
    color: white;
    font-family: sans-serif;
}

.block-container {
    max-width: 1750px;
    padding-top: 1rem;
    padding-left: 2rem;
    padding-right: 2rem;
}

/* TITLE */

.main-title {
    font-size: 36px;
    font-weight: 700;
    margin-bottom: 10px;
}

/* ADDRESS */

.address {
    color: #c8d2de;
    font-size: 18px;
    margin-top: -10px;
    margin-bottom: 30px;
}

/* IMAGES */

img {
    border-radius: 14px;
    object-fit: cover;
}

/* FEATURES */

.feature-grid {
    display: flex;
    gap: 20px;
    margin-top: 25px;
    margin-bottom: 40px;
}

.feature-box {
    flex: 1;
    background: #111827;
    border-radius: 14px;
    padding: 22px;
}

.feature-label {
    color: #8ea3b9;
    font-size: 14px;
}

.feature-value {
    font-size: 24px;
    font-weight: 700;
    margin-top: 8px;
}

/* SECTION */

.section-title {
    font-size: 34px;
    font-weight: 700;
    margin-top: 30px;
    margin-bottom: 20px;
}

/* INFO GRID */

.info-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
}

.info-item {
    background: #111827;
    border-radius: 14px;
    padding: 18px;
}

.info-key {
    color: #8ea3b9;
    font-size: 13px;
}

.info-value {
    margin-top: 8px;
    font-size: 17px;
    font-weight: 600;
}

/* SCOREBOARD */

.score-wrapper {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 18px;
    margin-bottom: 30px;
}

.score-box {
    flex: 1;
    text-align: center;
    padding: 22px;
    border-radius: 16px;
}

.player-box {
    background: #123d73;
    border: 2px solid #3d7edb;
}

.ai-box {
    background: #5a1d1d;
    border: 2px solid #d94c4c;
}

.score-label {
    font-size: 14px;
    opacity: 0.8;
}

.score-number {
    font-size: 42px;
    font-weight: 700;
}

.vs-box {
    background: #111827;
    padding: 14px 18px;
    border-radius: 12px;
    font-weight: 700;
}

/* PRICE CARD */

.flip-card {
    perspective: 1000px;
    margin-top: 20px;
}

.flip-inner {
    position: relative;
    width: 100%;
    height: 180px;
    transition: transform 0.7s;
    transform-style: preserve-3d;
}

.flipped {
    transform: rotateY(180deg);
}

.flip-front, .flip-back {

    position: absolute;
    width: 100%;
    height: 100%;
    backface-visibility: hidden;

    border-radius: 18px;

    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;

    padding: 20px;
}

.flip-front {
    background: #102443;
    border: 1px solid #1f4e87;
}

.flip-back {
    background: #16375e;
    border: 1px solid #4b88d9;
    transform: rotateY(180deg);
}

.price-main {
    font-size: 52px;
    font-weight: 700;
}

.price-sub {
    color: #9fb3c8;
    margin-top: 10px;
}

/* BUTTON */

.stButton > button {
    background-color: #f7a100;
    color: black;
    border-radius: 10px;
    border: none;
    font-weight: 700;
    padding: 12px 20px;
}

.stButton > button:hover {
    background-color: #ffb31a;
    color: black;
}

/* Play Again BUTTON */

.st-key-play_again {
    width: 100%;
}

.st-key-play_again > div {
    display: flex;
    justify-content: center;
    width: 100%;
}

.st-key-play_again button {

    width: auto !important;
    min-width: 240px;

    height: 64px !important;

    padding: 0 34px !important;

    font-size: 22px !important;
    font-weight: 800 !important;

    border-radius: 16px !important;

    background: linear-gradient(
        135deg,
        #f7a100 0%,
        #ffcc45 100%
    ) !important;

    color: #111 !important;

    box-shadow:
        0 10px 28px rgba(247,161,0,0.30);

    transition: 0.18s ease;
}

.st-key-play_again button:hover {

    transform: translateY(-2px);

    box-shadow:
        0 16px 36px rgba(247,161,0,0.40);
}

</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>

/* TYPEWRITER EFFECT */

.price-main {

    font-size: 52px;
    font-weight: 700;

    white-space: nowrap;

    display: inline-block;

    animation:
        popin 0.45s ease-out,
        typing 1s steps(12, end);

    transform-origin: center;
}

/* TYPE EFFECT */

@keyframes typing {

    from {
        clip-path: inset(0 100% 0 0);
    }

    to {
        clip-path: inset(0 0 0 0);
    }
}

/* SUBTLE POP */

@keyframes popin {

    0% {
        transform: scale(0.92);
        opacity: 0.6;
    }

    100% {
        transform: scale(1);
        opacity: 1;
    }
}

</style>
""", unsafe_allow_html=True)

# =====================================================
# HEADER
# =====================================================

st.markdown("""
<div style="
display:flex;
align-items:flex-end;
gap:18px;
margin-bottom:28px;
justify-content:space-between;
flex-wrap:wrap;
">

<div class="main-title" style="margin-bottom:0;">
🏡 Property Guessr
</div>

<div style="
font-size:22px;
color:#9fb3c8;
padding-bottom:10px;
">
Can you predict house prices better than AI?
</div>

</div>
""", unsafe_allow_html=True)
# =====================================================
# FINAL SCREEN
# =====================================================

if (game_finished):

    final_diff = abs(
        st.session_state.player_score
        - st.session_state.ai_score
    )

    if st.session_state.player_score > st.session_state.ai_score:

        final_title = "🏆 YOU BEAT THE AI"
        final_sub = "Human intuition wins."
        final_color = "#22e06f"

        final_bg = """
        linear-gradient(
            180deg,
            rgba(0,120,50,0.30) 0%,
            rgba(0,70,30,0.22) 100%
        )
        """

        final_border = "#22c55e"

    elif st.session_state.player_score < st.session_state.ai_score:

        final_title = "🤖 AI WINS"
        final_sub = "The model predicted better this time."
        final_color = "#ff6262"

        final_bg = """
        linear-gradient(
            180deg,
            rgba(120,20,20,0.30) 0%,
            rgba(70,15,15,0.22) 100%
        )
        """

        final_border = "#ef4444"

    else:

        final_title = "🤝 DRAW"
        final_sub = "You matched the AI exactly."
        final_color = "#fbbf24"

        final_bg = """
        linear-gradient(
            180deg,
            rgba(120,90,20,0.26) 0%,
            rgba(70,50,10,0.20) 100%
        )
        """

        final_border = "#fbbf24"

    max_score = st.session_state.max_rounds*100
    

    player_bar = (
        st.session_state.player_score
        / max_score
    ) * 100

    ai_bar = (
        st.session_state.ai_score
        / max_score
    ) * 100

    st.markdown(
        f"""
    <div style="
    margin-top:40px;
    padding:42px;
    border-radius:32px;
    background:{final_bg};
    border:1px solid {final_border};
    animation:popin 0.35s ease-out;
    ">

    <div style="
    text-align:center;
    font-size:64px;
    font-weight:800;
    color:{final_color};
    margin-bottom:10px;
    ">
    {final_title}
    </div>

    <div style="
    text-align:center;
    font-size:20px;
    color:#b6c4d4;
    margin-bottom:40px;
    ">
    {final_sub}
    </div>

    <div style="
    display:flex;
    gap:28px;
    margin-bottom:32px;
    ">

    <div style="
    flex:1;
    background:rgba(20,35,60,0.72);
    border:1px solid rgba(70,120,220,0.35);
    border-radius:24px;
    padding:28px;
    ">

    <div style="
    font-size:16px;
    color:#9db4cf;
    margin-bottom:12px;
    ">
    PLAYER
    </div>

    <div style="
    font-size:72px;
    font-weight:800;
    margin-bottom:20px;
    ">
    {st.session_state.player_score}
    </div>

    <div style="
    height:16px;
    background:rgba(255,255,255,0.06);
    border-radius:999px;
    overflow:hidden;
    margin-bottom:12px;
    ">

    <div style="
    width:{player_bar}%;
    height:100%;
    background:linear-gradient(
    90deg,
    #22c55e 0%,
    #4ade80 100%
    );
    ">
    </div>

    </div>

    <div style="
    font-size:15px;
    color:#8ea3b9;
    ">
    Your final score
    </div>

    </div>

    <div style="
    flex:1;
    background:rgba(60,20,20,0.68);
    border:1px solid rgba(220,70,70,0.32);
    border-radius:24px;
    padding:28px;
    ">

    <div style="
    font-size:16px;
    color:#c7a8a8;
    margin-bottom:12px;
    ">
    AI MODEL
    </div>

    <div style="
    font-size:72px;
    font-weight:800;
    margin-bottom:20px;
    ">
    {st.session_state.ai_score}
    </div>

    <div style="
    height:16px;
    background:rgba(255,255,255,0.06);
    border-radius:999px;
    overflow:hidden;
    margin-bottom:12px;
    ">

    <div style="
    width:{ai_bar}%;
    height:100%;
    background:linear-gradient(
    90deg,
    #ef4444 0%,
    #f87171 100%
    );
    ">
    </div>

    </div>

    <div style="
    font-size:15px;
    color:#8ea3b9;
    ">
    AI final score
    </div>

    </div>

    </div>

    <div style="
    background:rgba(255,255,255,0.04);
    border:1px solid rgba(255,255,255,0.06);
    border-radius:20px;
    padding:22px;
    text-align:center;
    margin-bottom:28px;
    ">

    <div style="
    font-size:16px;
    color:#8ea3b9;
    margin-bottom:10px;
    ">
    Final score difference
    </div>

    <div style="
    font-size:48px;
    font-weight:800;
    color:{final_color};
    ">
    {final_diff} points
    </div>

    </div>

    </div>
        """,
        unsafe_allow_html=True
    )


    st.write("")

    center = st.columns([1,1,1])[1]

    with center:

        if st.button(
            "Play again",
            key="play_again"
        ):

            st.session_state.round = 1
            st.session_state.player_score = 0
            st.session_state.ai_score = 0
            st.session_state.revealed = False

            st.session_state.guess_price = 500000

            st.session_state.used_indices = random.sample(
                range(len(df)),
                st.session_state.max_rounds
            )

            st.session_state.rules_open = False

            st.rerun()

else:
    # =====================================================
    # PROGRESS
    # =====================================================

    progress = (st.session_state.round - 1) / st.session_state.max_rounds

    st.progress(progress)

    st.write("")

    # =====================================================
    # MAIN LAYOUT
    # =====================================================

    left, spacer, right = st.columns([3.5, 0.18, 1.2])

    # =====================================================
    # LEFT SIDE (UNCHANGED)
    # =====================================================

    with left:

        imgs = get_images(current_idx)

        if len(imgs) > 0:

            col_big, col_small = st.columns([2.7, 2.5])

            with col_big:

                st.image(
                    imgs[0],
                    use_container_width=True
                )

            with col_small:

                top1, top2 = st.columns(2)

                if len(imgs) > 1:
                    with top1:
                        st.image(imgs[1], use_container_width=True)

                if len(imgs) > 2:
                    with top2:
                        st.image(imgs[2], use_container_width=True)

                bottom1, bottom2 = st.columns(2)

                if len(imgs) > 3:
                    with bottom1:
                        st.image(imgs[3], use_container_width=True)

                if len(imgs) > 4:
                    with bottom2:
                        st.image(imgs[4], use_container_width=True)

        st.markdown(
            f"# {safe(house['straat'])} {safe(house['huisnummer'])}"
        )

        st.markdown(
            f'<div class="address">{safe(house["postcode"])} {safe(house["plaats"])} - {safe(house["wijk"])}</div>',
            unsafe_allow_html=True
        )

        features_html = f"""
    <div class="feature-grid">

    <div class="feature-box">
    <div class="feature-label">Wonen</div>
    <div class="feature-value">{safe(house.get("Wonen"))}</div>
    </div>

    <div class="feature-box">
    <div class="feature-label">Kamers</div>
    <div class="feature-value">{safe(house.get("Aantal kamers"))}</div>
    </div>

    <div class="feature-box">
    <div class="feature-label">Bouwjaar</div>
    <div class="feature-value">{safe(house.get("Bouwjaar"))}</div>
    </div>

    </div>
    """

        st.markdown(
            features_html,
            unsafe_allow_html=True
        )

        st.markdown(
            '<div class="section-title">Kenmerken</div>',
            unsafe_allow_html=True
        )

        kenmerken = [
            ("Soort woonhuis", house.get("Soort woonhuis")),
            ("Energielabel", house.get("Energielabel")),
            ("Ligging", house.get("Ligging")),
            ("Tuin", house.get("Tuin")),
            ("Verwarming", house.get("Verwarming")),
            ("Perceel", house.get("Perceel")),
            ("Isolatie", house.get("Isolatie")),
            ("Warm water", house.get("Warm water"))
        ]

        info_html = '<div class="info-grid">'

        for k, v in kenmerken:

            info_html += f"""<div class="info-item">
    <div class="info-key">{safe(k)}</div>
    <div class="info-value">{safe(v)}</div>
    </div>"""

        info_html += "</div>"

        st.markdown(
            info_html,
            unsafe_allow_html=True
        )

    # =====================================================
    # RIGHT SIDE
    # =====================================================

    with right:

        # -------------------------------------------------
        # DEFAULT GUESS
        # -------------------------------------------------

        if "guess_price" not in st.session_state:
            st.session_state.guess_price = 500000

        # -------------------------------------------------
        # SCOREBOARD
        # -------------------------------------------------

        score_html = f"""
    <div class="score-wrapper">

    <div class="score-box player-box">
    <div class="score-label">PLAYER</div>
    <div class="score-number">{st.session_state.player_score}</div>
    </div>

    <div class="vs-box">
    VS.
    </div>

    <div class="score-box ai-box">
    <div class="score-label">AI</div>
    <div class="score-number">{st.session_state.ai_score}</div>
    </div>

    </div>
    """

        st.markdown(
            score_html,
            unsafe_allow_html=True
        )

        # -------------------------------------------------
        # FLIP CARD
        # -------------------------------------------------

        flipped = "flipped" if st.session_state.revealed else ""

        price = euro(house["Vraagprijs"])

        card_html = f"""
    <div class="flip-card">

    <div class="flip-inner {flipped}">

    <div class="flip-front">

    <div class="price-main">
    {euro(st.session_state.guess_price)}
    </div>

    <div class="price-sub">
    Guess the price
    </div>

    </div>

    <div class="flip-back">

    <div class="price-main">
    {price}
    </div>

    <div class="price-sub">
    Actual asking price
    </div>

    </div>

    </div>

    </div>
    """

        st.markdown(
            card_html,
            unsafe_allow_html=True
        )

        st.write("")

        # -------------------------------------------------
        # BUTTON STYLING
        # -------------------------------------------------
        st.markdown("""
    <style>

    /* ALGEMENE BUTTONS */

    div.stButton > button {
        width: 100%;
        height: 54px;
        font-size: 18px;
        font-weight: 700;
        border-radius: 12px;
        transition: 0.2s ease;
    }

    /* -50K */

    .st-key-minus50 button {

        background-color: #5a1d1d !important;
        color: white !important;

        border: 1px solid #d94c4c !important;
    }

    .st-key-minus50 button:hover {

        background-color: #742626 !important;
        border: 1px solid #ff6b6b !important;
    }

    /* -10K */

    .st-key-minus10 button {

        background-color: #6e1b1b !important;
        color: white !important;

        border: 1px solid #ff6b6b !important;
    }

    .st-key-minus10 button:hover {

        background-color: #842222 !important;
        border: 1px solid #ff8787 !important;
    }

    /* +10K */

    .st-key-plus10 button {

        background-color: #1d5a2b !important;
        color: white !important;

        border: 1px solid #4ade80 !important;
    }

    .st-key-plus10 button:hover {

        background-color: #26753a !important;
        border: 1px solid #86efac !important;
    }

    /* +50K */

    .st-key-plus50 button {

        background-color: #226c35 !important;
        color: white !important;

        border: 1px solid #86efac !important;
    }

    .st-key-plus50 button:hover {

        background-color: #2f8f46 !important;
        border: 1px solid #bbf7d0 !important;
    }

    /* CHECK PRICE */

    .st-key-check_price button {

        background: linear-gradient(
            135deg,
            #f7a100 0%,
            #ffbc2b 100%
        ) !important;

        color: #111 !important;

        border: none !important;

        border-radius: 14px !important;

        height: 58px !important;

        font-size: 20px !important;
        font-weight: 800 !important;

        letter-spacing: 0.3px;

        box-shadow:
            0 6px 18px rgba(247, 161, 0, 0.28);

        transition: all 0.18s ease-in-out !important;
    }

    .st-key-check_price button:hover {

        transform: translateY(-2px);

        background: linear-gradient(
            135deg,
            #ffb31a 0%,
            #ffca45 100%
        ) !important;

        color: #111 !important;

        box-shadow:
            0 10px 24px rgba(247, 161, 0, 0.4);
    }

    .st-key-check_price button:active {

        transform: scale(0.98);
    }

    </style>
    """, unsafe_allow_html=True)
        # -------------------------------------------------
        # PRICE CONTROLS
        # -------------------------------------------------

        if not st.session_state.revealed:

            minus50, minus10, plus10, plus50 = st.columns(4)

            with minus50:

                st.markdown(
                    '<div class="red-btn">',
                    unsafe_allow_html=True
                )

                if st.button("-50K", key="minus50"):

                    st.session_state.guess_price = max(
                        0,
                        st.session_state.guess_price - 50000
                    )

                    st.rerun()

                st.markdown(
                    '</div>',
                    unsafe_allow_html=True
                )

            with minus10:

                st.markdown(
                    '<div class="red-btn">',
                    unsafe_allow_html=True
                )

                if st.button("-10K", key="minus10"):

                    st.session_state.guess_price = max(
                        0,
                        st.session_state.guess_price - 10000
                    )

                    st.rerun()

                st.markdown(
                    '</div>',
                    unsafe_allow_html=True
                )

            with plus10:

                st.markdown(
                    '<div class="green-btn">',
                    unsafe_allow_html=True
                )

                if st.button("+10K", key="plus10"):

                    st.session_state.guess_price += 10000

                    st.rerun()

                st.markdown(
                    '</div>',
                    unsafe_allow_html=True
                )

            with plus50:

                st.markdown(
                    '<div class="green-btn">',
                    unsafe_allow_html=True
                )

                if st.button("+50K", key="plus50"):

                    st.session_state.guess_price += 50000

                    st.rerun()

                st.markdown(
                    '</div>',
                    unsafe_allow_html=True
                )

        # -------------------------------------------------
        # CHECK PRICE BUTTON
        # -------------------------------------------------

        check_left, check_mid, check_right = st.columns([1.4, 1, 1.4])

        with check_mid:

            if not st.session_state.revealed:

                if st.button(
                    "Check price",
                    key="check_price",
                    type="primary"
                ):

                    st.session_state.revealed = True

                    real = round(house["Vraagprijs"]/ 10000) * 10000
                    model = house["model_pred"]

                    guess = round(st.session_state.guess_price / 10000) * 10000

                    user_err = abs(real - guess)
                    ai_err = abs(real - model)

                    user_points = calc_points(user_err)
                    ai_points = calc_points(ai_err)

                    st.session_state.player_score += user_points
                    st.session_state.ai_score += ai_points

                    time.sleep(0.3)

                    st.rerun()

    # -------------------------------------------------
    # POINTS INFO BOX
    # -------------------------------------------------
        
        if not st.session_state.revealed:

            with st.expander("🎮 How to play", expanded=st.session_state.rules_open):

                st.markdown("""
                <div style="display:flex;flex-direction:column;gap:14px;padding-bottom:12px;">

                <div style="padding:14px 16px;background:rgba(59,130,246,0.10);border:1px solid rgba(59,130,246,0.30);border-radius:14px;">
                <div style="font-size:16px;font-weight:700;color:#dbeafe;margin-bottom:6px;">
                🏡 Guess the asking price
                </div>
                <div style="color:#9fb3c8;font-size:14px;line-height:1.5;">
                Use the buttons to increase or decrease your price estimate before revealing the real price.
                </div>
                </div>

                <div style="padding:14px 16px;background:rgba(239,68,68,0.08);border:1px solid rgba(239,68,68,0.24);border-radius:14px;">
                <div style="font-size:16px;font-weight:700;color:#fecaca;margin-bottom:6px;">
                🤖 Beat the AI
                </div>
                <div style="color:#9fb3c8;font-size:14px;line-height:1.5;">
                You are competing against my trained AI housing model. Score points based on how close your guess is to the actual listing price.
                </div>
                </div>

                <div style="padding:14px 16px;background:rgba(34,197,94,0.10);border:1px solid rgba(34,197,94,0.26);border-radius:14px;">
                <div style="font-size:16px;font-weight:700;color:#d7ffe5;margin-bottom:6px;">
                🏆 Win the game
                </div>
                <div style="color:#9fb3c8;font-size:14px;line-height:1.5;">
                Try to outperform the AI by estimating the asking price more accurately than the model prediction. The game lasts 5 rounds. Earn points each round and finish with a higher score than the AI to win! 
                </div>
                </div>

                </div>
                """, unsafe_allow_html=True)

            with st.expander("🎯 Score", expanded=False):
                st.markdown("""
                <div style="display:flex;flex-direction:column;gap:12px;padding-bottom:12px;">

                <div style="display:flex;justify-content:space-between;align-items:center;padding:12px 14px;background:rgba(34,197,94,0.12);border:1px solid rgba(34,197,94,0.35);border-radius:12px;">
                <div style="color:#d7ffe5;font-size:15px;">Within €10K</div>
                <div style="color:#22e06f;font-weight:800;font-size:18px;">+100</div>
                </div>

                <div style="display:flex;justify-content:space-between;align-items:center;padding:12px 14px;background:rgba(59,130,246,0.10);border:1px solid rgba(59,130,246,0.30);border-radius:12px;">
                <div style="color:#dbeafe;font-size:15px;">Within €30K</div>
                <div style="color:#60a5fa;font-weight:800;font-size:18px;">+80</div>
                </div>

                <div style="display:flex;justify-content:space-between;align-items:center;padding:12px 14px;background:rgba(245,158,11,0.10);border:1px solid rgba(245,158,11,0.30);border-radius:12px;">
                <div style="color:#fde7b0;font-size:15px;">Within €50K</div>
                <div style="color:#fbbf24;font-weight:800;font-size:18px;">+50</div>
                </div>

                <div style="display:flex;justify-content:space-between;align-items:center;padding:12px 14px;background:rgba(239,68,68,0.08);border:1px solid rgba(239,68,68,0.22);border-radius:12px;">
                <div style="color:#fecaca;font-size:15px;">Within €100K</div>
                <div style="color:#ff7b7b;font-weight:800;font-size:18px;">+20</div>
                </div>

                </div>
                """, unsafe_allow_html=True)

            with st.expander("🧠 About the data & AI model", expanded=False):

                st.markdown("""
                <div style="
                display:flex;
                flex-direction:column;
                gap:14px;
                padding-bottom:12px;
                ">

                <div style="
                padding:14px 16px;
                background:rgba(59,130,246,0.10);
                border:1px solid rgba(59,130,246,0.30);
                border-radius:14px;
                ">
                <div style="
                font-size:16px;
                font-weight:700;
                color:#dbeafe;
                margin-bottom:6px;
                ">
                🌐 Scraped housing data
                </div>

                <div style="
                color:#9fb3c8;
                font-size:14px;
                line-height:1.6;
                ">
                The houses shown in this game come from real Dutch property listings, specifically houses located in Almere.
                Listing information, prices and images were scraped and processed into a structured dataset.
                </div>
                </div>

                <div style="
                padding:14px 16px;
                background:rgba(168,85,247,0.10);
                border:1px solid rgba(168,85,247,0.28);
                border-radius:14px;
                ">
                <div style="
                font-size:16px;
                font-weight:700;
                color:#e9d5ff;
                margin-bottom:6px;
                ">
                🤖 Machine learning model
                </div>

                <div style="
                color:#9fb3c8;
                font-size:14px;
                line-height:1.6;
                ">
                The AI opponent is a trained regression model that predicts asking prices based on housing characteristics such as living area, location, energy label, rooms, insulation and more.
                </div>
                </div>

                <div style="
                padding:14px 16px;
                background:rgba(34,197,94,0.10);
                border:1px solid rgba(34,197,94,0.26);
                border-radius:14px;
                ">
                <div style="
                font-size:16px;
                font-weight:700;
                color:#d7ffe5;
                margin-bottom:6px;
                ">
                📊 Training vs testing
                </div>

                <div style="
                color:#9fb3c8;
                font-size:14px;
                line-height:1.6;
                ">
                The model was trained on a separate training dataset and is evaluated only on unseen test houses (90:10 split).
                Every house in this game comes from the test set, meaning the AI has never seen these listings before.
                </div>
                </div>
                </div>
                """, unsafe_allow_html=True)
        # -------------------------------------------------
        # RESULTS
        # -------------------------------------------------

        if st.session_state.revealed:

            real = round(house["Vraagprijs"]/ 10000) * 10000
            model = house["model_pred"]

            guess = round(st.session_state.guess_price / 10000) * 10000

            user_err = abs(real - guess)
            ai_err = abs(real - model)

            user_points = calc_points(user_err)
            ai_points = calc_points(ai_err)

            player_wins = user_err < ai_err

            

            display_user_err = abs(
                real - round(guess / 10000) * 10000
            )

            display_ai_err = abs(
                real - round(model / 10000) * 10000
            )

            display_user_guess = round(guess / 10000) * 10000
            display_ai_guess = round(model / 10000) * 10000

            display_user_err = abs(real - display_user_guess)
            display_ai_err = abs(real - display_ai_guess)

            # USER DIRECTION

            if display_user_guess > real:

                user_arrow = "↑"
                user_arrow_color = "#f87171"

            elif display_user_guess < real:

                user_arrow = "↓"
                user_arrow_color = "#4ade80"

            else:

                user_arrow = "•"
                user_arrow_color = "#ffffff"

            # AI DIRECTION

            if display_ai_guess > real:

                ai_arrow = "↑"
                ai_arrow_color = "#f87171"

            elif display_ai_guess < real:

                ai_arrow = "↓"
                ai_arrow_color = "#4ade80"

            else:

                ai_arrow = "•"
                ai_arrow_color = "#ffffff"

            if player_wins:

                winner_title = "🏆 YOU WIN"
                winner_points = f"+{user_points} points"

                loser_text = "AI loses this round"
                loser_points = f"+{ai_points} points"

                result_bg = "linear-gradient(180deg, rgba(0,120,50,0.28) 0%, rgba(0,70,30,0.20) 100%)"

                result_border = "#22c55e"
                winner_color = "#22e06f"

            else:

                winner_title = "🤖 AI WINS"
                winner_points = f"+{ai_points} points"

                loser_text = "You lose this round"
                loser_points = f"+{user_points} points"

                result_bg = "linear-gradient(180deg, rgba(120,20,20,0.30) 0%, rgba(70,15,15,0.22) 100%)"

                result_border = "#ef4444"
                winner_color = "#ff6262"

            st.markdown(
                f"""
        <div style="margin-top:28px;padding:34px 28px;border-radius:24px;background:{result_bg};border:1px solid {result_border};text-align:center;animation:popin 0.35s ease-out;">

        <div style="font-size:46px;font-weight:800;color:{winner_color};margin-bottom:10px;">
        {winner_title}
        </div>

        <div style="font-size:34px;font-weight:700;margin-bottom:18px;">
        {winner_points}
        </div>

        <div style="color:#aebed0;font-size:18px;margin-bottom:4px;">
        {loser_text}
        </div>

        <div style="color:#6f8197;font-size:16px;margin-bottom:30px;">
        {loser_points}
        </div>

        <div style="display:flex;justify-content:center;gap:46px;margin-bottom:8px;">

        <div>
        <div style="font-size:13px;color:#8ea3b9;margin-bottom:6px;">
        Your guess
        </div>

        <div style="font-size:34px;font-weight:700;">
        {euro(guess)}
        </div>

        <div style="
        font-size:14px;
        margin-top:6px;
        color:{'#4ade80' if display_user_err < display_ai_err else '#f87171'};
        ">
        <span style="color:{user_arrow_color} !important;font-weight:700;">
        {user_arrow}
        </span>
        {euro(display_user_err)} off
        </div>

        </div>

        <div>
        <div style="font-size:13px;color:#8ea3b9;margin-bottom:6px;">
        AI guess
        </div>

        <div style="font-size:34px;font-weight:700;">
        {euro(model)}
        </div>
        <div style="
        font-size:14px;
        margin-top:6px;
        color:{'#4ade80' if display_ai_err < display_user_err else '#f87171'};
        ">
        <span style="color:{ai_arrow_color} !important;font-weight:700;">
        {ai_arrow}
        </span>
        {euro(display_ai_err)} off
        </div>

        </div>

        </div>

        </div>
        """,
                unsafe_allow_html=True
            )

            st.write("")

            # -------------------------------------------------
            # NEXT ROUND BUTTON
            # -------------------------------------------------

            next_left, next_mid, next_right = st.columns([1.2, 1, 1.2])

            with next_mid:
                st.session_state.rules_open = False

                if st.session_state.round < st.session_state.max_rounds:

                    if st.button(
                        "Next round",
                        key="next_round",
                        type="primary"
                    ):

                        st.session_state.round += 1

                        st.session_state.revealed = False

                        st.session_state.guess_price = 500000

                        st.rerun()
    st.markdown("""
    <div style="
    margin-top:60px;
    padding-top:24px;
    padding-bottom:12px;
    border-top:1px solid rgba(255,255,255,0.08);
    display:flex;
    justify-content:space-between;
    align-items:center;
    flex-wrap:wrap;
    gap:16px;
    ">

    <div>

    <div style="
    font-size:18px;
    font-weight:700;
    color:white;
    margin-bottom:4px;
    ">
    🏡 Property Guessr
    </div>

    <div style="
    font-size:14px;
    color:#8ea3b9;
    line-height:1.5;
    max-width:700px;
    ">
    Interactive machine learning project using real Dutch housing listings
    to compare human intuition against AI-based house price predictions.
    </div>

    </div>

    <div style="
    display:flex;
    align-items:center;
    gap:18px;
    font-size:14px;
    color:#6f8197;
    ">

    <div>
    Built with Python & Streamlit
    </div>

    <div style="
    width:5px;
    height:5px;
    border-radius:999px;
    background:#42546a;
    ">
    </div>

    <div>
    Developed by Guido
    </div>

    <div style="
    width:5px;
    height:5px;
    border-radius:999px;
    background:#42546a;
    ">
    </div>

    <div>
    2026
    </div>

    </div>
 
    </div>
    """, unsafe_allow_html=True)

