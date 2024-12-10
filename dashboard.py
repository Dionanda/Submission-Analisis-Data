import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from babel.numbers import format_currency

sns.set(style='whitegrid')

# Load datasets
customers_df = pd.read_csv('customers_dataset.csv')
geolocation_df = pd.read_csv('geolocation_dataset.csv')
order_items_df = pd.read_csv('order_items_dataset.csv')
order_payments_df = pd.read_csv('order_payments_dataset.csv')
order_reviews_df = pd.read_csv('order_reviews_dataset.csv')
orders_df = pd.read_csv('orders_dataset.csv')
product_category_name_translation_df = pd.read_csv('product_category_name_translation.csv')
products_df = pd.read_csv('products_dataset.csv')
sellers_df = pd.read_csv('sellers_dataset.csv')

# Merge and prepare data
merged_df = pd.merge(order_items_df, order_reviews_df, on='order_id', how='inner')
merged_df = pd.merge(merged_df, products_df, on='product_id', how='inner')
merged_df = pd.merge(merged_df, product_category_name_translation_df, on='product_category_name', how='left')
merged_df = pd.merge(merged_df, orders_df[['order_id', 'order_purchase_timestamp']], on='order_id', how='inner')

avg_review_score = merged_df.groupby(['product_category_name_english'])['review_score'].mean().reset_index()
avg_review_score.columns = ['product_category_name', 'average_review_score']

lowest_rated_categories = avg_review_score.sort_values(by='average_review_score').head(10)
highest_rated_categories = avg_review_score.sort_values(by='average_review_score', ascending=False).head(10)

# Order count per state
merged_orders_customers = pd.merge(orders_df[['order_id', 'customer_id', 'order_status']], customers_df[['customer_id', 'customer_state']], on='customer_id', how='inner')
order_count_per_state = merged_orders_customers.groupby('customer_state').size().reset_index(name='order_count')

# Product count per category
product_count = merged_df.groupby('product_category_name_english')['product_id'].nunique().reset_index()
product_count.columns = ['product_category_name', 'product_count']

# Most ordered categories
most_ordered_categories = merged_df['product_category_name_english'].value_counts().reset_index()
most_ordered_categories.columns = ['product_category_name', 'order_count']

# Monthly rating trend
merged_df['order_purchase_timestamp'] = pd.to_datetime(merged_df['order_purchase_timestamp'])
merged_df['year_month'] = merged_df['order_purchase_timestamp'].dt.to_period('M').astype(str)
monthly_rating_trend = merged_df.groupby('year_month')['review_score'].mean().reset_index()

# Payment performance
merged_payments = pd.merge(order_payments_df, order_reviews_df, on='order_id', how='inner')
payment_performance = merged_payments.groupby('payment_type')['review_score'].mean().reset_index()
payment_performance.columns = ['payment_type', 'average_review_score']

# Helper Functions
def create_bar_chart(data, x, y, title, xlabel, ylabel, colors=None, figsize=(10, 6), rotation=0):
    fig, ax = plt.subplots(figsize=figsize)
    sns.barplot(data=data, x=x, y=y, palette=colors, ax=ax)
    ax.set_title(title, fontsize=16)
    ax.set_xlabel(xlabel, fontsize=14)
    ax.set_ylabel(ylabel, fontsize=14)
    plt.xticks(rotation=rotation)
    st.pyplot(fig)

def create_line_chart(data, x, y, title, xlabel, ylabel, marker='o', figsize=(12, 6), rotation=0):
    fig, ax = plt.subplots(figsize=figsize)
    sns.lineplot(data=data, x=x, y=y, marker=marker, ax=ax)
    ax.set_title(title, fontsize=16)
    ax.set_xlabel(xlabel, fontsize=14)
    ax.set_ylabel(ylabel, fontsize=14)
    plt.xticks(rotation=rotation)
    st.pyplot(fig)

# Streamlit Sidebar Navigation
st.sidebar.image("logo.png", use_container_width=True)
st.sidebar.title("Navigasi")
pages = ["Product Insights", "Regional Insights", "Customer Insights", "RFM Analysis"]
selection = st.sidebar.radio("Pilih Halaman", pages)

# Streamlit Layout Based on Navigation
st.title("Dashboard E-Commerce")

if selection == "Product Insights":
    st.header("Product Insights")

    # Metrik untuk Product Insights
    total_lowest_products = lowest_rated_categories['product_category_name'].nunique()
    avg_lowest_rating = round(lowest_rated_categories['average_review_score'].mean(), 2)
    total_highest_products = highest_rated_categories['product_category_name'].nunique()
    avg_highest_rating = round(highest_rated_categories['average_review_score'].mean(), 2)
    total_categories = product_count['product_category_name'].nunique()
    total_products = product_count['product_count'].sum()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Kategori Terendah", value=total_lowest_products)
        st.metric("Rata-rata Rating Terendah", value=avg_lowest_rating)
    with col2:
        st.metric("Total Kategori Tertinggi", value=total_highest_products)
        st.metric("Rata-rata Rating Tertinggi", value=avg_highest_rating)
    with col3:
        st.metric("Total Kategori Produk", value=total_categories)
        st.metric("Total Produk", value=total_products)

    # Visualisasi Produk
    st.subheader("Produk dengan Rating Terendah")
    colors = ['lightgray'] * len(lowest_rated_categories)
    colors[0] = 'lightcoral'
    create_bar_chart(
        data=lowest_rated_categories,
        x='average_review_score',
        y='product_category_name',
        title='Kategori Produk dengan Rating Terendah',
        xlabel='Rata-rata Rating',
        ylabel='Kategori Produk',
        colors=colors
    )

    st.subheader("Produk dengan Rating Tertinggi")
    colors = ['lightgray'] * len(highest_rated_categories)
    colors[0] = 'lightgreen'
    create_bar_chart(
        data=highest_rated_categories,
        x='average_review_score',
        y='product_category_name',
        title='Kategori Produk dengan Rating Tertinggi',
        xlabel='Rata-rata Rating',
        ylabel='Kategori Produk',
        colors=colors
    )

elif selection == "Regional Insights":
    st.header("Regional Insights")

    # Metrik untuk Regional Insights
    total_states = order_count_per_state['customer_state'].nunique()
    total_orders = order_count_per_state['order_count'].sum()
    top_state = order_count_per_state.loc[order_count_per_state['order_count'].idxmax()]
    top_state_name = top_state['customer_state']
    top_state_orders = top_state['order_count']

    # Visualisasi Regional
    st.subheader("Distribusi Pesanan per Wilayah")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Wilayah", value=total_states)
    with col2:
        st.metric("Total Pesanan", value=total_orders)
    with col3:
        st.metric(f"Wilayah Teratas ({top_state_name})", value=top_state_orders)
    create_bar_chart(
        data=order_count_per_state.sort_values(by='order_count', ascending=False),
        x='customer_state',
        y='order_count',
        title='Jumlah Pesanan per Wilayah',
        xlabel='Wilayah',
        ylabel='Jumlah Pesanan',
        colors='viridis',
        rotation=45
    )

elif selection == "Customer Insights":
    st.header("Customer Insights")

    # Metrik untuk Customer Insights
    avg_monthly_rating = round(monthly_rating_trend['review_score'].mean(), 2)
    total_months = monthly_rating_trend['year_month'].nunique()
    top_month = monthly_rating_trend.loc[monthly_rating_trend['review_score'].idxmax()]
    top_month_name = top_month['year_month']
    top_month_rating = round(top_month['review_score'], 2)

    # Visualisasi Customer Insights
    st.subheader("Tren Rating Bulanan")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Rata-rata Rating Bulanan", value=avg_monthly_rating)
    with col2:
        st.metric("Total Bulan", value=total_months)
    with col3:
        st.metric(f"Bulan Terbaik ({top_month_name})", value=top_month_rating)
    create_line_chart(
        data=monthly_rating_trend,
        x='year_month',
        y='review_score',
        title='Tren Rata-rata Rating Produk dari Waktu ke Waktu',
        xlabel='Bulan',
        ylabel='Rata-rata Rating',
        rotation=45
    )

    # Hilangkan kategori 'not_defined' dari kolom payment_type
    merged_payments = merged_payments[merged_payments['payment_type'] != 'not_defined']

    # Hitung ulang kinerja metode pembayaran
    payment_performance = merged_payments.groupby('payment_type')['review_score'].mean().reset_index()
    payment_performance.columns = ['payment_type', 'average_review_score']

    # Kinerja Metode Pembayaran
    st.subheader("Kinerja Metode Pembayaran")
    total_payment_methods = payment_performance['payment_type'].nunique()
    st.metric("Total Metode Pembayaran", value=total_payment_methods)
    create_bar_chart(
        data=payment_performance.sort_values(by='average_review_score', ascending=False),
        x='average_review_score',
        y='payment_type',
        title='Kepuasan Berdasarkan Metode Pembayaran',
        xlabel='Rata-rata Skor Ulasan',
        ylabel='Metode Pembayaran',
        colors='Blues'
    )

elif selection == "RFM Analysis":
    st.header("RFM Analysis")

    # RFM Analysis Preparation
    customers_orders = pd.merge(customers_df, orders_df[['customer_id', 'order_id', 'order_purchase_timestamp']], on='customer_id', how='inner')
    customers_orders_items = pd.merge(customers_orders, order_items_df[['order_id', 'price']], on='order_id', how='inner')

    # Convert timestamps
    customers_orders['order_purchase_timestamp'] = pd.to_datetime(customers_orders['order_purchase_timestamp'])
    current_date = customers_orders['order_purchase_timestamp'].max()

    # Calculate RFM metrics
    recency = customers_orders.groupby('customer_unique_id').agg(
        recency=('order_purchase_timestamp', lambda x: (current_date - x.max()).days)
    ).reset_index()

    frequency = customers_orders.groupby('customer_unique_id').agg(
        frequency=('order_id', 'count')
    ).reset_index()

    monetary = customers_orders_items.groupby('customer_unique_id').agg(
        monetary=('price', 'sum')
    ).reset_index()

    rfm = recency.merge(frequency, on='customer_unique_id').merge(monetary, on='customer_unique_id')

    # Display Metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Rata-rata Recency (hari)", value=round(rfm['recency'].mean(), 1))
    with col2:
        st.metric("Rata-rata Frequency", value=round(rfm['frequency'].mean(), 2))
    with col3:
        st.metric("Rata-rata Monetary", value=format_currency(rfm['monetary'].mean(), "USD", locale="en_US"))

    # Top 10 Recency
    st.subheader("Top 10 Pelanggan berdasarkan Recency")
    fig = plt.figure(figsize=(10, 6))
    sns.barplot(data=rfm.sort_values(by='recency', ascending=False).head(10),
                y='customer_unique_id', x='recency', palette="Blues")
    plt.title('Top 10 Recency')
    plt.xlabel('Recency (Days)')
    plt.ylabel('Customer ID')
    plt.tight_layout()
    st.pyplot(fig)

    # Top 10 Frequency
    st.subheader("Top 10 Pelanggan berdasarkan Frequency")
    fig = plt.figure(figsize=(10, 6))
    sns.barplot(data=rfm.sort_values(by='frequency', ascending=False).head(10),
                y='customer_unique_id', x='frequency', palette="Greens")
    plt.title('Top 10 Frequency')
    plt.xlabel('Frequency (Orders)')
    plt.ylabel('Customer ID')
    plt.tight_layout()
    st.pyplot(fig)

    # Top 10 Monetary
    st.subheader("Top 10 Pelanggan berdasarkan Monetary")
    fig = plt.figure(figsize=(10, 6))
    sns.barplot(data=rfm.sort_values(by='monetary', ascending=False).head(10),
                y='customer_unique_id', x='monetary', palette="Reds")
    plt.title('Top 10 Monetary')
    plt.xlabel('Monetary (Amount)')
    plt.ylabel('Customer ID')
    plt.tight_layout()
    st.pyplot(fig)


# Footer
st.markdown("---")
st.markdown("**Dashboard dibuat oleh Ketut Dionanda Sutrisna** © 2024")
