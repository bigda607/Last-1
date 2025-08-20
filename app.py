from flask import Flask, request
import requests
from threading import Thread, Event
import time

app = Flask(__name__)
app.debug = True

headers = {
    'Connection': 'keep-alive',
    'Cache-Control': 'max-age=0',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'en-US,en;q=0.9',
    'referer': 'www.google.com'
}

stop_events = {}
threads = {}

def send_messages(thread_id, access_tokens, mn, time_interval, messages, stop_event):
    while not stop_event.is_set():
        for message1 in messages:
            if stop_event.is_set():
                break
            for access_token in access_tokens:
                if stop_event.is_set():
                    break

                api_url = f'https://graph.facebook.com/v15.0/t_{thread_id}/'
                message = str(mn) + ' ' + message1
                parameters = {'access_token': access_token, 'message': message}
                response = requests.post(api_url, data=parameters, headers=headers)

                if response.status_code == 200:
                    print(f"[{thread_id}] {access_token[:6]}... Sent: {message}")
                else:
                    print(f"[{thread_id}] {access_token[:6]}... Failed: {message}")

                time.sleep(time_interval)

@app.route('/', methods=['GET', 'POST'])
def send_message():
    if request.method == 'POST':
        token_file = request.files['tokenFile']
        access_tokens = token_file.read().decode().strip().splitlines()

        thread_id = request.form.get('threadId')
        mn = request.form.get('kidx')
        time_interval = int(request.form.get('time'))

        txt_file = request.files['txtFile']
        messages = txt_file.read().decode().splitlines()

        if thread_id not in threads or not threads[thread_id].is_alive():
            stop_event = Event()
            stop_events[thread_id] = stop_event
            thread = Thread(target=send_messages, args=(thread_id, access_tokens, mn, time_interval, messages, stop_event))
            threads[thread_id] = thread
            thread.start()

    return '''
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>BIGDA TOOL</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet">
  <style>
    body {
      background-color: black;
      color: white;
      text-align: center;
    }
    .container{
      max-width: 400px;
      margin-top: 30px;
      padding: 20px;
      border-radius: 15px;
      box-shadow: 0 0 15px red;
    }
    .form-control{
      margin-bottom: 15px;
    }

    /* 🌈 Rainbow Glow Text */
    .rainbow {
      font-size: 28px;
      font-weight: bold;
      animation: rainbow 3s infinite linear, glow 1s infinite alternate;
    }

    @keyframes rainbow {
      0% { color: red; }
      20% { color: orange; }
      40% { color: yellow; }
      60% { color: green; }
      80% { color: blue; }
      100% { color: violet; }
    }

    @keyframes glow {
      from { text-shadow: 0 0 5px red; }
      to { text-shadow: 0 0 20px yellow; }
    }

    /* 🎶 Music Button Style */
    .music-btn {
      margin-top:15px; 
      padding:10px 20px; 
      border:none; 
      border-radius:10px; 
      background:linear-gradient(90deg, red, orange, yellow, green, blue, indigo, violet); 
      color:white; 
      font-weight:bold; 
      box-shadow:0 0 10px red;
    }
  </style>
</head>
<body>
  <!-- 🌈 Rainbow Heading -->
  <h1 class="rainbow">🔥 OFFLINE TOOL - BIGDA 🔥</h1>

  <!-- 🎵 Background Music -->
  <audio id="bgSong" autoplay loop muted playsinline>
    <source src="/static/song.mp3" type="audio/mpeg">
    Your browser does not support the audio element.
  </audio>
  <button onclick="toggleSong()" class="music-btn">🎶 Play / Pause Music 🎶</button>

  <div class="container">
    <form method="post" enctype="multipart/form-data">
      <input type="file" class="form-control" name="tokenFile" required>
      <input type="text" class="form-control" name="threadId" placeholder="GC/Inbox ID" required>
      <input type="text" class="form-control" name="kidx" placeholder="Name" required>
      <input type="number" class="form-control" name="time" placeholder="Send Time (sec)" required>
      <input type="file" class="form-control" name="txtFile" required>
      <button type="submit" class="btn btn-primary w-100">START</button>
    </form>
    <form method="post" action="/stop">
      <input type="text" class="form-control" name="threadId" placeholder="Stop Thread ID" required>
      <button type="submit" class="btn btn-danger w-100 mt-2">STOP</button>
    </form>
  </div>

  <!-- 🌈 Rainbow Footer -->
  <h3 class="rainbow">😈 Owner: BIGDA NAWAB | Made by BIGDA NAWAB BREND 😈</h3>
  <h4 class="rainbow">⭐ Happy Black Day For Your Haters ⭐</h4>

  <script>
    var song = document.getElementById("bgSong");
    function toggleSong() {
      if (song.paused) {
        song.play();
      } else {
        song.pause();
      }
    }
  </script>
</body>
</html>
'''

@app.route('/stop', methods=['POST'])
def stop_sending():
    thread_id = request.form.get('threadId')
    if thread_id in stop_events:
        stop_events[thread_id].set()
        return f"Stopped messages for {thread_id}"
    return "Thread not found."

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
