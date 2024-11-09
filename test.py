import streamlit as st
import pandas as pd

def calculate_metrics(
    monthly_traffic,
    conversion_rate,
    basket1_price,
    basket1_margin,
    basket1_volume,
    basket2_price,
    basket2_margin,
    basket2_volume,
    shipping_cost,
    seo_cost,
    ads_cost
):
    # Calcul du nombre de commandes
    orders = monthly_traffic * (conversion_rate / 100)
    
    # Calcul du panier moyen pondéré
    avg_basket = (basket1_price * (basket1_volume/100)) + (basket2_price * (basket2_volume/100))
    
    # Chiffre d'affaires
    revenue = orders * avg_basket
    
    # Coûts variables
    shopify_fees = (revenue * 0.029) + (orders * 0.30)  # 2.9% + 0.30€ par transaction
    
    # Prix d'achat moyen pondéré
    basket1_cost = basket1_price * (1 - basket1_margin/100)
    basket2_cost = basket2_price * (1 - basket2_margin/100)
    avg_purchase_cost = (basket1_cost * (basket1_volume/100)) + (basket2_cost * (basket2_volume/100))
    total_purchase_cost = orders * avg_purchase_cost
    
    # Coûts de livraison
    shipping_costs = orders * shipping_cost
    
    # Coûts fixes mensuels
    monthly_fixed_costs = 32 + seo_cost + 1.25 + ads_cost  # Shopify + SEO + Domaine + Pub
    
    # Calcul des marges
    gross_margin = revenue - total_purchase_cost - shipping_costs - shopify_fees
    net_margin = gross_margin - monthly_fixed_costs
    
    # Ratios
    gross_margin_rate = (gross_margin / revenue) * 100 if revenue > 0 else 0
    marketing_ratio = ((seo_cost + ads_cost) / revenue) * 100 if revenue > 0 else 0
    break_even = monthly_fixed_costs / (gross_margin_rate/100) if gross_margin_rate > 0 else 0
    
    return {
        "Commandes": round(orders, 2),
        "Chiffre d'affaires": round(revenue, 2),
        "Frais Shopify": round(shopify_fees, 2),
        "Coût d'achat total": round(total_purchase_cost, 2),
        "Frais de livraison": round(shipping_costs, 2),
        "Marge brute": round(gross_margin, 2),
        "Marge nette": round(net_margin, 2),
        "Taux de marge brute (%)": round(gross_margin_rate, 2),
        "Ratio marketing (%)": round(marketing_ratio, 2),
        "Point mort": round(break_even, 2)
    }

st.title("Prévisions Financières E-commerce")

# Sidebar pour les inputs
st.sidebar.header("Hypothèses")

st.sidebar.subheader("Trafic et Conversion")
traffic = st.sidebar.number_input("Trafic mensuel", min_value=0, value=1000)
conversion = st.sidebar.number_input("Taux de conversion (%)", min_value=0.0, value=2.0)

st.sidebar.subheader("Panier 1")
basket1_price = st.sidebar.number_input("Prix panier 1 (€)", min_value=0.0, value=80.0)
basket1_margin = st.sidebar.number_input("Marge panier 1 (%)", min_value=0.0, value=60.0)
basket1_volume = st.sidebar.number_input("Part volume panier 1 (%)", min_value=0.0, max_value=100.0, value=50.0)

st.sidebar.subheader("Panier 2")
basket2_price = st.sidebar.number_input("Prix panier 2 (€)", min_value=0.0, value=60.0)
basket2_margin = st.sidebar.number_input("Marge panier 2 (%)", min_value=0.0, value=40.0)
basket2_volume = st.sidebar.number_input("Part volume panier 2 (%)", min_value=0.0, max_value=100.0, value=50.0)

st.sidebar.subheader("Coûts")
shipping = st.sidebar.number_input("Frais de livraison par commande (€)", min_value=0.0, value=6.0)
seo = st.sidebar.number_input("Consultant SEO (€/mois)", min_value=0.0, value=200.0)
ads = st.sidebar.number_input("Budget publicité (€/mois)", min_value=0.0, value=300.0)

# Calcul des métriques
metrics = calculate_metrics(
    traffic, conversion,
    basket1_price, basket1_margin, basket1_volume,
    basket2_price, basket2_margin, basket2_volume,
    shipping, seo, ads
)

# Affichage des résultats en colonnes
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("Revenus")
    st.metric("Nombre de commandes", f"{metrics['Commandes']}")
    st.metric("Chiffre d'affaires", f"{metrics['Chiffre d'affaires']}€")
    st.metric("Frais Shopify", f"{metrics['Frais Shopify']}€")

with col2:
    st.subheader("Marges")
    st.metric("Marge brute", f"{metrics['Marge brute']}€")
    st.metric("Marge nette", f"{metrics['Marge nette']}€")
    st.metric("Taux de marge brute", f"{metrics['Taux de marge brute (%)']}%")

with col3:
    st.subheader("Ratios clés")
    st.metric("Ratio marketing", f"{metrics['Ratio marketing (%)']}%")
    st.metric("Point mort", f"{metrics['Point mort']}€")

# Tableau détaillé
st.subheader("Détails des calculs")
df = pd.DataFrame([metrics]).T
df.columns = ['Valeur']
st.dataframe(df)
