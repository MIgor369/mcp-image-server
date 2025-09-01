from flask import Flask, jsonify, request
import requests
import os

app = Flask(__name__)

# Вставь свой OpenAI API ключ (https://platform.openai.com/api-keys)
DALL_E_API_KEY = os.getenv("OPENAI_API_KEY", "sk-ваш-ключ-здесь")

# MCP Manifest — обязательный файл для интеграции с ИИ
@app.route("/.well-known/mcp.json")
def manifest():
    return jsonify({
        "version": "0.0.1",
        "name": "ImageGenMCP",
        "description": "Генерация фото для Telegram, ВК, YouTube",
        "functions": [
            {
                "name": "generate_telegram_avatar",
                "description": "Создаёт круглую иконку 240x240 для Telegram по теме",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "topic": {"type": "string", "description": "Тема аватара"}
                    },
                    "required": ["topic"]
                }
            },
            {
                "name": "generate_vk_cover",
                "description": "Создаёт шапку для ВКонтакте (1590x400) по бренду и цветам",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "brand": {"type": "string"},
                        "colors": {"type": "string"}
                    },
                    "required": ["brand"]
                }
            },
            {
                "name": "generate_youtube_thumbnail",
                "description": "Создаёт превью для YouTube (1280x720) с заголовком и эмоцией",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "emotion": {"type": "string", "enum": ["удивление", "радость", "страх", "гнев"]}
                    },
                    "required": ["title"]
                }
            }
        ]
    })

# Генерация аватара Telegram
@app.route("/generate_telegram_avatar", methods=["POST"])
def generate_telegram_avatar():
    topic = request.json.get("topic", "технологии")
    prompt = f"Minimalist circular logo, 240x240, white background, theme: {topic}, modern, clean, no text"
    return generate_image(prompt, "256x256")

# Генерация шапки ВКонтакте
@app.route("/generate_vk_cover", methods=["POST"])
def generate_vk_cover():
    brand = request.json.get("brand", "MyBrand")
    colors = request.json.get("colors", "blue, white")
    prompt = f"Cover for VK group, 1590x400, modern design, brand: {brand}, colors: {colors}, abstract background"
    return generate_image(prompt, "1792x1024")

# Генерация превью YouTube
@app.route("/generate_youtube_thumbnail", methods=["POST"])
def generate_youtube_thumbnail():
    title = request.json.get("title", "Новое видео")
    emotion = request.json.get("emotion", "удивление")
    prompt = f"YouTube thumbnail, 1280x720, bold text: '{title}', person with {emotion} expression, clickbait style"
    return generate_image(prompt, "1280x720")

# Универсальная функция генерации через DALL·E
def generate_image(prompt, size):
    try:
        response = requests.post(
            "https://api.openai.com/v1/images/generations",
            headers={"Authorization": f"Bearer {DALL_E_API_KEY}"},
            json={"prompt": prompt, "n": 1, "size": size}
        )
        data = response.json()
        image_url = data["data"][0]["url"]
        return jsonify({"image_url": image_url, "prompt": prompt})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    print("🔧 MCP-сервер запущен на http://localhost:5000")
    print("📌 Добавь в Make.com или ChatGPT: http://localhost:5000/.well-known/mcp.json")
    app.run(port=5000, debug=True)