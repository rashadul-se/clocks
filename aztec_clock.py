"""
Aztec Sun Stone Clock & Codex Borgia Oracle
Streamlit + SQLite — SVG rendered via st.components.v1.html (fixes raw-text leak)
"""

import streamlit as st
import streamlit.components.v1 as components
import sqlite3
import math
import time
import datetime

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Aztec Sun Stone Oracle",
    page_icon="☀️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── SQLite ────────────────────────────────────────────────────────────────────
DB_PATH = "/tmp/aztec_oracle.db"

def init_db():
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.executescript("""
        CREATE TABLE IF NOT EXISTS day_signs (
            id INTEGER PRIMARY KEY,
            nahuatl TEXT, english TEXT, emoji TEXT,
            deity TEXT, element TEXT, direction TEXT,
            personality TEXT, fortune TEXT, warning TEXT
        );
        CREATE TABLE IF NOT EXISTS trecena_numbers (
            num INTEGER PRIMARY KEY,
            label TEXT, intensity TEXT, description TEXT
        );
        CREATE TABLE IF NOT EXISTS readings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            input_date TEXT, day_sign TEXT, day_number INTEGER,
            deity TEXT, fortune TEXT, warning TEXT, role TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    if cur.execute("SELECT COUNT(*) FROM day_signs").fetchone()[0] == 0:
        signs = [
            (1,  "Cipactli","Crocodile","C","Tonacatecuhtli","Water","East",
             "Ambitious, resourceful, primordial strength",
             "Very lucky - first of the cycle, protected by the creator god",
             "Can become ruthless in pursuit of goals"),
            (2,  "Ehecatl","Wind","E","Quetzalcoatl","Air","North",
             "Intellectual, communicative, spiritually restless",
             "Favored by the Feathered Serpent - gifted speaker",
             "Prone to change, unreliable, scattered energy"),
            (3,  "Calli","House","H","Tepeyollotl","Earth","West",
             "Protective, introverted, keeper of secrets",
             "Stable domestic life, strong family bonds",
             "Can be overly conservative or fearful of change"),
            (4,  "Cuetzpalin","Lizard","L","Huehuecoyotl","Earth","South",
             "Playful, sensual, quick-witted trickster",
             "Creative prosperity, especially in arts",
             "Tendency toward deception and mischief"),
            (5,  "Coatl","Serpent","S","Chalchiuhtlicue","Water","East",
             "Wise, transformative, dual-natured",
             "Deep wisdom and healing potential",
             "Hidden dangers, betrayal if power is misused"),
            (6,  "Miquiztli","Death","D","Tecuciztecatl","Air","North",
             "Mystical, philosophical, unafraid of endings",
             "Not truly unlucky - rebirth follows death",
             "Must not dwell in grief; cycles must complete"),
            (7,  "Mazatl","Deer","De","Tlaloc","Water","West",
             "Gentle, graceful, highly adaptable",
             "Blessed by the rain god; fertile and nourishing",
             "Can be too passive; must develop assertiveness"),
            (8,  "Tochtli","Rabbit","R","Mayahuel","Earth","South",
             "Hardworking, fruitful, abundant provider",
             "Lucky/Balanced - 7 is a pivot number, protected from extremes",
             "The 400 Rabbits warn: abundance can become excess and drunkenness"),
            (9,  "Atl","Water","W","Xiuhtecuhtli","Water","East",
             "Emotional depth, powerful intuition, cleansing force",
             "Creative and spiritually gifted",
             "Emotional floods, overwhelming feelings"),
            (10, "Itzcuintli","Dog","Do","Mictlantecuhtli","Earth","North",
             "Loyal, guide of souls, fierce protector",
             "Faithful companion in life and death",
             "Can be overly subservient or lost without guidance"),
            (11, "Ozomatli","Monkey","M","Xochipilli","Air","West",
             "Joyful, artistic, comedian and performer",
             "Gifted in arts, music, and dance",
             "Frivolous spending of talents; clownish avoidance of duty"),
            (12, "Malinalli","Grass","G","Patecatl","Earth","South",
             "Resilient, healing, slow-burning endurance",
             "Medicinal knowledge, ability to outlast adversity",
             "Bitterness; like twisted grass that cuts"),
            (13, "Acatl","Reed","Re","Tezcatlipoca","Air","East",
             "Noble, authoritative, destined for leadership",
             "Strongly associated with rulership and the Fifth Sun",
             "Pride and rigidity; the reed snaps if it will not bend"),
            (14, "Ocelotl","Jaguar","J","Tlazolteotl","Earth","North",
             "Powerful, nocturnal, keeper of dark secrets",
             "Warrior strength; ability to navigate darkness",
             "Danger from hidden enemies; association with night sorcery"),
            (15, "Cuauhtli","Eagle","Ea","Xipe Totec","Air","West",
             "Visionary, courageous, solar warrior",
             "Associated with the sun warriors; great honor",
             "Arrogance; flying too high and losing touch with earth"),
            (16, "Cozcacuauhtli","Vulture","V","Itzpapalotl","Air","South",
             "Patient, wise elder, recycler of wisdom",
             "Long life through adaptability and patience",
             "Can feed on others misfortune if corrupted"),
            (17, "Ollin","Movement","Mv","Xolotl","Earth","East",
             "Dynamic, earthquake-born, agent of change",
             "Destined for great transformations in the world",
             "Instability; everything shakes around this sign"),
            (18, "Tecpatl","Flint","Fl","Chalchiuhtotolin","Air","North",
             "Sharp, decisive, warrior of truth",
             "Cutting through illusion; fierce justice",
             "Coldness, cruelty, severing bonds unnecessarily"),
            (19, "Quiahuitl","Rain","Ra","Tonatiuh","Water","West",
             "Nurturing, cyclical, bringer of renewal",
             "Agricultural abundance; life-giving force",
             "Destructive storms; overwhelming emotional downpours"),
            (20, "Xochitl","Flower","Fl","Xochiquetzal","Earth","South",
             "Beautiful, creative, pleasure-seeking artist",
             "Blessed by the goddess of beauty; gifted in love and art",
             "Vanity, superficiality, obsession with pleasure"),
        ]
        cur.executemany("INSERT INTO day_signs VALUES (?,?,?,?,?,?,?,?,?,?)", signs)

    if cur.execute("SELECT COUNT(*) FROM trecena_numbers").fetchone()[0] == 0:
        numbers = [
            (1,"Ce","Beginning","Pure potential; a new cycle dawns. The deity rules supreme."),
            (2,"Ome","Duality","Balance of opposites; creative tension between two forces."),
            (3,"Yei","Movement","Active energy, things set in motion, crossing a threshold."),
            (4,"Nahui","Stability","The four directions hold firm; foundation and order."),
            (5,"Macuilli","Challenge","Difficulties arise; the middle passage before renewal."),
            (6,"Chicuace","Flow","Energy moves freely; collaboration and community."),
            (7,"Chicome","Pivot","Exact center of the 13-day cycle; balance and protection from extremes."),
            (8,"Chicuei","Abundance","Harvest energy; rewards from past efforts manifest."),
            (9,"Chicnahui","Completion","Cycle nearing its end; wisdom and integration."),
            (10,"Matlactli","Mastery","Skills fully expressed; authority through experience."),
            (11,"Matlactlionce","Excess","Energies peak and overflow; ecstasy and danger of overreach."),
            (12,"Matlactliomome","Release","Letting go; surrendering attachments before the final turn."),
            (13,"Matlactliomei","Transcendence","The cycle completes; divine wholeness before rebirth."),
        ]
        cur.executemany("INSERT INTO trecena_numbers VALUES (?,?,?,?)", numbers)

    con.commit()
    con.close()


def get_all_signs():
    con = sqlite3.connect(DB_PATH)
    rows = con.execute("SELECT * FROM day_signs").fetchall()
    con.close()
    return rows


def get_number_info(num):
    con = sqlite3.connect(DB_PATH)
    row = con.execute("SELECT * FROM trecena_numbers WHERE num=?", (num,)).fetchone()
    con.close()
    return row


def save_reading(input_date, sign, number, deity, fortune, warning, role):
    con = sqlite3.connect(DB_PATH)
    con.execute(
        "INSERT INTO readings (input_date,day_sign,day_number,deity,fortune,warning,role) VALUES (?,?,?,?,?,?,?)",
        (input_date, sign, number, deity, fortune, warning, role),
    )
    con.commit()
    con.close()


def get_recent_readings(limit=6):
    con = sqlite3.connect(DB_PATH)
    rows = con.execute(
        "SELECT input_date,day_sign,day_number,deity,fortune,created_at FROM readings ORDER BY id DESC LIMIT ?",
        (limit,),
    ).fetchall()
    con.close()
    return rows


def tonalpohualli(date):
    epoch    = datetime.date(1900, 1, 1)
    days     = (date - epoch).days
    position = days % 260
    sign_idx = (position % 20) + 1
    number   = (position % 13) + 1
    return sign_idx, number


# ── SVG builder (pure string concat — no f-string interpolation of lists) ─────
def build_svg(highlighted_idx=None, size=380):
    cx = size // 2
    cy = size // 2
    r  = size // 2 - 10

    sign_labels = ["CIP","EHE","CAL","CUE","COA","MIQ","MAZ","TOC",
                   "ATL","ITZ","OZO","MAL","ACA","OCE","CUA","COZ",
                   "OLL","TEC","QUI","XOC"]

    parts = []

    # SVG open + defs
    parts.append(
        '<svg xmlns="http://www.w3.org/2000/svg"'
        ' width="' + str(size) + '" height="' + str(size) + '"'
        ' viewBox="0 0 ' + str(size) + ' ' + str(size) + '">'
        '<defs>'
        '<radialGradient id="bg" cx="50%" cy="50%" r="50%">'
        '<stop offset="0%" stop-color="#1e1508"/>'
        '<stop offset="100%" stop-color="#0d0a05"/>'
        '</radialGradient>'
        '<radialGradient id="ct" cx="50%" cy="50%" r="50%">'
        '<stop offset="0%" stop-color="#3a2010"/>'
        '<stop offset="100%" stop-color="#1a0e05"/>'
        '</radialGradient>'
        '<style>'
        '@keyframes ro{from{transform:rotate(0deg)}to{transform:rotate(360deg)}}'
        '@keyframes rm{from{transform:rotate(0deg)}to{transform:rotate(-360deg)}}'
        '@keyframes pu{0%,100%{opacity:.75}50%{opacity:1}}'
        '.ro{animation:ro 100s linear infinite;transform-box:fill-box;transform-origin:center}'
        '.rm{animation:rm 55s linear infinite;transform-box:fill-box;transform-origin:center}'
        '.pu{animation:pu 3s ease-in-out infinite}'
        '</style>'
        '</defs>'
    )

    # Background
    parts.append(
        '<circle cx="' + str(cx) + '" cy="' + str(cy) + '" r="' + str(r) + '" fill="url(#bg)"/>'
    )

    # Outer ring with ticks
    parts.append('<g class="ro">')
    parts.append(
        '<circle cx="' + str(cx) + '" cy="' + str(cy) + '"'
        ' r="' + str(round(r * 0.96, 1)) + '"'
        ' fill="none" stroke="#c9a84c" stroke-width="1.5"/>'
    )
    for i in range(52):
        a  = math.radians(-90 + i * 360 / 52)
        r1 = r * 0.87
        r2 = r * 0.94 if (i % 4 == 0) else r * 0.91
        sw = "2" if (i % 4 == 0) else "1"
        parts.append(
            '<line x1="' + str(round(cx + r1 * math.cos(a), 1)) +
            '" y1="' + str(round(cy + r1 * math.sin(a), 1)) +
            '" x2="' + str(round(cx + r2 * math.cos(a), 1)) +
            '" y2="' + str(round(cy + r2 * math.sin(a), 1)) +
            '" stroke="#c9a84c" stroke-width="' + sw + '"/>'
        )
    parts.append('</g>')

    # Calendar band circles
    parts.append(
        '<circle cx="' + str(cx) + '" cy="' + str(cy) + '"'
        ' r="' + str(round(r * 0.82, 1)) + '"'
        ' fill="#130d04" stroke="#c9a84c" stroke-width="1.5"/>'
        '<circle cx="' + str(cx) + '" cy="' + str(cy) + '"'
        ' r="' + str(round(r * 0.60, 1)) + '"'
        ' fill="#0d0a05" stroke="#7a5020" stroke-width="1"/>'
    )

    # Day sign ring (counter-rotating)
    parts.append('<g class="rm">')
    for i in range(20):
        angle_rad = math.radians(-90 + i * 18)
        ring_r    = r * 0.71
        sx = cx + ring_r * math.cos(angle_rad)
        sy = cy + ring_r * math.sin(angle_rad)
        is_hi  = (highlighted_idx is not None and (i + 1) == highlighted_idx)
        fill   = "#c9a84c" if is_hi else "#2a1f10"
        stroke = "#ffe080" if is_hi else "#5a3a10"
        sw     = "2.5" if is_hi else "1"
        label  = sign_labels[i]
        parts.append(
            '<rect x="' + str(round(sx - 16, 1)) +
            '" y="' + str(round(sy - 11, 1)) +
            '" width="32" height="22" rx="3"'
            ' fill="' + fill + '" stroke="' + stroke + '" stroke-width="' + sw + '"/>'
            '<text x="' + str(round(sx, 1)) +
            '" y="' + str(round(sy + 5, 1)) +
            '" text-anchor="middle" font-size="9"'
            ' fill="' + ('#1a0e05' if is_hi else '#c9a84c') + '"'
            ' font-family="Georgia,serif" font-weight="bold">' + label + '</text>'
        )
    parts.append('</g>')

    # Number dots
    parts.append(
        '<circle cx="' + str(cx) + '" cy="' + str(cy) + '"'
        ' r="' + str(round(r * 0.56, 1)) + '"'
        ' fill="#1a1208" stroke="#5a3a10" stroke-width="1"/>'
    )
    for i in range(13):
        a      = math.radians(-90 + i * 360 / 13)
        ring_r = r * 0.47
        dx = cx + ring_r * math.cos(a)
        dy = cy + ring_r * math.sin(a)
        parts.append(
            '<circle cx="' + str(round(dx, 1)) + '" cy="' + str(round(dy, 1)) +
            '" r="10" fill="#1a1208" stroke="#c9a84c" stroke-width="1.5"/>'
            '<text x="' + str(round(dx, 1)) + '" y="' + str(round(dy + 4, 1)) +
            '" text-anchor="middle" font-size="10" fill="#e8c05a"'
            ' font-family="Georgia,serif">' + str(i + 1) + '</text>'
        )

    # Centre sun (pulsing)
    parts.append('<g class="pu">')
    parts.append(
        '<circle cx="' + str(cx) + '" cy="' + str(cy) + '"'
        ' r="' + str(round(r * 0.30, 1)) + '"'
        ' fill="url(#ct)" stroke="#c9a84c" stroke-width="2"/>'
    )
    for j in range(8):
        parts.append(
            '<line x1="' + str(cx) + '" y1="' + str(round(cy - r * 0.30, 1)) +
            '" x2="' + str(cx) + '" y2="' + str(round(cy - r * 0.39, 1)) +
            '" stroke="#c9a84c" stroke-width="3"'
            ' transform="rotate(' + str(j * 45) + ',' + str(cx) + ',' + str(cy) + ')"/>'
        )
    parts.append(
        '<text x="' + str(cx) + '" y="' + str(round(cy + 8, 1)) +
        '" text-anchor="middle" font-size="' + str(round(r * 0.18)) +
        '" font-family="serif">&#9728;&#65039;</text>'
        '<text x="' + str(cx) + '" y="' + str(round(cy + r * 0.27, 1)) +
        '" text-anchor="middle" font-size="9" fill="#c9a84c"'
        ' font-family="Georgia,serif">TONATIUH</text>'
    )
    parts.append('</g>')

    # 13-Reed anchor at top
    parts.append(
        '<rect x="' + str(cx - 24) + '" y="' + str(cy - r + 3) +
        '" width="48" height="22" rx="3"'
        ' fill="#3a2010" stroke="#c9a84c" stroke-width="1.5"/>'
        '<text x="' + str(cx) + '" y="' + str(cy - r + 18) +
        '" text-anchor="middle" font-size="10" fill="#e8c05a"'
        ' font-family="Georgia,serif">13-REED</text>'
    )

    parts.append('</svg>')
    return ''.join(parts)


def render_stone(highlighted_idx=None, size=380):
    svg  = build_svg(highlighted_idx, size)
    html = (
        '<!DOCTYPE html><html><head><style>'
        'html,body{margin:0;padding:0;background:#0d0a05;'
        'display:flex;justify-content:center;align-items:center;'
        'height:' + str(size + 16) + 'px;overflow:hidden;}'
        'svg{display:block;}'
        '</style></head><body>' + svg + '</body></html>'
    )
    components.html(html, height=size + 16, scrolling=False)


# ── CSS ───────────────────────────────────────────────────────────────────────
def inject_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel+Decorative:wght@400;700;900&family=Cinzel:wght@400;600&family=Lato:wght@300;400&display=swap');
    :root{--gold:#c9a84c;--amber:#e8c05a;--obsidian:#0d0a05;--cream:#f5e8c8;}
    html,body,[class*="css"]{font-family:'Lato',sans-serif;
        background:var(--obsidian)!important;color:var(--cream);}
    .stApp{background:var(--obsidian)!important;}
    .hero-title{text-align:center;font-family:'Cinzel Decorative',serif;
        font-size:clamp(1.3rem,3.5vw,2.4rem);font-weight:900;color:var(--amber);
        text-shadow:0 0 40px #c9a84c55;letter-spacing:.06em;margin-bottom:.15em;}
    .hero-sub{text-align:center;font-family:'Cinzel',serif;font-size:.78rem;
        color:#a08040;letter-spacing:.22em;text-transform:uppercase;margin-bottom:1.4rem;}
    .gold-div{height:1px;
        background:linear-gradient(90deg,transparent,#c9a84c,transparent);
        margin:1rem 0;}
    .step-box{background:#1a1208;border:1px solid #3a2a10;border-radius:4px;
        padding:.75rem 1rem;margin:.3rem 0;font-size:.84rem;
        color:#c8b070;line-height:1.5;}
    .sn{font-family:'Cinzel Decorative',serif;color:var(--amber);
        font-size:.9rem;margin-right:.4rem;}
    .rcard{background:linear-gradient(135deg,#1a1208,#2a1f10,#1a0e05);
        border:1px solid var(--gold);border-radius:4px;
        padding:1.4rem 1.6rem;margin:.7rem 0;
        box-shadow:inset 0 0 40px #c9a84c0e,0 4px 24px #00000077;}
    .rtitle{font-family:'Cinzel Decorative',serif;font-size:1.4rem;
        color:var(--amber);margin:0 0 .2rem 0;}
    .rsub{font-family:'Cinzel',serif;font-size:.7rem;letter-spacing:.25em;
        color:#a08040;text-transform:uppercase;margin-bottom:.9rem;}
    .pr{display:grid;grid-template-columns:125px 1fr;gap:.3rem .7rem;
        margin:.4rem 0;align-items:start;}
    .pl{font-family:'Cinzel',serif;font-size:.7rem;letter-spacing:.1em;
        text-transform:uppercase;color:var(--gold);padding-top:2px;}
    .pv{font-size:.9rem;color:var(--cream);line-height:1.5;}
    .wbox{background:#3a0a0a66;border-left:3px solid #8b1a0a;
        padding:.65rem .85rem;margin-top:.8rem;border-radius:0 4px 4px 0;}
    .wlbl{font-family:'Cinzel',serif;font-size:.66rem;letter-spacing:.16em;
        color:#c04030;text-transform:uppercase;margin-bottom:.2rem;}
    .wtxt{font-size:.86rem;color:#e8a090;}
    .hr{display:grid;grid-template-columns:1fr 1fr 38px 1fr 1fr;
        gap:.25rem;padding:.4rem .65rem;
        border-bottom:1px solid #2a1f10;font-size:.78rem;color:#b8a060;}
    .hh{color:var(--gold);font-family:'Cinzel',serif;font-size:.66rem;
        letter-spacing:.1em;text-transform:uppercase;}
    .stButton>button{
        background:linear-gradient(135deg,#6b3a10,#3a1a05)!important;
        border:1px solid var(--gold)!important;color:var(--amber)!important;
        font-family:'Cinzel Decorative',serif!important;font-size:.82rem!important;
        letter-spacing:.1em!important;border-radius:3px!important;
        padding:.5rem 1.4rem!important;transition:all .3s!important;}
    .stButton>button:hover{box-shadow:0 0 18px #c9a84c44!important;}
    section[data-testid="stSidebar"]{background:#0d0a05!important;}
    </style>
    """, unsafe_allow_html=True)


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    init_db()
    inject_css()

    st.markdown('<div class="hero-title">&#9728; Aztec Sun Stone Oracle &#9728;</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-sub">Tonalpohualli &middot; Sacred 260-Day Calendar &middot; Codex Borgia Interpreter</div>', unsafe_allow_html=True)

    col_stone, col_form = st.columns([1, 1], gap="large")

    with col_stone:
        stone_slot = st.empty()
        with stone_slot.container():
            render_stone(None, 380)

    with col_form:
        st.markdown('<div class="gold-div"></div>', unsafe_allow_html=True)
        st.markdown(
            '<p style="font-family:Cinzel,serif;color:#a08040;'
            'letter-spacing:.2em;font-size:.76rem;text-transform:uppercase;">'
            'Consult the Oracle</p>',
            unsafe_allow_html=True,
        )

        birth_date = st.date_input(
            "Birth date",
            value=datetime.date(1990, 3, 21),
            min_value=datetime.date(1900, 1, 1),
            max_value=datetime.date(2100, 12, 31),
        )

        seek_btn = st.button("&#9728;  Read the Stone", use_container_width=True)

        if seek_btn:
            signs     = get_all_signs()
            sign_idx, number = tonalpohualli(birth_date)
            sign_data = signs[sign_idx - 1]
            num_data  = get_number_info(number)

            with st.spinner("The priest consults the stone…"):
                for step in range(1, sign_idx + 1):
                    stone_slot.empty()
                    with stone_slot.container():
                        render_stone(step, 380)
                    time.sleep(0.14)

            save_reading(
                str(birth_date), sign_data[2], number,
                sign_data[4], sign_data[8], sign_data[9], sign_data[7],
            )
            st.session_state["last"] = {
                "sign": sign_data, "number": number,
                "num_data": num_data, "sign_idx": sign_idx,
                "date": str(birth_date),
            }

        if "last" in st.session_state:
            lr = st.session_state["last"]
            sd = lr["sign"]
            nd = lr["num_data"]

            st.markdown('<div class="gold-div"></div>', unsafe_allow_html=True)
            st.markdown(
                '<p style="font-family:Cinzel,serif;color:#c9a84c;'
                'font-size:.76rem;letter-spacing:.2em;text-transform:uppercase;">'
                "The Priest's Ritual</p>",
                unsafe_allow_html=True,
            )

            st.markdown(
                '<div class="step-box"><span class="sn">I.</span>'
                ' <b>Anchor set</b> — The priest touches the <b>13-Reed</b> glyph'
                ' at the crown of the stone, marking the birth of the Fifth Sun.</div>'
                '<div class="step-box"><span class="sn">II.</span>'
                ' <b>Counter-clockwise sweep</b> — He counts <b>'
                + str(lr["sign_idx"]) + ' steps</b>'
                ' and lands on <b>' + sd[2] + ' (' + sd[1] + ')</b>.</div>'
                '<div class="step-box"><span class="sn">III.</span>'
                ' <b>Codex — Number ' + str(lr["number"]) + ' (' + nd[1] + ')</b><br>'
                + nd[3] + '</div>'
                '<div class="step-box"><span class="sn">IV.</span>'
                ' <b>Ruling deity:</b> <b>' + sd[4] + '</b>'
                ', lord of the <b>' + sd[6] + '</b>.</div>',
                unsafe_allow_html=True,
            )

            st.markdown('<div class="gold-div"></div>', unsafe_allow_html=True)
            st.markdown(
                '<div class="rcard">'
                '<div class="rtitle">' + sd[2] + '</div>'
                '<div class="rsub">' + nd[1] + ' &mdash; Day ' + str(lr["number"])
                + ' of 13 &middot; Sign ' + str(lr["sign_idx"]) + ' of 20</div>'
                '<div class="pr"><span class="pl">Nahuatl</span>'
                '<span class="pv">' + sd[1] + '</span></div>'
                '<div class="pr"><span class="pl">Deity</span>'
                '<span class="pv">' + sd[4] + '</span></div>'
                '<div class="pr"><span class="pl">Element / Dir.</span>'
                '<span class="pv">' + sd[5] + ' &middot; ' + sd[6] + '</span></div>'
                '<div class="pr"><span class="pl">Character</span>'
                '<span class="pv">' + sd[7] + '</span></div>'
                '<div class="pr"><span class="pl">Fortune</span>'
                '<span class="pv">' + sd[8] + '</span></div>'
                '<div class="pr"><span class="pl">Number energy</span>'
                '<span class="pv">' + nd[2] + ' &mdash; ' + nd[3] + '</span></div>'
                '<div class="wbox"><div class="wlbl">&#9888; Codex Borgia Warning</div>'
                '<div class="wtxt">' + sd[9] + '</div></div>'
                '</div>',
                unsafe_allow_html=True,
            )

    # History
    st.markdown('<div class="gold-div"></div>', unsafe_allow_html=True)
    st.markdown(
        '<p style="font-family:\'Cinzel Decorative\',serif;color:#c9a84c;font-size:.9rem;">'
        'Recent Consultations</p>',
        unsafe_allow_html=True,
    )
    readings = get_recent_readings(6)
    if readings:
        st.markdown(
            '<div class="hr hh">'
            '<span>Date</span><span>Sign</span><span>#</span>'
            '<span>Deity</span><span>Logged</span></div>',
            unsafe_allow_html=True,
        )
        for row in readings:
            ts = str(row[5])[:16] if row[5] else "—"
            st.markdown(
                '<div class="hr">'
                '<span>' + str(row[0]) + '</span>'
                '<span>' + str(row[1]) + '</span>'
                '<span>' + str(row[2]) + '</span>'
                '<span>' + str(row[3]) + '</span>'
                '<span>' + ts + '</span></div>',
                unsafe_allow_html=True,
            )
    else:
        st.markdown(
            '<p style="color:#5a3a10;font-size:.8rem;">'
            'No consultations yet &mdash; enter a date above.</p>',
            unsafe_allow_html=True,
        )

    st.markdown('<div class="gold-div"></div>', unsafe_allow_html=True)
    with st.expander("&#128220; How the Oracle Works — Stone as Map, Codex as Encyclopedia"):
        st.markdown("""
**The Sun Stone as Cosmic Clock Face**

The Aztec Sun Stone (*Piedra del Sol*) encodes the 260-day Tonalpohualli. It is a grand public clock
telling you *what time it is* in the cosmic cycle, while the Codex Borgia is the priest's private manual
explaining *what that time means for a human life*.

**Three-part reading:**
- **The Stone** → the *Name* of the day (1 of 20 signs)
- **The Number** → the *Intensity / Balance* (1–13 in the trecena)
- **The Codex** → *Personality and Fate* via the ruling deity

**Correlation:** Alfonso Caso — 1 January 1900 = 1 Cipactli.
        """)


if __name__ == "__main__":
    main()
