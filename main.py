# main.py
import sys
import os
import logging
from dotenv import load_dotenv

# ==============================================================================
# 1. Инициализация окружения и LangSmith
# ==============================================================================
# Загружаем переменные из .env (LANGCHAIN_API_KEY, HF_TOKEN и т.д.)
load_dotenv()

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("app.log", encoding="utf-8")
    ]
)
logger = logging.getLogger(__name__)

# Проверка подключения LangSmith
project_name = os.getenv("LANGCHAIN_PROJECT")
logger.info(f"✅ LangSmith подключен к проекту: {project_name or 'Не настроен'}")

# Импорты проекта (после загрузки env)
from src.agent.graph import create_graph

# ==============================================================================
# 2. Создание приложения
# ==============================================================================
def create_app():
    """Инициализирует и возвращает скомпилированный граф"""
    logger.info("=" * 60)
    logger.info("🚀 Запуск AI Career Partner")
    logger.info("=" * 60)
    
    try:
        app = create_graph()
        logger.info("✅ Граф успешно создан и готов к работе")
        return app
    except Exception as e:
        logger.error(f"❌ Ошибка создания графа: {e}")
        raise

# ==============================================================================
# 3. Режим 1: Демонстрационный сценарий (Автотест)
# ==============================================================================
def run_demo(app):
    """Запускает демонстрационный диалог без участия пользователя"""
    logger.info("\n🎬 Запуск демонстрационного сценария...\n")
    
    state = {"messages": []}
    
    # --- Шаг 1: Загрузка резюме ---
    logger.info("📄 Шаг 1: Пользователь загружает резюме")
    resume_text = """
    Я Python разработчик с опытом работы 3 года.
    Специализируюсь на backend-разработке.
    Ключевые навыки: Python, FastAPI, Docker, PostgreSQL, Git, Linux, Redis, Celery.
    Работал с микросервисной архитектурой и CI/CD.
    Ожидаемая зарплата: 180000 рублей.
    """
    
    result = app.invoke({"messages": state["messages"] + [("user", resume_text)]})
    state["messages"] = result["messages"]
    print("\n" + "="*60)
    print("🤖 АГЕНТ:")
    print(result["messages"][-1].content)
    print("="*60 + "\n")
    
    # --- Шаг 2: Поиск вакансий ---
    logger.info("🔍 Шаг 2: Пользователь просит найти вакансии")
    result = app.invoke({"messages": state["messages"] + [("user", "Найди вакансии по моему профилю")]})
    state["messages"] = result["messages"]
    print("\n" + "="*60)
    print("🤖 АГЕНТ:")
    print(result["messages"][-1].content)
    print("="*60 + "\n")
    
    # --- Шаг 3: Вопрос по вакансиям ---
    logger.info("❓ Шаг 3: Пользователь спрашивает про условия")
    result = app.invoke({"messages": state["messages"] + [("user", "Какая зарплата и стек в лучшей вакансии?")]})
    state["messages"] = result["messages"]
    print("\n" + "="*60)
    print("🤖 АГЕНТ:")
    print(result["messages"][-1].content)
    print("="*60 + "\n")
    
    logger.info("✅ Демонстрационный сценарий завершен")

# ==============================================================================
# 4. Режим 2: Интерактивный чат
# ==============================================================================
def run_interactive(app):
    """Запускает интерактивный чат с пользователем"""
    logger.info("\n💬 Запуск интерактивного режима (введите 'exit' для выхода)\n")
    
    state = {"messages": []}
    
    while True:
        try:
            user_input = input("\n👤 Вы: ").strip()
            
            if user_input.lower() in ["exit", "quit", "выход"]:
                logger.info("Завершение работы")
                print("\n👋 До свидания!")
                break
            
            if not user_input:
                continue
            
            # Инвоцируем граф с текущим состоянием (историей)
            result = app.invoke({"messages": state["messages"] + [("user", user_input)]})
            
            # Получаем ответ агента
            response = result["messages"][-1].content
            print(f"\n🤖 АГЕНТ: {response}")
            
            # Обновляем состояние (сохраняем историю диалога)
            state["messages"] = result["messages"]
            
        except KeyboardInterrupt:
            print("\n\n👋 До свидания!")
            break
        except Exception as e:
            logger.error(f"Ошибка в диалоге: {e}")
            print(f"\n❌ Произошла ошибка: {e}")

# ==============================================================================
# 5. Точка входа
# ==============================================================================
if __name__ == "__main__":
    # Создаем приложение
    app = create_app()
    
    # === ВЫБОР РЕЖИМА ===
    # Раскомментируйте нужный вариант:
    
    # Вариант 1: Автотест (демонстрация работы)
    # run_demo(app)
    
    # Вариант 2: Живой чат (по умолчанию)
    run_interactive(app)