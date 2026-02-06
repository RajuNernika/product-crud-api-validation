#!/bin/python3
import random
import string
import requests
import json
from datetime import datetime, timedelta
from result_output import ResultOutput
import os
import sys
import psycopg2
from psycopg2 import Error

class PostgreSQL:
    def __init__(self, db_url, db_name, db_username, db_password):
        self.db_url = db_url
        self.db_name = db_name
        self.db_username = db_username
        self.db_password = db_password
        self.connection = None
        self.cursor = None

    def connect_to_db(self):
        try:
            self.connection = psycopg2.connect(
                host=self.db_url,
                database=self.db_name,
                user=self.db_username,
                password=self.db_password
            )
            if self.connection:
                self.cursor = self.connection.cursor()
        except (Exception, Error) as error:
            pass

    def disconnect_from_db(self):
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()

    def truncate_table(self, table_name):
        if not self.cursor:
            return
        try:
            query = f"TRUNCATE TABLE {table_name} CASCADE"
            self.cursor.execute(query)
            self.connection.commit()
        except (Exception, Error) as error:
            pass

    def get_all_records(self, table_name):
        if not self.cursor:
            return None
        try:
            query = f"SELECT * FROM {table_name};"
            self.cursor.execute(query)
            records = self.cursor.fetchall()
            return records
        except (Exception, Error) as error:
            return None

    def getItemById(self, table_name, id):
        if not self.cursor:
            return None
        try:
            query = f"SELECT * FROM {table_name} WHERE id={id};"
            self.cursor.execute(query)
            records = self.cursor.fetchall()
            return records
        except (Exception, Error) as error:
            return None

    def create_document_product(self, name, price, quantity):
        if not self.cursor:
            return None
        try:
            query = f"INSERT INTO products (name, price, quantity) VALUES (%s, %s, %s) RETURNING id;"
            self.cursor.execute(query, (name, price, quantity))
            self.connection.commit()
            product_id = self.cursor.fetchone()[0]
            return product_id
        except (Exception, Error) as error:
            return None

    def clear_tables(self):
        tables = ["products", "customers", "billing"]
        for table in tables:
            self.truncate_table(table)

def generate_random_string(length):
    letters = string.ascii_letters + string.digits
    return "".join(random.choice(letters) for _ in range(length))

class Activity(PostgreSQL):
    def __init__(self):
        self.product_id = None
        self.isCreatedSuccessful = False
        super().__init__("localhost", "database_name", "postgres", "password")

    def testcase_create_product(self, test_object):
        testcase_description = "Test product creation endpoint"
        expected_result = "Product created successfully!"
        actual = "Product creation failed!"
        marks = 15
        marks_obtained = 0

        test_object.update_pre_result(testcase_description, expected_result)

        try:
            api_url = "http://localhost:8080/api/products"
            headers = {"Content-Type": "application/json"}
            payload = {
                "name": "Test Product",
                "price": 100,
                "quantity": 10
            }

            try:
                response = requests.post(api_url, json=payload, headers=headers, timeout=5)
                response.raise_for_status()
            except requests.RequestException as e:
                test_object.update_result(
                    0, expected_result, "API call failed", testcase_description, "N/A", marks, marks_obtained
                )
                return

            if response.status_code == 201:
                json_data = response.json()
                product_id = json_data.get('id', None)

                if product_id is not None:
                    self.product_id = product_id
                    self.connect_to_db()
                    products = self.getItemById("products", product_id)
                    self.disconnect_from_db()

                    if products is not None and len(products) > 0 and products[0][1] == payload['name']:
                        marks_obtained = marks
                        self.isCreatedSuccessful = True
                        return test_object.update_result(
                            1, expected_result, expected_result, testcase_description, "N/A", marks, marks_obtained
                        )
            return test_object.update_result(
                0, expected_result, actual, testcase_description, "N/A", marks, marks_obtained
            )
        except Exception as e:
            test_object.update_result(
                0, expected_result, actual, testcase_description, "N/A", marks, marks_obtained
            )
            test_object.eval_message["testcase_name"] = str(e)

    def testcase_get_product_by_id(self, test_object):
        testcase_description = "Test product retrieval by ID"
        expected_result = "Product retrieved successfully!"
        actual = "Product not retrieved!"
        marks = 15
        marks_obtained = 0

        test_object.update_pre_result(testcase_description, expected_result)

        try:
            if self.product_id is None:
                test_object.update_result(
                    0, expected_result, "Product creation failed!", testcase_description, "N/A", marks, marks_obtained
                )
                return

            api_url = f"http://localhost:8080/api/products/{self.product_id}"
            headers = {"Content-Type": "application/json"}

            response = requests.get(api_url, headers=headers, timeout=5)
            json_data = response.json()

            if response.status_code == 200 and json_data['id'] == self.product_id:
                marks_obtained = marks
                return test_object.update_result(
                    1, expected_result, expected_result, testcase_description, "N/A", marks, marks_obtained
                )
            return test_object.update_result(
                0, expected_result, actual, testcase_description, "N/A", marks, marks_obtained
            )
        except Exception as e:
            test_object.update_result(
                0, expected_result, actual, testcase_description, "N/A", marks, marks_obtained
            )
            test_object.eval_message["testcase_name"] = str(e)

    def testcase_get_all_products(self, test_object):
        testcase_description = "Test retrieving all products"
        expected_result = "All products retrieved successfully!"
        actual = "All products not retrieved!"
        marks = 15
        marks_obtained = 0

        test_object.update_pre_result(testcase_description, expected_result)

        try:
            api_url = "http://localhost:8080/api/products"
            headers = {"Content-Type": "application/json"}

            response = requests.get(api_url, headers=headers, timeout=5)
            json_data = response.json()

            if response.status_code == 200 and len(json_data) > 0:
                marks_obtained = marks
                return test_object.update_result(
                    1, expected_result, expected_result, testcase_description, "N/A", marks, marks_obtained
                )
            return test_object.update_result(
                0, expected_result, actual, testcase_description, "N/A", marks, marks_obtained
            )
        except Exception as e:
            test_object.update_result(
                0, expected_result, actual, testcase_description, "N/A", marks, marks_obtained
            )
            test_object.eval_message["testcase_name"] = str(e)

    def testcase_update_product(self, test_object):
        testcase_description = "Test product update endpoint"
        expected_result = "Product updated successfully!"
        actual = "Product not updated!"
        marks = 15
        marks_obtained = 0

        test_object.update_pre_result(testcase_description, expected_result)

        try:
            if self.product_id is None:
                test_object.update_result(
                    0, expected_result, "Product creation failed!", testcase_description, "N/A", marks, marks_obtained
                )
                return

            api_url = f"http://localhost:8080/api/products/{self.product_id}"
            headers = {"Content-Type": "application/json"}
            payload = {
                "name": "Updated Product",
                "price": 150,
                "quantity": 5
            }

            response = requests.put(api_url, json=payload, headers=headers, timeout=5)

            if response.status_code == 200:
                self.connect_to_db()
                products = self.getItemById("products", self.product_id)
                self.disconnect_from_db()

                if products and len(products) > 0 and products[0][1] == payload['name']:
                    marks_obtained = marks
                    return test_object.update_result(
                        1, expected_result, expected_result, testcase_description, "N/A", marks, marks_obtained
                    )
            return test_object.update_result(
                0, expected_result, actual, testcase_description, "N/A", marks, marks_obtained
            )
        except Exception as e:
            test_object.update_result(
                0, expected_result, actual, testcase_description, "N/A", marks, marks_obtained
            )
            test_object.eval_message["testcase_name"] = str(e)

    def testcase_delete_product(self, test_object):
        testcase_description = "Test product deletion endpoint"
        expected_result = "Product deleted successfully!"
        actual = "Product not deleted!"
        marks = 15
        marks_obtained = 0

        test_object.update_pre_result(testcase_description, expected_result)

        try:
            if self.product_id is None:
                test_object.update_result(
                    0, expected_result, "Product creation failed!", testcase_description, "N/A", marks, marks_obtained
                )
                return

            api_url = f"http://localhost:8080/api/products/{self.product_id}"
            headers = {"Content-Type": "application/json"}

            response = requests.delete(api_url, headers=headers, timeout=5)

            if response.status_code == 200:
                self.connect_to_db()
                products = self.getItemById("products", self.product_id)
                self.disconnect_from_db()

                if products is None or len(products) == 0:
                    marks_obtained = marks
                    return test_object.update_result(
                        1, expected_result, expected_result, testcase_description, "N/A", marks, marks_obtained
                    )
            return test_object.update_result(
                0, expected_result, actual, testcase_description, "N/A", marks, marks_obtained
            )
        except Exception as e:
            test_object.update_result(
                0, expected_result, actual, testcase_description, "N/A", marks, marks_obtained
            )
            test_object.eval_message["testcase_name"] = str(e)

def start_tests(args):
    args = args.replace("{", "")
    args = args.replace("}", "")
    args = args.split(":")
    args = {"token": args[1]}
    args = json.dumps(args)

    test_object = ResultOutput(args, Activity)
    challenge_test = Activity()
    challenge_test.connect_to_db()
    challenge_test.clear_tables()
    challenge_test.disconnect_from_db()

    challenge_test.testcase_create_product(test_object)
    challenge_test.testcase_get_product_by_id(test_object)
    challenge_test.testcase_get_all_products(test_object)
    challenge_test.testcase_update_product(test_object)
    challenge_test.testcase_delete_product(test_object)

    challenge_test.connect_to_db()
    challenge_test.clear_tables()
    challenge_test.disconnect_from_db()

    result = test_object.result_final()
    result = json.dumps(json.loads(result), indent=4)
    print(result)
    return result

def main():
    args = sys.argv[2]
    start_tests(args)

if __name__ == "__main__":
    main()