import json
import os
import random
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Mini Game Tổng Hợp", page_icon="🎮")
st.title("🎮 Trò Chơi Mini (Vòng Quay & Mở Hộp)")

DATA_FILE = "game_data.json"


def load_data():
  if os.path.exists(DATA_FILE):
    try:
      with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)
    except:
      pass
  return None


saved_data = load_data()

# 1. Khởi tạo dữ liệu Người chơi
if "players_df" not in st.session_state:
  loaded_players = None
  if saved_data and "players" in saved_data:
    try:
      loaded_players = pd.DataFrame(saved_data["players"])
      if (
          "Chọn" not in loaded_players.columns
          or "Tên người chơi" not in loaded_players.columns
      ):
        loaded_players = None
    except:
      loaded_players = None

  if loaded_players is not None:
    st.session_state.players_df = loaded_players
  else:
    players = [
        "Vũ Thành Đạt",
        "Nguyễn Phương Linh",
        "Trần Tuấn Anh",
        "Trần Thị Hân",
        "Vũ Thị Thuỳ Dung",
        "Vũ Phương Chi",
        "Đoàn Khánh Hoà",
        "Minh Ánh",
        "Phan Ngọc Anh",
        "Nguyễn Hoàng Lâm",
        "Vũ Khánh Linh",
        "Nguyễn Sinh Huy",
    ]
    st.session_state.players_df = pd.DataFrame({
        "Chọn": [True] * len(players),
        "Tên người chơi": players,
    })

# 2. Khởi tạo dữ liệu Điểm
if "points_df" not in st.session_state:
  loaded_points = None
  if saved_data and "points" in saved_data:
    try:
      loaded_points = pd.DataFrame(saved_data["points"])
      if (
          "Chọn" not in loaded_points.columns
          or "Số điểm" not in loaded_points.columns
      ):
        loaded_points = None
    except:
      loaded_points = None

  if loaded_points is not None:
    st.session_state.points_df = loaded_points
  else:
    st.session_state.points_df = pd.DataFrame({
        "Chọn": [True, True, True, True, True, True],
        "Số điểm": [
            "+1 điểm",
            "+2 điểm",
            "+3 điểm",
            "Nhường lượt",
            "+10 điểm",
            "+5 điểm",
        ],
    })

# 3. Khởi tạo kho phần thưởng hộp quà (Chia thành May mắn và Đen đủi)
if "box_lucky_val" not in st.session_state:
  if saved_data and "box_lucky" in saved_data:
    st.session_state.box_lucky_val = saved_data["box_lucky"]
  else:
    st.session_state.box_lucky_val = (
        "🎁 x2 Điểm, 🎁 x3 Điểm, 🎁 Xin 20 Điểm của bạn cao nhất, 🎁 X4 Điểm"
    )

if "box_unlucky_val" not in st.session_state:
  if saved_data and "box_unlucky" in saved_data:
    st.session_state.box_unlucky_val = saved_data["box_unlucky"]
  else:
    st.session_state.box_unlucky_val = (
        "💀 -5 điểm, 💀 -10 Điểm, 💀 Chúc may mắn lần sau,💀 Tặng 10 điểm cho bạn thấp nhất "
    )

if "box_opened_state" not in st.session_state:
  st.session_state.box_opened_state = [False] * 6
  st.session_state.box_contents = [""] * 6
  st.session_state.box_types = [""] * 6

if "holding_wand" not in st.session_state:
  st.session_state.holding_wand = False


def save_all_data():
  data = {
      "players": st.session_state.players_df.to_dict("records"),
      "points": st.session_state.points_df.to_dict("records"),
      "box_lucky": st.session_state.box_lucky_val,
      "box_unlucky": st.session_state.box_unlucky_val,
  }
  with open(DATA_FILE, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=4)


# Chia tab rõ ràng
tab1, tab2, tab3 = st.tabs(
    ["👤 Vòng quay Tên", "⭐ Vòng quay Điểm", "🎁 Mở Hộp Quà (Gậy Ngôi Sao)"]
)

# --- TAB 1: Vòng quay Tên ---
with tab1:
  st.subheader("Quản lý danh sách người chơi")
  edited_players_df = st.data_editor(
      st.session_state.players_df,
      num_rows="dynamic",
      use_container_width=True,
      key="player_editor",
      column_config={
          "Chọn": st.column_config.CheckboxColumn(
              "Tham gia?", default=True
          )
      },
  )

  if st.button("💾 Lưu danh sách người chơi", key="save_players"):
    st.session_state.players_df = edited_players_df
    save_all_data()
    st.success("Đã lưu danh sách!")
    st.rerun()

  active_players = st.session_state.players_df[
      st.session_state.players_df["Chọn"] == True
  ]
  players_list = [
      str(p).strip()
      for p in active_players["Tên người chơi"].dropna().tolist()
      if str(p).strip()
  ]

  st.markdown("---")
  st.subheader("Vòng Quay Tên Người Chơi")

  if not players_list:
    st.warning("⚠️ Vui lòng tích chọn ít nhất một người chơi!")
  else:
    items_json = json.dumps(players_list)
    wheel_html_name = f"""
        <!DOCTYPE html>
        <html>
        <head>
        <style>
          body {{ display: flex; flex-direction: column; align-items: center; justify-content: center; margin: 0; background: transparent; color: white; font-family: sans-serif; }}
          .container {{ display: flex; flex-direction: column; align-items: center; position: relative; }}
          canvas {{ cursor: pointer; }}
          .pointer {{ width: 0; height: 0; border-left: 14px solid transparent; border-right: 14px solid transparent; border-top: 28px solid #ff4b4b; border-bottom: 0; margin-bottom: -5px; z-index: 10; }}
          button {{ margin-top: 15px; padding: 12px 24px; font-size: 16px; font-weight: bold; background-color: #ff4b4b; color: white; border: none; border-radius: 8px; cursor: pointer; }}
          button:active {{ background-color: #cc3a3a; }}
          #result {{ margin-top: 10px; font-size: 22px; font-weight: bold; height: 35px; color: #4ade80; text-align: center; }}
        </style>
        </head>
        <body>
        <div class="container">
          <div class="pointer"></div>
          <canvas id="canvas" width="400" height="400"></canvas>
          <button onclick="spinWheel()">QUAY TÊN</button>
          <div id="result"></div>
        </div>
        <script>
          const canvas = document.getElementById("canvas");
          const ctx = canvas.getContext("2d");
          const prizes = {items_json};
          const colors = ["#f87171", "#fb923c", "#facc15", "#4ade80", "#38bdf8", "#c084fc", "#f472b6", "#818cf8"];
          
          const spinSound = new Audio('https://raw.githubusercontent.com/lamtacghe-collab/lopk36/refs/heads/main/quayvong%20(mp3cut.net).mp3');
          const spinTimeTotal = 10000;

          let startAngle = 0;
          let arc = prizes.length > 0 ? (Math.PI / (prizes.length / 2)) : 0;
          let spinTimeout = null, spinAngleStart = 0, spinTime = 0;

          function drawWheel() {{
            ctx.clearRect(0, 0, 400, 400);
            if (prizes.length === 0) return;
            let outsideRadius = 180, textRadius = 120, insideRadius = 35;
            ctx.strokeStyle = "#ffffff"; ctx.lineWidth = 2;
            for(let i = 0; i < prizes.length; i++) {{
              let angle = startAngle + i * arc;
              ctx.fillStyle = colors[i % colors.length];
              ctx.beginPath();
              ctx.arc(200, 200, outsideRadius, angle, angle + arc, false);
              ctx.arc(200, 200, insideRadius, angle + arc, angle, true);
              ctx.stroke(); ctx.fill();
              ctx.save();
              ctx.fillStyle = "#000000";
              ctx.translate(200 + Math.cos(angle + arc / 2) * textRadius, 200 + Math.sin(angle + arc / 2) * textRadius);
              ctx.rotate(angle + arc / 2 + Math.PI / 2);
              let text = prizes[i];
              if (text.length > 12) text = text.substring(0, 10) + '...';
              ctx.font = "bold 14px sans-serif";
              ctx.fillText(text, -ctx.measureText(text).width / 2, 0);
              ctx.restore();
            }}
            ctx.fillStyle = "#ffffff"; ctx.beginPath(); ctx.arc(200, 200, 25, 0, 2 * Math.PI, false); ctx.fill(); ctx.stroke();
          }}

          function rotateWheel() {{
            spinTime += 30;
            if(spinTime >= spinTimeTotal) {{ stopRotateWheel(); return; }}
            let spinAngle = spinAngleStart - easeOut(spinTime, 0, spinAngleStart, spinTimeTotal);
            startAngle += (spinAngle * Math.PI / 180);
            drawWheel();
            spinTimeout = setTimeout(rotateWheel, 30);
          }}

          function easeOut(t, b, c, d) {{ let ts = (t/=d)*t; let tc = ts*t; return b+c*(tc + -3*ts + 3*t); }}
          
          function spinWheel() {{
            if (prizes.length === 0) return;
            document.getElementById("result").innerText = "";
            
            spinSound.currentTime = 0;
            spinSound.play().catch(e => console.log(e));

            spinAngleStart = Math.random() * 15 + 20;;
            spinTime = 0;
            rotateWheel();
          }}

          function stopRotateWheel() {{
            let degrees = startAngle * 180 / Math.PI + 90;
            let arcd = arc * 180 / Math.PI;
            let index = Math.floor((360 - degrees % 360) / arcd);
            document.getElementById("result").innerText = "Kết quả: " + prizes[index];
          }}
          drawWheel();
        </script>
        </body>
        </html>
        """
    st.components.v1.html(wheel_html_name, height=530)

# --- TAB 2: Vòng quay Điểm ---
with tab2:
  st.subheader("Quản lý danh sách điểm")
  edited_points_df = st.data_editor(
      st.session_state.points_df,
      num_rows="dynamic",
      use_container_width=True,
      key="points_editor",
      column_config={
          "Chọn": st.column_config.CheckboxColumn("Tham gia?", default=True)
      },
  )

  if st.button("💾 Lưu danh sách điểm", key="save_points"):
    st.session_state.points_df = edited_points_df
    save_all_data()
    st.success("Đã lưu danh sách điểm!")
    st.rerun()

  active_points = st.session_state.points_df[
      st.session_state.points_df["Chọn"] == True
  ]
  points_list = [
      str(p).strip()
      for p in active_points["Số điểm"].dropna().tolist()
      if str(p).strip()
  ]

  st.markdown("---")
  st.subheader("Vòng Quay Số Điểm")

  if not points_list:
    st.warning("⚠️ Vui lòng tích chọn ít nhất một mức điểm!")
  else:
    points_json = json.dumps(points_list)
    wheel_html_point = f"""
        <!DOCTYPE html>
        <html>
        <head>
        <style>
          body {{ display: flex; flex-direction: column; align-items: center; justify-content: center; margin: 0; background: transparent; color: white; font-family: sans-serif; }}
          .container {{ display: flex; flex-direction: column; align-items: center; position: relative; }}
          canvas {{ cursor: pointer; }}
          .pointer {{ width: 0; height: 0; border-left: 14px solid transparent; border-right: 14px solid transparent; border-top: 28px solid #ff4b4b; border-bottom: 0; margin-bottom: -5px; z-index: 10; }}
          button {{ margin-top: 15px; padding: 12px 24px; font-size: 16px; font-weight: bold; background-color: #ff4b4b; color: white; border: none; border-radius: 8px; cursor: pointer; }}
          button:active {{ background-color: #cc3a3a; }}
          #result {{ margin-top: 10px; font-size: 22px; font-weight: bold; height: 35px; color: #4ade80; text-align: center; }}
        </style>
        </head>
        <body>
        <div class="container">
          <div class="pointer"></div>
          <canvas id="canvas" width="400" height="400"></canvas>
          <button onclick="spinWheel()">QUAY ĐIỂM</button>
          <div id="result"></div>
        </div>
        <script>
          const canvas = document.getElementById("canvas");
          const ctx = canvas.getContext("2d");
          const prizes = {points_json};
          const colors = ["#f87171", "#fb923c", "#facc15", "#4ade80", "#38bdf8", "#c084fc", "#f472b6", "#818cf8"];
          
          const spinSound = new Audio('https://raw.githubusercontent.com/lamtacghe-collab/lopk36/refs/heads/main/quayvong%20(mp3cut.net).mp3');
          const spinTimeTotal = 10000;

          let startAngle = 0;
          let arc = prizes.length > 0 ? (Math.PI / (prizes.length / 2)) : 0;
          let spinTimeout = null, spinAngleStart = 0, spinTime = 0;

          function drawWheel() {{
            ctx.clearRect(0, 0, 400, 400);
            if (prizes.length === 0) return;
            let outsideRadius = 180, textRadius = 120, insideRadius = 35;
            ctx.strokeStyle = "#ffffff"; ctx.lineWidth = 2;
            for(let i = 0; i < prizes.length; i++) {{
              let angle = startAngle + i * arc;
              ctx.fillStyle = colors[i % colors.length];
              ctx.beginPath();
              ctx.arc(200, 200, outsideRadius, angle, angle + arc, false);
              ctx.arc(200, 200, insideRadius, angle + arc, angle, true);
              ctx.stroke(); ctx.fill();
              ctx.save();
              ctx.fillStyle = "#000000";
              ctx.translate(200 + Math.cos(angle + arc / 2) * textRadius, 200 + Math.sin(angle + arc / 2) * textRadius);
              ctx.rotate(angle + arc / 2 + Math.PI / 2);
              let text = prizes[i];
              if (text.length > 12) text = text.substring(0, 10) + '...';
              ctx.font = "bold 14px sans-serif";
              ctx.fillText(text, -ctx.measureText(text).width / 2, 0);
              ctx.restore();
            }}
            ctx.fillStyle = "#ffffff"; ctx.beginPath(); ctx.arc(200, 200, 25, 0, 2 * Math.PI, false); ctx.fill(); ctx.stroke();
          }}

          function rotateWheel() {{
            spinTime += 30;
            if(spinTime >= spinTimeTotal) {{ stopRotateWheel(); return; }}
            let spinAngle = spinAngleStart - easeOut(spinTime, 0, spinAngleStart, spinTimeTotal);
            startAngle += (spinAngle * Math.PI / 180);
            drawWheel();
            spinTimeout = setTimeout(rotateWheel, 30);
          }}

          function easeOut(t, b, c, d) {{ let ts = (t/=d)*t; let tc = ts*t; return b+c*(tc + -3*ts + 3*t); }}
          
          function spinWheel() {{
            if (prizes.length === 0) return;
            document.getElementById("result").innerText = "";
            
            spinSound.currentTime = 0;
            spinSound.play().catch(e => console.log(e));

            spinAngleStart = Math.random() * 15 + 20;

            spinTime = 0;
            rotateWheel();
          }}

          function stopRotateWheel() {{
            let degrees = startAngle * 180 / Math.PI + 90;
            let arcd = arc * 180 / Math.PI;
            let index = Math.floor((360 - degrees % 360) / arcd);
            document.getElementById("result").innerText = "Kết quả: " + prizes[index];
          }}
          drawWheel();
        </script>
        </body>
        </html>
        """
    st.components.v1.html(wheel_html_point, height=530)

# --- TAB 3: Mở Hộp Quà (Chia làm May Mắn & Đen Đủi) ---
with tab3:
  st.subheader("Cài đặt kho phần thưởng hộp quà")

  col_config1, col_config2 = st.columns(2)
  with col_config1:
    box_lucky_input = st.text_area(
        "✨ Phần thưởng MAY MẮN (cách nhau bằng dấu phẩy):",
        value=st.session_state.box_lucky_val,
        key="box_lucky_textarea",
    )
  with col_config2:
    box_unlucky_input = st.text_area(
        "💀 Phần thưởng ĐEN ĐỦI (cách nhau bằng dấu phẩy):",
        value=st.session_state.box_unlucky_val,
        key="box_unlucky_textarea",
    )

  if st.button("💾 Lưu kho phần thưởng hộp quà", key="save_boxes"):
    st.session_state.box_lucky_val = box_lucky_input
    st.session_state.box_unlucky_val = box_unlucky_input
    save_all_data()
    st.success("Đã cập nhật kho phần thưởng!")
    st.rerun()

  lucky_pool_list = [
      p.strip()
      for p in st.session_state.box_lucky_val.split(",")
      if p.strip()
  ]
  unlucky_pool_list = [
      p.strip()
      for p in st.session_state.box_unlucky_val.split(",")
      if p.strip()
  ]

  st.markdown("---")
  st.subheader("🎁 Mở Hộp Quà Bằng Gậy Ngôi Sao")

  col_wand1, col_wand2 = st.columns([2, 1])
  with col_wand1:
    if not st.session_state.holding_wand:
      if st.button(
          "🪄 BẤM VÀO ĐÂY ĐỂ CẦM GẬY NGÔI SAO",
          use_container_width=True,
          type="primary",
      ):
        st.session_state.holding_wand = True
        st.rerun()
    else:
      if st.button(
          "✨ ĐANG CẦM GẬY (Bấm để cất)",
          use_container_width=True,
          type="secondary",
      ):
        st.session_state.holding_wand = False
        st.rerun()

  with col_wand2:
    if st.button("🔄 Đặt lại hộp", use_container_width=True):
      st.session_state.box_opened_state = [False] * 6
      st.session_state.box_contents = [""] * 6
      st.session_state.box_types = [""] * 6
      st.session_state.holding_wand = False
      st.rerun()

  if st.session_state.holding_wand:
    st.success(
        "🪄 Bạn đang cầm gậy ngôi sao trên tay! Hãy chạm vào các hộp bên dưới để"
        " mở quà."
    )
  else:
    st.warning("⚠️ Bạn chưa cầm gậy ngôi sao! Hãy bấm nút bên trên để lấy gậy.")

  box_colors = ["#ef4444", "#f97316", "#eab308", "#22c55e", "#0ea5e9", "#a855f7"]
  cols = st.columns(3)

  for i in range(6):
    col_idx = i % 3
    with cols[col_idx]:
      color = box_colors[i]
      is_opened = st.session_state.box_opened_state[i]

      if not is_opened:
        st.markdown(
            f"""
                <div style="
                    background: linear-gradient(135deg, {color}, #090d16);
                    height: 105px;
                    border-radius: 14px;
                    position: relative;
                    box-shadow: 0 6px 15px rgba(0,0,0,0.4);
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                    color: white;
                    font-weight: bold;
                    border: 3px solid #facc15;
                    margin-bottom: 8px;
                ">
                    <div style="position: absolute; width: 16px; height: 100%; background: #facc15; top: 0; left: 50%; transform: translateX(-50%); opacity: 0.85;"></div>
                    <div style="position: absolute; width: 100%; height: 16px; background: #facc15; top: 50%; left: 0; transform: translateY(-50%); opacity: 0.85;"></div>
                    <div style="z-index: 2; font-size: 20px; margin-bottom: 2px;">🎁</div>
                    <div style="z-index: 2; font-size: 14px; text-shadow: 1px 1px 2px rgba(0,0,0,0.8);">Hộp #{i+1}</div>
                </div>
                """,
            unsafe_allow_html=True,
        )

        if st.button(
            f"Dùng gậy mở #{i+1}", key=f"open_box_{i}", use_container_width=True
        ):
          if not st.session_state.holding_wand:
            st.error("❌ Bạn phải bấm 'Cầm gậy ngôi sao' trước khi mở hộp!")
          else:
            has_lucky = len(lucky_pool_list) > 0
            has_unlucky = len(unlucky_pool_list) > 0

            if has_lucky and has_unlucky:
              is_lucky = random.choice([True, False])
            elif has_lucky:
              is_lucky = True
            elif has_unlucky:
              is_lucky = False
            else:
              is_lucky = True

            if is_lucky:
              chosen_reward = random.choice(
                  lucky_pool_list
                  if lucky_pool_list
                  else ["Phần thưởng may mắn trống"]
              )
              box_type = "lucky"
            else:
              chosen_reward = random.choice(
                  unlucky_pool_list
                  if unlucky_pool_list
                  else ["Phần thưởng đen đủi trống"]
              )
              box_type = "unlucky"

            st.session_state.box_opened_state[i] = True
            st.session_state.box_contents[i] = chosen_reward
            st.session_state.box_types[i] = box_type
            st.balloons()
            st.rerun()
      else:
        reward = st.session_state.box_contents[i]
        box_type = st.session_state.box_types[i]

        win_audio_url = "https://raw.githubusercontent.com/lamtacghe-collab/lopk36/refs/heads/main/win.mp3"
        lose_audio_url = "https://raw.githubusercontent.com/lamtacghe-collab/lopk36/refs/heads/main/lose.mp3"

        audio_tag = ""
        if box_type == "lucky":
          audio_tag = f'<audio src="{win_audio_url}" autoplay></audio>'
        elif box_type == "unlucky":
          audio_tag = f'<audio src="{lose_audio_url}" autoplay></audio>'

        st.markdown(
            f"""
                <div style="
                    background: linear-gradient(135deg, #0f172a, #1e293b);
                    height: 105px;
                    border-radius: 14px;
                    border: 3px dashed {color};
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                    text-align: center;
                    color: #4ade80;
                    font-weight: bold;
                    margin-bottom: 8px;
                    box-shadow: inset 0 2px 6px rgba(0,0,0,0.5);
                ">
                    <div style="font-size: 16px;">✨ ĐÃ MỞ ✨</div>
                    <div style="color: #facc15; font-size: 15px; margin-top: 3px;">{reward}</div>
                </div>
                {audio_tag}
                """,
            unsafe_allow_html=True,
        )
        if st.button(
            f"Đã mở #{i+1}",
            key=f"opened_btn_{i}",
            disabled=True,
            use_container_width=True,
        ):
          pass
