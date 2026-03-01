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

# 页面样式配置（手机友好）
st.set_page_config(
    page_title="街舞考勤",
    page_icon="💃",
    layout="centered",
    initial_sidebar_state="collapsed"  # 侧边栏默认收起
)

# 全局样式优化
st.markdown("""
<style>
div.block-container { padding-top:1rem; padding-bottom:2rem; }
div.stButton > button { width:100%; }
.stSelectbox, .stTextInput { margin-bottom:10px; }
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

# ===================== 顶部导航栏（核心修复） =====================
with st.container():
    page = option_menu(
        menu_title=None,
        options=["首页", "考勤录入", "学员管理", "月度统计", "学生追踪", "记录管理", "数据备份恢复"],
        icons=["house", "pencil-square", "people", "bar-chart", "search", "trash", "cloud"],
        menu_icon="cast",
        default_index=0,
        orientation="horizontal",
        styles={
            "container": {"padding": "0!important", "background-color": "#262730"},
            "icon": {"color": "white", "font-size": "16px"},
            "nav-link": {"font-size": "10px", "text-align": "center", "margin": "0px", "--hover-color": "#4169E1"},
            "nav-link-selected": {"background-color": "#4169E1"},
        }
    )

# ------------------- 1. 首页 -------------------
if page == "首页":
    st.title("🎉 街舞考勤系统")
    st.divider()
    st.markdown("#### 功能说明")
    col1, col2 = st.columns(2)
    with col1:
        st.info("📝 考勤录入\n👥 学员管理\n📊 月度统计")
    with col2:
        st.info("🔍 学生追踪\n🗑️ 记录管理\n💾 备份恢复")
    st.divider()
    st.success("请从顶部导航选择功能开始操作 ✅")

# ------------------- 2. 考勤录入（修复重复保存问题） -------------------
elif page == "考勤录入":
    st.title("📝 考勤录入")
    current_class = st.selectbox("选择班级", ["街舞1班", "街舞2班"], key="att_class")
    students = config[current_class]["students"]
    
    # 日期选择
    selected_date = st.date_input("选择日期", datetime.now(), key="att_date")
    date_str = selected_date.strftime("%Y-%m-%d")

    # 学员勾选（两列排版，手机友好）
    st.subheader(f"{current_class} 学员列表")
    cols = st.columns(2)
    attended_students = []
    for idx, name in enumerate(students):
        with cols[idx % 2]:
            if st.checkbox(name, key=f"stu_{current_class}_{name}"):
                attended_students.append(name)

    # 保存考勤（先删旧记录，再存新记录，避免重复）
    if st.button("✅ 保存考勤记录", type="primary"):
        # 第一步：删除当天该班级的旧记录
        delete_batch_records(date_str, current_class)
        # 第二步：写入新的考勤记录
        rows = [[date_str, current_class, s, "1" if s in attended_students else "0"] for s in students]
        with open(CSV_FILE, 'a', encoding='utf-8', newline='') as f:
            csv.writer(f).writerows(rows)
        st.success(f"保存成功｜{current_class} 到课 {len(attended_students)} 人")

# ------------------- 3. 学员管理 -------------------
elif page == "学员管理":
    st.title("👥 学员管理")
    tab1, tab2, tab3, tab4 = st.tabs(["新增", "改名", "分班", "删除"])
    
    with tab1:
        new_stu = st.text_input("学员姓名", key="add_stu")
        add_class = st.selectbox("所属班级", ["街舞1班", "街舞2班"], key="add_class")
        if st.button("添加学员"):
            if new_stu.strip() and new_stu not in config[add_class]["students"]:
                config[add_class]["students"].append(new_stu)
                save_student_config(config)
                st.success(f"✅ 已添加「{new_stu}」到{add_class}")
                st.rerun()
            elif new_stu in config[add_class]["students"]:
                st.error(f"❌ {add_class} 已有学员「{new_stu}」")
    
    with tab2:
        edit_class = st.selectbox("选择班级", ["街舞1班", "街舞2班"], key="edit_class")
        old_name = st.text_input("原姓名", key="edit_old")
        new_name = st.text_input("新姓名", key="edit_new")
        if st.button("修改姓名"):
            if old_name in config[edit_class]["students"] and new_name.strip():
                idx = config[edit_class]["students"].index(old_name)
                config[edit_class]["students"][idx] = new_name
                save_student_config(config)
                st.success(f"✅ 已将「{old_name}」改为「{new_name}」")
                st.rerun()
    
    with tab3:
        move_stu = st.text_input("学员姓名", key="move_stu")
        from_cls = st.selectbox("原班级", ["街舞1班", "街舞2班"], key="move_from")
        to_cls = st.selectbox("目标班级", ["街舞1班", "街舞2班"], key="move_to")
        if st.button("调整分班"):
            if move_stu in config[from_cls]["students"] and from_cls != to_cls:
                config[from_cls]["students"].remove(move_stu)
                config[to_cls]["students"].append(move_stu)
                save_student_config(config)
                st.success(f"✅ 已将「{move_stu}」从{from_cls}调整到{to_cls}")
                st.rerun()
    
    with tab4:
        for cls in ["街舞1班", "街舞2班"]:
            st.markdown(f"**{cls}**")
            for name in config[cls]["students"]:
                col_a, col_b = st.columns([4,1])
                with col_a:
                    st.write(name)
                with col_b:
                    if st.button("删", key=f"del_{cls}_{name}"):
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
    
    if st.button("查询统计", type="primary"):
        if year.isdigit() and month.isdigit():
            ym = f"{year}-{month.zfill(2)}"
            all_records = []
            if os.path.exists(CSV_FILE):
                with open(CSV_FILE, encoding='utf-8') as f:
                    all_records = [r for r in csv.DictReader(f) if r["日期"].startswith(ym)]
            
            # 统计到课记录
            ok_records = [r for r in all_records if r["是否到课"] == "1"]
            total = len(ok_records)
            st.success(f"📈 本月总到课：{total} 人次｜总收入：{total*PRICE_PER_PERSON} 元")
            
            # 分班级统计
            for cls in ["街舞1班", "街舞2班"]:
                cls_ok = [r for r in ok_records if r["班级"] == cls]
                st.write(f"**{cls}**：{len(cls_ok)} 人次｜{len(cls_ok)*PRICE_PER_PERSON} 元")

# ------------------- 5. 学生追踪 -------------------
elif page == "学生追踪":
    st.title("🔍 学生考勤追踪")
    all_students = sorted({s for c in config.values() for s in c["students"]})
    selected_stu = st.selectbox("选择学生", all_students, key="track_stu")
    
    if st.button("查询", type="primary"):
        records = []
        if os.path.exists(CSV_FILE):
            with open(CSV_FILE, encoding='utf-8') as f:
                records = [r for r in csv.DictReader(f) if r["学生姓名"] == selected_stu and r["是否到课"] == "1"]
        
        st.success(f"{selected_stu} 累计到课 {len(records)} 次")
        for r in records:
            st.write(f"- {r['日期']} | {r['班级']}")

# ------------------- 6. 记录管理（优化：默认只显示到课记录） -------------------
elif page == "记录管理":
    st.title("🗑️ 考勤记录管理")
    # 筛选条件（加唯一key，避免控件冲突）
    date_filter = st.text_input("日期筛选（格式：2026-03）", key="rec_date_filter")
    class_filter = st.selectbox("班级筛选", ["", "街舞1班", "街舞2班"], key="rec_class_filter")
    # 新增：显示类型筛选，默认只看「到课」
    show_type = st.radio("显示类型", ["到课", "缺课", "全部"], index=0, horizontal=True, key="show_type")
    
    # 加载并筛选记录
    records = []
    if os.path.exists(CSV_FILE):
        with open(CSV_FILE, encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # 日期筛选
                if date_filter and not row["日期"].startswith(date_filter):
                    continue
                # 班级筛选
                if class_filter and row["班级"] != class_filter:
                    continue
                # 显示类型筛选（核心优化）
                if show_type == "到课" and row["是否到课"] != "1":
                    continue
                if show_type == "缺课" and row["是否到课"] != "0":
                    continue
                # 全部则不额外过滤
                records.append(row)
    
    # 显示记录并提供删除按钮
    if records:
        for idx, r in enumerate(records):
            col1, col2, col3, col4, col5 = st.columns([3,2,2,2,2])
            with col1: st.write(r["日期"])
            with col2: st.write(r["班级"])
            with col3: st.write(r["学生姓名"])
            with col4: st.write("✅ 到课" if r["是否到课"] == "1" else "❌ 缺课")
            with col5:
                if st.button("删除", key=f"del_rec_{idx}"):
                    delete_record(r["日期"], r["班级"], r["学生姓名"])
                    st.success(f"已删除 {r['日期']} {r['班级']} {r['学生姓名']} 的记录")
                    st.rerun()
    else:
        st.info("暂无符合条件的考勤记录")

# ------------------- 7. 数据备份恢复 -------------------
elif page == "数据备份恢复":
    st.title("💾 数据备份与恢复")
    st.divider()
    
    # 导出备份
    st.subheader("📤 导出数据（备份到本地）")
    col1, col2 = st.columns(2)
    with col1:
        if os.path.exists(CSV_FILE):
            with open(CSV_FILE, "rb") as f:
                st.download_button(
                    label="考勤记录 (CSV)",
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
                    label="学员信息 (JSON)",
                    data=f,
                    file_name=f"街舞学员信息_{datetime.now().strftime('%Y%m%d')}.json",
                    mime="application/json",
                    use_container_width=True
                )
        else:
            st.warning("暂无学员信息可导出")
    
    st.divider()
    
    # 导入恢复
    st.subheader("📥 导入数据（从本地恢复）")
    st.warning("⚠️ 导入会覆盖当前服务器数据，请先备份！")
    
    # 导入考勤CSV
    csv_file = st.file_uploader("上传考勤记录CSV", type=["csv"], key="import_csv")
    if st.button("导入考勤记录", use_container_width=True):
        if csv_file:
            success, msg = import_attendance_csv(csv_file)
            if success:
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)
    
    # 导入学员JSON
    json_file = st.file_uploader("上传学员信息JSON", type=["json"], key="import_json")
    if st.button("导入学员信息", use_container_width=True):
        if json_file:
            success, msg = import_student_json(json_file)
            if success:
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)