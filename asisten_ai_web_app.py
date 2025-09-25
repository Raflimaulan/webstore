# Nama file: asisten_ai_web_app.py
# Deskripsi: Aplikasi web sederhana menggunakan Flask yang mensimulasikan asisten AI.
# Catatan: Karena ini adalah aplikasi web, perintah seperti 'buka kalkulator' akan
# dieksekusi di server, bukan di komputer pengguna. Ini berguna untuk lingkungan
# yang lebih terkontrol, tetapi tidak untuk penggunaan pribadi.

from flask import Flask, request, jsonify, render_template_string
import datetime
import webbrowser
import os
import sys

# Inisialisasi aplikasi Flask
app = Flask(__name__)

# Fungsi untuk mendapatkan waktu saat ini
def get_current_time():
    """Mengembalikan waktu dan tanggal saat ini."""
    now = datetime.datetime.now()
    return now.strftime("Waktu saat ini adalah %H:%M:%S pada tanggal %Y-%m-%d.")

# Fungsi untuk membuka sebuah website
def open_website(url):
    """Membuka URL yang diberikan."""
    try:
        webbrowser.open(url)
        return f"Berhasil membuka website {url}."
    except Exception as e:
        return f"Gagal membuka website. Error: {e}"

# Fungsi untuk membuka aplikasi tertentu
def open_app(app_name):
    """Mencoba untuk membuka aplikasi di server."""
    if sys.platform == "win32":
        try:
            os.startfile(app_name)
            return f"Berhasil membuka aplikasi {app_name} di server."
        except FileNotFoundError:
            return f"Aplikasi '{app_name}' tidak ditemukan di server."
        except Exception as e:
            return f"Gagal membuka aplikasi di server. Error: {e}"
    elif sys.platform == "darwin":
        try:
            os.system(f"open /Applications/{app_name}.app")
            return f"Berhasil membuka aplikasi {app_name} di server."
        except Exception as e:
            return f"Gagal membuka aplikasi di server. Error: {e}"
    else:
        return "Fungsi ini hanya mendukung Windows dan macOS."

# Template HTML untuk antarmuka web
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Asisten AI Sederhana</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { font-family: 'Inter', sans-serif; }
    </style>
</head>
<body class="bg-gray-100 flex items-center justify-center min-h-screen">
    <div class="bg-white rounded-xl shadow-lg p-8 w-full max-w-lg mx-4">
        <h1 class="text-3xl font-bold text-center text-gray-800 mb-4">Asisten AI</h1>
        <p class="text-center text-gray-600 mb-6">Ketik perintah dan tekan 'Enter'.</p>

        <div id="chat-box" class="bg-gray-50 h-64 overflow-y-auto rounded-lg p-4 mb-4 border border-gray-200">
            <div class="text-gray-500 mb-2">Asisten: Halo! Saya adalah asisten virtual Anda.</div>
            <div class="text-gray-500 mb-2">Saya bisa melakukan beberapa hal sederhana. Coba katakan:</div>
            <div class="text-gray-500 mb-2">- 'tanya jam'</div>
            <div class="text-gray-500 mb-2">- 'buka google'</div>
            <div class="text-gray-500 mb-2">- 'buka kalkulator'</div>
        </div>

        <div class="flex">
            <input type="text" id="user-input" placeholder="Ketik perintah di sini..."
                   class="flex-1 rounded-l-lg border-t border-b border-l border-gray-300 p-3 focus:outline-none focus:ring-2 focus:ring-blue-500 transition duration-200">
            <button id="send-btn"
                    class="bg-blue-500 text-white p-3 rounded-r-lg hover:bg-blue-600 transition duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500">
                Kirim
            </button>
        </div>
    </div>

    <script>
        document.addEventListener('DOMContentLoaded', () => {
            const userInput = document.getElementById('user-input');
            const sendBtn = document.getElementById('send-btn');
            const chatBox = document.getElementById('chat-box');

            const addMessage = (sender, message) => {
                const messageDiv = document.createElement('div');
                messageDiv.classList.add('mb-2');
                const senderSpan = document.createElement('span');
                senderSpan.classList.add('font-bold');
                senderSpan.textContent = sender + ': ';
                messageDiv.appendChild(senderSpan);
                messageDiv.appendChild(document.createTextNode(message));
                chatBox.appendChild(messageDiv);
                chatBox.scrollTop = chatBox.scrollHeight;
            };

            const sendMessage = async () => {
                const command = userInput.value.trim();
                if (command === '') return;

                addMessage('Anda', command);
                userInput.value = '';

                try {
                    const response = await fetch('/process', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({ command: command }),
                    });

                    const data = await response.json();
                    addMessage('Asisten', data.response);
                } catch (error) {
                    addMessage('Asisten', 'Terjadi kesalahan. Silakan coba lagi.');
                    console.error('Error:', error);
                }
            };

            sendBtn.addEventListener('click', sendMessage);
            userInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    sendMessage();
                }
            });
        });
    </script>
</body>
</html>
"""

# Route utama untuk menampilkan halaman web
@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

# Route untuk memproses perintah pengguna
@app.route('/process', methods=['POST'])
def process_command():
    data = request.json
    user_command = data.get('command', '').lower()
    response = "Maaf, saya tidak mengerti perintah itu."

    if "tanya jam" in user_command:
        response = get_current_time()
    elif "buka " in user_command:
        # Menangani perintah 'buka [website/aplikasi]'
        parts = user_command.split("buka ", 1)
        if len(parts) > 1:
            target = parts[1].strip()
            if "google" in target:
                response = open_website("https://www.google.com")
            elif "kalkulator" in target:
                response = open_app("calc.exe")  # Ganti dengan "Calculator" jika di macOS
            else:
                response = "Maaf, saya hanya bisa membuka Google dan Kalkulator."
    
    return jsonify({"response": response})

# Jalankan server jika skrip dieksekusi langsung
if __name__ == '__main__':
    # Untuk menjalankan di lingkungan produksi, gunakan gunicorn atau uWSGI
    # Debug=True hanya untuk pengembangan
    app.run(debug=True)
