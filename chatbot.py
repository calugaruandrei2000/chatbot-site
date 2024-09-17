from flask import Flask, request, jsonify
import openai
import os
from dotenv import load_dotenv
import requests
from requests.auth import HTTPBasicAuth

# Încarcă variabilele de mediu din fișierul .env
load_dotenv()

# Setează cheia OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')

# Detalii WooCommerce
consumer_key = os.getenv('WC_CONSUMER_KEY')  # Cheia ta de consum WooCommerce
consumer_secret = os.getenv('WC_CONSUMER_SECRET')  # Secretul de consum WooCommerce
store_url = 'https://parfumuriselecte.ro/wp-json/wc/v3/products'  # Înlocuiește cu URL-ul site-ului tău

# Funcție pentru a extrage produsele din WooCommerce
def get_products_from_woocommerce():
    response = requests.get(store_url, auth=HTTPBasicAuth(consumer_key, consumer_secret))
    
    if response.status_code == 200:
        products = response.json()  # Convertește răspunsul în JSON
        return products
    else:
        print(f"Eroare la conectarea cu WooCommerce: {response.status_code}")
        return []

# Funcție pentru a trimite prompturi GPT
def get_gpt_response(prompt):
    products = get_products_from_woocommerce()
    
    if not products:
        return "Nu am găsit produse relevante în baza de date."
    
    # Creează o listă de produse și detalii pe care GPT le poate folosi
    product_details = [
        f"Nume: {product['name']}, Preț: {product['price']}, Descriere: {product['description']}"
        for product in products
    ]
    
    # Creează mesajul de trimis la GPT, incluzând detalii despre produse
    system_message = (
        "Tu ești un asistent pentru un magazin online de parfumuri. "
        "Ai acces la următoarele produse și detalii: \n" + "\n".join(product_details)
    )
    
    # Răspunsul GPT pe baza întrebării utilizatorului și a produselor
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt}
        ]
    )
    
    return response['choices'][0]['message']['content']

# Exemplu de utilizare
question = "Ce parfumuri dulci îmi recomanzi?"
response = get_gpt_response(question)
print(response)
