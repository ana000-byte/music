# استخدام نسخة بايثون خفيفة
FROM python:3.10-slim

# تثبيت FFmpeg من نظام التشغيل
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

# تحديد مجلد العمل داخل الحاوية
WORKDIR /app

# نسخ ملف المتطلبات وتثبيتها
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# نسخ باقي ملفات المشروع
COPY . .

# أمر تشغيل البوت
CMD ["python", "main.py"]
