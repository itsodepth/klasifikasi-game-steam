from flask import Flask, render_template, request
import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import LabelEncoder
import numpy as np
import os

app = Flask(__name__)

# --- 1. Persiapan Data & Pelatihan Model ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(BASE_DIR, 'Steam_2024_bestRevenue_1500.csv')

df = pd.read_csv(csv_path)

median_revenue = df['revenue'].median() 
df['is_high_revenue'] = (df['revenue'] > median_revenue).astype(int)

features = ['price', 'reviewScore', 'publisherClass', 'avgPlaytime', 'copiesSold']
df = df.dropna(subset=features + ['is_high_revenue'])

le = LabelEncoder()
df['publisherClass_encoded'] = le.fit_transform(df['publisherClass'].astype(str))

X = df[['price', 'reviewScore', 'publisherClass_encoded', 'avgPlaytime', 'copiesSold']]
y = df['is_high_revenue']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

dtree = DecisionTreeClassifier(
    criterion='entropy',
    max_depth=10,
    min_impurity_decrease=0.01,
    min_samples_leaf=2,
    random_state=42
)
dtree.fit(X_train, y_train)

# --- 2. Menghitung Metrik Dashboard ---
y_pred = dtree.predict(X_test)
accuracy = round(accuracy_score(y_test, y_pred) * 100, 2)
avg_data = df.groupby('is_high_revenue')[['price', 'reviewScore', 'avgPlaytime', 'copiesSold']].mean().round(2)

analisis_stats = {
    "rendah": {
        "price": avg_data.loc[0, 'price'],
        "review": avg_data.loc[0, 'reviewScore'],
        "playtime": avg_data.loc[0, 'avgPlaytime'],
        "copies": int(avg_data.loc[0, 'copiesSold'])
    },
    "tinggi": {
        "price": avg_data.loc[1, 'price'],
        "review": avg_data.loc[1, 'reviewScore'],
        "playtime": avg_data.loc[1, 'avgPlaytime'],
        "copies": int(avg_data.loc[1, 'copiesSold'])
    }
}

# --- 3. Rute Web Flask (Hanya 1 Halaman) ---
@app.route('/')
def index():
    # Kirim data stats ke index.html saat pertama kali dibuka
    return render_template('index.html', result=None, accuracy=accuracy, stats=analisis_stats)

@app.route('/predict', methods=['POST'])
def predict():
    if request.method == 'POST':
        price = float(request.form['price'])
        review_score = float(request.form['reviewScore'])
        pub_class = request.form['publisherClass']
        playtime = float(request.form['avgPlaytime'])
        copies_sold = int(request.form['copiesSold'])

        try:
            pub_class_encoded = le.transform([pub_class])[0]
        except ValueError:
            pub_class_encoded = 3 

        input_data = np.array([[price, review_score, pub_class_encoded, playtime, copies_sold]])
        prediction = dtree.predict(input_data)[0]
        
        if prediction == 1:
            hasil_prediksi = "TINGGI"
            rekomendasi = "Kombinasi performa penjualan dan retensi pemain Anda berada di jalur aman. Pertahankan kualitas layanan pasca-rilis untuk mengamankan posisi revenue Tinggi."
        else:
            hasil_prediksi = "RENDAH"
            rekomendasi = f"Meskipun game telah dirilis, model mendeteksi performa total berada di kategori revenue Rendah. Evaluasi kembali volume penjualan {copies_sold} atau naikkan retensi main melalui pembaruan konten."

        # Kembalikan ke halaman index beserta hasil prediksi dan data dashboard
        return render_template('index.html', result=hasil_prediksi, recommendation=rekomendasi, accuracy=accuracy, stats=analisis_stats)

if __name__ == '__main__':
    app.run(debug=True)