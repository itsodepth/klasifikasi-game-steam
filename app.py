import os
import pandas as pd
import numpy as np
from flask import Flask, jsonify, request, render_template
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier, _tree
from sklearn.metrics import confusion_matrix, classification_report

app = Flask(__name__)

# --------------------------------------------------------------------
# 1. LOAD DATASET & PREPROCESSING
# --------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "consumer_electronics_sales_data.csv")

# Definisikan mapping kategorikal yang konsisten
category_map = {
    'Smartphones': 0, 
    'Smart Watches': 1, 
    'Tablets': 2, 
    'Laptops': 3, 
    'Headphones': 4
}
category_reverse = {v: k for k, v in category_map.items()}

brand_map = {
    'Other Brands': 0, 
    'Samsung': 1, 
    'Sony': 2, 
    'HP': 3, 
    'Apple': 4
}
brand_reverse = {v: k for k, v in brand_map.items()}

# Membaca data dan melatih model saat start
df = pd.read_csv(DATA_PATH)

# Buat dataframe versi encoded untuk model training
df_model = df.copy()
df_model['ProductCategory_encoded'] = df_model['ProductCategory'].map(category_map)
df_model['ProductBrand_encoded'] = df_model['ProductBrand'].map(brand_map)

# Tentukan Fitur dan Label
feature_cols = [
    'ProductCategory_encoded', 
    'ProductBrand_encoded', 
    'ProductPrice', 
    'CustomerAge', 
    'CustomerGender', 
    'PurchaseFrequency', 
    'CustomerSatisfaction'
]
X = df_model[feature_cols]
y = df_model['PurchaseIntent']

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Latih Decision Tree Classifier berdasarkan parameter RapidMiner:
# - criterion: gain ratio (di sklearn didekati dengan 'entropy' / Information Gain)
# - maximal depth: 10
# - minimal gain (prepruning): 0.01 (min_impurity_decrease)
# - minimal leaf size: 2 (min_samples_leaf)
# - split data: 80% train, 20% test (test_size=0.2)
model = DecisionTreeClassifier(
    criterion='entropy',
    max_depth=10,
    min_samples_leaf=2,
    min_impurity_decrease=0.01,
    random_state=42
)
model.fit(X_train, y_train)

# Hitung Akurasi
train_accuracy = model.score(X_train, y_train)
test_accuracy = model.score(X_test, y_test)
y_pred = model.predict(X_test)

print("=== HASIL PENGUJIAN MODEL ===")
print(f"Akurasi Training: {train_accuracy * 100:.2f}%")
print(f"Akurasi Testing: {test_accuracy * 100:.2f}%")
print("\nConfusion Matrix:")
print(confusion_matrix(y_test, y_pred))
print("\nLaporan Klasifikasi:")
print(classification_report(y_test, y_pred))
print("=============================")

# Hitung Feature Importances
importances = model.feature_importances_
feature_labels = [
    'Kategori Produk', 
    'Brand Produk', 
    'Harga Produk', 
    'Umur Pelanggan', 
    'Gender Pelanggan', 
    'Frekuensi Pembelian', 
    'Tingkat Kepuasan'
]
feature_importance_list = [
    {'feature': label, 'importance': round(float(imp) * 100, 2)}
    for label, imp in zip(feature_labels, importances)
]
# Sort berdasarkan tingkat kepentingan tertinggi
feature_importance_list = sorted(feature_importance_list, key=lambda x: x['importance'], reverse=True)


# Ekstraksi Aturan Utama Decision Tree untuk Penjelasan Teks
def get_rules(tree, feature_names):
    tree_ = tree.tree_
    feature_name = [
        feature_names[i] if i != _tree.TREE_UNDEFINED else "undefined!"
        for i in tree_.feature
    ]
    
    rules = []
    
    def recurse(node, depth, path):
        if tree_.feature[node] != _tree.TREE_UNDEFINED:
            name = feature_name[node]
            threshold = tree_.threshold[node]
            
            # Cabang Kiri (<= threshold)
            left_path = path + [f"{name} <= {round(threshold, 2)}"]
            recurse(tree_.children_left[node], depth + 1, left_path)
            
            # Cabang Kanan (> threshold)
            right_path = path + [f"{name} > {round(threshold, 2)}"]
            recurse(tree_.children_right[node], depth + 1, right_path)
        else:
            value = tree_.value[node][0]
            samples = tree_.n_node_samples[node]
            class_0_count = value[0]
            class_1_count = value[1]
            total = class_0_count + class_1_count
            
            prob_purchase = class_1_count / total
            
            if samples > 150:
                if prob_purchase >= 0.75:
                    rules.append({
                        'conditions': path,
                        'outcome': 'Berniat Membeli',
                        'probability': round(prob_purchase * 100, 1),
                        'samples': int(samples)
                    })
                elif prob_purchase <= 0.15:
                    rules.append({
                        'conditions': path,
                        'outcome': 'Tidak Berniat Membeli',
                        'probability': round((1 - prob_purchase) * 100, 1),
                        'samples': int(samples)
                    })
                    
    recurse(0, 1, [])
    rules = sorted(rules, key=lambda x: x['samples'], reverse=True)[:4]
    return rules

english_feature_names = [
    'Kategori Produk', 
    'Brand Produk', 
    'Harga Produk ($)', 
    'Umur', 
    'Gender', 
    'Frekuensi Pembelian', 
    'Kepuasan Pelanggan'
]
extracted_rules = get_rules(model, english_feature_names)


# Ekstraksi Struktur Pohon untuk Visualisasi Bagan Pohon Dinamis di Frontend
def get_tree_json(tree, feature_names):
    tree_ = tree.tree_
    
    def recurse(node):
        if tree_.feature[node] != _tree.TREE_UNDEFINED:
            name = feature_names[tree_.feature[node]]
            threshold = tree_.threshold[node]
            left_child = int(tree_.children_left[node])
            right_child = int(tree_.children_right[node])
            
            return {
                "name": name,
                "threshold": round(float(threshold), 2),
                "is_leaf": False,
                "left": recurse(left_child),
                "right": recurse(right_child)
            }
        else:
            value = tree_.value[node][0]
            class_0 = float(value[0])
            class_1 = float(value[1])
            total = class_0 + class_1
            prob = class_1 / total
            outcome = "Membeli" if prob >= 0.5 else "Tidak Membeli"
            confidence = round(prob * 100, 1) if prob >= 0.5 else round((1 - prob) * 100, 1)
            
            return {
                "name": outcome,
                "is_leaf": True,
                "confidence": confidence,
                "samples": int(tree_.n_node_samples[node])
            }
            
    return recurse(0)

tree_structure = get_tree_json(model, english_feature_names)

# --------------------------------------------------------------------
# 2. ROUTES & API ENDPOINTS
# --------------------------------------------------------------------

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/model-info', methods=['GET'])
def get_model_info():
    total_samples = len(df)
    buyer_count = int((df['PurchaseIntent'] == 1).sum())
    non_buyer_count = int((df['PurchaseIntent'] == 0).sum())
    
    return jsonify({
        'accuracy': round(test_accuracy * 100, 2),
        'train_accuracy': round(train_accuracy * 100, 2),
        'total_samples': total_samples,
        'buyer_count': buyer_count,
        'non_buyer_count': non_buyer_count,
        'feature_importances': feature_importance_list,
        'rules': extracted_rules,
        'tree_structure': tree_structure
    })

@app.route('/api/data', methods=['GET'])
def get_data():
    limit_param = request.args.get('limit', '100')
    df_display = df.copy()
    
    # Format agar lebih user-friendly
    df_display['ProductPrice'] = df_display['ProductPrice'].round(2)
    df_display['CustomerGender'] = df_display['CustomerGender'].map({0: 'Laki-laki', 1: 'Perempuan'})
    df_display['PurchaseIntent'] = df_display['PurchaseIntent'].map({0: 'Tidak Membeli', 1: 'Membeli'})
    
    if limit_param == '100':
        data_subset = df_display.head(100)
    else:
        data_subset = df_display
        
    records = data_subset.to_dict(orient='records')
    return jsonify({
        'count': len(records),
        'total_rows': len(df),
        'data': records
    })

@app.route('/api/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        
        category = data.get('ProductCategory')
        brand = data.get('ProductBrand')
        price = float(data.get('ProductPrice'))
        age = int(data.get('CustomerAge'))
        gender = int(data.get('CustomerGender'))  # 0: Laki-laki, 1: Perempuan
        frequency = int(data.get('PurchaseFrequency'))
        satisfaction = int(data.get('CustomerSatisfaction'))
        
        if category not in category_map:
            return jsonify({'error': f'Kategori produk {category} tidak dikenal'}), 400
        if brand not in brand_map:
            return jsonify({'error': f'Brand produk {brand} tidak dikenal'}), 400
            
        encoded_category = category_map[category]
        encoded_brand = brand_map[brand]
        
        input_data = pd.DataFrame([[
            encoded_category,
            encoded_brand,
            price,
            age,
            gender,
            frequency,
            satisfaction
        ]], columns=feature_cols)
        
        pred = int(model.predict(input_data)[0])
        prob = model.predict_proba(input_data)[0]
        confidence = round(float(prob[pred]) * 100, 1)
        
        recommendations = []
        if pred == 1:
            recommendations.append(
                f"Pelanggan ini memiliki minat beli yang <strong>Tinggi ({confidence}%)</strong>!"
            )
            recommendations.append(
                f"Tawarkan program bundling aksesoris tambahan atau voucher loyalitas untuk produk <strong>{category} {brand}</strong> guna memaksimalkan transaksi."
            )
            if price > 1500:
                recommendations.append(
                    f"Karena harga produk cukup tinggi (${price:,.2f}), berikan opsi cicilan 0% atau gratis perlindungan tambahan (garansi) selama 2 tahun untuk mengamankan transaksi."
                )
            if satisfaction < 3:
                recommendations.append(
                    f"Meskipun berminat membeli, tingkat kepuasan pelanggan saat ini rendah ({satisfaction}/5). Pastikan pelayanan cepat dan berikan kartu garansi purna jual premium."
                )
        else:
            recommendations.append(
                f"Pelanggan ini memiliki minat beli yang <strong>Rendah (probabilitas membeli hanya {round(float(prob[1])*100, 1)}%)</strong>."
            )
            if satisfaction < 3:
                recommendations.append(
                    f"<strong>Fokus Utama:</strong> Tingkatkan kepuasan pelanggan (saat ini {satisfaction}/5). Tawarkan bantuan live chat atau panduan produk interaktif."
                )
            if price > 1800:
                recommendations.append(
                    f"Harga produk (${price:,.2f}) tergolong tinggi. Coba rekomendasikan produk alternatif dari brand <strong>{brand}</strong> dengan harga di bawah $1,000, atau tawarkan potongan harga langsung sebesar 15%."
                )
            if frequency < 5:
                recommendations.append(
                    f"Frekuensi transaksi pelanggan ini rendah ({frequency} kali). Kirimkan newsletter berkala atau tawarkan diskon khusus transaksi pertama di platform Anda."
                )
            if not recommendations or len(recommendations) == 1:
                recommendations.append(
                    f"Tawarkan sesi konsultasi produk gratis untuk membantu pelanggan memahami keunggulan <strong>{category} {brand}</strong>."
                )
                
        return jsonify({
            'prediction': pred,
            'confidence': confidence,
            'recommendations': recommendations
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5001)