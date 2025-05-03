from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import shutil
from werkzeug.utils import secure_filename
from threading import Thread
from rao_extractor import extract_tables_from_pdf, extract_custom_page
from flask import send_from_directory

app = Flask(__name__, static_folder='static')

app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['STATIC_FOLDER'] = 'static'

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['STATIC_FOLDER'], exist_ok=True)

# Global store for progress and logs
progress_data = {"progress": 0, "logs": [], "filename": ""}


def run_extraction(pdf_path, page_range, output_path, custom_page):
    progress_data["logs"].append(f"📄 Processing file: {os.path.basename(pdf_path)}")
    logs, _ = extract_tables_from_pdf(pdf_path, page_range, output_path, progress_data)

    progress_data["logs"].extend(logs)

    if custom_page:
        custom_output = output_path.replace('.xlsx', '_Custom.xlsx')
        custom_logs = extract_custom_page(pdf_path, custom_page, custom_output)
        progress_data["logs"].append(f"📄 Custom page saved as: {os.path.basename(custom_output)}")
        progress_data["logs"].extend(custom_logs)

    shutil.copyfile(output_path, os.path.join(app.config['STATIC_FOLDER'], os.path.basename(output_path)))
    progress_data["filename"] = os.path.basename(output_path)
    progress_data["progress"] = 100


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        uploaded_file = request.files['pdf_file']
        page_range = request.form.get('page_range')
        custom_page = request.form.get('custom_page')
        save_name = request.form.get('save_name')

        filename = secure_filename(uploaded_file.filename)
        pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        uploaded_file.save(pdf_path)

        if not save_name.lower().endswith('.xlsx'):
            save_name += ".xlsx"

        output_path = os.path.join(app.config['UPLOAD_FOLDER'], save_name)

        # Reset global tracker
        progress_data["progress"] = 0
        progress_data["logs"] = []
        progress_data["filename"] = ""

        # Start extraction
        Thread(target=run_extraction, args=(pdf_path, page_range, output_path, custom_page)).start()

        return jsonify(success=True, filename=save_name)

    return render_template("index.html")


@app.route('/progress')
def progress():
    return jsonify(progress=progress_data["progress"], logs=progress_data["logs"], filename=progress_data["filename"])


@app.route('/static/<path:filename>')
def download_file(filename):
    return send_from_directory(app.config['STATIC_FOLDER'], filename)
from flask import Response

@app.route('/robots.txt')
def robots_txt():
    content = """User-agent: *
Allow: /
Sitemap: https://rao-extractor-surf-analysis.onrender.com/sitemap.xml
"""
    return Response(content, mimetype='text/plain')


@app.route('/sitemap.xml')
def sitemap_xml():
    content = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://rao-extractor-surf-analysis.onrender.com/</loc>
    <changefreq>weekly</changefreq>
    <priority>1.0</priority>
  </url>
</urlset>
"""
    return Response(content, mimetype='application/xml')

@app.route('/google9358c78bdb4eb68e.html')
def google_verify():
    return send_from_directory('static', 'google9358c78bdb4eb68e.html')

if __name__ == '__main__':
    app.run(debug=True)
