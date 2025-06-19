from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

if not os.path.exists('uploads'):
    os.makedirs('uploads')

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    if request.method == 'POST':
        file = request.files['file']
        if file and file.filename.endswith(('.xlsx', '.xls')):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            df = pd.read_excel(filepath)

            # Basit analiz örneği: ürün gruplarının adedi
            if 'ÜRÜN GRUBU' in df.columns:
                result = df['ÜRÜN GRUBU'].value_counts().reset_index()
                result.columns = ['Ürün Grubu', 'Adet']
            else:
                result = 'Excel dosyasında "ÜRÜN GRUBU" sütunu bulunamadı.'

    return render_template('index.html', result=result)

if __name__ == '__main__':
    app.run(debug=True)
