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
            if password == "123456":  # 可自行修改密码
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("密码错误，请重试")
        st.stop()

check_access()

# 页面样式配置（手机友好）- 注意：set_page_config必须是第一个st命令
st.set_page_config(
    page_title="街舞考勤",
    page_icon="💃",
    layout="centered",
    initial_sidebar_state="collapsed"  # 侧边栏默认收起
)

# 全局样式优化 - 增大字体和优化间距
st.markdown("""
<style>
/* 基础字体大小调整 */
html, body, [class*="css"] {
    font-size: 16px !important;
}

/* 标题字体 */
h1 {
    font-size: 28px !important;
    font-weight: 700 !important;
    margin-bottom: 1rem !important;
}

h2 {
    font-size: 22px !important;
    font-weight: 600 !important;
}

h3 {
    font-size: 18px !important;
    font-weight: 600 !important;
}

/* 页面容器边距 */
div.block-container { 
    padding-top: 0.5rem; 
    padding-bottom: 2rem;
    max-width: 100%;
}

/* 按钮全宽和字体 */
div.stButton > button { 
    width: 100%; 
    font-size: 16px !important;
    padding: 0.6rem 1rem !important;
    border-radius: 8px !important;
}

/* 输入框字体 */
.stSelectbox, .stTextInput, .stDateInput {
    font-size: 16px !important;
    margin-bottom: 12px;
}

/* 选项菜单导航栏样式修复 */
nav[data-testid="stSidebarNav"] {
    font-size: 14px !important;
}

/* 卡片式信息框字体 */
.stInfo, .stSuccess, .stWarning, .stError {
    font-size: 15px !important;
    padding: 1rem !important;
}

/* 复选框标签字体 */
.stCheckbox label {
    font-size: 16px !important;
}

/* 表格和列表字体 */
.stDataFrame, .stTable {
    font-size: 14px !important;
}

/* 标签页字体 */
button[data-baseweb="tab"] {
    font-size: 15px !important;
    padding: 0.5rem 1rem !important;
}

/* 移动端优化 */
@media (max-width: 768px) {
    h1 { font-size: 24px !important; }
    h2 { font-size: 20px !important; }
    html, body, [class*="css"] { font-size: 15px !important; }
}
</style>
""", unsafe_allow_html=True)

# 基础文件配置
CSV_FILE = "dance_student_records.csv"
STUDENT_CONFIG_FILE = "dance_students.json"
PRICE_PER_PERSON = 80  # 单人次课时费

# 初始化数据文件
def init_files():
    # 初始化考勤CSV
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
            csv.writer(f).writerow(["日期", "班级", "学生姓名", "是否到课"])
    # 初始化学员配置JSON
    if not os.path.exists(STUDENT_CONFIG_FILE):
        default_config = {
            "街舞1班": {"students": ["小明", "小红", "小刚", "小丽", "小亮"], "color": "#4169E1"},
            "街舞2班": {"students": ["小美", "小杰", "小宇", "小诺", "小泽", "小琳"], "color": "#32CD32"}
        }
        with open(STUDENT_CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, ensure_ascii=False, indent=2)

# 获取/保存学员配置
def get_student_config():
    init_files()
    with open(STUDENT_CONFIG_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_student_config(config):
    with open(STUDENT_CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

# 删除单条考勤记录
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

# 批量删除指定日期+班级的考勤记录（解决重复保存问题）
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

# 数据导入功能
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

# ===================== 顶部导航栏（字体修复） =====================
with st.container():
    page = option_menu(
        menu_title=None,
        options=["首页", "考勤录入", "学员管理", "月度统计", "学生追踪", "记录管理", "数据备份恢复"],
        icons=["house", "pencil-square", "people", "bar-chart", "search", "trash", "cloud"],
        menu_icon="cast",
        default_index=0,
        orientation="horizontal",
        styles={
            "container": {
                "padding": "0.5rem!important", 
                "background-color": "#1E1E1E",
                "border-radius": "8px",
                "margin-bottom": "1rem"
            },
            "icon": {
                "color": "white", 
                "font-size": "18px",
                "margin-bottom": "4px"
            },
            "nav-link": {
                "font-size": "14px",  # 从10px改为14px，移动端可读
                "text-align": "center", 
                "margin": "0px 2px", 
                "--hover-color": "#4169E1",
                "padding": "8px 4px",
                "border-radius": "6px",
                "color": "#CCCCCC"
            },
            "nav-link-selected": {
                "background-color": "#4169E1",
                "color": "white",
                "font-weight": "600",
                "font-size": "14px"
            },
        }
    )

# ------------------- 1. 首页 -------------------
if page == "首页":
    st.title("🎉 街舞考勤系统")
    st.divider()
    st.markdown("### 功能说明")
    
    # 使用更大的卡片式布局
    col1, col2 = st.columns(2)
    with col1:
        with st.container(border=True):
            st.markdown("""
            📝 **考勤录入**  
            👥 **学员管理**  
            📊 **月度统计**
            """)
    with col2:
        with st.container(border=True):
            st.markdown("""
            🔍 **学生追踪**  
            🗑️ **记录管理**  
            💾 **备份恢复**
            """)
    
    st.divider()
    st.success("👆 请从顶部导航选择功能开始操作")

# ------------------- 2. 考勤录入 -------------------
elif page == "考勤录入":
    st.title("📝 考勤录入")
    
    # 使用两列布局让选择器更紧凑
    col1, col2 = st.columns(2)
    with col1:
        current_class = st.selectbox("选择班级", ["街舞1班", "街舞2班"], key="att_class")
    with col2:
        selected_date = st.date_input("选择日期", datetime.now(), key="att_date")
    
    date_str = selected_date.strftime("%Y-%m-%d")
    students = config[current_class]["students"]
    
    st.markdown(f"#### {current_class} 学员列表（{len(students)}人）")
    
    # 学员勾选（两列排版，手机友好）
    cols = st.columns(2)
    attended_students = []
    for idx, name in enumerate(students):
        with cols[idx % 2]:
            if st.checkbox(name, key=f"stu_{current_class}_{name}"):
                attended_students.append(name)

    # 统计信息
    st.info(f"已选择：{len(attended_students)}/{len(students)} 人")

    # 保存考勤
    if st.button("✅ 保存考勤记录", type="primary"):
        # 第一步：删除当天该班级的旧记录
        delete_batch_records(date_str, current_class)
        # 第二步：写入新的考勤记录
        rows = [[date_str, current_class, s, "1" if s in attended_students else "0"] for s in students]
        with open(CSV_FILE, 'a', encoding='utf-8', newline='') as f:
            csv.writer(f).writerows(rows)
        st.success(f"✅ 保存成功！{current_class} 到课 {len(attended_students)} 人，缺课 {len(students)-len(attended_students)} 人")

# ------------------- 3. 学员管理 -------------------
elif page == "学员管理":
    st.title("👥 学员管理")
    tab1, tab2, tab3, tab4 = st.tabs(["➕ 新增", "✏️ 改名", "🔄 分班", "🗑️ 删除"])
    
    with tab1:
        st.markdown("#### 添加新学员")
        col1, col2 = st.columns([2, 1])
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
        st.markdown("#### 修改学员姓名")
        edit_class = st.selectbox("选择班级", ["街舞1班", "街舞2班"], key="edit_class")
        col1, col2 = st.columns(2)
        with col1:
            old_name = st.text_input("原姓名", key="edit_old")
        with col2:
            new_name = st.text_input("新姓名", key="edit_new")
        if st.button("✏️ 修改姓名", use_container_width=True):
            if old_name in config[edit_class]["students"] and new_name.strip():
                idx = config[edit_class]["students"].index(old_name)
                config[edit_class]["students"][idx] = new_name
                save_student_config(config)
                st.success(f"✅ 已将「{old_name}」改为「{new_name}」")
                st.rerun()
    
    with tab3:
        st.markdown("#### 调整学员班级")
        move_stu = st.text_input("学员姓名", key="move_stu")
        col1, col2 = st.columns(2)
        with col1:
            from_cls = st.selectbox("原班级", ["街舞1班", "街舞2班"], key="move_from")
        with col2:
            to_cls = st.selectbox("目标班级", ["街舞1班", "街舞2班"], key="move_to")
        if st.button("🔄 调整分班", use_container_width=True):
            if move_stu in config[from_cls]["students"] and from_cls != to_cls:
                config[from_cls]["students"].remove(move_stu)
                config[to_cls]["students"].append(move_stu)
                save_student_config(config)
                st.success(f"✅ 已将「{move_stu}」从{from_cls}调整到{to_cls}")
                st.rerun()
            else:
                st.error("❌ 学员不存在或班级选择错误")
    
    with tab4:
        st.markdown("#### 删除学员")
        for cls in ["街舞1班", "街舞2班"]:
            with st.expander(f"📂 {cls}（{len(config[cls]['students'])}人）"):
                for name in config[cls]["students"]:
                    col_a, col_b = st.columns([4, 1])
                    with col_a:
                        st.write(f"👤 {name}")
                    with col_b:
                        if st.button("🗑️ 删除", key=f"del_{cls}_{name}"):
                            config[cls]["students"].remove(name)
                            save_student_config(config)
                            st.rerun()

# ------------------- 4. 月度统计 -------------------
elif page == "月度统计":
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
            
            # 统计到课记录
            ok_records = [r for r in all_records if r["是否到课"] == "1"]
            total = len(ok_records)
            
            # 使用大字体显示总收入
            st.markdown(f"""
            <div style="background-color:#0E1117; padding:20px; border-radius:10px; text-align:center; margin:20px 0;">
                <div style="font-size:16px; color:#888;">本月总到课</div>
                <div style="font-size:36px; font-weight:bold; color:#00CC00;">{total} 人次</div>
                <div style="font-size:14px; color:#888; margin-top:10px;">总收入</div>
                <div style="font-size:28px; font-weight:bold; color:#FFD700;">¥{total*PRICE_PER_PERSON}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # 分班级统计
            st.markdown("#### 分班统计")
            cols = st.columns(2)
            for idx, cls in enumerate(["街舞1班", "街舞2班"]):
                cls_ok = [r for r in ok_records if r["班级"] == cls]
                with cols[idx]:
                    with st.container(border=True):
                        st.markdown(f"**{cls}**")
                        st.markdown(f"<div style='font-size:24px; font-weight:bold;'>{len(cls_ok)} 人次</div>", unsafe_allow_html=True)
                        st.markdown(f"<div style='color:#888;'>¥{len(cls_ok)*PRICE_PER_PERSON}</div>", unsafe_allow_html=True)

# ------------------- 5. 学生追踪 -------------------
elif page == "学生追踪":
    st.title("🔍 学生考勤追踪")
    all_students = sorted({s for c in config.values() for s in c["students"]})
    selected_stu = st.selectbox("选择学生", all_students, key="track_stu")
    
    if st.button("🔍 查询考勤记录", type="primary", use_container_width=True):
        records = []
        if os.path.exists(CSV_FILE):
            with open(CSV_FILE, encoding='utf-8') as f:
                records = [r for r in csv.DictReader(f) if r["学生姓名"] == selected_stu and r["是否到课"] == "1"]
        
        # 统计卡片
        st.markdown(f"""
        <div style="background-color:#0E1117; padding:15px; border-radius:8px; text-align:center; margin:15px 0;">
            <div style="font-size:14px; color:#888;">{selected_stu} 累计到课</div>
            <div style="font-size:32px; font-weight:bold; color:#4169E1;">{len(records)} 次</div>
        </div>
        """, unsafe_allow_html=True)
        
        if records:
            st.markdown("#### 详细记录")
            for r in records:
                st.write(f"📅 {r['日期']} | 📍 {r['班级']}")
        else:
            st.info("暂无考勤记录")

# ------------------- 6. 记录管理 -------------------
elif page == "记录管理":
    st.title("🗑️ 考勤记录管理")
    
    # 筛选条件
    col1, col2 = st.columns(2)
    with col1:
        date_filter = st.text_input("日期筛选（如：2026-03）", key="rec_date_filter")
    with col2:
        class_filter = st.selectbox("班级筛选", ["全部", "街舞1班", "街舞2班"], key="rec_class_filter", index=0)
    
    show_type = st.radio("显示类型", ["到课", "缺课", "全部"], index=0, horizontal=True, key="show_type")
    
    # 加载并筛选记录
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
    
    # 显示统计
    st.info(f"共找到 {len(records)} 条记录")
    
    # 显示记录并提供删除按钮
    if records:
        for idx, r in enumerate(records):
            with st.container(border=True):
                col1, col2, col3, col4, col5 = st.columns([3, 2.5, 2, 2, 2])
                with col1: 
                    st.write(f"📅 {r['日期']}")
                with col2: 
                    st.write(f"📍 {r['班级']}")
                with col3: 
                    st.write(f"👤 {r['学生姓名']}")
                with col4: 
                    status_color = "🟢" if r["是否到课"] == "1" else "🔴"
                    st.write(f"{status_color} {'到课' if r['是否到课'] == '1' else '缺课'}")
                with col5:
                    if st.button("🗑️ 删除", key=f"del_rec_{idx}"):
                        delete_record(r["日期"], r["班级"], r["学生姓名"])
                        st.success(f"已删除记录")
                        st.rerun()
    else:
        st.info("暂无符合条件的考勤记录")

# ------------------- 7. 数据备份恢复 -------------------
elif page == "数据备份恢复":
    st.title("💾 数据备份与恢复")
    st.divider()
    
    # 导出备份
    st.markdown("### 📤 导出数据（备份到本地）")
    col1, col2 = st.columns(2)
    with col1:
        if os.path.exists(CSV_FILE):
            with open(CSV_FILE, "rb") as f:
                st.download_button(
                    label="📄 考勤记录 (CSV)",
                    data=f,
                    file_name=f"街舞考勤记录_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
        else:
            st.warning("暂无考勤记录可导出")
    
    with col2:
        if os.path.exists(STUDENT_CONFIG_FILE):
            with open(STUDENT_CONFIG_FILE, "rb") as f:
                st.download_button(
                    label="👥 学员信息 (JSON)",
                    data=f,
                    file_name=f"街舞学员信息_{datetime.now().strftime('%Y%m%d')}.json",
                    mime="application/json",
                    use_container_width=True
                )
        else:
            st.warning("暂无学员信息可导出")
    
    st.divider()
    
    # 导入恢复
    st.markdown("### 📥 导入数据（从本地恢复）")
    st.warning("⚠️ 导入会覆盖当前服务器数据，请先备份！")
    
    # 导入考勤CSV
    csv_file = st.file_uploader("上传考勤记录CSV", type=["csv"], key="import_csv")
    if st.button("📥 导入考勤记录", use_container_width=True):
        if csv_file:
            success, msg = import_attendance_csv(csv_file)
            if success:
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)
    
    # 导入学员JSON
    json_file = st.file_uploader("上传学员信息JSON", type=["json"], key="import_json")
    if st.button("📥 导入学员信息", use_container_width=True):
        if json_file:
            success, msg = import_student_json(json_file)
            if success:
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)
