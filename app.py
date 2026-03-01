import streamlit as st
import csv
import os
from datetime import datetime
import json
import pandas as pd

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

# ===================== 关键修复：页面加载时自动收起侧边栏 =====================
# 第一次进来展开，之后切换页面都自动收起
if "sidebar_collapsed" not in st.session_state:
    st.session_state.sidebar_collapsed = False

# 自动收起逻辑
if st.session_state.get("last_page") != st.session_state.get("current_page"):
    st.session_state.sidebar_collapsed = True
    st.session_state.last_page = st.session_state.current_page

# 应用到页面配置
st.set_page_config(
    page_title="街舞考勤",
    page_icon="💃",
    layout="centered",
    initial_sidebar_state="collapsed" if st.session_state.sidebar_collapsed else "expanded"
)

# 全局样式
st.markdown("""
<style>
div.block-container { padding-top:1rem; padding-bottom:2rem; }
div.stButton > button { width:100%; }
</style>
""", unsafe_allow_html=True)

# 文件配置
CSV_FILE = "dance_student_records.csv"
STUDENT_CONFIG_FILE = "dance_students.json"
PRICE_PER_PERSON = 80

# 初始化文件
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
        writer.wrows(records)

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

def import_attendance_csv(uf):
    try:
        df = pd.read_csv(uf, encoding='utf-8')
        req = ["日期", "班级", "学生姓名", "是否到课"]
        if not all(c in df.columns for c in req):
            return False, "列名不正确"
        df.to_csv(CSV_FILE, index=False, encoding='utf-8')
        return True, "导入成功"
    except Exception as e:
        return False, str(e)

def import_student_json(uf):
    try:
        cfg = json.load(uf)
        if "街舞1班" not in cfg or "街舞2班" not in cfg:
            return False, "格式不正确"
        save_student_config(cfg)
        return True, "导入成功"
    except Exception as e:
        return False, str(e)

# 主逻辑
init_files()
config = get_student_config()

# ===================== 菜单 =====================
st.sidebar.title("💃 街舞考勤系统")
menu_options = ["首页", "考勤录入", "学员管理", "月度统计", "学生追踪", "记录管理", "数据备份恢复"]
page = st.sidebar.radio("功能菜单", menu_options)

# 记录当前页面，用于自动收起
st.session_state.current_page = page

# ------------------- 首页 -------------------
if page == "首页":
    st.title("🎉 街舞考勤系统")
    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        st.info("📝 考勤录入\n👥 学员管理\n📊 月度统计")
    with col2:
        st.info("🔍 学生追踪\n🗑️ 记录管理\n💾 备份恢复")
    st.divider()
    st.success("请从左侧菜单选择功能开始操作 ✅")

# ------------------- 考勤录入 -------------------
elif page == "考勤录入":
    st.title("📝 考勤录入")
    current_class = st.selectbox("选择班级", ["街舞1班", "街舞2班"], key="att_class")
    students = config[current_class]["students"]
    selected_date = st.date_input("日期", datetime.now(), key="att_date")
    date_str = selected_date.strftime("%Y-%m-%d")

    st.subheader(f"{current_class} 学员")
    cols = st.columns(2)
    attended = []
    for i, name in enumerate(students):
        with cols[i % 2]:
            if st.checkbox(name, key=f"k_{name}"):
                attended.append(name)

    if st.button("✅ 保存考勤", type="primary"):
        delete_batch_records(date_str, current_class)
        rows = [[date_str, current_class, s, "1" if s in attended else "0"] for s in students]
        with open(CSV_FILE, 'a', encoding='utf-8', newline='') as f:
            csv.writer(f).writerows(rows)
        st.success(f"保存成功｜到课 {len(attended)} 人")

# ------------------- 学员管理 -------------------
elif page == "学员管理":
    st.title("👥 学员管理")
    tab1, tab2, tab3, tab4 = st.tabs(["新增", "改名", "分班", "删除"])
    with tab1:
        s = st.text_input("学员姓名")
        c = st.selectbox("班级", ["街舞1班", "街舞2班"])
        if st.button("添加"):
            if s and s not in config[c]["students"]:
                config[c]["students"].append(s)
                save_student_config(config)
                st.success("添加成功")
                st.rerun()
    with tab2:
        c = st.selectbox("班级", ["街舞1班", "街舞2班"], key="e_c")
        old = st.text_input("原姓名")
        new = st.text_input("新姓名")
        if st.button("修改姓名"):
            if old in config[c]["students"] and new:
                idx = config[c]["students"].index(old)
                config[c]["students"][idx] = new
                save_student_config(config)
                st.success("修改成功")
                st.rerun()
    with tab3:
        s = st.text_input("学员")
        f = st.selectbox("原班级", ["街舞1班", "街舞2班"])
        t = st.selectbox("目标班级", ["街舞1班", "街舞2班"])
        if st.button("调整分班"):
            if s in config[f]["students"] and f != t:
                config[f]["students"].remove(s)
                config[t]["students"].append(s)
                save_student_config(config)
                st.success("调整成功")
                st.rerun()
    with tab4:
        for cls in ["街舞1班", "街舞2班"]:
            st.markdown(f"**{cls}**")
            for name in config[cls]["students"]:
                col_a, col_b = st.columns([4,1])
                with col_a:
                    st.write(name)
                with col_b:
                    if st.button("删", key=f"d_{cls}_{name}"):
                        config[cls]["students"].remove(name)
                        save_student_config(config)
                        st.rerun()

# ------------------- 月度统计 -------------------
elif page == "月度统计":
    st.title("📊 月度统计")
    y = st.text_input("年份", value=str(datetime.now().year))
    m = st.text_input("月份", value=str(datetime.now().month))
    if st.button("查询", type="primary"):
        if y.isdigit() and m.isdigit():
            ym = f"{y}-{m.zfill(2)}"
            all_records = []
            if os.path.exists(CSV_FILE):
                with open(CSV_FILE, encoding='utf-8') as f:
                    all_records = [r for r in csv.DictReader(f) if r["日期"].startswith(ym)]
            ok = [r for r in all_records if r["是否到课"]=="1"]
            total = len(ok)
            st.success(f"本月总到课：{total} 人次｜收入：{total*PRICE_PER_PERSON} 元")
            for cls in ["街舞1班", "街舞2班"]:
                cls_ok = [r for r in ok if r["班级"]==cls]
                st.write(f"**{cls}：{len(cls_ok)} 人次**")

# ------------------- 学生追踪 -------------------
elif page == "学生追踪":
    st.title("🔍 学生考勤追踪")
    all_stu = sorted({s for c in config.values() for s in c["students"]})
    who = st.selectbox("选择学生", all_stu)
    if st.button("查询", type="primary"):
        recs = []
        if os.path.exists(CSV_FILE):
            with open(CSV_FILE, encoding='utf-8') as f:
                recs = [r for r in csv.DictReader(f) if r["学生姓名"]==who and r["是否到课"]=="1"]
        st.success(f"{who} 共到课 {len(recs)} 次")
        for r in recs:
            st.write(f"- {r['日期']} {r['班级']}")

# ------------------- 记录管理 -------------------
elif page == "记录管理":
    st.title("🗑️ 考勤记录管理")
    date_filter = st.text_input("日期筛选（2026-03）", key="rec_date_filter")
    class_filter = st.selectbox("班级", ["", "街舞1班", "街舞2班"], key="rec_class_filter")
    show_type = st.radio("显示类型", ["到课", "缺课", "全部"], index=0, horizontal=True)

    records = []
    if os.path.exists(CSV_FILE):
        with open(CSV_FILE, encoding='utf-8') as f:
            for r in csv.DictReader(f):
                if date_filter and not r["日期"].startswith(date_filter):
                    continue
                if class_filter and r["班级"] != class_filter:
                    continue
                if show_type == "到课" and r["是否到课"] != "1":
                    continue
                if show_type == "缺课" and r["是否到课"] != "0":
                    continue
                records.append(r)

    for i, r in enumerate(records):
        a,b,c,d,e = st.columns([3,2,2,2,2])
        with a: st.write(r["日期"])
        with b: st.write(r["班级"])
        with c: st.write(r["学生姓名"])
        with d: st.write("✅" if r["是否到课"]=="1" else "❌")
        with e:
            if st.button("删", key=f"rr_{i}"):
                delete_record(r["日期"], r["班级"], r["学生姓名"])
                st.rerun()

# ------------------- 备份恢复 -------------------
elif page == "数据备份恢复":
    st.title("💾 数据备份与恢复")
    st.divider()
    st.subheader("📤 导出备份")
    c1,c2 = st.columns(2)
    with c1:
        if os.path.exists(CSV_FILE):
            with open(CSV_FILE, "rb") as f:
                st.download_button("考勤记录(CSV)", f, f"考勤_{datetime.now():%Y%m%d}.csv", "text/csv")
    with c2:
        if os.path.exists(STUDENT_CONFIG_FILE):
            with open(STUDENT_CONFIG_FILE, "rb") as f:
                st.download_button("学员信息(JSON)", f, f"学员_{datetime.now():%Y%m%d}.json", "application/json")

    st.divider()
    st.subheader("📥 导入恢复")
    st.warning("导入会覆盖当前数据，请先备份！")
    csv_up = st.file_uploader("上传考勤CSV", type="csv")
    if st.button("导入考勤记录"):
        if csv_up:
            ok,msg = import_attendance_csv(csv_up)
            st.success(msg) if ok else st.error(msg)

    json_up = st.file_uploader("上传学员JSON", type="json")
    if st.button("导入学员信息"):
        if json_up:
            ok,msg = import_student_json(json_up)
            st.success(msg) if ok else st.error(msg)