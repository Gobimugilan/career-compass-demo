import streamlit as st
from fpdf import FPDF
import base64
import time
import pandas as pd
import qrcode
from io import BytesIO

# --- 1. CONFIG & STYLES ---
st.set_page_config(page_title="LifePath AI 2.0", page_icon="🚀", layout="centered")

# Injecting the "Neon Horizon" CSS
st.markdown("""
    <style>
    /* MAIN BACKGROUND */
    .stApp {
        background-color: #0e1117;
        color: #FAFAFA;
    }
    
    /* NEON BUTTON STYLE */
    .stButton>button {
        width: 100%;
        border-radius: 12px;
        height: 3.8em;
        background: linear-gradient(135deg, #1f2937 0%, #111827 100%);
        color: #00d4ff; /* Neon Cyan Text */
        font-weight: 700;
        border: 1px solid #00d4ff;
        transition: all 0.3s ease;
        font-size: 16px;
        letter-spacing: 0.5px;
    }
    
    /* BUTTON HOVER GLOW EFFECT */
    .stButton>button:hover {
        background: #00d4ff;
        color: #000000;
        border-color: #00d4ff;
        box-shadow: 0 0 15px rgba(0, 212, 255, 0.6); /* Cyan Glow */
        transform: translateY(-2px);
    }

    /* QUESTION CARD STYLE */
    .question-box {
        background: rgba(255, 255, 255, 0.05); /* Glass effect */
        padding: 30px;
        border-radius: 15px;
        border-left: 5px solid #BC13FE; /* Neon Purple accent */
        font-size: 24px;
        font-weight: 600;
        margin-bottom: 30px;
        text-align: center;
        color: #ffffff;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    
    /* PROGRESS BAR COLOR */
    .stProgress > div > div > div > div {
        background-color: #BC13FE;
    }
    
    /* HEADERS */
    h1, h2, h3 {
        color: #ffffff !important;
        font-family: 'Helvetica Neue', sans-serif;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. THE UNIVERSAL QUESTION BANK (20 Questions) ---
questions_db = [
    {
        "q": "1. It's Friday night. What are you doing?",
        "options": [
            {"text": "🎸 Jamming on my Guitar/Keyboard.", "scores": {"Musician": 10, "Filmmaker": 3}},
            {"text": "💻 Coding a personal project.", "scores": {"Full Stack Developer": 10, "Game Developer": 10}},
            {"text": "📈 analyzing the Stock Market.", "scores": {"Stock Trader": 10, "Chartered Accountant": 5}},
            {"text": "🧬 Reading biology / medical news.", "scores": {"Doctor": 10, "Psychologist": 5}}
        ]
    },
    {
        "q": "2. Pick a tool you would love to master:",
        "options": [
            {"text": "🎥 Cinema Camera & Premiere Pro.", "scores": {"Filmmaker": 10, "Digital Marketer": 5}},
            {"text": "🩺 Stethoscope & Surgical tools.", "scores": {"Doctor": 10}},
            {"text": "🎹 Synthesizer & FL Studio.", "scores": {"Musician": 10}},
            {"text": "📊 Excel Sheets & Balance Sheets.", "scores": {"Chartered Accountant": 10, "Stock Trader": 5}}
        ]
    },
    {
        "q": "3. You see a problem in the world. How do you fix it?",
        "options": [
            {"text": "I build an App to solve it.", "scores": {"Full Stack Developer": 10, "Entrepreneur": 5}},
            {"text": "I create art/content to raise awareness.", "scores": {"Musician": 5, "Filmmaker": 10}},
            {"text": "I organize a fundraiser (Money).", "scores": {"Entrepreneur": 5, "Chartered Accountant": 3}},
            {"text": "I help people heal mentally/physically.", "scores": {"Psychologist": 10, "Doctor": 5}}
        ]
    },
    {
        "q": "4. What is your relationship with Mathematics?",
        "options": [
            {"text": "❤️ Love Statistics & Probability.", "scores": {"Data Scientist": 10, "Stock Trader": 10}},
            {"text": "💰 Like Money/Profit calculations.", "scores": {"Chartered Accountant": 10, "Entrepreneur": 5}},
            {"text": "🎨 Hate it. Give me Colors & Sound.", "scores": {"Musician": 5, "Fashion Designer": 10, "Filmmaker": 5}},
            {"text": "🧪 It's okay, but prefer Biology.", "scores": {"Doctor": 10, "Psychologist": 5}}
        ]
    },
    {
        "q": "5. Organizing a College Fest. What is your role?",
        "options": [
            {"text": "🎤 The Performer (Star on stage).", "scores": {"Musician": 10, "Entrepreneur": 5}},
            {"text": "💸 The Treasurer (Handling cash).", "scores": {"Chartered Accountant": 10, "Stock Trader": 5}},
            {"text": "🎨 The Designer (Posters/Look).", "scores": {"Fashion Designer": 10, "Graphic Designer": 10}},
            {"text": "🔌 The Tech Lead (Website/WiFi).", "scores": {"Full Stack Developer": 10, "Cybersecurity Analyst": 10}}
        ]
    },
    {
        "q": "6. A friend is depressed. What do you do?",
        "options": [
            {"text": "Listen deeply and analyze feelings.", "scores": {"Psychologist": 10}},
            {"text": "Distract them with fun content.", "scores": {"Filmmaker": 5, "Musician": 5}},
            {"text": "Offer practical help (Food/Money).", "scores": {"Chartered Accountant": 3}},
            {"text": "Check physical symptoms (Sickness?).", "scores": {"Doctor": 5}}
        ]
    },
    {
        "q": "7. Pick a workspace:",
        "options": [
            {"text": "🎙️ Soundproof Studio.", "scores": {"Musician": 10}},
            {"text": "📈 Trading floor with 4 monitors.", "scores": {"Stock Trader": 10}},
            {"text": "🏥 Hospital Emergency Room.", "scores": {"Doctor": 10}},
            {"text": "🖥️ Dark Room with glowing code.", "scores": {"Cybersecurity Analyst": 10, "Full Stack Developer": 5}}
        ]
    },
    {
        "q": "8. Pick a celebrity you admire:",
        "options": [
            {"text": "🎵 A.R. Rahman / Anirudh.", "scores": {"Musician": 10}},
            {"text": "🚀 Elon Musk / Ratan Tata.", "scores": {"Entrepreneur": 10, "Stock Trader": 5}},
            {"text": "🎬 Christopher Nolan.", "scores": {"Filmmaker": 10}},
            {"text": "💻 Sundar Pichai.", "scores": {"Full Stack Developer": 10, "Data Scientist": 5}}
        ]
    },
    {
        "q": "9. How do you view 'Clothing'?",
        "options": [
            {"text": "It's Art. Fabrics, cuts, trends.", "scores": {"Fashion Designer": 10}},
            {"text": "Functional. Whatever is clean.", "scores": {"Full Stack Developer": 5, "Doctor": 5}},
            {"text": "Status. Dress to impress.", "scores": {"Chartered Accountant": 5, "Entrepreneur": 5}},
            {"text": "Costume. Defines a character.", "scores": {"Filmmaker": 5, "Musician": 3}}
        ]
    },
    {
        "q": "10. What drives you the most?",
        "options": [
            {"text": "✨ Creativity & Fame.", "scores": {"Musician": 10, "Filmmaker": 10, "Fashion Designer": 10}},
            {"text": "💰 Money & Power.", "scores": {"Stock Trader": 10, "Entrepreneur": 10, "Chartered Accountant": 5}},
            {"text": "❤️ Helping Others.", "scores": {"Doctor": 10, "Psychologist": 10}},
            {"text": "🚀 Innovation/Future.", "scores": {"Full Stack Developer": 10, "Data Scientist": 10}}
        ]
    },
    {
        "q": "11. Found a wallet with ₹10,000. What now?",
        "options": [
            {"text": "Find owner (Ethics).", "scores": {"Chartered Accountant": 10, "Doctor": 5}},
            {"text": "Invest it to make ₹20,000.", "scores": {"Stock Trader": 10, "Entrepreneur": 5}},
            {"text": "Buy gear for my passion.", "scores": {"Game Developer": 5, "Musician": 5}},
            {"text": "Analyze clues to find owner.", "scores": {"Data Scientist": 10, "Psychologist": 5}}
        ]
    },
    {
        "q": "12. Handling high pressure?",
        "options": [
            {"text": "Stay calm, follow rules.", "scores": {"Doctor": 10, "Cybersecurity Analyst": 5}},
            {"text": "Thrive on risk!", "scores": {"Stock Trader": 10, "Entrepreneur": 10}},
            {"text": "Anxious but finish the job.", "scores": {"Graphic Designer": 5, "Full Stack Developer": 5}},
            {"text": "Express stress via Art.", "scores": {"Musician": 10, "Filmmaker": 5}}
        ]
    },
    {
        "q": "13. Start a YouTube Channel about:",
        "options": [
            {"text": "Gaming or Coding.", "scores": {"Game Developer": 10, "Full Stack Developer": 5}},
            {"text": "Fashion or Makeup.", "scores": {"Fashion Designer": 10, "Digital Marketer": 5}},
            {"text": "Finance & Crypto.", "scores": {"Stock Trader": 10, "Chartered Accountant": 5}},
            {"text": "Short Films / Covers.", "scores": {"Filmmaker": 10, "Musician": 10}}
        ]
    },
    {
        "q": "14. What annoys you most?",
        "options": [
            {"text": "Ugly Design / Fonts.", "scores": {"Graphic Designer": 10, "Fashion Designer": 5}},
            {"text": "Wasting Money.", "scores": {"Chartered Accountant": 10, "Entrepreneur": 5}},
            {"text": "Slow Internet / Bugs.", "scores": {"Full Stack Developer": 10, "Game Developer": 5}},
            {"text": "Liars / Fake People.", "scores": {"Psychologist": 10, "Doctor": 3}}
        ]
    },
    {
        "q": "15. Role in a Team?",
        "options": [
            {"text": "The Leader.", "scores": {"Entrepreneur": 10, "Filmmaker": 5}},
            {"text": "The Specialist.", "scores": {"Doctor": 10, "Cybersecurity Analyst": 10}},
            {"text": "The Creative.", "scores": {"Graphic Designer": 10, "Musician": 5}},
            {"text": "The Analyst.", "scores": {"Data Scientist": 10, "Chartered Accountant": 5}}
        ]
    },
    {
        "q": "16. Video Game Type?",
        "options": [
            {"text": "Strategy / Tycoon.", "scores": {"Entrepreneur": 10, "Stock Trader": 5}},
            {"text": "FPS / Action.", "scores": {"Game Developer": 5, "Cybersecurity Analyst": 5}},
            {"text": "Story / RPG.", "scores": {"Filmmaker": 10, "Musician": 5}},
            {"text": "Puzzle / Logic.", "scores": {"Full Stack Developer": 10, "Data Scientist": 10}}
        ]
    },
    {
        "q": "17. Preferred Payment Mode?",
        "options": [
            {"text": "Stable Salary.", "scores": {"Doctor": 5, "Chartered Accountant": 10}},
            {"text": "Commission / Profit.", "scores": {"Stock Trader": 10, "Entrepreneur": 10}},
            {"text": "Per Project / Gig.", "scores": {"Filmmaker": 10, "Musician": 10, "Graphic Designer": 10}},
            {"text": "Salary + Stocks.", "scores": {"Full Stack Developer": 10, "Data Scientist": 5}}
        ]
    },
    {
        "q": "18. Build a building:",
        "options": [
            {"text": "Hospital / Lab.", "scores": {"Doctor": 10, "Psychologist": 5}},
            {"text": "Corporate HQ.", "scores": {"Entrepreneur": 10, "Chartered Accountant": 3}},
            {"text": "Museum / Concert Hall.", "scores": {"Musician": 10, "Fashion Designer": 5}},
            {"text": "Server Farm.", "scores": {"Cloud Architect": 10, "Cybersecurity Analyst": 5}}
        ]
    },
    {
        "q": "19. Look at an object. You see:",
        "options": [
            {"text": "Materials & Craft.", "scores": {"Fashion Designer": 5, "Full Stack Developer": 3}},
            {"text": "Cost & Profit.", "scores": {"Chartered Accountant": 10, "Entrepreneur": 5}},
            {"text": "Beauty & Light.", "scores": {"Filmmaker": 10, "Graphic Designer": 10}},
            {"text": "Data & Dimensions.", "scores": {"Data Scientist": 10}}
        ]
    },
    {
        "q": "20. Ultimate Goal?",
        "options": [
            {"text": "Create timeless beauty.", "scores": {"Musician": 10, "Filmmaker": 10, "Fashion Designer": 10}},
            {"text": "Solve complex problems.", "scores": {"Doctor": 10, "Full Stack Developer": 10, "Data Scientist": 10}},
            {"text": "Financial Freedom.", "scores": {"Stock Trader": 10, "Entrepreneur": 10}},
            {"text": "Truth & Safety.", "scores": {"Psychologist": 10, "Cybersecurity Analyst": 10}}
        ]
    }
]

# --- 3. SESSION STATE ---
if 'step' not in st.session_state:
    st.session_state.step = 0
if 'scores' not in st.session_state:
    st.session_state.scores = {
        "Musician": 0, "Filmmaker": 0, "Fashion Designer": 0, "Graphic Designer": 0,
        "Chartered Accountant": 0, "Stock Trader": 0, "Entrepreneur": 0, "Digital Marketer": 0,
        "Doctor": 0, "Psychologist": 0,
        "Full Stack Developer": 0, "Cybersecurity Analyst": 0, "Data Scientist": 0, "Game Developer": 0, "Cloud Architect": 0
    }

# --- 4. FUNCTIONS ---
def reset_quiz():
    st.session_state.step = 0
    st.session_state.scores = {k: 0 for k in st.session_state.scores}

def create_pdf(name, domain, roadmap):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=16)
    pdf.cell(200, 10, txt=f"LIFEPATH CAREER TICKET: {name.upper()}", ln=1, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Recommended Role: {domain}", ln=1)
    pdf.ln(5)
    pdf.cell(200, 10, txt="Your Action Plan:", ln=1)
    for step in roadmap:
        pdf.cell(200, 8, txt=f"- {step}", ln=1)
    return pdf.output(dest='S').encode('latin-1')

def generate_qr(url):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    return img

# --- 5. MAIN APP ---
def main():
    
  # --- SIDEBAR FOR QR CODE ---
    with st.sidebar:
        st.header("📱 Scan to Play")
        st.write("Scan this to open the app on your phone:")
        
        # PASTE YOUR NEW LINK HERE AS THE DEFAULT
        url_input = st.text_input("App URL:", "https://career-compass-demo-5qkuzf9irhgypuccsvx4fu.streamlit.app/")
        
        if url_input:
            qr_img = generate_qr(url_input)
            buf = BytesIO()
            qr_img.save(buf)
            st.image(buf, caption="Scan to Open", use_container_width=True)
        

    # HEADER
    st.title("🚀 LifePath AI")
    st.caption("The Universal Career GPS | Powered by AI Logic")
    
    # PROGRESS BAR
    if st.session_state.step > 0 and st.session_state.step <= len(questions_db):
        progress = st.session_state.step / len(questions_db)
        st.progress(progress)

    # LANDING PAGE
    if st.session_state.step == 0:
        st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=200)
        st.write("### 🔮 Unlock Your Future.")
        st.write("Are you a **Creator**, a **Healer**, a **Leader**, or a **Coder**?")
        st.write("Take the 20-Question AI Assessment to find out.")
        if st.button("Start Assessment"):
            st.session_state.step = 1
            st.rerun()

    # QUIZ LOOP
    elif 1 <= st.session_state.step <= len(questions_db):
        q_index = st.session_state.step - 1
        q_data = questions_db[q_index]
        
        st.markdown(f"<div class='question-box'>{q_data['q']}</div>", unsafe_allow_html=True)
        
        for option in q_data['options']:
            if st.button(option['text']):
                for domain, points in option['scores'].items():
                    if domain in st.session_state.scores:
                        st.session_state.scores[domain] += points
                st.session_state.step += 1
                time.sleep(0.1)
                st.rerun()

    # RESULT PAGE
    else:
        winner = max(st.session_state.scores, key=st.session_state.scores.get)
        st.balloons()
        
        # Result Header
        st.markdown(f"""
            <div style='background: #111827; padding: 20px; border-radius: 10px; border: 1px solid #00d4ff; text-align: center;'>
                <h1 style='color: #00d4ff; margin: 0;'>🎉 You are a {winner}!</h1>
            </div>
            """, unsafe_allow_html=True)
        
        # --- PERSONALITY CHART ---
        st.write("### 📊 Your Personality DNA")
        creative_score = st.session_state.scores["Musician"] + st.session_state.scores["Filmmaker"] + st.session_state.scores["Fashion Designer"] + st.session_state.scores["Graphic Designer"]
        logic_score = st.session_state.scores["Full Stack Developer"] + st.session_state.scores["Data Scientist"] + st.session_state.scores["Cybersecurity Analyst"] + st.session_state.scores["Game Developer"]
        business_score = st.session_state.scores["Stock Trader"] + st.session_state.scores["Chartered Accountant"] + st.session_state.scores["Entrepreneur"] + st.session_state.scores["Digital Marketer"]
        empathy_score = st.session_state.scores["Doctor"] + st.session_state.scores["Psychologist"]

        chart_data = {
            "Category": ["Creativity 🎨", "Logic 🧠", "Business 💼", "Empathy ❤️"],
            "Score": [creative_score, logic_score, business_score, empathy_score]
        }
        st.bar_chart(pd.DataFrame(chart_data).set_index("Category"), color="#00d4ff")

        # --- DATABASE ---
        details = {
            "Musician": {"sal": "₹3L - ₹50L+", "degree": "BA Music / Audio Eng", "link": "https://www.youtube.com/watch?v=1s9pSgsQ9sM", "map": ["Learn Instrument", "Music Theory", "DAW Mastery"]},
            "Filmmaker": {"sal": "₹4L - ₹20L", "degree": "B.Sc VisCom", "link": "https://www.youtube.com/watch?v=7I0t23kXqys", "map": ["Scriptwriting", "Editing", "Short Films"]},
            "Fashion Designer": {"sal": "₹4L - ₹15L", "degree": "B.Des (NIFT)", "link": "https://www.youtube.com/watch?v=wXhGzVvE4V8", "map": ["Sketching", "Fabrics", "Sewing"]},
            "Graphic Designer": {"sal": "₹3.5L - ₹8L", "degree": "B.Des / Fine Arts", "link": "https://www.youtube.com/watch?v=sTcuqhxFGP8", "map": ["Color Theory", "Photoshop", "Portfolio"]},
            "Chartered Accountant": {"sal": "₹7L - ₹25L", "degree": "B.Com + CA", "link": "https://www.youtube.com/watch?v=Is3j_gG5G94", "map": ["CPT", "IPCC", "Articleship"]},
            "Stock Trader": {"sal": "Unlimited Risk", "degree": "BBA Finance / CFA", "link": "https://www.youtube.com/watch?v=Xn7KWR9EOGQ", "map": ["Tech Analysis", "Risk Mgmt", "Paper Trading"]},
            "Entrepreneur": {"sal": "Self-Made", "degree": "MBA (Optional)", "link": "https://www.youtube.com/watch?v=lJjILQu2xM8", "map": ["MVP", "Sales", "Funding"]},
            "Digital Marketer": {"sal": "₹4L - ₹8L", "degree": "BBA / Google Certs", "link": "https://www.youtube.com/watch?v=bixR-KIJKYM", "map": ["SEO", "Ads", "Content"]},
            "Doctor": {"sal": "₹6L - ₹30L+", "degree": "MBBS + MD", "link": "https://www.youtube.com/watch?v=4s5o-KqTjFk", "map": ["NEET", "MBBS", "Internship"]},
            "Psychologist": {"sal": "₹4L - ₹12L", "degree": "BA + MA Psychology", "link": "https://www.youtube.com/watch?v=vo4pMVb0R6M", "map": ["Degree", "Internship", "License"]},
            "Full Stack Developer": {"sal": "₹5-9 LPA", "degree": "B.Tech CSE", "link": "https://www.youtube.com/watch?v=lI1ae4REbFM", "map": ["HTML/JS", "React", "Node.js"]},
            "Cybersecurity Analyst": {"sal": "₹5-10 LPA", "degree": "B.Tech Cyber", "link": "https://www.youtube.com/watch?v=nzZkKoREEGo", "map": ["Linux", "Network+", "Ethical Hacking"]},
            "Data Scientist": {"sal": "₹8-14 LPA", "degree": "B.Sc Stats / AI", "link": "https://www.youtube.com/watch?v=ua-CiDNNj30", "map": ["Python", "ML", "Pandas"]},
            "Game Developer": {"sal": "₹5-10 LPA", "degree": "B.Tech / Game Cert", "link": "https://www.youtube.com/watch?v=IlKaB1etrik", "map": ["Unity", "C#", "3D Math"]},
            "Cloud Architect": {"sal": "₹8-16 LPA", "degree": "B.Tech / AWS Cert", "link": "https://www.youtube.com/watch?v=N4sJj-SxX00", "map": ["AWS", "Docker", "Kubernetes"]}
        }
        
        info = details.get(winner, details["Full Stack Developer"])
        
        st.info(f"💰 **Salary:** {info['sal']}")
        st.warning(f"🎓 **Degree:** {info['degree']}")
        
        if 'link' in info:
            st.markdown(f"""<a href="{info['link']}" target="_blank"><button style="background-color: #00d4ff; color: black; padding: 12px 20px; border: none; border-radius: 8px; font-weight: bold; width: 100%; margin: 15px 0; cursor: pointer;">▶ Watch {winner} Guide on YouTube</button></a>""", unsafe_allow_html=True)
        
        with st.expander("Show Career Roadmap"):
            for s in info['map']:
                st.write(f"- {s}")
        
        name = st.text_input("Enter Name for Ticket:")
        if name:
            pdf = create_pdf(name, winner, info['map'])
            b64 = base64.b64encode(pdf).decode()
            href = f'<a href="data:application/octet-stream;base64,{b64}" download="LifePath_Ticket.pdf" style="color: #00d4ff; text-decoration: none; font-weight: bold;">📥 Download Official Ticket (PDF)</a>'
            st.markdown(href, unsafe_allow_html=True)
            
        if st.button("🔄 Start Again"):
            reset_quiz()
            st.rerun()

    # --- ADMIN ---
    st.markdown("---")
    with st.expander("🔐 Teacher / Admin Dashboard"):
        st.write("### 🏫 Class Pulse")
        mock_data = pd.DataFrame({
            "Student": ["Arun", "Priya", "Rahul", "Sneha", "Vikram"],
            "Career": ["Doctor", "Coder", "Musician", "CA", "Gamer"],
            "Score": [85, 92, 78, 88, 95]
        })
        st.dataframe(mock_data)
        st.download_button("Download Report", mock_data.to_csv(), "class_report.csv")

if __name__ == "__main__":

    main()
