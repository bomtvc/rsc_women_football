import streamlit as st
import random
import time
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Wedge, Circle, Polygon
from matplotlib.figure import Figure
import base64
import math

# Thiết lập trang / Page setup
st.set_page_config(page_title="Bốc Thăm Bảng Đấu / Draw Tournament Groups", layout="wide")

# Ngôn ngữ mặc định / Default language
if 'language' not in st.session_state:
    st.session_state.language = 'vi'  # 'vi' for Vietnamese, 'en' for English

# Từ điển song ngữ / Bilingual dictionary
translations = {
    'title': {
        'vi': "🏆 BỐC THĂM BẢNG THI ĐẤU GIẢI BÓNG ĐÁ TRUYỀN THỐNG ROCHDALE SPEARS 🏆",
        'en': "🏆 OFFICIAL GROUP STAGE DRAW -- ROCHDALE SPEARS TRADITIONAL FOOTBALL TOURNAMENT 🏆"
    },
    'draw_header': {
        'vi': "Bốc thăm bảng thi đấu",
        'en': "Draw Tournament Groups"
    },
    'teams_left': {
        'vi': "Còn lại: {}/8 đội",
        'en': "Remaining: {}/8 teams"
    },
    'select_team': {
        'vi': "Chọn đội để bốc thăm:",
        'en': "Select team to draw:"
    },
    'draw_button': {
        'vi': "Bốc thăm",
        'en': "Draw"
    },
    'reset_button': {
        'vi': "Bắt đầu lại",
        'en': "Restart"
    },
    'all_teams_drawn': {
        'vi': "Đã bốc thăm xong tất cả các đội!",
        'en': "All teams have been drawn!"
    },
    'spinning': {
        'vi': "Đang quay vòng quay...",
        'en': "Spinning the wheel..."
    },
    'result': {
        'vi': "Kết quả: {} → {}",
        'en': "Result: {} → {}"
    },
    'results_header': {
        'vi': "Kết quả bốc thăm",
        'en': "Draw Results"
    },
    'position': {
        'vi': "Vị trí",
        'en': "Position"
    },
    'group': {
        'vi': "Bảng {}",
        'en': "Group {}"
    },
    'language_selector': {
        'vi': "Ngôn ngữ / Language:",
        'en': "Ngôn ngữ / Language:"
    }
}

# Hàm lấy văn bản theo ngôn ngữ / Function to get text based on language
def get_text(key, **kwargs):
    text = translations.get(key, {}).get(st.session_state.language, key)
    if kwargs:
        return text.format(*kwargs.values())
    return text

# Khởi tạo session state
if 'positions' not in st.session_state:
    # Tạo tất cả các vị trí có thể
    positions = []
    for group in ['A', 'B']:
        for i in range(1, 5):
            positions.append(f"{group}{i}")
    st.session_state.positions = positions

if 'available_positions' not in st.session_state:
    st.session_state.available_positions = st.session_state.positions.copy()

if 'results' not in st.session_state:
    st.session_state.results = {}

if 'spinning' not in st.session_state:
    st.session_state.spinning = False

if 'wheel_angle' not in st.session_state:
    st.session_state.wheel_angle = 0

if 'result_table' not in st.session_state:
    # Khởi tạo bảng kết quả trống
    st.session_state.result_table = {
        'A': [None] * 4,  # 4 vị trí cho bảng A
        'B': [None] * 4,  # 4 vị trí cho bảng B
    }

# Danh sách 8 đội thi đấu
all_teams = [
    "HR - PLANNING", "WW P2", "GA", "FINISHING P1", 
    "UPH", "WW P1", "INLAY", "FINISHING P2"
]

# Lọc các đội đã được bốc thăm
if 'used_teams' not in st.session_state:
    st.session_state.used_teams = []

available_teams = [team for team in all_teams if team not in st.session_state.used_teams]

# Hàm easeInOutCirc cải tiến
def easeInOutCirc(x):
    if x < 0.5:
        return 0.5 * (1 - math.sqrt(1 - 4 * x * x))
    else:
        return 0.5 * (math.sqrt(-((2 * x - 3) * (2 * x - 1))) + 1)

# Hàm vẽ vòng quay may mắn với góc quay và hiệu ứng 3D - không sử dụng patheffects
def create_wheel(positions, angle=0):
    fig = Figure(figsize=(10, 10), dpi=100)
    ax = fig.add_subplot(111)
    
    # Số lượng phần tử trên vòng quay
    n = len(positions)
    
    # Tạo gradient màu hơi sáng để hiển thị đẹp
    colors = []
    base_colors = ['#FF5252', '#FF7752', '#FFCA52', '#FFE552', '#B4FF52', '#52FF8F', '#52FFDF', '#52BFFF', '#5275FF', '#8A52FF', '#D452FF', '#FF52C9']
    
    for i in range(n):
        color_idx = i % len(base_colors)
        colors.append(base_colors[color_idx])
    
    # Vẽ các phần tử trên vòng quay
    theta1 = angle  # Bắt đầu từ góc quay hiện tại
    theta2 = 360 / n
    
    wedges = []
    labels_pos = []
    
    # Vẽ hình nền (đổ bóng)
    shadow_circle = Circle((0.02, -0.02), 0.95, fc='#00000022', zorder=0)
    ax.add_patch(shadow_circle)
    
    # Vẽ viền ngoài vòng quay
    outer_circle = Circle((0, 0), 0.95, fc='none', ec='#333333', lw=2, zorder=1)
    ax.add_patch(outer_circle)
    
    for i in range(n):
        # Thêm hiệu ứng 3D với độ sáng khác nhau cho các phần
        base_color = colors[i]
        
        # Tạo wedge chính
        wedge = Wedge((0, 0), 0.92, theta1, theta1 + theta2, fc=base_color, ec='white', lw=1, zorder=2)
        ax.add_patch(wedge)
        wedges.append(wedge)
        
        # Thêm nhãn
        mid_angle = np.radians((theta1 + theta1 + theta2) / 2)
        text_radius = 0.6  # Đặt nhãn gần tâm hơn một chút để dễ đọc
        text_x = text_radius * np.cos(mid_angle)
        text_y = text_radius * np.sin(mid_angle)
        
        # Thay thế patheffects bằng cách vẽ text hai lần - đầu tiên là đường viền đen, sau đó là text trắng
        # Vẽ đường viền đen
        for dx, dy in [(-0.005, 0), (0.005, 0), (0, -0.005), (0, 0.005), 
                       (-0.005, -0.005), (-0.005, 0.005), (0.005, -0.005), (0.005, 0.005)]:
            ax.text(text_x + dx, text_y + dy, positions[i], ha='center', va='center', 
                    fontsize=14, fontweight='bold', color='black')
        
        # Vẽ text chính màu trắng
        ax.text(text_x, text_y, positions[i], ha='center', va='center', 
                fontsize=14, fontweight='bold', color='white')
        
        # Lưu vị trí của nhãn để xác định kết quả
        labels_pos.append((mid_angle, positions[i]))
        
        theta1 += theta2
    
    # Thêm vòng tròn ở giữa
    inner_circle_bg = Circle((0, 0), 0.27, fc='#333333', ec='#555555', lw=4, zorder=5)
    ax.add_patch(inner_circle_bg)
    
    center_circle = Circle((0, 0), 0.25, fc='#444444', ec='#666666', lw=2, zorder=6)
    ax.add_patch(center_circle)
    
    # Logo hoặc văn bản ở giữa - sử dụng kỹ thuật tương tự để tạo hiệu ứng đường viền
    # Vẽ đường viền đen
    for dx, dy in [(-0.01, 0), (0.01, 0), (0, -0.01), (0, 0.01), 
                 (-0.01, -0.01), (-0.01, 0.01), (0.01, -0.01), (0.01, 0.01)]:
        ax.text(0 + dx, 0 + dy, "RS", ha='center', va='center', fontsize=30, 
                fontweight='bold', color='black', zorder=7)
                
    # Vẽ text trắng ở giữa
    ax.text(0, 0, "RS", ha='center', va='center', fontsize=30, 
            fontweight='bold', color='white', zorder=8)
    
    # Thêm mũi tên chỉ vị trí (ở trên cùng với hiệu ứng đẹp hơn)
    arrow_height = 0.15
    arrow_width = 0.08
    arrow_x = 0
    arrow_y = 0.92
    
    # Tạo hình mũi tên
    arrow_shape = np.array([[arrow_x, arrow_y], 
                           [arrow_x - arrow_width/2, arrow_y + arrow_height/2], 
                           [arrow_x, arrow_y - arrow_height/2],
                           [arrow_x + arrow_width/2, arrow_y + arrow_height/2]])
    
    arrow = Polygon(arrow_shape, fc='red', ec='darkred', lw=1, zorder=10)
    ax.add_patch(arrow)
    
    # Thêm viền ngoài để thêm hiệu ứng đổ bóng
    highlight_circle = Circle((0, 0), 0.97, fc='none', ec='#FFFFFF55', lw=3, zorder=1)
    ax.add_patch(highlight_circle)
    
    ax.set_xlim(-1, 1)
    ax.set_ylim(-1, 1)
    ax.set_aspect('equal')
    ax.axis('off')
    
    # Đặt màu nền trong suốt
    fig.patch.set_alpha(0.0)
    
    return fig, labels_pos

# Hàm xác định vị trí được chọn dựa trên góc quay
def get_selected_position(labels_pos, angle):
    # Chuyển đổi góc quay sang radian
    angle_rad = np.radians(angle)
    
    # Điều chỉnh góc để phù hợp với hệ tọa độ của matplotlib
    adjusted_angle = (angle_rad - np.pi/2) % (2*np.pi)
    
    # Tìm vị trí gần nhất với mũi tên (trên cùng)
    arrow_angle = 0  # Vì đã điều chỉnh góc
    
    # Tìm vị trí có góc gần với mũi tên nhất
    min_diff = float('inf')
    selected_position = None
    
    for pos_angle, position in labels_pos:
        # Điều chỉnh góc của vị trí
        adjusted_pos_angle = (pos_angle - np.pi/2) % (2*np.pi)
        
        # Tính khoảng cách góc
        diff = min((adjusted_pos_angle - arrow_angle) % (2*np.pi), 
                   (arrow_angle - adjusted_pos_angle) % (2*np.pi))
        
        if diff < min_diff:
            min_diff = diff
            selected_position = position
    
    return selected_position

# Hàm cập nhật bảng kết quả
def update_result_table(position, team):
    group = position[0]  # Lấy chữ cái đầu (A, B)
    index = int(position[1:]) - 1  # Lấy số (0-based index)
    st.session_state.result_table[group][index] = team

# Hàm tạo HTML để phát âm thanh
def autoplay_audio(url):
    audio_html = f"""
        <audio id="wheelAudio" autoplay loop>
            <source src="{url}" type="audio/ogg">
            Your browser does not support the audio element.
        </audio>
        <script>
            var audio = document.getElementById("wheelAudio");
            audio.volume = 0.5;
        </script>
    """
    return audio_html

# Hàm phát âm thanh kết quả
def play_result_audio():
    result_html = f"""
        <audio id="resultAudio" autoplay>
            <source src="https://www.soundjay.com/buttons/sounds/button-09.mp3" type="audio/mpeg">
            Your browser does not support the audio element.
        </audio>
    """
    return result_html

# Hàm dừng âm thanh
def stop_audio():
    stop_html = """
        <script>
            var audio = document.getElementById("wheelAudio");
            if (audio) {
                audio.pause();
                audio.currentTime = 0;
            }
        </script>
    """
    return stop_html

# CSS để tạo giao diện đẹp mắt
css = """
<style>
    /* Thiết lập toàn trang */
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;700&display=swap');

    .main {
        background: linear-gradient(135deg, #f0f2f5, #e6e9ef);
        font-family: 'Montserrat', sans-serif;
    }
    
    h1, h2, h3 {
        color: #1a3a5f;
        font-family: 'Montserrat', sans-serif;
        font-weight: 700;
    }
    
    /* Khu vực bốc thăm */
    .draw-container {
        background-color: white;
        border-radius: 15px;
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
        padding: 20px;
        margin-bottom: 20px;
        transition: all 0.3s ease;
    }
    
    .draw-container:hover {
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.18);
        transform: translateY(-2px);
    }
    
    /* Vòng quay */
    .wheel-container {
        display: flex;
        justify-content: center;
        align-items: center;
        position: relative;
        margin: 20px auto;
    }
    
    /* Nút bốc thăm */
    .stButton > button {
        background: linear-gradient(135deg, #064990, #0a5dbd);
        color: white;
        font-weight: bold;
        border: none;
        padding: 10px 20px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(10, 93, 189, 0.3);
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #053c7c, #084da0);
        box-shadow: 0 6px 16px rgba(10, 93, 189, 0.4);
        transform: translateY(-2px);
    }
    
    /* Nút reset */
    .stButton.reset > button {
        background: linear-gradient(135deg, #e74c3c, #c0392b);
        box-shadow: 0 4px 12px rgba(231, 76, 60, 0.3);
    }
    
    .stButton.reset > button:hover {
        background: linear-gradient(135deg, #c0392b, #a93226);
        box-shadow: 0 6px 16px rgba(231, 76, 60, 0.4);
    }
    
    /* Bảng kết quả */
    .styled-table {
        width: 100%;
        border-collapse: collapse;
        margin: 25px 0;
        font-size: 18px;
        font-family: 'Montserrat', sans-serif;
        box-shadow: 0 0 30px rgba(0, 0, 0, 0.15);
        border-radius: 10px;
        overflow: hidden;
    }
    
    .styled-table thead tr {
        background: linear-gradient(135deg, #1a3a5f, #2980b9);
        color: white;
        text-align: center;
    }
    
    .styled-table th,
    .styled-table td {
        padding: 15px;
        text-align: center;
        border: none;
    }
    
    .styled-table tbody tr {
        border-bottom: 1px solid #dddddd;
        transition: all 0.3s ease;
    }
    
    .styled-table tbody tr:nth-of-type(even) {
        background-color: #f8f9fa;
    }
    
    .styled-table tbody tr:hover {
        background-color: #f1f1f1;
        transform: scale(1.01);
    }
    
    .styled-table tbody tr:last-of-type {
        border-bottom: 2px solid #1a3a5f;
    }
    
    .empty-cell {
        color: #bbb;
        font-style: italic;
    }
    
    .header-cell {
        font-weight: bold;
        background-color: #e9ecef;
    }
    
    /* Language toggle */
    .language-toggle {
        display: flex;
        justify-content: flex-end;
        margin-bottom: 10px;
    }
    
    /* Điểm nhấn và hiệu ứng */
    .highlight-result {
        background: linear-gradient(135deg, #2ecc71, #27ae60);
        color: white;
        padding: 15px;
        border-radius: 8px;
        font-weight: bold;
        text-align: center;
        box-shadow: 0 4px 15px rgba(46, 204, 113, 0.3);
        animation: pulse 1.5s infinite;
    }
    
    @keyframes pulse {
        0% {
            box-shadow: 0 0 0 0 rgba(46, 204, 113, 0.6);
        }
        70% {
            box-shadow: 0 0 0 15px rgba(46, 204, 113, 0);
        }
        100% {
            box-shadow: 0 0 0 0 rgba(46, 204, 113, 0);
        }
    }
    
    /* Progress bar */
    .stProgress > div > div {
        background-color: #2980b9;
    }
    
    /* Select box styling */
    .stSelectbox [data-baseweb="select"] {
        border-radius: 8px;
        border: 2px solid #e0e0e0;
    }
    
    .stSelectbox [data-baseweb="select"]:hover {
        border-color: #2980b9;
    }
    
    /* Logo và tiêu đề */
    .title-container {
        text-align: center;
        margin-bottom: 20px;
    }
    
    .title-container h1 {
        color: #1a3a5f;
        text-shadow: 1px 1px 3px rgba(0,0,0,0.2);
        animation: title-glow 3s infinite alternate;
    }
    
    @keyframes title-glow {
        from {
            text-shadow: 1px 1px 5px rgba(26, 58, 95, 0.2);
        }
        to {
            text-shadow: 1px 1px 15px rgba(26, 58, 95, 0.6);
        }
    }
    
    /* Khi đã bốc thăm xong */
    .completed-message {
        background: linear-gradient(135deg, #3498db, #2980b9);
        color: white;
        padding: 15px;
        border-radius: 8px;
        text-align: center;
        font-weight: bold;
        box-shadow: 0 4px 15px rgba(52, 152, 219, 0.3);
    }
</style>
"""

# Hiển thị CSS
st.markdown(css, unsafe_allow_html=True)

# Placeholder cho audio
audio_placeholder = st.empty()
result_audio_placeholder = st.empty()

# Chọn ngôn ngữ / Language selector
lang_col1, lang_col2 = st.columns([6, 1])
with lang_col2:
    selected_language = st.selectbox(
        get_text('language_selector'),
        options=['vi', 'en'],
        format_func=lambda x: "Tiếng Việt" if x == 'vi' else "English",
        index=0 if st.session_state.language == 'vi' else 1
    )
    if selected_language != st.session_state.language:
        st.session_state.language = selected_language
        st.rerun()

# Tiêu đề ứng dụng với lớp CSS
st.markdown(f'<div class="title-container"><h1>{get_text("title")}</h1></div>', unsafe_allow_html=True)

# Container 1: Phần droplist và button (trên)
with st.container():
    st.markdown('<div class="draw-container">', unsafe_allow_html=True)
    st.header(get_text('draw_header'))
    
    # Hiển thị số đội còn lại cần bốc thăm
    st.subheader(get_text('teams_left', count=len(available_teams)))
    
    # Chia cột cho phần điều khiển
    control_col1, control_col2, control_col3 = st.columns([2, 1, 1])
    
    with control_col1:
        if available_teams:
            # Dropdown để chọn đội
            selected_team = st.selectbox(get_text('select_team'), available_teams)
        else:
            st.markdown(f'<div class="completed-message">{get_text("all_teams_drawn")}</div>', unsafe_allow_html=True)
            selected_team = None
    
    with control_col2:
        # Nút bốc thăm
        if available_teams and st.button(get_text('draw_button'), use_container_width=True):
            st.session_state.spinning = True
            st.session_state.current_team = selected_team
            st.session_state.used_teams.append(selected_team)
            st.rerun()
            
    with control_col3:
        # Nút reset
        if st.button(get_text('reset_button'), use_container_width=True, key="reset_button"):
            for key in list(st.session_state.keys()):
                if key != 'language':  # Giữ nguyên ngôn ngữ đã chọn
                    del st.session_state[key]
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

# Container 2: Vòng xoay và kết quả bốc thăm (dưới)
with st.container():
    st.markdown('<div class="draw-container">', unsafe_allow_html=True)
    
    # Chia cột cho vòng xoay và kết quả
    wheel_col, results_col = st.columns([2, 5])
    
    # Cột 1: Vòng xoay
    with wheel_col:
        st.markdown('<div class="wheel-container">', unsafe_allow_html=True)
        
        # Hiển thị vòng quay may mắn
        wheel_container = st.empty()
        result_container = st.empty()
        
        if st.session_state.spinning and st.session_state.available_positions:
            audio_url = "https://tiengdong.com/wp-content/uploads/Am-thanh-vong-quay-chiec-non-ky-dieu-www_tiengdong_com.mp3?_=1"
            audio_placeholder.markdown(autoplay_audio(audio_url), unsafe_allow_html=True)
            
            with st.spinner(get_text('spinning')):
                progress_bar = st.progress(0)
                
                # Điều chỉnh tham số quay
                total_spins = 10  # Tăng số khung hình
                spin_duration = 0.2  # Thời gian quay 5 giây
                
                n = len(st.session_state.available_positions)
                segment_angle = 360 / n
                
                random_index = random.randint(0, n - 1)
                target_angle = random_index * segment_angle + segment_angle / 2
                target_angle += random.randint(15, 25) * 360  # Thêm nhiều vòng quay hơn
                
                angles = []
                current_angle = st.session_state.wheel_angle
                
                # Tạo hiệu ứng quay cải tiến
                for i in range(total_spins):
                    progress = i / total_spins
                    t = easeInOutCirc(progress)
                    
                    # Điều chỉnh các giai đoạn quay
                    if progress < 0.25:
                        current_angle += (target_angle - current_angle) * 0.04 * (1 + progress * 8)
                    elif progress < 0.7:
                        current_angle += (target_angle - current_angle) * 0.04 * 2.5
                    else:
                        current_angle += (target_angle - current_angle) * 0.04 * (1 + (1 - progress) * 6)
                    
                    # Thêm nhiễu ngẫu nhiên
                    if i < total_spins * 0.9:
                        current_angle += random.uniform(-0.5, 0.5)
                    
                    angles.append(current_angle % 360)
                
                # Thêm hiệu ứng nảy khi dừng
                final_angle = angles[-1]
                for j in range(3):
                    angles.append((final_angle + (1 if j % 2 else -1) * (j + 1) * 0.3) % 360)
                angles.append(final_angle % 360)
                
                # Thực hiện quay
                labels_pos = None
                for i, angle in enumerate(angles):
                    fig, labels_pos = create_wheel(st.session_state.available_positions, angle)
                    wheel_container.pyplot(fig)
                    progress_bar.progress(int((i + 1) / len(angles) * 100))
                    time.sleep(spin_duration / len(angles))
                
                # Lưu góc quay cuối cùng
                st.session_state.wheel_angle = angles[-1] % 360
                
                # Xác định vị trí được chọn dựa trên góc quay cuối cùng
                selected_position = get_selected_position(labels_pos, st.session_state.wheel_angle)
                
                # Lưu kết quả
                st.session_state.results[st.session_state.current_team] = selected_position
                st.session_state.available_positions.remove(selected_position)
                
                # Cập nhật bảng kết quả
                update_result_table(selected_position, st.session_state.current_team)
                
                # Dừng âm thanh quay và phát âm thanh kết quả
                audio_placeholder.markdown(stop_audio(), unsafe_allow_html=True)
                result_audio_placeholder.markdown(play_result_audio(), unsafe_allow_html=True)
                
                # Hiển thị kết quả với hiệu ứng
                result_html = f'<div class="highlight-result">{get_text("result", team=st.session_state.current_team, position=selected_position)}</div>'
                result_container.markdown(result_html, unsafe_allow_html=True)
                
                st.session_state.spinning = False
        else:
            # Hiển thị vòng quay tĩnh
            if st.session_state.available_positions:
                fig, _ = create_wheel(st.session_state.available_positions, st.session_state.wheel_angle)
                wheel_container.pyplot(fig)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Cột 2: Kết quả bốc thăm
    with results_col:
        st.header(get_text('results_header'))
        
        # Tạo HTML cho bảng song ngữ
        table_html = '<table class="styled-table"><thead><tr>'
        
        # Tiêu đề cột song ngữ
        if st.session_state.language == 'vi':
            position_text = f"{get_text('position')} / Position"
        else:
            position_text = f"Position / {get_text('position')}"
        
        table_html += f'<th>{position_text}</th>'
        
        for group in ['A', 'B']:
            if st.session_state.language == 'vi':
                group_text = f"{get_text('group', group=group)} / Group {group}"
            else:
                group_text = f"Group {group} / {get_text('group', group=group)}"
            table_html += f'<th>{group_text}</th>'
        
        table_html += '</tr></thead><tbody>'
        
        # Thêm dữ liệu vào bảng
        for i in range(4):
            table_html += '<tr>'
            table_html += f'<td class="header-cell">{i+1}</td>'
            
            # Bảng A
            cell_value = st.session_state.result_table['A'][i] if i < len(st.session_state.result_table['A']) and st.session_state.result_table['A'][i] is not None else ""
            cell_class = "empty-cell" if cell_value == "" else ""
            cell_content = cell_value if cell_value != "" else "_____"
            table_html += f'<td class="{cell_class}">{cell_content}</td>'
            
            # Bảng B
            cell_value = st.session_state.result_table['B'][i] if i < len(st.session_state.result_table['B']) and st.session_state.result_table['B'][i] is not None else ""
            cell_class = "empty-cell" if cell_value == "" else ""
            cell_content = cell_value if cell_value != "" else "_____"
            table_html += f'<td class="{cell_class}">{cell_content}</td>'
            
            table_html += '</tr>'
        
        table_html += '</tbody></table>'
        
        # Hiển thị bảng
        st.markdown(table_html, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
