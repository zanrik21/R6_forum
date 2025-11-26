Інструкція розгортання проекту
1. Клонувати репозиторій
git clone <repo>
cd r6_forum

2. Створити віртуальне середовище

python -m venv venv
venv\Scripts\activate  (Windows)
source venv/bin/activate (Linux/Mac)


3. Встановити залежності
pip install -r requirements.txt


4. Налаштувати БД
python manage.py migrate


5. Створити адміністратора
python manage.py createsuperuser


6. Запустити сервер
python manage.py runserver
