import streamlit as st
import pandas as pd
import plotly.graph_objects as go

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

def main():
    st.title("Prévisions Financières E-commerce")
    
    with st.sidebar:
        st.header("Hypothèses")
        
        st.subheader("Trafic et Conversion")
        traffic = st.number_input("Trafic mensuel", min_value=0, value=1000)
        conversion = st.number_input("Taux de conversion (%)", min_value=0.0, value=2.0)
        
        st.subheader("Panier 1")
        basket1_price = st.number_input("Prix panier 1 (€)", min_value=0.0, value=80.0)
        basket1_margin = st.number_input("Marge panier 1 (%)", min_value=0.0, value=60.0)
        basket1_volume = st.number_input("Part volume panier 1 (%)", min_value=0.0, max_value=100.0, value=50.0)
        
        st.subheader("Panier 2")
        basket2_price = st.number_input("Prix panier 2 (€)", min_value=0.0, value=60.0)
        basket2_margin = st.number_input("Marge panier 2 (%)", min_value=0.0, value=40.0)
        basket2_volume = st.number_input("Part volume panier 2 (%)", min_value=0.0, max_value=100.0, value=50.0)
        
        st.subheader("Coûts")
        shipping = st.number_input("Frais de livraison par commande (€)", min_value=0.0, value=6.0)
        seo = st.number_input("Consultant SEO (€/mois)", min_value=0.0, value=200.0)
        ads = st.number_input("Budget publicité (€/mois)", min_value=0.0, value=300.0)
    
    # Calcul des métriques
    metrics = calculate_metrics(
        traffic, conversion,
        basket1_price, basket1_margin, basket1_volume,
        basket2_price, basket2_margin, basket2_volume,
        shipping, seo, ads
    )
    
    # Affichage des résultats
    col1, col2 = st.columns(2)
    
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
    
    # Graphique en cascade
    fig = go.Figure(go.Waterfall(
        name="Cascade financière",
        orientation="v",
        measure=["relative", "relative", "relative", "relative", "relative", "total", "relative", "total"],
        x=["CA", "Frais Shopify", "Coût d'achat", "Livraison", "Marge brute", "Coûts fixes", "Marge nette"],
        y=[
            metrics["Chiffre d'affaires"],
            -metrics["Frais Shopify"],
            -metrics["Coût d'achat total"],
            -metrics["Frais de livraison"],
            metrics["Marge brute"],
            -(seo + ads + 32 + 1.25),  # Coûts fixes
            metrics["Marge nette"]
        ],
        connector={"line": {"color": "rgb(63, 63, 63)"}},
    ))

    fig.update_layout(
        title="Décomposition du résultat",
        showlegend=False,
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Ratios additionnels
    st.subheader("Ratios clés")
    st.metric("Ratio marketing", f"{metrics['Ratio marketing (%)']}%")
    st.metric("Point mort", f"{metrics['Point mort']}€")

if __name__ == "__main__":
    main()
