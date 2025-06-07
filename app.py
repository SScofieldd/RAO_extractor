from flask import Flask, render_template, request, jsonify, send_from_directory, Response
import os
import shutil
from werkzeug.utils import secure_filename
from threading import Thread
from rao_extractor import extract_tables_from_pdf, extract_custom_page

app = Flask(__name__, static_folder='static')

app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['STATIC_FOLDER'] = 'static'

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['STATIC_FOLDER'], exist_ok=True)

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


# ✅ Homepage (About Me + Links to Tools)
@app.route('/')
def homepage():
    return render_template('home.html')


# ✅ Tool Page
@app.route('/rao-extractor', methods=['GET', 'POST'])
def rao_tool():
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

        # Reset progress
        progress_data.update({"progress": 0, "logs": [], "filename": ""})

        # Start thread
        Thread(target=run_extraction, args=(pdf_path, page_range, output_path, custom_page)).start()

        return jsonify(success=True, filename=save_name)

    return render_template("index.html")


# ✅ Live Progress
@app.route('/progress')
def progress():
    return jsonify(progress=progress_data["progress"], logs=progress_data["logs"], filename=progress_data["filename"])


# ✅ Static File Download
@app.route('/static/<path:filename>')
def download_file(filename):
    return send_from_directory(app.config['STATIC_FOLDER'], filename)


# ✅ SEO Files
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

from flask import Flask, render_template, request, jsonify

# ... (your existing code above)

@app.route('/orcaflex-toolkit')
def orcaflex_toolkit():
    return render_template('orcaflex_toolkit.html')

# Vessel Corner Generator (AJAX)
@app.route('/orcaflex-toolkit/corner', methods=['POST'])
def orcaflex_corner():
    try:
        overall_length = float(request.form['overall_length'])
        lbp = float(request.form['lbp'])
        breadth = float(request.form['breadth'])
        depth = float(request.form['depth'])

        def round_up(val, decimals=2):
            import math
            factor = 10 ** decimals
            return math.ceil(val * factor) / factor
        def truncate(val, decimals=2):
            factor = 10 ** decimals
            return int(val * factor) / factor

        half_lbp = lbp / 2
        half_breadth = breadth / 2
        bow_x = round(overall_length / 2, 2)
        z_top = round_up(0.508 * depth, 2)
        z_bottom = truncate(-0.492 * depth, 2)

        coords = [
            (bow_x, 0, z_top),
            (half_lbp - 5,  half_breadth, z_top),
            (-half_lbp,     half_breadth, z_top),
            (-half_lbp,    -half_breadth, z_top),
            (half_lbp - 5, -half_breadth, z_top),
            (half_lbp, 0, z_bottom),
            (half_lbp - 5,  half_breadth, z_bottom),
            (-half_lbp,     half_breadth, z_bottom),
            (-half_lbp,    -half_breadth, z_bottom),
            (half_lbp - 5, -half_breadth, z_bottom),
        ]
        result = "\n".join([f"{x:.2f}\t{y:.2f}\t{z:.2f}" for x, y, z in coords])
        return jsonify(result=result)
    except Exception as e:
        return jsonify(result="⚠️ Error: " + str(e))

# Stiffness Calculator (AJAX)
@app.route('/orcaflex-toolkit/stiffness', methods=['POST'])
def orcaflex_stiffness():
    try:
        D = float(request.form['d'])
        Su = float(request.form['su'])
        Nc = 5.14
        z = 0.5 * D
        ρ = float(request.form.get('rho', '0'))

        Vk = (20 / D) * (Su + ρ * z)
        Nk = (20 * Nc * Su) / D

        result = f"Shear Stiffness (Vk): <b>{Vk:.6f}</b><br>Normal Stiffness (Nk): <b>{Nk:.6f}</b>"
        return jsonify(result=result)
    except Exception as e:
        return jsonify(result="⚠️ Error: " + str(e))

# Drag Coefficient Calculator (AJAX)
@app.route('/orcaflex-toolkit/drag', methods=['POST'])
def orcaflex_drag():
    import numpy as np
    try:
        # Inputs
        D = float(request.form['d'])
        eps = float(request.form['epsilon'])
        lambdaT = 1.0

        # --- Constants and preliminary calculations ---
        e_by_D = eps / D
        E = e_by_D * 1000
        lamR = 7 - 6 * np.exp(-0.11 * E)
        log10_Reea = 5.55 + 0.19 * np.exp(-0.32 * (E**0.35))
        log10_Reeb = 5.65 + 0.22 * np.exp(-0.7 * (E**0.5))
        Reea = 10**log10_Reea
        Reeb = 10**log10_Reeb
        b = (4.5 / (1 + ((np.log10(E) - 0.15)**2) * 5)) + 4
        CM = 1.04 - 0.47 * np.exp(-((0.9 * E) + 0.55 * (E**0.5))) + 0.11 * (1 - np.exp(-0.0008 * E**2))
        CB = 1.1 - 0.83 * np.exp(-(0.01 * E + 0.34 * (E**0.5)))
        n = 0.06 * np.exp(-0.04 * E**2)

        ree_list = [
            30000, 40000, 50000, 100000, 280000, 300000, 350000, 400000, 450000,
            500000, 600000, 700000, 800000, 1000000, 1500000, 2000000,
            5000000, 10000000, 20000000, 30000000
        ]

        rows = []
        # Table 1: Cd*, R
        cd_star_list, r_list = [], []
        for Ree in ree_list:
            Cd_star = 0.27 + 0.93 * np.exp(-1.65e-7 * (Ree * 1e-5)**10) if Ree < Reea else 0.27
            R = np.log10(Ree / Reeb)
            cd_star_list.append(Cd_star)
            r_list.append(R)

        # Table 2: f1, Cd, Cd*, lambdaR
        f1_list, cd_list, cd_star2_list, lambdaR_list = [], [], [], []
        for i, Ree in enumerate(ree_list):
            R = r_list[i]
            Cd_star1 = cd_star_list[i]
            f1 = 1 - np.exp(-(R + 2 * b * R**2 - b * R**3))
            Cd = f1 * (CM - CB) + CB - n * (1 - np.exp(-(0.5 * (R**2)**2)))
            lambdaR = 1 + (lamR - 1) * (1 - np.exp(-5 * (Ree * 1e4)**2))
            Cd_star2 = Cd_star1 if Ree < Reea else Cd

            f1_list.append(f1)
            cd_list.append(Cd)
            cd_star2_list.append(Cd_star2)
            lambdaR_list.append(lambdaR)

        # Table 3: Re and Cd (final output)
        re_list, final_cd_list = [], []
        for i in range(len(ree_list)):
            Re = ree_list[i] / (lambdaR_list[i] * lambdaT)
            Cd = cd_star2_list[i] * (1 + 2 * eps / D)
            re_list.append(Re)
            final_cd_list.append(Cd)

        # Prepare output table
        table = "<b>Re</b>&emsp;<b>Cd</b><br>" + "<br>".join(
            f"{re_list[i]:.2f}&emsp;{final_cd_list[i]:.4f}" for i in range(len(re_list))
        )

        return jsonify(result=f"<pre>{table}</pre>")
    except Exception as e:
        return jsonify(result="⚠️ Error: " + str(e))



if __name__ == '__main__':
    app.run(debug=True)
