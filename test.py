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
    shopify_fees = (revenue * 0.029) + (orders * 0.30)  # 2.9% + 0.30 par transaction
    
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
        "Chiffre_affaires": round(revenue, 2),
        "Frais_Shopify": round(shopify_fees, 2),
        "Cout_achat_total": round(total_purchase_cost, 2),
        "Frais_livraison": round(shipping_costs, 2),
        "Marge_brute": round(gross_margin, 2),
        "Marge_nette": round(net_margin, 2),
        "Taux_marge_brute": round(gross_margin_rate, 2),
        "Ratio_marketing": round(marketing_ratio, 2),
        "Point_mort": round(break_even, 2)
    }

def main():
    st.title("Previsions Financieres E-commerce")
    
    with st.sidebar:
        st.header("Hypotheses")
        
        st.subheader("Trafic et Conversion")
        traffic = st.number_input("Trafic mensuel", min_value=0, value=1000)
        conversion = st.number_input("Taux de conversion (%)", min_value=0.0, value=2.0)
        
        st.subheader("Panier 1")
        basket1_price = st.number_input("Prix panier 1 (EUR)", min_value=0.0, value=80.0)
        basket1_margin = st.number_input("Marge panier 1 (%)", min_value=0.0, value=60.0)
        basket1_volume = st.number_input("Part volume panier 1 (%)", min_value=0.0, max_value=100.0, value=50.0)
        
        st.subheader("Panier 2")
        basket2_price = st.number_input("Prix panier 2 (EUR)", min_value=0.0, value=60.0)
        basket2_margin = st.number_input("Marge panier 2 (%)", min_value=0.0, value=40.0)
        basket2_volume = st.number_input("Part volume panier 2 (%)", min_value=0.0, max_value=100.0, value=50.0)
        
        st.subheader("Couts")
        shipping = st.number_input("Frais de livraison par commande (EUR)", min_value=0.0, value=6.0)
        seo = st.number_input("Consultant SEO (EUR/mois)", min_value=0.0, value=200.0)
        ads = st.number_input("Budget publicite (EUR/mois)", min_value=0.0, value=300.0)
    
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
        st.metric("Nombre de commandes", str(metrics["Commandes"]))
        st.metric("Chiffre d'affaires", f"{metrics['Chiffre_affaires']} EUR")
        st.metric("Frais Shopify", f"{metrics['Frais_Shopify']} EUR")
    
    with col2:
        st.subheader("Marges")
        st.metric("Marge brute", f"{metrics['Marge_brute']} EUR")
        st.metric("Marge nette", f"{metrics['Marge_nette']} EUR")
        st.metric("Taux de marge brute", f"{metrics['Taux_marge_brute']}%")
    
    # Graphique en cascade
    fig = go.Figure(go.Waterfall(
        name="Cascade financiere",
        orientation="v",
        measure=["relative", "relative", "relative", "relative", "relative", "total", "relative", "total"],
        x=["CA", "Frais Shopify", "Cout d'achat", "Livraison", "Marge brute", "Couts fixes", "Marge nette"],
        y=[
            metrics["Chiffre_affaires"],
            -metrics["Frais_Shopify"],
            -metrics["Cout_achat_total"],
            -metrics["Frais_livraison"],
            metrics["Marge_brute"],
            -(seo + ads + 32 + 1.25),  # Coûts fixes
            metrics["Marge_nette"]
        ],
        connector={"line": {"color": "rgb(63, 63, 63)"}},
    ))

    fig.update_layout(
        title="Decomposition du resultat",
        showlegend=False,
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Ratios additionnels
    st.subheader("Ratios cles")
    st.metric("Ratio marketing", f"{metrics['Ratio_marketing']}%")
    st.metric("Point mort", f"{metrics['Point_mort']} EUR")

if __name__ == "__main__":
    main()
