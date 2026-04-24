import streamlit as st
from jinja2 import Template
import pdfkit
import pandas as pd

# 網頁基本設定
st.set_page_config(page_title="應修科目表產生器", layout="wide")
st.title("🎓 大學學系應修科目表產生器")

# ================= 1. 網頁填寫區塊 =================

st.header("一、基本資訊")
col1, col2 = st.columns(2)
with col1:
    dept_name = st.text_input("學系名稱", "資訊工程學系")
with col2:
    year = st.text_input("適用入學年度", "113學年度")

st.header("二、學系課程規劃 (可動態新增/刪除列)")
# 使用 data_editor 讓使用者能在網頁上直接編輯表格
default_courses = pd.DataFrame({
    "科目名稱": ["程式設計", "資料結構", "專題實作(一)"],
    "學期或學年": ["一上", "一下", "三上"],
    "學分數": [3, 3, 2],
    "修讀條件/模組/擋修": ["無", "擋修:程式設計", "模組:核心必修"]
})
courses_df = st.data_editor(default_courses, num_rows="dynamic", use_container_width=True)

st.header("三、畢業學分數結構")
c1, c2, c3 = st.columns(3)
with c1:
    uni_req = st.number_input("校訂必修 (學分)", 0, 100, 28)
with c2:
    dept_req = st.number_input("學系必修 (學分)", 0, 150, 60)
with c3:
    free_elec = st.number_input("自由選修 (學分)", 0, 100, 40)
st.info(f"**總畢業學分數：{uni_req + dept_req + free_elec} 學分**")

st.header("四、校訂必修各類課程科目表")
uni_courses = pd.DataFrame({
    "類別": ["國文", "外國語文", "通識課程", "體育", "全人核心課程"],
    "規定說明": ["必修4學分", "必修4學分(需達畢業英檢門檻)", "必修14學分(需涵蓋三大領域)", "必修0學分(應修滿4學期)", "必修6學分"]
})
uni_courses_df = st.data_editor(uni_courses, use_container_width=True)

st.header("五、學系說明規定與會議資訊")
notes = st.text_area("學系說明規定 (支援多行)", "1. 學生修讀本系課程需依循先修科目規定。\n2. 跨系選修最多承認 15 學分。")
meeting_info = st.text_input("本表通過會議及時間資訊", "113年5月10日 112學年度第2學期第3次系務會議通過")


# ================= 2. PDF 產出邏輯 =================

# HTML 模板設計 (包含 CSS 排版)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body { font-family: "Microsoft JhengHei", "Heiti TC", sans-serif; margin: 20px; line-height: 1.6; }
        h2, h3 { text-align: center; margin: 5px 0; }
        table { width: 100%; border-collapse: collapse; margin-bottom: 20px; font-size: 14px; }
        th, td { border: 1px solid #000; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; text-align: center; }
        .section-title { font-weight: bold; font-size: 16px; margin-top: 20px; border-bottom: 2px solid #000; display: inline-block; }
        .summary-box { border: 1px solid #000; padding: 10px; background-color: #fafafa; }
    </style>
</head>
<body>
    <h2>{{ dept_name }} 應修科目表</h2>
    <h3>適用入學年度：{{ year }}</h3>

    <div class="section-title">一、學系課程規劃</div>
    <table>
        <tr>
            <th width="30%">科目名稱</th>
            <th width="15%">學期或學年</th>
            <th width="10%">學分數</th>
            <th width="45%">修讀條件限制 / 模組規劃 / 擋修</th>
        </tr>
        {% for index, row in courses_df.iterrows() %}
        <tr>
            <td>{{ row['科目名稱'] }}</td>
            <td style="text-align: center;">{{ row['學期或學年'] }}</td>
            <td style="text-align: center;">{{ row['學分數'] }}</td>
            <td>{{ row['修讀條件/模組/擋修'] }}</td>
        </tr>
        {% endfor %}
    </table>

    <div class="section-title">二、畢業學分數結構</div>
    <div class="summary-box">
        校訂必修： <b>{{ uni_req }}</b> 學分 ＋ 
        學系必修： <b>{{ dept_req }}</b> 學分 ＋ 
        自由選修： <b>{{ free_elec }}</b> 學分 ＝ 
        應修總畢業學分： <b>{{ total_req }}</b> 學分
    </div>

    <div class="section-title">三、校訂必修各類課程科目表</div>
    <table>
        <tr>
            <th width="20%">課程類別</th>
            <th width="80%">規定說明</th>
        </tr>
        {% for index, row in uni_courses_df.iterrows() %}
        <tr>
            <td style="text-align: center; font-weight: bold;">{{ row['類別'] }}</td>
            <td>{{ row['規定說明'] }}</td>
        </tr>
        {% endfor %}
    </table>

    <div class="section-title">四、學系規定與會議資訊</div>
    <div>
        <p>{{ notes | replace('\n', '<br>') }}</p>
        <p style="text-align: right; font-weight: bold; margin-top: 30px;">通過會議與時間：{{ meeting_info }}</p>
    </div>
</body>
</html>
"""

st.markdown("---")
# 產出按鈕
if st.button("產生 PDF 下載連結", type="primary"):
    with st.spinner("正在產生 PDF 中，請稍候..."):
        # 將資料綁定到 HTML 模板
        template = Template(HTML_TEMPLATE)
        html_content = template.render(
            dept_name=dept_name,
            year=year,
            courses_df=courses_df,
            uni_req=uni_req,
            dept_req=dept_req,
            free_elec=free_elec,
            total_req=uni_req + dept_req + free_elec,
            uni_courses_df=uni_courses_df,
            notes=notes,
            meeting_info=meeting_info
        )

        # PDF 參數設定 (支援中文字型與邊距)
        options = {
            'page-size': 'A4',
            'margin-top': '0.5in',
            'margin-right': '0.5in',
            'margin-bottom': '0.5in',
            'margin-left': '0.5in',
            'encoding': "UTF-8",
            'enable-local-file-access': None
        }

        try:
            # 將 HTML 轉為 PDF
            pdf_bytes = pdfkit.from_string(html_content, False, options=options)
            
            st.success("✅ PDF 產生成功！")
            # 提供下載按鈕
            st.download_button(
                label="📥 點此下載 PDF 檔案",
                data=pdf_bytes,
                file_name=f"{year}_{dept_name}應修科目表.pdf",
                mime="application/pdf"
            )
        except Exception as e:
            st.error("產生 PDF 時發生錯誤。請確認系統是否已正確安裝 `wkhtmltopdf` 並加入環境變數。")
            st.exception(e)