import json
import unittest
from parameterized import parameterized
import csv
import pandas as pd
from sklearn.model_selection import train_test_split
from typing import List, Tuple
from chatbot import Chatbot


with open('config.json') as f:
    config = json.loads(f.read())
    sample_size = config['sample_size']


def get_data() -> Tuple[str, str, str, str, str]:
    """
    will get a full single row of data for test_chaining_questions
    :return: the data below
    """
    df_1 = pd.read_csv('dummy_data/clean_data/order_items.csv')
    df_2 = pd.read_csv('dummy_data/clean_data/orders.csv')

    df = df_1.join(df_2.set_index('order_id'), on='order_id').dropna(axis=0).iloc[0, :]
    columns = ['customer_id', 'order_id', 'order_status', 'product_category_name', 'payment_type']

    customer_id, order_id, order_status, product_type, payment_type = df[columns]
    return customer_id, order_id, order_status, product_type, payment_type


def generate_sample_data(df_1_name: str, df_2_name: str = None, target_column: str = None)\
        -> Tuple[List[str], List[str], List[str]]:
    """
    this will generate a sample data set, the original data has over 100k rows
    feel free to make the samples as large as you want
    :param df_1_name: first dataframe to load
    :param df_2_name: second dataframe to load if join is needed
    :param target_column: the column to stratify samples from some samples are much more prevalent than others
    :return: the customer_ids, order_ids, and target column for the tests
    """
    df = pd.read_csv('dummy_data/clean_data/' + df_1_name + '.csv').dropna(axis=0)
    if df_2_name:  # will read df_2 if passed and join it to df_1 on the shared key order_id
        df_2 = pd.read_csv('dummy_data/clean_data/' + df_2_name + '.csv')
        df = df.join(df_2.set_index('order_id'), on='order_id').dropna(axis=0)
    if target_column:
        # just using the sklearn train_test_split to stratify the data and get 100 rows
        _, sample_df = train_test_split(df, stratify=df[target_column], test_size=100)

        # will get a much smaller sample sklearn doesn't let sample size < number of classes
        sample_df = sample_df.sample(sample_size)
        target = list(sample_df[target_column])
    else:
        # if no target just reduce the size
        sample_df = df.sample(sample_size)
        target = None

    customer_ids = list(sample_df['customer_id'])
    order_ids = list(sample_df['order_id'])

    return zip(customer_ids, order_ids, target)


class ChatbotTest(unittest.TestCase):

    @staticmethod
    def check_order_status(chatbot: Chatbot, prompt: str, customer_id: str, order_id: str, order_status: str) -> bool:
        """
        will check if the chatbot can get an order status by if it gets the customer_id and order_id or not
        if not it must ask for them
        :param chatbot: the chatbot
        :param prompt: the prompt requesting order status
        :param customer_id: the customer id to check
        :param order_id: the order id to check
        :param order_status: the order status to check
        :return: True or False
        """
        response = chatbot.run_chat(prompt)

        if chatbot.messages[-2]['name'] == 'get_order_status':
            return order_status.replace('_', ' ') in response.lower().replace('_', ' ')

        for i in range(2):
            check_for_id = True
            if chatbot.messages[-2]['name'] == 'get_order_id':
                prompt = order_id
            elif chatbot.messages[-2]['name'] == 'get_customer_id':
                prompt = customer_id
            else:
                check_for_id = False

            if not check_for_id:
                return False
            response = chatbot.run_chat(prompt)

        return order_status.replace('_', ' ') in response.lower().replace('_', ' ')

    @parameterized.expand(generate_sample_data('orders', target_column='order_status'))
    def test_get_order_status(self, customer_id: str, order_id: str, order_status: str) -> None:
        """

        :param customer_id: the customer id to check
        :param order_id: the order id to check
        :param order_status: the status to check if the chatbot can get
        :return: none
        """
        chatbot = Chatbot()
        prompt = f'what is the status of my order with my customer id {customer_id} and my order id {order_id}'
        self.assertTrue(self.check_order_status(chatbot, prompt, customer_id, order_id, order_status))

    @parameterized.expand(generate_sample_data('order_items', 'orders', 'product_category_name'))
    def test_get_order_product_type(self, customer_id: str, order_id: str, product_category: str) -> None:
        """
        will check if the chatbot can get a product type from the database
        :param customer_id: the customer id to send to the chatbot
        :param order_id:  the order id to send to the chatbot
        :param product_category: the product category to check against what the chatbot returns
        :return: none
        """
        chatbot = Chatbot()
        prompt = f'what is the product type of my order with my customer_id = {customer_id} and order_id = {order_id}'
        response = chatbot.run_chat(prompt)
        self.assertIn(product_category.replace('_', ' '), response.lower().replace('_', ' '))

    @staticmethod
    def check_return_policy(chatbot, prompt, product_type) -> bool:
        """
        will check if the chatbot can get the return policy
        :param chatbot: the chatbot
        :param prompt: the prompt to request returns
        :param product_type: the type of product to check if it is returnable
        :return:
        """
        response = chatbot.run_chat(prompt)
        if 'order id' in response.lower() or 'order_id' in response.lower():
            prompt = 'Its the same order as before'  # somtimes it needs to be reminded it knows the order id
            response = chatbot.run_chat(prompt)
        return product_type.replace('_', ' ') in response.lower().replace('_', ' ')

    @parameterized.expand([
        ('table', 'yes'),
        ('computer', 'yes'),
        ('diapers', 'no'),
        ('pizza', 'no'),
        ('tooth_brush', 'no')
    ])
    def test_get_return_policy(self, item: str, returnable: str) -> None:
        """
        will check if the chatbot knows what can and cannot be returned
        :param item: name of the item to check
        :param returnable: either yes or no according to the return policy
        :return: none
        """
        chatbot = Chatbot()
        prompt = f'can I return this item it is a {item} just say yes or no with no other words'
        response = chatbot.run_chat(prompt)
        self.assertIn(returnable.replace('_', ' '), response.lower().replace('_', ' '))

    @staticmethod
    def check_refund_policy(chatbot: Chatbot, prompt: str, payment_type: str) -> bool:
        """

        :param chatbot: the chatbot
        :param prompt: the prompt to request refund policy
        :param payment_type: either credit card, debit card, cash, or check
        :return: bool
        """
        response = chatbot.run_chat(prompt)
        if payment_type == 'credit_card':
            return 'credit card' in response.lower().replace('_', ' ')
        if payment_type == 'debit_card':
            return 'debit card' in response.lower().replace('_', ' ')
        if payment_type == 'cash' or payment_type == 'check':
            return 'cash' in response.lower().replace('_', ' ')
        return False

    @parameterized.expand(generate_sample_data('orders', target_column='payment_type'))
    def test_get_refund_policy(self, customer_id: str, order_id: str, payment_type: str) -> None:
        """
        will check if the chatbot can get the correct refund policy
        :param customer_id: the customer id to send to the chatbot
        :param order_id:  the order id to send to the chatbot
        :param payment_type: the payment_type to check against refund policy the chatbot returns
        :return: none
        """
        chatbot = Chatbot()
        prompt = f'how will I get my refund with my customer_id = {customer_id} and order_id = {order_id}'
        self.assertTrue(self.check_refund_policy(chatbot, prompt, payment_type))

    @staticmethod
    def check_contact_information(chatbot: Chatbot, prompt: str, name: str, email: str, phone_number: str) -> bool:
        """
        will check the to see if the chatbot can get users contact information after the user requests a person
        it will also check if the chatbot can save the contact information to the contact_info.csv file
        :param chatbot: the chatbot
        :param prompt: the prompt to request a person
        :param name: name of user
        :param email: email of user
        :param phone_number: phone number of user
        :return: bool
        """
        chatbot.run_chat(prompt)

        # checking if correct tool_call was called
        if chatbot.messages[-2]['name'] == 'get_human_representative':

            # then it gives the chatbot the contact information
            prompt = f'My name is {name} my email is {email} and my phone number is {phone_number}'
            chatbot.run_chat(prompt)
            contact_info = (name, email, phone_number)

            # finally it checks if the chatbot wrote it to the csv file
            with open('contact_info.csv') as file:
                contact_info_data = tuple(list(csv.reader(file))[-2])
                return contact_info == contact_info_data
        return False

    @parameterized.expand([
        ("John Doe", "johndoe@gmail.com", "(818) 123-4567"),
        ("Jane Smith", "janesmith@aol.com", "(747) 234-5678"),
        ("Michael Johnson", "michaeljohnson@yahoo.com", "(323) 345-6789"),
        ("Emily Davis Jr", "emilydavis@gmail.com", "(310) 456-7890"),
        ("Chris Brown", "chrisbrown@gmail.com", "(310) 567-8901"),
    ])
    def test_get_contact_information(self, full_name: str, email: str, phone_number: str) -> None:
        """
        will check to see if the chatbot can ask for and then write the users contact information
        :param full_name: the users name to send to the chatbot
        :param email: the users email to send to the chatbot
        :param phone_number: the users phone to send to the chatbot
        :return: none
        """
        chatbot = Chatbot()
        prompt = 'I would like to speak to a person please'
        self.assertTrue(self.check_contact_information(chatbot, prompt, full_name, email, phone_number))

    def test_chaining_questions(self) -> None:
        """
        THis is the big test it is designed to simulate a full conversation with the agent
        it should remember information such as order_id and customer id from previous interactions
        :return: none
        """

        customer_id, order_id, order_status, product_type, payment_type = get_data()
        name, email, phone_number = 'Joseph A Schoen', 'josephaschoen@gmail.com', '0507093180'
        chatbot = Chatbot()

        prompt = 'I would like to check the status of my order'
        order_status = self.check_order_status(chatbot, prompt, customer_id, order_id, order_status)

        prompt = 'Can I return this'
        return_policy = self.check_return_policy(chatbot, prompt, product_type)

        prompt = 'How will I get my refund for this order'
        refund_policy = self.check_refund_policy(chatbot, prompt, payment_type)

        prompt = 'I would like to speak to a person please'
        contact_information = self.check_contact_information(chatbot, prompt, name, email, phone_number)

        self.assertTrue(order_status and return_policy and refund_policy and contact_information)


if __name__ == '__main__':
    unittest.main()
