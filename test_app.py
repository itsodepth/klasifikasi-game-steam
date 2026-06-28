import unittest
import json
from app import app

class FlaskAppTestCase(unittest.TestCase):
    def setUp(self):
        # Mengatur Flask App ke mode testing
        app.config['TESTING'] = True
        app.config['DEBUG'] = False
        self.client = app.test_client()

    def test_index_route(self):
        """Menguji apakah halaman utama (HTML) berhasil di-load dengan status 200"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        # Pastikan konten bertipe HTML
        self.assertIn('text/html', response.content_type)

    def test_model_info_route(self):
        """Menguji endpoint /api/model-info untuk detail model dan performa"""
        response = self.client.get('/api/model-info')
        self.assertEqual(response.status_code, 200)
        self.assertIn('application/json', response.content_type)
        
        data = json.loads(response.data)
        # Memastikan semua key yang diperlukan ada dalam response JSON
        self.assertIn('accuracy', data)
        self.assertIn('train_accuracy', data)
        self.assertIn('total_samples', data)
        self.assertIn('buyer_count', data)
        self.assertIn('non_buyer_count', data)
        self.assertIn('feature_importances', data)
        self.assertIn('rules', data)
        self.assertIn('tree_structure', data)
        
        # Memastikan tipe data benar
        self.assertIsInstance(data['accuracy'], float)
        self.assertIsInstance(data['feature_importances'], list)

    def test_data_route_default(self):
        """Menguji endpoint /api/data dengan parameter default (limit 100)"""
        response = self.client.get('/api/data')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('count', data)
        self.assertIn('total_rows', data)
        self.assertIn('data', data)
        self.assertEqual(data['count'], 100) # Default limit adalah 100

    def test_data_route_all(self):
        """Menguji endpoint /api/data dengan parameter limit=all"""
        response = self.client.get('/api/data?limit=all')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data['count'], data['total_rows'])

    def test_predict_success(self):
        """Menguji prediksi dengan input data yang valid"""
        payload = {
            "ProductCategory": "Smartphones",
            "ProductBrand": "Samsung",
            "ProductPrice": 1200.0,
            "CustomerAge": 25,
            "CustomerGender": 0, # Laki-laki
            "PurchaseFrequency": 3,
            "CustomerSatisfaction": 4
        }
        response = self.client.post(
            '/api/predict',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('prediction', data)
        self.assertIn('confidence', data)
        self.assertIn('recommendations', data)
        self.assertIn(data['prediction'], [0, 1])
        self.assertIsInstance(data['confidence'], float)
        self.assertIsInstance(data['recommendations'], list)

    def test_predict_invalid_category(self):
        """Menguji penanganan error ketika kategori produk tidak valid (status 400)"""
        payload = {
            "ProductCategory": "KategoriPalsu",
            "ProductBrand": "Samsung",
            "ProductPrice": 1200.0,
            "CustomerAge": 25,
            "CustomerGender": 0,
            "PurchaseFrequency": 3,
            "CustomerSatisfaction": 4
        }
        response = self.client.post(
            '/api/predict',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertIn('Kategori produk KategoriPalsu tidak dikenal', data['error'])

    def test_predict_invalid_brand(self):
        """Menguji penanganan error ketika brand produk tidak valid (status 400)"""
        payload = {
            "ProductCategory": "Smartphones",
            "ProductBrand": "BrandPalsu",
            "ProductPrice": 1200.0,
            "CustomerAge": 25,
            "CustomerGender": 0,
            "PurchaseFrequency": 3,
            "CustomerSatisfaction": 4
        }
        response = self.client.post(
            '/api/predict',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertIn('Brand produk BrandPalsu tidak dikenal', data['error'])

    def test_predict_missing_or_bad_data(self):
        """Menguji kegagalan parsing / missing fields (status 400)"""
        payload = {
            "ProductCategory": "Smartphones",
            # missing ProductBrand dan field lainnya
        }
        response = self.client.post(
            '/api/predict',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        
        data = json.loads(response.data)
        self.assertIn('error', data)

if __name__ == '__main__':
    unittest.main()
