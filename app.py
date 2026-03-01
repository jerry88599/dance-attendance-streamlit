import streamlit as st
import csv
import os
from datetime import datetime
import json

# 访问密码验证（改成你自己的密码）
def check_access():
    # 初始化密码状态
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    
    # 未验证时显示密码输入框
    if not st.session_state.authenticated:
        st.title("🔒 请验证访问权限")
        password = st.text_input("输入访问密码", type="password")
        if st.button("验证"):
            # 改成你自己的密码（比如你的手机号后6位）
            if password == "123456":  
                st.session_state.authenticated = True
                st.rerun()  # 验证通过后刷新页面
            else:
                st.error("密码错误，请重试")
        st.stop()  # 未验证通过则停止执行后续代码

# 执行密码验证
check_access()

# 页面配置（手机适配）
st.set_page_config(
    page_title="街舞考勤系统",
    page_icon="💃",
    layout="centered",  # 移动端优先
    initial_sidebar_state="collapsed"
)

# 初始化会话状态
if "selected_page" not in st.session_state:
    st.session_state["selected_page"] = "首页"
if "default_class" not in st.session_state:
    st.session_state["default_class"] = "街舞1班"

# 基础配置
CSV_FILE = "dance_student_records.csv"
STUDENT_CONFIG_FILE = "dance_students.json"
PRICE_PER_PERSON = 80  # 固定课时费

# 初始化文件
def init_files():
    # 初始化考勤CSV
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["日期", "班级", "学生姓名", "是否到课"])
    
    # 初始化学员配置JSON
    if not os.path.exists(STUDENT_CONFIG_FILE):
        default_config = {
            "街舞1班": {
                "students": ["小明", "小红", "小刚", "小丽", "小亮"],
                "color": "#007bff"
            },
            "街舞2班": {
                "students": ["小美", "小杰", "小宇", "小诺", "小泽", "小琳"],
                "color": "#28a745"
            }
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

# 删除考勤记录
def delete_record(date, class_name, student):
    records = []
    with open(CSV_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if not (row["日期"] == date and row["班级"] == class_name and row["学生姓名"] == student):
                records.append(row)
    
    with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=["日期", "班级", "学生姓名", "是否到课"])
        writer.writeheader()
        writer.writerows(records)

# ---------------------- 主页面逻辑 ----------------------
init_files()
config = get_student_config()

# 侧边栏导航（移动端自动折叠）
st.sidebar.title("💃 街舞考勤系统")
page = st.sidebar.radio(
    "选择功能",
    ["首页", "考勤录入", "学员管理", "月度统计", "学生追踪", "记录管理"],
    index=["首页", "考勤录入", "学员管理", "月度统计", "学生追踪", "记录管理"].index(st.session_state["selected_page"])
)

# 1. 首页（有效按钮版）
if page == "首页":
    st.title("选择班级")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("街舞1班", type="primary", use_container_width=True):
            st.session_state["default_class"] = "街舞1班"
            st.session_state["selected_page"] = "考勤录入"
            st.rerun()
    with col2:
        if st.button("街舞2班", type="primary", use_container_width=True):
            st.session_state["default_class"] = "街舞2班"
            st.session_state["selected_page"] = "考勤录入"
            st.rerun()

# 2. 考勤录入（自动选班版）
elif page == "考勤录入":
    st.title("考勤录入")
    # 优先使用按钮选中的班级，否则默认选街舞1班
    current_class = st.selectbox(
        "选择班级",
        ["街舞1班", "街舞2班"],
        index=["街舞1班", "街舞2班"].index(st.session_state["default_class"])
    )
    students = config[current_class]["students"]
    
    # 日期选择
    selected_date = st.date_input("选择日期", datetime.now(), key="att_date")
    selected_date_str = selected_date.strftime("%Y-%m-%d")
    
    # 学员勾选
    st.subheader(f"{current_class} 学员列表")
    attended_students = []
    for student in students:
        if st.checkbox(student, key=f"stu_{student}"):
            attended_students.append(student)
    
    # 保存考勤
    if st.button("保存考勤记录", type="primary", use_container_width=True):
        records = []
        for s in students:
            records.append([selected_date_str, current_class, s, "1" if s in attended_students else "0"])
        with open(CSV_FILE, 'a', encoding='utf-8', newline='') as f:
            csv.writer(f).writerows(records)
        st.success(f"✅ {selected_date_str} {current_class} 到课 {len(attended_students)} 人")

# 3. 学员管理
elif page == "学员管理":
    st.title("学员管理")
    
    # 新增学员
    st.subheader("新增学员")
    new_student = st.text_input("学员姓名", key="new_stu")
    add_class = st.selectbox("所属班级", ["街舞1班", "街舞2班"], key="add_class")
    if st.button("添加学员", key="add_btn"):
        if new_student.strip():
            if new_student not in config[add_class]["students"]:
                config[add_class]["students"].append(new_student)
                save_student_config(config)
                st.success(f"✅ 已添加「{new_student}」到{add_class}")
                st.rerun()  # 刷新页面
            else:
                st.error(f"❌ {add_class} 已有学员「{new_student}」")
        else:
            st.error("❌ 请输入学员姓名")
    
    # 修改姓名
    st.subheader("修改学员姓名")
    edit_class = st.selectbox("选择班级", ["街舞1班", "街舞2班"], key="edit_class")
    old_name = st.text_input("原姓名", key="old_name")
    new_name = st.text_input("新姓名", key="new_name")
    if st.button("修改姓名", key="edit_btn"):
        if old_name and new_name:
            if old_name in config[edit_class]["students"]:
                if new_name not in config[edit_class]["students"]:
                    idx = config[edit_class]["students"].index(old_name)
                    config[edit_class]["students"][idx] = new_name
                    save_student_config(config)
                    st.success(f"✅ 已将「{old_name}」修改为「{new_name}」")
                    st.rerun()
                else:
                    st.error(f"❌ {edit_class} 已有「{new_name}」")
            else:
                st.error(f"❌ {edit_class} 无学员「{old_name}」")
    
    # 调整分班
    st.subheader("调整学员分班")
    move_stu = st.text_input("学员姓名", key="move_stu")
    from_class = st.selectbox("原班级", ["街舞1班", "街舞2班"], key="from_class")
    to_class = st.selectbox("新班级", ["街舞1班", "街舞2班"], key="to_class")
    if st.button("调整分班", key="move_btn"):
        if move_stu and from_class != to_class:
            if move_stu in config[from_class]["students"]:
                config[from_class]["students"].remove(move_stu)
                if move_stu not in config[to_class]["students"]:
                    config[to_class]["students"].append(move_stu)
                    save_student_config(config)
                    st.success(f"✅ 已将「{move_stu}」从{from_class}调整到{to_class}")
                    st.rerun()
                else:
                    st.error(f"❌ {to_class} 已有「{move_stu}」")
            else:
                st.error(f"❌ {from_class} 无学员「{move_stu}」")
    
    # 学员列表 & 删除
    st.subheader("学员列表（点击删除）")
    for cls in ["街舞1班", "街舞2班"]:
        st.write(f"### {cls}")
        for stu in config[cls]["students"]:
            col1, col2 = st.columns([4, 1])
            with col1:
                st.write(stu)
            with col2:
                if st.button("删除", key=f"del_{cls}_{stu}"):
                    config[cls]["students"].remove(stu)
                    save_student_config(config)
                    st.success(f"✅ 已删除{cls}的「{stu}」")
                    st.rerun()

# 4. 月度统计
elif page == "月度统计":
    st.title("月度统计")
    col1, col2 = st.columns(2)
    with col1:
        year = st.text_input("年份", str(datetime.now().year), key="stat_year")
    with col2:
        month = st.text_input("月份", str(datetime.now().month), key="stat_month")
    
    if st.button("查询统计", type="primary", use_container_width=True):
        if year.isdigit() and month.isdigit():
            ym = f"{year}-{month.zfill(2)}"
            if os.path.exists(CSV_FILE):
                records = []
                with open(CSV_FILE, encoding='utf-8') as f:
                    for r in csv.DictReader(f):
                        if r['日期'].startswith(ym):
                            records.append(r)
                if records:
                    total = 0
                    for cls in ["街舞1班", "街舞2班"]:
                        cls_records = [x for x in records if x['班级']==cls and x['是否到课']=='1']
                        cls_count = len(cls_records)
                        total += cls_count
                        st.subheader(f"{cls}（{cls_count}人次 | {cls_count*PRICE_PER_PERSON}元）")
                        # 学员明细
                        stu_stats = {}
                        for s in config[cls]["students"]:
                            stu_stats[s] = len([x for x in cls_records if x['学生姓名']==s])
                        for s, cnt in stu_stats.items():
                            st.write(f"{s}：{cnt}次")
                    st.success(f"### 总计：{total}人次 | {total*PRICE_PER_PERSON}元")
                else:
                    st.warning(f"❌ {ym} 暂无考勤记录")
            else:
                st.error("❌ 暂无任何考勤记录")
        else:
            st.error("❌ 请输入有效的年份/月份")

# 5. 学生追踪
elif page == "学生追踪":
    st.title("学生考勤追踪")
    all_students = sorted({s for c in config.values() for s in c['students']})
    selected_stu = st.selectbox("选择学生", all_students, key="track_stu")
    
    if st.button("查询", type="primary", use_container_width=True):
        if os.path.exists(CSV_FILE):
            records = []
            with open(CSV_FILE, encoding='utf-8') as f:
                for r in csv.DictReader(f):
                    if r['学生姓名']==selected_stu and r['是否到课']=='1':
                        records.append(r)
            if records:
                records.sort(key=lambda x:x['日期'])
                st.success(f"✅ {selected_stu} 共{len(records)}次到课")
                for r in records:
                    st.write(f"{r['日期']}（{r['班级']}）")
            else:
                st.warning(f"❌ {selected_stu} 暂无到课记录")
        else:
            st.error("❌ 暂无任何考勤记录")

# 6. 记录管理（修复重复key报错）
elif page == "记录管理":
    st.title("管理考勤记录")
    # 筛选
    col1, col2 = st.columns(2)
    with col1:
        filter_date = st.text_input("日期筛选（如2026-03）", key="filter_date")
    with col2:
        filter_class = st.selectbox("班级筛选", ["", "街舞1班", "街舞2班"], key="filter_class")
    
    # 加载记录
    records = []
    if os.path.exists(CSV_FILE):
        with open(CSV_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if filter_date and not row['日期'].startswith(filter_date):
                    continue
                if filter_class and row['班级'] != filter_class:
                    continue
                records.append(row)
    
    # 显示记录 & 删除（新增索引i确保key唯一）
    if records:
        for i, r in enumerate(records):
            col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 2, 2])
            with col1:
                st.write(r['日期'])
            with col2:
                st.write(r['班级'])
            with col3:
                st.write(r['学生姓名'])
            with col4:
                st.write("✅ 到课" if r['是否到课']=='1' else "❌ 缺课")
            with col5:
                if st.button("删除", key=f"del_rec_{i}_{r['日期']}_{r['班级']}_{r['学生姓名']}"):
                    delete_record(r['日期'], r['班级'], r['学生姓名'])
                    st.success(f"✅ 已删除 {r['日期']} {r['班级']} {r['学生姓名']} 的记录")
                    st.rerun()
    else:
        st.info("暂无符合条件的考勤记录")
