import unittest
from app import app  # importing the Flask app
import mysql.connector

class SweetShopTests(unittest.TestCase):

    def setUp(self):
        self.client = app.test_client()
        self.client.testing = True

        self.db = mysql.connector.connect(
            host="localhost", user="root", password="", database="sweet_shop"
        )
        self.cursor = self.db.cursor()

    def tearDown(self):
        self.cursor.execute("DELETE FROM sweets WHERE id = 'test1'")
        self.cursor.execute("DELETE FROM sweets WHERE id = 'test2'")
        self.db.commit()

    def test_homepage_loads(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Sweet", response.data)

    def test_add_sweet(self):
        response = self.client.post('/add', data={
            'id': 'test1',
            'sweet_name': 'Gulab Jamun',
            'category': 'Traditional',
            'price': '20',
            'qty': '10'
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Sweet added successfully', response.data)

    def test_delete_sweet(self):
        self.cursor.execute("INSERT INTO sweets (id, s_name, s_category, s_price, s_qty) VALUES (%s,%s,%s,%s,%s)",
                            ('test1', 'Rasgulla', 'Traditional', '30', '10'))
        self.db.commit()

        response = self.client.post('/delete_stock', data={'id': 'test1'})
        self.assertIn(b'Product Deleted successfully', response.data)

    def test_update_stock_not_found(self):
        response = self.client.post('/update_stock', data={
            'id': 'unknown',
            'qty': '5',
            'price': '15'
        })

        self.assertIn(b'Sweet Not Found', response.data)

    def test_purchase_sweet(self):
    # Add sweet using the app route
        self.client.post('/add', data={
            'id': 'test2',
            'sweet_name': 'Barfi',
            'category': 'Traditional',
            'price': '25',
            'qty': '5'
        }, follow_redirects=True)
    
        # Then try purchasing it
        response = self.client.post('/purchase_sweet', data={
            'id': 'test2',
            'qty': '2'
        })
    
        self.assertIn(b'Purchase Successful', response.data)


# Run the tests
if __name__ == '__main__':
    unittest.main()
