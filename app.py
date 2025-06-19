import os
from flask import Flask, render_template, request
import pandas as pd
from itertools import combinations
from collections import Counter

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    if request.method == 'POST':
        file = request.files['file']
        analysis_type = request.form['analysis']

        if file and file.filename.endswith('.xlsx'):
            df = pd.read_excel(file)

            if analysis_type == 'sales':
                result = product_sales(df)
            elif analysis_type == 'lift':
                result = lift_analysis(df)
            elif analysis_type == 'frequent':
                result = top_combinations(df)
            elif analysis_type == 'customer':
                result = customer_type(df)

    return render_template('index.html', result=result)

def product_sales(df):
    df = df.drop_duplicates(subset=['FATURA NO', 'ÜRÜN GRUBU'])
    sales = df['ÜRÜN GRUBU'].value_counts().reset_index()
    sales.columns = ['Ürün Grubu', 'Fatura Sayısı']
    return sales.to_html(index=False, classes='table table-bordered')

def lift_analysis(df):
    transactions = df.groupby('FATURA NO')['ÜRÜN GRUBU'].apply(set)
    all_combinations = []

    for items in transactions:
        all_combinations.extend(combinations(sorted(items), 2))

    combo_counts = Counter(all_combinations)
    result_df = pd.DataFrame(combo_counts.items(), columns=['Ürün Kombinasyonu', 'Fatura Sayısı'])
    result_df[['Ürün 1', 'Ürün 2']] = pd.DataFrame(result_df['Ürün Kombinasyonu'].tolist(), index=result_df.index)
    result_df.drop(columns='Ürün Kombinasyonu', inplace=True)

    total_fat = len(transactions)
    result_df['Lift Oranı'] = result_df['Fatura Sayısı'] / total_fat
    result_df.sort_values(by='Lift Oranı', ascending=False, inplace=True)

    return result_df.to_html(index=False, classes='table table-bordered')

def top_combinations(df):
    transactions = df.groupby('FATURA NO')['ÜRÜN GRUBU'].apply(set)
    combos = []

    for items in transactions:
        combos.extend(combinations(sorted(items), 2))

    count_df = pd.DataFrame(Counter(combos).most_common(10), columns=['Ürünler', 'Adet'])
    count_df[['Ürün 1', 'Ürün 2']] = pd.DataFrame(count_df['Ürünler'].tolist(), index=count_df.index)
    count_df.drop(columns='Ürünler', inplace=True)

    return count_df.to_html(index=False, classes='table table-striped')

def customer_type(df):
    # Örnek bir yapı: müşteri tipi bilgisi varsa gruplama yapılabilir
    if 'MÜŞTERİ TİPİ' in df.columns:
        group = df.groupby('MÜŞTERİ TİPİ')['FATURA NO'].nunique().reset_index()
        group.columns = ['Müşteri Tipi', 'Fatura Sayısı']
        return group.to_html(index=False, classes='table table-hover')
    else:
        return "<p>Müşteri tipi sütunu bulunamadı.</p>"

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
