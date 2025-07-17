import unittest
from app import app  # importing the Flask app
import mysql.connector

# Optional: Use a test database or clean up after each test
# Here, we'll use the same DB and add test entries

class SweetShopTests(unittest.TestCase):

    def setUp(self):
        # Set up a test client
        self.client = app.test_client()
        self.client.testing = True

        # Setup database connection
        self.db = mysql.connector.connect(
            host="localhost", user="root", password="", database="sweet_shop"
        )
        self.cursor = self.db.cursor()

    def tearDown(self):
        # Clean up test data
        self.cursor.execute("DELETE FROM sweets WHERE id = 'test1'")
        self.cursor.execute("DELETE FROM sweets WHERE id = 'test2'")
        self.db.commit()

    def test_homepage_loads(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Sweet", response.data)  # Assuming your homepage contains the word “Sweet”

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

    def test_purchase_sweet_success(self):
        # Insert sweet manually before purchase
        self.cursor.execute("INSERT INTO sweets (id, s_name, s_category, s_price, s_qty) VALUES (%s,%s,%s,%s,%s)",
                            ('test2', 'Barfi', 'Traditional', '25', '5'))
        self.db.commit()

        response = self.client.post('/purchase_sweet', data={
            'id': 'test2',
            'qty': '2'
        })
        self.assertIn(b'Purchase Successfull', response.data)

    def test_purchase_sweet_insufficient_stock(self):
        # Insert sweet manually with only 1 quantity
        self.cursor.execute("INSERT INTO sweets (id, s_name, s_category, s_price, s_qty) VALUES (%s,%s,%s,%s,%s)",
                            ('test2', 'Kaju Katli', 'Premium', '50', '1'))
        self.db.commit()

        response = self.client.post('/purchase_sweet', data={
            'id': 'test2',
            'qty': '3'
        })
        self.assertIn(b'Insufficient Stock', response.data)

    def test_purchase_sweet_not_found(self):
        response = self.client.post('/purchase_sweet', data={
            'id': 'nonexistent',
            'qty': '2'
        })
        self.assertIn(b'Sweet Not Found', response.data)

    def test_delete_sweet(self):
        # Insert a sweet to delete
        self.cursor.execute("INSERT INTO sweets (id, s_name, s_category, s_price, s_qty) VALUES (%s,%s,%s,%s,%s)",
                            ('test1', 'Rasgulla', 'Traditional', '30', '10'))
        self.db.commit()

        response = self.client.post('/delete_stock', data={'id': 'test1'})
        self.assertIn(b'Product Deleted successfully', response.data)

    def test_update_stock(self):
        # Insert test sweet
        self.cursor.execute("INSERT INTO sweets (id, s_name, s_category, s_price, s_qty) VALUES (%s,%s,%s,%s,%s)",
                            ('test1', 'Halwa', 'Traditional', '10', '10'))
        self.db.commit()

        # Add 5 more
        response = self.client.post('/update_stock', data={
            'id': 'test1',
            'qty': '5',
            'price': '12'
        })

        self.assertIn(b'Product restocked successfully', response.data)

    def test_update_stock_not_found(self):
        response = self.client.post('/update_stock', data={
            'id': 'unknown',
            'qty': '5',
            'price': '15'
        })

        self.assertIn(b'Sweet Not Found', response.data)

# Run the tests
if __name__ == '__main__':
    unittest.main()
