import csv
import json
from sqlalchemy import create_engine, text

with open('config.json') as f:
    config = json.loads(f.read())


class ChatBotFunctions:
    @staticmethod
    def function_not_found() -> str:
        """
        rarely the chatbot makes up a function name
        so, it defaults to this one if it calls a non-existing function in the available functions dictionary
        :return: the prompt
        """
        prompt = 'function in tool call not found'
        return prompt

    @staticmethod
    def get_customer_id() -> str:
        """
        will ask customer for there customer id for security, so they don't see other orders
        :return: the prompt
        """
        prompt = 'I need your customer id for this'
        return prompt

    @staticmethod
    def get_order_id() -> str:
        """
        will ask the customer for an order id to do things with orders like returns check status etc...
        :return: the prompt for the chatbot
        """
        prompt = 'what is the order_id for the order you would like to see'
        return prompt

    @staticmethod
    def get_order_status(order_id: str, customer_id: str) -> str:
        """
        will query the database for the order status
        :param order_id: the id of the order to check
        :param customer_id: the id of the customer
        :return: the status of the order
        """

        engine = create_engine(config['database']['name'])
        with engine.connect() as conn:
            query = (f"SELECT order_status FROM orders "
                     f"WHERE order_id=='{order_id}' AND customer_id=='{customer_id}';")
            result = conn.execute(text(query))

        prompt = 'here is the status of the order: ' + str(result.all())
        return prompt

    @staticmethod
    def get_human_representative() -> str:
        """
        will be called if the user wants a human, it will tell the user to send contact info
        :return: the prompt
        """
        prompt = ('We will get a human representative to contact you please give '
                  'us your contact information we need your full name email and phone number.')
        return prompt

    @staticmethod
    def get_contact_info(full_name: str, email: str, phone_number: str) -> str:
        """
        will get the users contact information and save it to a csv file
        :param full_name: users full name
        :param email: users email
        :param phone_number: users phone number
        :return: the prompt
        """
        with open('contact_info.csv', 'a') as file:
            writer = csv.writer(file)
            writer.writerow([full_name, email, phone_number])
            prompt = 'We saved your contact info and a human representative will reach you soon'
        return prompt

    @staticmethod
    def get_return_policy_for_product() -> str:
        """
        will ask the user to say the name type of product the chatbot know the return policy
        also the user can send a specific order id and the chatbot can get the product type for the user
        :return: the prompt
        """
        prompt = ('We need you to specify the name or type of the product '
                  'or you can input the order_id of a specific product')
        return prompt

    @staticmethod
    def get_order_product_type(order_id: str, customer_id: str) -> str:
        """
        will run a query from the database to get the type of product in the order
        this can help determine if the item is returnable
        :param order_id: the id of the order to check
        :param customer_id: the id of the customer
        :return:
        """
        engine = create_engine(config['database']['name'])
        with engine.connect() as conn:
            query = (f"SELECT product_category_name FROM order_items "
                     f"INNER JOIN orders ON order_items.order_id == orders.order_id "
                     f"WHERE order_items.order_id=='{order_id}' AND orders.customer_id=='{customer_id}';")
            result = conn.execute(text(query))

        prompt = 'the product type is: ' + str(result.all())
        return prompt

    @staticmethod
    def get_refund_policy(order_id: str, customer_id: str) -> str:
        """
        will run a query from the database to get the payment type of the order
        this will help tell the user how he / she will be refunded
        :param order_id: the id of the order to check
        :param customer_id: the id of the customer
        :return:
        """
        engine = create_engine(config['database']['name'])
        with engine.connect() as conn:
            query = (f"SELECT payment_type, payment_value FROM orders "
                     f"WHERE order_id=='{order_id}' AND customer_id=='{customer_id}';")
            result = conn.execute(text(query))

        prompt = 'the payment_type and price of the order is the following: ' + str(result.all())
        return prompt
