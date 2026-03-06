# app.py
import uuid
import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage

from src.agent.graph import create_graph


# ==============================================================================
# Настройка страницы
# ==============================================================================
st.set_page_config(
    page_title="AI Career Partner",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==============================================================================
# CSS стили
# ==============================================================================
st.markdown(
    """
    <style>
    /* ========== ПРЕДОТВРАЩЕНИЕ АВТО-СКРОЛЛА ========== */
    
    /* Фиксируем позицию чата */
    .stChatMessage {
        scroll-margin-top: 100vh !important;
    }
    
    /* Стили для чата */
    [data-testid="stChatInput"] {
        background: linear-gradient(135deg, #fce7f3 0%, #fbcfe8 50%, #e0e7ff 100%) !important;
        border: none !important;
        outline: none !important;
        box-shadow: 0 4px 15px rgba(236, 72, 153, 0.2) !important;
        border-radius: 24px !important;
        padding: 8px 16px !important;
        position: sticky !important;
        bottom: 20px !important;
        z-index: 999 !important;
    }
    
    [data-testid="stChatInput"] textarea {
        background: #ffffff !important;
        color: #000000 !important;
        border: none !important;
        outline: none !important;
        box-shadow: none !important;
        font-size: 1rem !important;
    }
    
    [data-testid="stChatInput"] textarea::placeholder {
        color: #6b7280 !important;
    }
    
    /* Кнопка отправки */
    [data-testid="stChatInput"] button {
        background: linear-gradient(135deg, #ec4899 0%, #8b5cf6 100%) !important;
        border: none !important;
        outline: none !important;
        border-radius: 50% !important;
        width: 40px !important;
        height: 40px !important;
        color: white !important;
        box-shadow: 0 2px 10px rgba(236, 72, 153, 0.3) !important;
    }
    
    [data-testid="stChatInput"] button:hover {
        background: linear-gradient(135deg, #db2777 0%, #7c3aed 100%) !important;
        box-shadow: 0 4px 15px rgba(236, 72, 153, 0.4) !important;
    }
    
    /* При фокусе */
    [data-testid="stChatInput"]:focus-within {
        border: none !important;
        outline: none !important;
        box-shadow: 0 0 0 3px rgba(236, 72, 153, 0.3) !important;
    }
    </style>
    
    <script>
    // ========== JAVASCRIPT ДЛЯ КОНТРОЛЯ СКРОЛЛА ==========
    
    // Функция для прокрутки к полю ввода
    function scrollToInput() {
        setTimeout(() => {
            const inputElement = document.querySelector('[data-testid="stChatInput"]');
            if (inputElement) {
                inputElement.scrollIntoView({ behavior: 'smooth', block: 'end' });
                // Фокус на поле ввода
                const textarea = inputElement.querySelector('textarea');
                if (textarea) {
                    textarea.focus();
                }
            }
        }, 100);
    }
    
    // Слушаем изменения в DOM
    const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
            if (mutation.addedNodes.length > 0) {
                // Проверяем, добавлено ли новое сообщение
                const newMessage = Array.from(mutation.addedNodes).find(
                    node => node.classList && node.classList.contains('stChatMessage')
                );
                if (newMessage) {
                    // Прокручиваем к полю ввода вместо ответа
                    scrollToInput();
                }
            }
        });
    });
    
    // Запускаем observer после загрузки страницы
    window.addEventListener('load', () => {
        const chatContainer = document.querySelector('[data-testid="stChatMessageContainer"]');
        if (chatContainer) {
            observer.observe(chatContainer, { childList: true, subtree: true });
        }
    });
    </script>
    """,
    unsafe_allow_html=True,
)
st.markdown(
    """
    <style>
    /* ========== УБИРАЕМ ВСЕ ЭЛЕМЕНТЫ STREAMLIT ========== */

    /* Убираем header (верхнюю панель) */
    [data-testid="stHeader"] {
        display: none !important;
        visibility: hidden !important;
    }

    /* Убираем footer (нижнюю панель) */
    [data-testid="stFooter"] {
        display: none !important;
        visibility: hidden !important;
    }

    /* Убираем меню (три точки) */
    [data-testid="stToolbar"] {
        display: none !important;
        visibility: hidden !important;
    }

    /* Убираем боковую панель */
    [data-testid="stSidebar"] {
        display: none !important;
        visibility: hidden !important;
    }

    /* Убираем все отступы */
    .block-container {
        padding: 0rem 1rem !important;
        max-width: 100% !important;
        margin: 0 !important;
    }

    /* Убираем отступы у main контейнера */
    .main > div {
        padding: 0 !important;
        margin: 0 !important;
    }

    /* Убираем отступы у всего приложения */
    .stApp {
        padding: 0 !important;
        margin: 0 !important;
        min-height: 100vh !important;
    }

    /* Делаем фон на всю высоту экрана */
    body {
        margin: 0 !important;
        padding: 0 !important;
        height: 100vh !important;
        overflow-x: hidden !important;
    }

    /* Убираем стандартные элементы */
    header {
        visibility: hidden !important;
        display: none !important;
    }

    footer {
        visibility: hidden !important;
        display: none !important;
    }
    /* ========== ОСНОВНОЙ ФОН (сине-зелёный градиент) ========== */
    .main { 
        background: linear-gradient(180deg, #0d9488 0%, #0891b2 50%, #1e40af 100%) !important;
    }
    
    /* Убираем стандартный фон Streamlit */
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(180deg, #0d9488 0%, #0891b2 50%, #1e40af 100%) !important;
    }
    
    /* ========== HERO СЕКЦИЯ ========== */
    .hero {
        padding: 2.5rem 2rem 1.8rem 2rem;
        border-radius: 24px;
        background: linear-gradient(135deg, #0d9488 0%, #14b8a6 50%, #86efac 100%);
        color: white;
        box-shadow: 0 16px 40px rgba(13, 148, 136, 0.40);
        margin-bottom: 1.2rem;
    }
    .hero h1 { 
        font-size: 2.4rem; 
        margin-bottom: 0.2rem; 
        color: white !important;
        text-shadow: 0 2px 8px rgba(0,0,0,0.2);
    }
    .hero p { 
        font-size: 1.05rem; 
        color: #f0fdfa !important;
        margin: 0; 
    }
    
    /* ========== КАРТОЧКИ (тёмно-розовый → синий градиент) ========== */
    .section-card {
        background: linear-gradient(135deg, #831843 0%, #9d174d 25%, #5b21b6 75%, #1e40af 100%);
        border: 1px solid rgba(236, 72, 153, 0.3);
        border-radius: 22px;
        padding: 1.1rem 1.1rem 1rem 1.1rem;
        box-shadow: 0 10px 30px rgba(236, 72, 153, 0.25);
        margin-bottom: 1rem;
        color: #ffffff !important;
    }
    
    /* ========== ВАКАНСИИ (тёмно-розовый → синий градиент) ========== */
    .vacancy-card {
        background: linear-gradient(135deg, #831843 0%, #9d174d 30%, #5b21b6 70%, #1e40af 100%);
        border-radius: 18px;
        padding: 1rem;
        border: 1px solid rgba(236, 72, 153, 0.35);
        box-shadow: 0 8px 20px rgba(236, 72, 153, 0.2);
        margin-bottom: 0.8rem;
        color: #ffffff !important;
    }
    
    /* ========== ТЕКСТ В ПОЛЯХ ВВОДА ========== */
    .stTextInput input,
    .stTextArea textarea,
    [data-baseweb="textarea"] textarea {
        color: #000000 !important;
        background: rgba(255, 255, 255, 0.95) !important;
    }
    
    .stTextInput input::placeholder,
    .stTextArea textarea::placeholder {
        color: #666666 !important;
    }
    
    /* ========== ВСЕ ТЕКСТОВЫЕ ЭЛЕМЕНТЫ ========== */
    .stMarkdown, 
    .stText, 
    p, 
    h1, h2, h3, h4, h5, h6,
    label,
    .element-container,
    .stMarkdown p,
    .stMarkdown li,
    .stMarkdown strong {
        color: #ffffff !important;
    }
    
    /* ========== МЕТРИКИ (навыки) ========== */
    .metric-pill {
        display: inline-block;
        padding: 0.35rem 0.7rem;
        border-radius: 999px;
        background: linear-gradient(135deg, #fbcfe8 0%, #c4b5fd 100%);
        color: #831843;
        font-size: 0.88rem;
        margin: 0.15rem 0.2rem 0.15rem 0;
        border: 1px solid #f472b6;
        font-weight: 600;
    }
    
    /* ========== УСПЕШНЫЕ СООБЩЕНИЯ ========== */
    .success-box {
        background: linear-gradient(135deg, #059669 0%, #047857 100%);
        border: 1px solid #34d399;
        border-radius: 12px;
        padding: 0.8rem;
        color: #ffffff !important;
        margin: 0.5rem 0;
    }
    
    /* ========== ЗАГОЛОВКИ ========== */
    .small-title { 
        font-weight: 700; 
        font-size: 1.08rem; 
        margin-bottom: 0.3rem;
        color: #fbcfe8 !important;
    }
    
    .subtle { 
        color: #e2e8f0 !important;
        font-size: 0.94rem; 
    }
    
    .muted { 
        color: #cbd5e1 !important; 
        font-size: 0.95rem; 
    }
    
    /* ========== КНОПКИ ========== */
    .stButton > button {
        background: linear-gradient(135deg, #ec4899 0%, #8b5cf6 100%);
        color: white !important;
        border: none;
        border-radius: 12px;
        font-weight: 600;
        box-shadow: 0 4px 15px rgba(236, 72, 153, 0.3);
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #db2777 0%, #7c3aed 100%);
        box-shadow: 0 6px 20px rgba(236, 72, 153, 0.4);
    }
    
    /* ========== CHAT INPUT (поле ввода) ========== */
    [data-testid="stChatInput"] {
        background: linear-gradient(135deg, #fce7f3 0%, #fbcfe8 50%, #e0e7ff 100%) !important;
        border: none !important;
        outline: none !important;
        box-shadow: 0 4px 15px rgba(236, 72, 153, 0.2) !important;
        border-radius: 24px !important;
        padding: 8px 16px !important;
    }

    /* Внутренний textarea - делаем белым */
    [data-testid="stChatInput"] textarea {
        background: #ffffff !important;
        color: #000000 !important;
        border: none !important;
        outline: none !important;
        box-shadow: none !important;
        font-size: 1rem !important;
    }

    /* Placeholder текст */
    [data-testid="stChatInput"] textarea::placeholder {
        color: #6b7280 !important;
    }

    /* Кнопка отправки */
    [data-testid="stChatInput"] button {
        background: linear-gradient(135deg, #ec4899 0%, #8b5cf6 100%) !important;
        border: none !important;
        outline: none !important;
        border-radius: 50% !important;
        width: 40px !important;
        height: 40px !important;
        color: white !important;
        box-shadow: 0 2px 10px rgba(236, 72, 153, 0.3) !important;
    }

    [data-testid="stChatInput"] button:hover {
        background: linear-gradient(135deg, #db2777 0%, #7c3aed 100%) !important;
        box-shadow: 0 4px 15px rgba(236, 72, 153, 0.4) !important;
    }

    /* При фокусе */
    [data-testid="stChatInput"]:focus-within {
        border: none !important;
        outline: none !important;
        box-shadow: 0 0 0 3px rgba(236, 72, 153, 0.3) !important;
    }
        </style>
    """,
    unsafe_allow_html=True,
)


# ==============================================================================
# Инициализация сессии
# ==============================================================================
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

if "graph_state" not in st.session_state:
    st.session_state.graph_state = {
        "messages": [],
        "profile": None,
        "last_search_results": [],
        "search_mode": False,
        "resume_processed": False,
        "loop_step": 0,
    }

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "quick_prompt" not in st.session_state:
    st.session_state.quick_prompt = ""

if "app" not in st.session_state:
    # Создаём граф один раз при старте
    with st.spinner("🚀 Инициализация агента..."):
        st.session_state.app = create_graph()

# ==============================================================================
# Функция: Обработка сообщения через граф
# ==============================================================================
def send_to_agent(user_message: str):
    """Отправляет сообщение в граф и обновляет состояние"""
    app = st.session_state.app
    
    # Формируем входные данные
    inputs = {"messages": [HumanMessage(content=user_message)]}
    config = {"configurable": {"thread_id": st.session_state.thread_id}}
    
    # Инвоцируем граф с текущим состоянием
    result = app.invoke(
        {**st.session_state.graph_state, **inputs},
        config=config,
    )
    
    # Обновляем состояние
    st.session_state.graph_state.update(result)
    
    # Возвращаем ответ агента
    ai_messages = result.get("messages", [])
    if ai_messages and isinstance(ai_messages[-1], (AIMessage, HumanMessage)):
        return ai_messages[-1].content
    return "Не удалось сформировать ответ."

# ==============================================================================
# Функция: Загрузка резюме из текста/файла
# ==============================================================================
def process_resume_input(text_content: str):
    """Обрабатывает текст резюме через граф"""
    response = send_to_agent(text_content)
    
    # Проверяем, обновился ли профиль
    profile = st.session_state.graph_state.get("profile")
    if profile and profile.get("skills"):
        return True, response
    return False, response

# ==============================================================================
# Hero секция
# ==============================================================================
st.markdown(
    """
    <div class="hero">
        <h1>💼 AI Career Partner</h1>
        <p>
            От обсуждения карьерных целей до поиска вакансий и разбора найденного списка.
            Загрузите резюме — и я подберу подходящие позиции!
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ==============================================================================
# Верхние метрики
# ==============================================================================
profile = st.session_state.graph_state.get("profile")
has_profile = bool(profile and profile.get("skills"))
results = st.session_state.graph_state.get("last_search_results", [])

last_user_query = "Пока нет"
for item in reversed(st.session_state.chat_history):
    if item["role"] == "user":
        last_user_query = item["content"][:50] + "..." if len(item["content"]) > 50 else item["content"]
        break

cols = st.columns(3)
with cols[0]:
    st.markdown('<div class="section-card"><div class="small-title">👤 Профиль</div>', unsafe_allow_html=True)
    status = "✅ Загружен" if has_profile else "⏳ Не загружен"
    st.markdown(f"<span style='color: {'#16a34a' if has_profile else '#64748b'}'>{status}</span>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with cols[1]:
    st.markdown('<div class="section-card"><div class="small-title">🔍 Последний запрос</div>', unsafe_allow_html=True)
    st.write(last_user_query)
    st.markdown('</div>', unsafe_allow_html=True)

with cols[2]:
    st.markdown('<div class="section-card"><div class="small-title">📋 Вакансии в памяти</div>', unsafe_allow_html=True)
    st.write(f"{len(results)} найдено")
    st.markdown('</div>', unsafe_allow_html=True)

# ==============================================================================
# Основная секция: Профиль + Загрузка + Действия
# ==============================================================================
left, right = st.columns([1, 1.2], gap="large")

# ---------- ЛЕВАЯ КОЛОНКА: Профиль и загрузка ----------
with left:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.subheader("📄 Профиль кандидата")
    
    # === Блок загрузки резюме ===
    with st.expander("📤 Загрузить резюме", expanded=not has_profile):
        tab1, tab2 = st.tabs(["✍️ Вставить текст", "📁 Загрузить файл .txt"])
        
        with tab1:
            resume_text = st.text_area(
                "Вставьте текст вашего резюме:",
                height=150,
                placeholder="Я Python-разработчик с опытом 3 года. Навыки: FastAPI, Docker, PostgreSQL...",
                key="resume_text_input"
            )
            if st.button("Обработать резюме", type="primary", use_container_width=True, key="btn_process_text"):
                if resume_text and len(resume_text) > 50:
                    with st.spinner("🔍 Анализирую резюме..."):
                        success, response = process_resume_input(resume_text)
                        if success:
                            st.success("✅ Резюме успешно обработано!")
                            st.rerun()
                        else:
                            st.warning(f"⚠️ {response}")
                else:
                    st.error("Введите текст резюме (минимум 50 символов)")
        
        with tab2:
            uploaded_file = st.file_uploader(
                "Загрузите файл .txt с резюме",
                type=["txt"],
                key="resume_file_uploader"
            )
            if uploaded_file is not None:
                try:
                    # Читаем текстовый файл
                    text_content = uploaded_file.getvalue().decode("utf-8")
                    
                    if len(text_content) > 50:
                        if st.button("Обработать файл", type="primary", use_container_width=True, key="btn_process_file"):
                            with st.spinner("🔍 Анализирую файл..."):
                                success, response = process_resume_input(text_content)
                                if success:
                                    st.success("✅ Файл успешно обработан!")
                                    # Очищаем uploader после успешной обработки
                                    st.session_state.resume_file_uploader = None
                                    st.rerun()
                                else:
                                    st.warning(f"⚠️ {response}")
                    else:
                        st.error("Файл слишком короткий или пустой")
                        
                except UnicodeDecodeError:
                    st.error("❌ Ошибка кодировки. Поддерживаются только UTF-8 текстовые файлы.")
                except Exception as e:
                    st.error(f"❌ Ошибка чтения файла: {e}")
    
    # === Отображение профиля ===
    current_profile = st.session_state.graph_state.get("profile")
    
    if current_profile and current_profile.get("skills"):
        st.markdown('<div class="success-box">', unsafe_allow_html=True)
        st.markdown("**✅ Профиль активен**")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("**🎯 Желаемая роль**")
        st.write(current_profile.get("desired_role") or "Не определена")
        
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**📅 Опыт**")
            st.write(f"{current_profile.get('experience_years', 0)} лет")
        with c2:
            st.markdown("**💰 Ожидания по ЗП**")
            salary = current_profile.get("salary_expectation", 0)
            st.write(f"{salary:,} RUB" if salary else "Не указаны")
        
        st.markdown("**🛠 Навыки**")
        skills = current_profile.get("skills", [])
        if skills:
            st.markdown(
                "".join([f'<span class="metric-pill">{skill}</span>' for skill in skills[:20]]),
                unsafe_allow_html=True,
            )
        else:
            st.write("Навыки не извлечены.")
    else:
        st.info("📋 Загрузите резюме, чтобы начать подбор вакансий")
    
    st.markdown('</div>', unsafe_allow_html=True)

# ---------- ПРАВАЯ КОЛОНКА: Быстрые действия ----------
with right:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.subheader("⚡ Быстрые действия")
    
    a1, a2, a3 = st.columns(3)
    
    if a1.button("🔍 Найти вакансии", use_container_width=True, key="btn_find_jobs"):
        if has_profile:
            st.session_state.quick_prompt = "Найди вакансии по моему профилю"
        else:
            st.warning("Сначала загрузите резюме!")
    
    if a2.button("📊 Топ навыков", use_container_width=True, key="btn_top_skills"):
        st.session_state.quick_prompt = "Какие навыки сейчас востребованы для разработчика?"
    
    if a3.button("🎯 Анализ гэпов", use_container_width=True, key="btn_gaps"):
        if has_profile:
            st.session_state.quick_prompt = "Каких навыков мне не хватает для позиции Senior?"
        else:
            st.warning("Сначала загрузите резюме!")
    
    st.markdown(
        '<p class="muted">💡 Нажмите на кнопку или введите свой запрос в чат ниже.</p>',
        unsafe_allow_html=True,
    )
    st.markdown('</div>', unsafe_allow_html=True)

# ==============================================================================
# Чат
# ==============================================================================
st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.subheader("💬 Career Chat")

# Отображение истории чата
for item in st.session_state.chat_history:
    with st.chat_message(item["role"]):
        st.markdown(item["content"])

# Поле ввода
user_prompt = st.chat_input("Например: найди вакансии ML Engineer в Москве")

# Обработка быстрого промпта
if not user_prompt and st.session_state.get("quick_prompt"):
    user_prompt = st.session_state.quick_prompt
    st.session_state.quick_prompt = ""

# Обработка сообщения пользователя
if user_prompt:
    # Добавляем в историю
    st.session_state.chat_history.append({"role": "user", "content": user_prompt})
    
    # Отправляем в агент
    with st.spinner("🤔 Думаю..."):
        ai_response = send_to_agent(user_prompt)
    
    # Добавляем ответ в историю
    st.session_state.chat_history.append({"role": "assistant", "content": ai_response})
    
    # Перерисовываем
    st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

# ==============================================================================
# Результаты поиска вакансий
# ==============================================================================
st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.subheader("📋 Последние найденные вакансии")

results = st.session_state.graph_state.get("last_search_results", [])

if not results:
    st.write("🔍 Пока нет сохранённых результатов поиска. Запросите поиск вакансий в чате.")
else:
    for v in results:
        score = float(v.get("match_score") or 0.0)
        
        # Форматирование зарплаты
        salary_min = v.get("salary_min")
        salary_max = v.get("salary_max")
        salary_currency = v.get("salary_currency", "RUR")
        
        if salary_min and salary_max:
            salary_text = f"{salary_min:,} - {salary_max:,} {salary_currency}"
        elif salary_min:
            salary_text = f"от {salary_min:,} {salary_currency}"
        elif salary_max:
            salary_text = f"до {salary_max:,} {salary_currency}"
        else:
            salary_text = "не указана"
        
        st.markdown('<div class="vacancy-card">', unsafe_allow_html=True)
        st.markdown(f"### {v.get('title', 'Без названия')}")
        st.markdown(
            f"<p class='subtle'>{v.get('company', 'Не указано')} · "
            f"{v.get('location', 'Не указано')} · 💰 {salary_text}</p>",
            unsafe_allow_html=True,
        )
        
        # Match score прогресс
        st.progress(min(max(score, 0.0), 1.0), text=f"🎯 Match score: {score:.0%}")
        
        # Навыки
        key_skills = v.get("key_skills", [])
        # key_skills может быть списком или строкой
        if isinstance(key_skills, str):
            key_skills = [s.strip() for s in key_skills.split(",") if s.strip()]
        
        if key_skills:
            st.markdown(
                "".join([f'<span class="metric-pill">{s}</span>' for s in key_skills[:10]]),
                unsafe_allow_html=True,
            )
        
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**📅 Требуемый опыт:**")
            st.write(v.get("experience_required") or "Не указан")
        with c2:
            if v.get("url"):
                st.link_button("🔗 Открыть вакансию", v["url"])
        
        # Описание в экспандере
        description = v.get("description")
        if description:
            with st.expander("📝 Описание вакансии"):
                st.write(description[:1500] + "..." if len(description) > 1500 else description)
        
        st.markdown("</div>", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ==============================================================================
# Футер / Справка
# ==============================================================================
st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.subheader("ℹ️ Возможности MVP")

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("**✅ Чат с агентом**\n- Естественный диалог на русском")
with col2:
    st.markdown("**✅ Поиск вакансий**\n- По навыкам, локации, должности")
with col3:
    st.markdown("**✅ Загрузка резюме**\n- Текст или файл .txt")

st.markdown(
    '<p class="muted" style="margin-top: 1rem;">'
    '💡 Поддерживаются только текстовые файлы (.txt). '
    'Для PDF/DOCX потребуется дополнительная настройка парсера.'
    '</p>',
    unsafe_allow_html=True,
)
st.markdown('</div>', unsafe_allow_html=True)