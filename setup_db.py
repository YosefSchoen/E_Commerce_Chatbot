import pandas as pd
from sqlalchemy import create_engine


def change_payment_type(payment_type: str) -> str:
    """
    the payment_type in the csv file had many different option so i simplified it for testing
    :param payment_type: the payment_type string to be converted
    :return: the simplified payment_type string
    """

    if payment_type == 'credit_card' or payment_type == 'debit_card':
        return payment_type
    if payment_type == 'voucher':
        return 'check'
    return 'cash'


def get_product_df() -> pd.DataFrame:
    """
    this will read the csv files for the products and their english translation
    and create a simplified dataframe
    :return: the product data frame with the columns product_id and product_category_name
    """

    products_df = pd.read_csv('dummy_data/raw_data/olist_products_dataset.csv')
    translation_df = pd.read_csv('dummy_data/raw_data/product_category_name_translation.csv')

    products_df = products_df.join(translation_df.set_index('product_category_name'), on='product_category_name')
    products_df['product_category_name'] = products_df['product_category_name_english']
    products_df = products_df[['product_id', 'product_category_name']]
    return products_df


def get_orders_df() -> pd.DataFrame:
    """
    will read in the orders csv file and join it with the order_payments csv file
    :return: the simplified orders data frame
    """
    orders_df = pd.read_csv('dummy_data/raw_data/olist_orders_dataset.csv')
    orders_payment_df = pd.read_csv('dummy_data/raw_data/olist_order_payments_dataset.csv')

    orders_payment_df = orders_payment_df[['order_id', 'payment_type', 'payment_value']]

    orders_df = orders_df.join(orders_payment_df.set_index('order_id'), on='order_id')

    orders_df['payment_type'] = orders_df['payment_type'].apply(lambda n: change_payment_type(n))
    return orders_df


def get_order_items_df() -> pd.DataFrame:
    """
    will read in the order_item csv file and replace the product id with the product category
    :return: the simplified order_items data frame
    """
    order_items_df = pd.read_csv('dummy_data/raw_data/olist_order_items_dataset.csv')
    order_items_df = order_items_df.join(get_product_df().set_index('product_id'), on='product_id')
    order_items_df = order_items_df.drop(['product_id', 'seller_id'], axis=1)
    return order_items_df


def get_clean_csvs() -> None:
    orders_df = get_orders_df()
    orders_df.name = 'orders'
    orders_df.to_csv('dummy_data/clean_data/orders.csv', index=False)

    order_items_df = get_order_items_df()
    order_items_df.name = 'order_items'
    order_items_df.to_csv('dummy_data/clean_data/order_items.csv', index=False)


def make_db():
    engine = create_engine('sqlite:///dummy_database.db', echo=True)
    orders_df = pd.read_csv('dummy_data/clean_data/orders.csv')
    orders_df.name = 'orders'

    orders_df.to_sql(
        name=orders_df.name,
        con=engine,
        if_exists='replace',
        index=False
    )

    orders_items_df = pd.read_csv('dummy_data/clean_data/order_items.csv')
    orders_items_df.name = 'order_items'

    orders_items_df.to_sql(
        name=orders_items_df.name,
        con=engine,
        if_exists='replace',
        index=False
    )


get_clean_csvs()
make_db()
