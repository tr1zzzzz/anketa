import firebase_admin
from firebase_admin import credentials, firestore
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os

st.set_page_config(
    page_title="Гибкий график обучения",
    page_icon="📅",
    layout="centered"
)

st.markdown("""
<style>
    .stApp { background-color: #0a1628; }
    section[data-testid="stMain"] { background-color: #0a1628; }

    html, body, [class*="css"], .stMarkdown, .stText, label,
    .stRadio label, .stCheckbox label, p, span, div {
        color: #ffffff !important;
    }

    h1, h2, h3, h4 { color: #7eb8f7 !important; }

    section[data-testid="stForm"] {
        background-color: #102040;
        border-radius: 14px;
        padding: 1.5rem;
        border: 1px solid #1e3a5f;
    }

    input, textarea, select {
        background-color: #1a2f4a !important;
        color: #ffffff !important;
        border: 1px solid #2e5080 !important;
        border-radius: 8px !important;
    }

    .stSlider > div > div { background-color: #2e5080 !important; }

    .stFormSubmitButton > button, .stButton > button {
        background-color: #1a5cb8 !important;
        color: #ffffff !important;
        border-radius: 8px !important;
        border: none !important;
        padding: 0.5rem 2rem !important;
        font-size: 1rem !important;
    }
    .stFormSubmitButton > button:hover, .stButton > button:hover {
        background-color: #2471d4 !important;
    }

    hr { border-color: #1e3a5f !important; }

    [data-testid="metric-container"] {
        background-color: #102040;
        border-radius: 10px;
        padding: 0.8rem;
        border: 1px solid #1e3a5f;
    }

    /* Multiselect и selectbox — контейнер */
    [data-baseweb="select"] > div {
        background-color: #1a2f4a !important;
        border-color: #2e5080 !important;
    }

    /* Текст внутри multiselect поля */
    [data-baseweb="select"] span,
    [data-baseweb="select"] input,
    [data-baseweb="select"] div {
        color: #ffffff !important;
        background-color: #1a2f4a !important;
    }

    /* Выбранные теги */
    [data-baseweb="tag"] {
        background-color: #1a5cb8 !important;
        color: #ffffff !important;
    }
    [data-baseweb="tag"] span { color: #ffffff !important; }

    /* Выпадающий список вариантов */
    [data-baseweb="popover"] {
        background-color: #1a2f4a !important;
    }
    [data-baseweb="menu"] {
        background-color: #1a2f4a !important;
    }
    [data-baseweb="menu"] ul {
        background-color: #1a2f4a !important;
    }
    [data-baseweb="menu"] li {
        background-color: #1a2f4a !important;
        color: #ffffff !important;
    }
    [data-baseweb="menu"] li:hover {
        background-color: #2e5080 !important;
        color: #ffffff !important;
    }
    [data-baseweb="option"] {
        background-color: #1a2f4a !important;
        color: #ffffff !important;
    }
</style>
""", unsafe_allow_html=True)

if not firebase_admin._apps:
    try:
        key_dict = dict(st.secrets["firebase"])
        cred = credentials.Certificate(key_dict)
    except Exception:
        KEY_PATH = os.getenv("FIREBASE_KEY", "serviceAccountKey.json")
        if not os.path.exists(KEY_PATH):
            st.error("Ошибка: файл serviceAccountKey.json не найден.")
            st.stop()
        cred = credentials.Certificate(KEY_PATH)
    firebase_admin.initialize_app(cred)

db = firestore.client()

st.title("📅 Отношение к гибкому графику обучения")
st.markdown(
    "Опрос об отношении студентов к гибкому расписанию. "
    "Все ответы анонимны и используются только в учебных целях."
)
st.divider()

with st.form("survey"):
    st.subheader("Заполните опрос")

    st.markdown("**👤 О себе**")
    col1, col2 = st.columns(2)
    with col1:
        age = st.number_input("Ваш возраст", min_value=14, max_value=60, step=1, value=20)
        study_year = st.selectbox(
            "Курс обучения",
            ["1 курс", "2 курс", "3 курс", "4 курс", "Магистратура / аспирантура"]
        )
    with col2:
        gender = st.radio("Пол", ["Мужской", "Женский", "Предпочитаю не указывать"])
        format_ = st.radio(
            "Текущий формат обучения",
            ["Очный", "Заочный", "Дистанционный", "Гибридный"]
        )

    st.markdown("---")
    st.markdown("**📋 Текущее расписание**")
    satisfaction = st.slider(
        "Насколько вы довольны текущим расписанием? (1 — совсем не доволен, 10 — полностью доволен)",
        min_value=1, max_value=10, value=5
    )
    schedule_stress = st.select_slider(
        "Насколько текущее расписание вызывает у вас стресс?",
        options=["Совсем не вызывает", "Редко", "Иногда", "Часто", "Постоянно"]
    )
    hours_per_day = st.slider(
        "Сколько часов в день вы тратите на учёбу?",
        min_value=1, max_value=16, value=5
    )

    st.markdown("---")
    st.markdown("**🔄 Опыт гибкого обучения**")
    flexible_exp = st.radio(
        "Был ли у вас опыт гибкого графика обучения?",
        ["Да, и мне понравилось", "Да, но не понравилось", "Нет, но хочу попробовать", "Нет и не хочу"]
    )
    self_org = st.slider(
        "Оцените свой уровень самоорганизации (1 — низкий, 10 — высокий)",
        min_value=1, max_value=10, value=5
    )
    productivity = st.select_slider(
        "При гибком графике ваша продуктивность, по вашему мнению:",
        options=["Значительно снизится", "Немного снизится", "Не изменится", "Немного вырастет", "Значительно вырастет"]
    )

    st.markdown("---")
    st.markdown("**⏰ Дедлайны и нагрузка**")
    deadlines = st.select_slider(
        "Как вы справляетесь с дедлайнами при свободном графике?",
        options=["Очень тяжело", "Тяжело", "Нейтрально", "Справляюсь", "Легко справляюсь"]
    )
    procrastination = st.radio(
        "Склонны ли вы к прокрастинации при отсутствии чёткого расписания?",
        ["Да, сильно", "Иногда", "Редко", "Нет, справляюсь сам"]
    )

    st.markdown("---")
    st.markdown("**✅ Плюсы и минусы**")
    benefits = st.multiselect(
        "Какие плюсы гибкого графика важны для вас?",
        [
            "Можно учиться в удобное время",
            "Больше времени на работу / подработку",
            "Меньше стресса от расписания",
            "Можно совмещать с хобби и спортом",
            "Самостоятельное управление темпом",
            "Больше времени на сон и отдых",
            "Нет плюсов"
        ]
    )
    barriers = st.multiselect(
        "Что мешает эффективно учиться при гибком графике?",
        [
            "Прокрастинация",
            "Сложно без чёткого расписания",
            "Мало общения с однокурсниками",
            "Технические проблемы",
            "Нехватка мотивации",
            "Сложно разграничить учёбу и отдых",
            "Ничего не мешает"
        ]
    )

    st.markdown("---")
    st.markdown("**💬 Итоговое мнение**")
    would_choose = st.radio(
        "Если бы у вас был выбор, вы бы предпочли гибкий график?",
        ["Да, однозначно", "Скорее да", "Скорее нет", "Нет, предпочитаю фиксированное расписание"]
    )
    recommend = st.radio(
        "Порекомендовали бы вы гибкий график другим студентам?",
        ["Да, всем", "Да, но не всем", "Скорее нет", "Нет"]
    )
    ideal_schedule = st.multiselect(
        "Каким должен быть идеальный график обучения?",
        [
            "Полностью свободный — сам выбираю время",
            "Гибкий с обязательными встречами раз в неделю",
            "Фиксированный, но с возможностью переноса занятий",
            "Полностью фиксированный — чёткое расписание",
            "Смешанный: очные пары + свободные задания онлайн"
        ]
    )

    comment = st.text_area("Дополнительные комментарии (необязательно)", placeholder="Ваше мнение...")

    submitted = st.form_submit_button("Отправить ответ ✅")

if submitted:
    if not benefits or not ideal_schedule:
        st.warning("Пожалуйста, заполните все поля с множественным выбором.")
    else:
        record = {
            "age": int(age),
            "gender": gender,
            "study_year": study_year,
            "format": format_,
            "satisfaction": int(satisfaction),
            "schedule_stress": schedule_stress,
            "hours_per_day": int(hours_per_day),
            "flexible_exp": flexible_exp,
            "self_org": int(self_org),
            "productivity": productivity,
            "deadlines": deadlines,
            "procrastination": procrastination,
            "benefits": benefits,
            "barriers": barriers,
            "would_choose": would_choose,
            "recommend": recommend,
            "ideal_schedule": ideal_schedule,
            "comment": comment,
            "timestamp": datetime.utcnow()
        }
        try:
            db.collection("responses").add(record)
            st.success("Спасибо! Ваш ответ сохранён. 🎉")
            st.balloons()
        except Exception as e:
            st.error(f"Ошибка при сохранении: {e}")

st.divider()
if st.checkbox("📊 Показать аналитику (для преподавателя)"):
    docs = db.collection("responses").stream()
    data = [doc.to_dict() for doc in docs]

    if not data:
        st.info("Ответов пока нет.")
    else:
        df = pd.DataFrame(data)
        df["timestamp"] = pd.to_datetime(df["timestamp"])

        st.subheader("Ключевые показатели")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Всего ответов", len(df))
        col2.metric("Средняя удовлетворённость", f"{df['satisfaction'].mean():.1f} / 10")
        col3.metric("Средняя самоорганизация", f"{df['self_org'].mean():.1f} / 10")
        col4.metric("Среднее часов в день", f"{df['hours_per_day'].mean():.1f} ч")

        st.subheader("Сводная таблица ответов")
        st.dataframe(df.drop(columns=["timestamp", "comment"], errors="ignore").head(20), use_container_width=True)

        st.subheader("О респондентах")
        col1, col2 = st.columns(2)
        with col1:
            fig = px.pie(df, names="gender", title="Пол респондентов",
                color_discrete_sequence=px.colors.sequential.Blues_r)
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            fig = px.bar(df["study_year"].value_counts().reset_index(),
                x="study_year", y="count", title="Курс обучения",
                labels={"study_year": "", "count": "Кол-во"},
                color_discrete_sequence=["#1a5cb8"])
            st.plotly_chart(fig, use_container_width=True)

        col1, col2 = st.columns(2)
        with col1:
            fig = px.pie(df, names="format", title="Формат обучения",
                color_discrete_sequence=px.colors.sequential.Blues_r)
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            fig = px.histogram(df, x="age", nbins=10, title="Возраст респондентов",
                labels={"age": "Возраст", "count": "Кол-во"},
                color_discrete_sequence=["#2471d4"])
            st.plotly_chart(fig, use_container_width=True)

        st.subheader("Текущее расписание")
        col1, col2 = st.columns(2)
        with col1:
            fig = px.histogram(df, x="satisfaction", nbins=10,
                title="Удовлетворённость расписанием",
                labels={"satisfaction": "Оценка (1-10)", "count": "Кол-во"},
                color_discrete_sequence=["#1a5cb8"])
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            stress_order = ["Совсем не вызывает", "Редко", "Иногда", "Часто", "Постоянно"]
            fig = px.bar(df["schedule_stress"].value_counts().reindex(stress_order).reset_index(),
                x="schedule_stress", y="count", title="Стресс от расписания",
                labels={"schedule_stress": "", "count": "Кол-во"},
                color_discrete_sequence=["#2471d4"])
            st.plotly_chart(fig, use_container_width=True)

        fig = px.histogram(df, x="hours_per_day", nbins=10,
            title="Часов в день на учёбу",
            labels={"hours_per_day": "Часов", "count": "Кол-во"},
            color_discrete_sequence=["#1a5cb8"])
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Опыт и отношение к гибкому обучению")
        col1, col2 = st.columns(2)
        with col1:
            fig = px.pie(df, names="flexible_exp", title="Опыт гибкого обучения",
                color_discrete_sequence=px.colors.sequential.Blues_r)
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            fig = px.histogram(df, x="self_org", nbins=10,
                title="Уровень самоорганизации",
                labels={"self_org": "Оценка (1-10)", "count": "Кол-во"},
                color_discrete_sequence=["#2471d4"])
            st.plotly_chart(fig, use_container_width=True)

        prod_order = ["Значительно снизится", "Немного снизится", "Не изменится", "Немного вырастет", "Значительно вырастет"]
        fig = px.bar(df["productivity"].value_counts().reindex(prod_order).reset_index(),
            x="productivity", y="count", title="Ожидаемая продуктивность при гибком графике",
            labels={"productivity": "", "count": "Кол-во"},
            color_discrete_sequence=["#1a5cb8"])
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Дедлайны и прокрастинация")
        col1, col2 = st.columns(2)
        with col1:
            dead_order = ["Очень тяжело", "Тяжело", "Нейтрально", "Справляюсь", "Легко справляюсь"]
            fig = px.bar(df["deadlines"].value_counts().reindex(dead_order).reset_index(),
                x="deadlines", y="count", title="Справляемость с дедлайнами",
                labels={"deadlines": "", "count": "Кол-во"},
                color_discrete_sequence=["#2471d4"])
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            fig = px.pie(df, names="procrastination", title="Склонность к прокрастинации",
                color_discrete_sequence=px.colors.sequential.Blues_r)
            st.plotly_chart(fig, use_container_width=True)

        st.subheader("Плюсы и барьеры")
        benefits_counts = pd.Series(
            [item for sublist in df["benefits"].dropna() for item in sublist]
        ).value_counts().reset_index()
        benefits_counts.columns = ["benefit", "count"]
        fig = px.bar(benefits_counts, x="count", y="benefit", orientation="h",
            title="Плюсы гибкого графика",
            labels={"benefit": "", "count": "Кол-во упоминаний"},
            color_discrete_sequence=["#1a5cb8"])
        st.plotly_chart(fig, use_container_width=True)

        barriers_counts = pd.Series(
            [item for sublist in df["barriers"].dropna() for item in sublist]
        ).value_counts().reset_index()
        barriers_counts.columns = ["barrier", "count"]
        fig = px.bar(barriers_counts, x="count", y="barrier", orientation="h",
            title="Барьеры при гибком обучении",
            labels={"barrier": "", "count": "Кол-во упоминаний"},
            color_discrete_sequence=["#2471d4"])
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Итоговое мнение")
        col1, col2 = st.columns(2)
        with col1:
            fig = px.pie(df, names="would_choose", title="Предпочли бы гибкий график?",
                color_discrete_sequence=px.colors.sequential.Blues_r)
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            fig = px.pie(df, names="recommend", title="Рекомендовали бы другим?",
                color_discrete_sequence=px.colors.sequential.Blues_r)
            st.plotly_chart(fig, use_container_width=True)

        ideal_counts = pd.Series(
            [item for sublist in df["ideal_schedule"].dropna() for item in sublist]
        ).value_counts().reset_index()
        ideal_counts.columns = ["schedule", "count"]
        fig = px.bar(ideal_counts, x="count", y="schedule", orientation="h",
            title="Идеальный формат расписания",
            labels={"schedule": "", "count": "Кол-во упоминаний"},
            color_discrete_sequence=["#1a5cb8"])
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Корреляция: самоорганизация и удовлетворённость")
        fig = px.scatter(df, x="self_org", y="satisfaction",
            title="Самоорганизация vs Удовлетворённость расписанием",
            labels={"self_org": "Самоорганизация", "satisfaction": "Удовлетворённость"},
            color_discrete_sequence=["#7eb8f7"])
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Корреляция: часы учёбы и самоорганизация")
        fig = px.scatter(df, x="hours_per_day", y="self_org",
            title="Часов в день vs Самоорганизация",
            labels={"hours_per_day": "Часов в день", "self_org": "Самоорганизация"},
            color_discrete_sequence=["#2471d4"])
        st.plotly_chart(fig, use_container_width=True)
