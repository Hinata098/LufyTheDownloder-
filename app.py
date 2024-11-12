from flask import Flask, render_template, request, send_file
import yt_dlp
import os

app = Flask(__name__)

# Create the downloads folder if it doesn't exist
os.makedirs('downloads', exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/preview', methods=['POST'])
def preview():
    url = request.form['url']
    ydl_opts = {'format': 'best'}
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            video_url = info.get('url', '')
            title = info.get("title", "Video")
            return render_template('index.html', video_url=video_url, title=title, url=url)
    except Exception as e:
        return f"Error: {str(e)}"

@app.route('/download', methods=['POST'])
def download():
    url = request.form['url']
    format_choice = request.form['format']  # "mp3" or "mp4"
    
    ydl_opts = {
        'format': 'bestaudio/best' if format_choice == 'mp3' else 'bestvideo+bestaudio/best',
        'outtmpl': 'downloads/%(title)s.%(ext)s',
    }

    if format_choice == 'mp3':
        ydl_opts['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            # Get the filename with the proper extension
            if format_choice == 'mp3':
                filename = os.path.join('downloads', f"{info['title']}.mp3")
            else:
                filename = ydl.prepare_filename(info)

            # Ensure the file exists before attempting to send it
            if not os.path.exists(filename):
                return f"Error: File not found ({filename})"
            
            return send_file(filename, as_attachment=True, download_name=os.path.basename(filename))
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080, debug=True)