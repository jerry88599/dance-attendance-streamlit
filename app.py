import streamlit as st
import csv
import os
from datetime import datetime
import json
import pandas as pd
from streamlit_option_menu import option_menu

# 访问密码验证
def check_access():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        st.title("🔒 街舞考勤系统 - 登录")
        password = st.text_input("请输入访问密码", type="password")
        if st.button("登录", type="primary"):
            if password == "123456":
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("密码错误，请重试")
        st.stop()

check_access()

# 页面配置
st.set_page_config(
    page_title="街舞考勤",
    page_icon="💃",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 全局样式 - 深色主题优化
st.markdown("""
<style>
/* 基础设置 */
html, body, [class*="css"] {
    font-size: 16px;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

/* 标题样式 */
h1 {
    font-size: 24px !important;
    font-weight: 700 !important;
    margin-bottom: 1rem !important;
    color: white !important;
}

h2 {
    font-size: 20px !important;
    font-weight: 600 !important;
    color: white !important;
}

h3 {
    font-size: 17px !important;
    font-weight: 600 !important;
    color: white !important;
}

/* 页面容器 */
div.block-container { 
    padding-top: 0.5rem; 
    padding-bottom: 2rem;
    max-width: 100%;
    background-color: #0E1117;
}

/* 按钮样式 */
div.stButton > button { 
    width: 100%; 
    font-size: 16px !important;
    padding: 0.6rem 1rem !important;
    border-radius: 8px !important;
    background-color: #262730 !important;
    color: white !important;
    border: 1px solid #4169E1 !important;
}

div.stButton > button:hover {
    background-color: #4169E1 !important;
}

div.stButton > button[kind="primary"] {
    background-color: #4169E1 !important;
    border: none !important;
}

/* 输入框样式 */
.stTextInput > div > div > input,
.stSelectbox > div > div > select {
    font-size: 16px !important;
    background-color: #262730 !important;
    color: white !important;
    border: 1px solid #444 !important;
    border-radius: 8px !important;
    padding: 0.6rem !important;
}

/* 标签页样式优化 */
.stTabs [data-baseweb="tab-list"] {
    gap: 0;
    background-color: #1E1E1E;
    border-radius: 8px;
    padding: 4px;
}

.stTabs [data-baseweb="tab"] {
    font-size: 15px !important;
    padding: 8px 16px !important;
    color: #888 !important;
    border-radius: 6px !important;
    border: none !important;
    background-color: transparent !important;
}

.stTabs [aria-selected="true"] {
    color: #FF6B6B !important;
    background-color: #2A2A2A !important;
    font-weight: 600 !important;
}

/* 复选框样式 */
.stCheckbox > label {
    font-size: 16px !important;
    color: white !important;
}

/* 信息框样式 */
.stInfo, .stSuccess, .stWarning, .stError {
    font-size: 15px !important;
    padding: 1rem !important;
    border-radius: 8px !important;
}

.stSuccess {
    background-color: #1E3A2F !important;
    color: #4ADE80 !important;
    border: 1px solid #4ADE80 !important;
}

.stInfo {
    background-color: #1E2A3A !important;
    color: #60A5FA !important;
    border: 1px solid #60A5FA !important;
}

/* 分隔线 */
hr {
    border-color: #333 !important;
    margin: 1rem 0 !important;
}

/* 导航栏关键样式 */
.nav-link {
    white-space: nowrap !important;
}

/* 隐藏默认streamlit元素 */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# 基础文件配置
CSV_FILE = "dance_student_records.csv"
STUDENT_CONFIG_FILE = "dance_students.json"
PRICE_PER_PERSON = 80

# 初始化数据文件
def init_files():
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
            csv.writer(f).writerow(["日期", "班级", "学生姓名", "是否到课"])
    if not os.path.exists(STUDENT_CONFIG_FILE):
        default_config = {
            "街舞1班": {"students": ["小明", "小红", "小刚", "小丽", "小亮"], "color": "#4169E1"},
            "街舞2班": {"students": ["小美", "小杰", "小宇", "小诺", "小泽", "小琳"], "color": "#32CD32"}
        }
        with open(STUDENT_CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, ensure_ascii=False, indent=2)

def get_student_config():
    init_files()
    with open(STUDENT_CONFIG_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_student_config(config):
    with open(STUDENT_CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

def delete_record(date, class_name, student):
    records = []
    with open(CSV_FILE, 'r', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            if not (row["日期"] == date and row["班级"] == class_name and row["学生姓名"] == student):
                records.append(row)
    with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=["日期", "班级", "学生姓名", "是否到课"])
        writer.writeheader()
        writer.writerows(records)

def delete_batch_records(date_str, class_name):
    records = []
    with open(CSV_FILE, 'r', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            if not (row["日期"] == date_str and row["班级"] == class_name):
                records.append(row)
    with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=["日期", "班级", "学生姓名", "是否到课"])
        writer.writeheader()
        writer.writerows(records)

def import_attendance_csv(uploaded_file):
    try:
        df = pd.read_csv(uploaded_file, encoding='utf-8')
        required_cols = ["日期", "班级", "学生姓名", "是否到课"]
        if not all(col in df.columns for col in required_cols):
            return False, "CSV列名错误！需包含：日期、班级、学生姓名、是否到课"
        df.to_csv(CSV_FILE, index=False, encoding='utf-8')
        return True, "考勤记录导入成功！"
    except Exception as e:
        return False, f"导入失败：{str(e)}"

def import_student_json(uploaded_file):
    try:
        config = json.load(uploaded_file)
        if "街舞1班" not in config or "街舞2班" not in config:
            return False, "JSON格式错误！需包含街舞1班、街舞2班配置"
        save_student_config(config)
        return True, "学员信息导入成功！"
    except Exception as e:
        return False, f"导入失败：{str(e)}"

# 主逻辑执行
init_files()
config = get_student_config()

# ===================== 顶部导航栏（优化版） =====================
with st.container():
    # 使用更短的名称确保一行显示
    page = option_menu(
        menu_title=None,
        options=["首页", "考勤", "学员", "统计", "追踪", "记录", "备份"],
        icons=["house", "pencil", "people", "bar-chart", "search", "trash", "cloud"],
        menu_icon="cast",
        default_index=0,
        orientation="horizontal",
        styles={
            "container": {
                "padding": "0.4rem !important", 
                "background-color": "#1E1E1E",
                "border-radius": 10,
                "margin-bottom": "1rem",
                "border": "1px solid #333"
            },
            "icon": {
                "color": "#666", 
                "font-size": "14px",
                "margin-bottom": "2px"
            },
            "nav-link": {
                "font-size": "13px",
                "text-align": "center", 
                "margin": "0 2px", 
                "--hover-color": "#4169E1",
                "padding": "8px 10px",
                "border-radius": "6px",
                "color": "#999",
                "white-space": "nowrap"
            },
            "nav-link-selected": {
                "background-color": "#4169E1",
                "color": "white",
                "font-weight": "600",
                "font-size": "13px"
            },
        }
    )

# ------------------- 1. 首页 -------------------
if page == "首页":
    st.title("🎉 街舞考勤系统")
    
    # 功能卡片
    col1, col2 = st.columns(2)
    with col1:
        with st.container(border=True):
            st.markdown("""
            <div style="text-align: center; padding: 10px;">
                <div style="font-size: 28px; margin-bottom: 8px;">📝</div>
                <div style="font-weight: 600; color: #60A5FA; margin-bottom: 4px;">考勤录入</div>
                <div style="font-size: 13px; color: #888;">快速记录学员到课情况</div>
            </div>
            """, unsafe_allow_html=True)
            
        with st.container(border=True):
            st.markdown("""
            <div style="text-align: center; padding: 10px;">
                <div style="font-size: 28px; margin-bottom: 8px;">👥</div>
                <div style="font-weight: 600; color: #60A5FA; margin-bottom: 4px;">学员管理</div>
                <div style="font-size: 13px; color: #888;">添加、修改、删除学员</div>
            </div>
            """, unsafe_allow_html=True)
            
        with st.container(border=True):
            st.markdown("""
            <div style="text-align: center; padding: 10px;">
                <div style="font-size: 28px; margin-bottom: 8px;">📊</div>
                <div style="font-weight: 600; color: #60A5FA; margin-bottom: 4px;">月度统计</div>
                <div style="font-size: 13px; color: #888;">查看月度考勤报表</div>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        with st.container(border=True):
            st.markdown("""
            <div style="text-align: center; padding: 10px;">
                <div style="font-size: 28px; margin-bottom: 8px;">🔍</div>
                <div style="font-weight: 600; color: #60A5FA; margin-bottom: 4px;">学生追踪</div>
                <div style="font-size: 13px; color: #888;">查询个人考勤记录</div>
            </div>
            """, unsafe_allow_html=True)
            
        with st.container(border=True):
            st.markdown("""
            <div style="text-align: center; padding: 10px;">
                <div style="font-size: 28px; margin-bottom: 8px;">🗑️</div>
                <div style="font-weight: 600; color: #60A5FA; margin-bottom: 4px;">记录管理</div>
                <div style="font-size: 13px; color: #888;">删除错误考勤记录</div>
            </div>
            """, unsafe_allow_html=True)
            
        with st.container(border=True):
            st.markdown("""
            <div style="text-align: center; padding: 10px;">
                <div style="font-size: 28px; margin-bottom: 8px;">💾</div>
                <div style="font-weight: 600; color: #60A5FA; margin-bottom: 4px;">数据备份</div>
                <div style="font-size: 13px; color: #888;">导入导出数据文件</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.success("👆 请点击顶部导航选择功能")

# ------------------- 2. 考勤录入 -------------------
elif page == "考勤":
    st.title("📝 考勤录入")
    
    col1, col2 = st.columns(2)
    with col1:
        current_class = st.selectbox("选择班级", ["街舞1班", "街舞2班"], key="att_class")
    with col2:
        selected_date = st.date_input("选择日期", datetime.now(), key="att_date")
    
    date_str = selected_date.strftime("%Y-%m-%d")
    students = config[current_class]["students"]
    
    st.markdown(f"**{current_class}** 共 {len(students)} 人")
    st.markdown("---")
    
    # 学员列表 - 两列显示
    cols = st.columns(2)
    attended_students = []
    for idx, name in enumerate(students):
        with cols[idx % 2]:
            if st.checkbox(name, key=f"stu_{current_class}_{name}"):
                attended_students.append(name)

    st.markdown("---")
    st.info(f"✅ 已到课：{len(attended_students)} 人 | ❌ 缺课：{len(students)-len(attended_students)} 人")

    if st.button("💾 保存考勤记录", type="primary"):
        delete_batch_records(date_str, current_class)
        rows = [[date_str, current_class, s, "1" if s in attended_students else "0"] for s in students]
        with open(CSV_FILE, 'a', encoding='utf-8', newline='') as f:
            csv.writer(f).writerows(rows)
        st.success(f"✅ 保存成功！{current_class} {date_str} 到课 {len(attended_students)} 人")

# ------------------- 3. 学员管理 -------------------
elif page == "学员":
    st.title("👥 学员管理")
    
    # 自定义标签页样式
    tab1, tab2, tab3, tab4 = st.tabs(["➕ 新增", "✏️ 改名", "🔄 分班", "🗑️ 删除"])
    
    with tab1:
        st.markdown("### 添加新学员")
        col1, col2 = st.columns([3, 2])
        with col1:
            new_stu = st.text_input("学员姓名", key="add_stu", placeholder="请输入姓名")
        with col2:
            add_class = st.selectbox("所属班级", ["街舞1班", "街舞2班"], key="add_class")
        
        if st.button("➕ 添加学员", use_container_width=True):
            if new_stu.strip() and new_stu not in config[add_class]["students"]:
                config[add_class]["students"].append(new_stu)
                save_student_config(config)
                st.success(f"✅ 已添加「{new_stu}」到{add_class}")
                st.rerun()
            elif new_stu in config[add_class]["students"]:
                st.error(f"❌ {add_class} 已有学员「{new_stu}」")
    
    with tab2:
        st.markdown("### 修改学员姓名")
        edit_class = st.selectbox("选择班级", ["街舞1班", "街舞2班"], key="edit_class")
        col1, col2 = st.columns(2)
        with col1:
            old_name = st.text_input("原姓名", key="edit_old", placeholder="输入要修改的姓名")
        with col2:
            new_name = st.text_input("新姓名", key="edit_new", placeholder="输入新姓名")
        
        if st.button("✏️ 确认修改", use_container_width=True):
            if old_name in config[edit_class]["students"] and new_name.strip():
                idx = config[edit_class]["students"].index(old_name)
                config[edit_class]["students"][idx] = new_name
                save_student_config(config)
                st.success(f"✅ 已将「{old_name}」改为「{new_name}」")
                st.rerun()
            else:
                st.error("❌ 学员不存在或新姓名为空")
    
    with tab3:
        st.markdown("### 调整学员班级")
        move_stu = st.text_input("学员姓名", key="move_stu", placeholder="输入要调整的学员姓名")
        col1, col2 = st.columns(2)
        with col1:
            from_cls = st.selectbox("原班级", ["街舞1班", "街舞2班"], key="move_from")
        with col2:
            to_cls = st.selectbox("目标班级", ["街舞1班", "街舞2班"], key="move_to")
        
        if st.button("🔄 确认调整", use_container_width=True):
            if move_stu in config[from_cls]["students"] and from_cls != to_cls:
                config[from_cls]["students"].remove(move_stu)
                config[to_cls]["students"].append(move_stu)
                save_student_config(config)
                st.success(f"✅ 已将「{move_stu}」从{from_cls}调整到{to_cls}")
                st.rerun()
            elif from_cls == to_cls:
                st.error("❌ 原班级和目标班级不能相同")
            else:
                st.error(f"❌ {from_cls} 中没有找到学员「{move_stu}」")
    
    with tab4:
        st.markdown("### 删除学员")
        for cls in ["街舞1班", "街舞2班"]:
            with st.expander(f"📂 {cls}（当前{len(config[cls]['students'])}人）"):
                if config[cls]["students"]:
                    for name in config[cls]["students"]:
                        col_a, col_b = st.columns([5, 2])
                        with col_a:
                            st.write(f"👤 {name}")
                        with col_b:
                            if st.button("🗑️ 删除", key=f"del_{cls}_{name}"):
                                config[cls]["students"].remove(name)
                                save_student_config(config)
                                st.rerun()
                else:
                    st.info("该班级暂无学员")

# ------------------- 4. 月度统计 -------------------
elif page == "统计":
    st.title("📊 月度统计")
    
    col1, col2 = st.columns(2)
    with col1:
        year = st.text_input("年份", value=str(datetime.now().year), key="stat_year")
    with col2:
        month = st.text_input("月份", value=str(datetime.now().month), key="stat_month")
    
    if st.button("🔍 查询统计", type="primary", use_container_width=True):
        if year.isdigit() and month.isdigit():
            ym = f"{year}-{month.zfill(2)}"
            all_records = []
            if os.path.exists(CSV_FILE):
                with open(CSV_FILE, encoding='utf-8') as f:
                    all_records = [r for r in csv.DictReader(f) if r["日期"].startswith(ym)]
            
            ok_records = [r for r in all_records if r["是否到课"] == "1"]
            total = len(ok_records)
            
            # 大数字展示
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #1E3A2F 0%, #2D5A3D 100%); 
                        padding: 25px; border-radius: 15px; text-align: center; 
                        margin: 20px 0; border: 1px solid #4ADE80;">
                <div style="font-size: 14px; color: #4ADE80; margin-bottom: 10px;">{ym} 月度总到课</div>
                <div style="font-size: 48px; font-weight: bold; color: #4ADE80; margin-bottom: 5px;">{total}</div>
                <div style="font-size: 16px; color: #4ADE80;">人次</div>
                <div style="margin-top: 15px; padding-top: 15px; border-top: 1px solid #4ADE8055;">
                    <div style="font-size: 14px; color: #4ADE80AA;">课时费收入</div>
                    <div style="font-size: 32px; font-weight: bold; color: #FFD700;">¥{total*PRICE_PER_PERSON}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # 分班统计
            st.markdown("### 分班详情")
            cols = st.columns(2)
            for idx, cls in enumerate(["街舞1班", "街舞2班"]):
                cls_ok = [r for r in ok_records if r["班级"] == cls]
                with cols[idx]:
                    color = "#4169E1" if idx == 0 else "#32CD32"
                    st.markdown(f"""
                    <div style="background-color: #1E1E1E; padding: 20px; border-radius: 10px; 
                                text-align: center; border: 1px solid {color};">
                        <div style="font-size: 16px; color: {color}; font-weight: 600; margin-bottom: 10px;">{cls}</div>
                        <div style="font-size: 36px; font-weight: bold; color: white; margin-bottom: 5px;">{len(cls_ok)}</div>
                        <div style="font-size: 14px; color: #888; margin-bottom: 10px;">人次</div>
                        <div style="font-size: 20px; color: {color}; font-weight: 600;">¥{len(cls_ok)*PRICE_PER_PERSON}</div>
                    </div>
                    """, unsafe_allow_html=True)

# ------------------- 5. 学生追踪 -------------------
elif page == "追踪":
    st.title("🔍 学生考勤追踪")
    
    all_students = sorted({s for c in config.values() for s in c["students"]})
    selected_stu = st.selectbox("选择学生", all_students, key="track_stu")
    
    if st.button("🔍 查询记录", type="primary", use_container_width=True):
        records = []
        if os.path.exists(CSV_FILE):
            with open(CSV_FILE, encoding='utf-8') as f:
                records = [r for r in csv.DictReader(f) if r["学生姓名"] == selected_stu and r["是否到课"] == "1"]
        
        # 统计卡片
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #1E2A4A 0%, #2D3A5A 100%); 
                    padding: 25px; border-radius: 15px; text-align: center; 
                    margin: 20px 0; border: 1px solid #4169E1;">
            <div style="font-size: 16px; color: #888; margin-bottom: 10px;">{selected_stu} 累计到课</div>
            <div style="font-size: 56px; font-weight: bold; color: #4169E1;">{len(records)}</div>
            <div style="font-size: 16px; color: #888;">次</div>
        </div>
        """, unsafe_allow_html=True)
        
        if records:
            st.markdown("### 详细记录")
            for r in sorted(records, key=lambda x: x['日期'], reverse=True):
                with st.container(border=True):
                    col1, col2 = st.columns([2, 1])
                    with col1:
                        st.write(f"📅 {r['日期']}")
                    with col2:
                        st.write(f"📍 {r['班级']}")
        else:
            st.info("暂无考勤记录")

# ------------------- 6. 记录管理 -------------------
elif page == "记录":
    st.title("🗑️ 考勤记录管理")
    
    # 筛选条件
    col1, col2 = st.columns(2)
    with col1:
        date_filter = st.text_input("日期筛选（如：2026-03）", key="rec_date_filter")
    with col2:
        class_filter = st.selectbox("班级筛选", ["全部", "街舞1班", "街舞2班"], key="rec_class_filter", index=0)
    
    show_type = st.radio("显示类型", ["到课", "缺课", "全部"], index=0, horizontal=True, key="show_type")
    
    # 加载记录
    records = []
    if os.path.exists(CSV_FILE):
        with open(CSV_FILE, encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if date_filter and not row["日期"].startswith(date_filter):
                    continue
                if class_filter != "全部" and row["班级"] != class_filter:
                    continue
                if show_type == "到课" and row["是否到课"] != "1":
                    continue
                if show_type == "缺课" and row["是否到课"] != "0":
                    continue
                records.append(row)
    
    st.info(f"📋 共找到 {len(records)} 条记录")
    
    if records:
        for idx, r in enumerate(sorted(records, key=lambda x: x['日期'], reverse=True)):
            with st.container(border=True):
                col1, col2, col3, col4, col5 = st.columns([2.5, 2, 2, 1.5, 2])
                with col1: 
                    st.write(f"📅 {r['日期']}")
                with col2: 
                    st.write(f"📍 {r['班级']}")
                with col3: 
                    st.write(f"👤 {r['学生姓名']}")
                with col4: 
                    if r["是否到课"] == "1":
                        st.markdown("<span style='color: #4ADE80;'>🟢 到课</span>", unsafe_allow_html=True)
                    else:
                        st.markdown("<span style='color: #FF6B6B;'>🔴 缺课</span>", unsafe_allow_html=True)
                with col5:
                    if st.button("🗑️ 删除", key=f"del_rec_{idx}"):
                        delete_record(r["日期"], r["班级"], r["学生姓名"])
                        st.success("已删除")
                        st.rerun()
    else:
        st.info("暂无符合条件的考勤记录")

# ------------------- 7. 数据备份 -------------------
elif page == "备份":
    st.title("💾 数据备份与恢复")
    
    # 导出备份
    st.markdown("### 📤 导出数据")
    col1, col2 = st.columns(2)
    with col1:
        if os.path.exists(CSV_FILE):
            with open(CSV_FILE, "rb") as f:
                st.download_button(
                    label="📄 下载考勤记录 (CSV)",
                    data=f,
                    file_name=f"街舞考勤记录_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
        else:
            st.warning("暂无考勤记录")
    
    with col2:
        if os.path.exists(STUDENT_CONFIG_FILE):
            with open(STUDENT_CONFIG_FILE, "rb") as f:
                st.download_button(
                    label="👥 下载学员信息 (JSON)",
                    data=f,
                    file_name=f"街舞学员信息_{datetime.now().strftime('%Y%m%d')}.json",
                    mime="application/json",
                    use_container_width=True
                )
        else:
            st.warning("暂无学员信息")
    
    st.markdown("---")
    
    # 导入恢复
    st.markdown("### 📥 导入数据")
    st.warning("⚠️ 警告：导入会覆盖现有数据，请先备份！")
    
    csv_file = st.file_uploader("上传考勤记录 CSV 文件", type=["csv"], key="import_csv")
    if st.button("📥 导入考勤记录", use_container_width=True):
        if csv_file:
            success, msg = import_attendance_csv(csv_file)
            if success:
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)
    
    json_file = st.file_uploader("上传学员信息 JSON 文件", type=["json"], key="import_json")
    if st.button("📥 导入学员信息", use_container_width=True):
        if json_file:
            success, msg = import_student_json(json_file)
            if success:
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)
