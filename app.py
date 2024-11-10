import streamlit as st
import pandas as pd
import numpy as np

def calculate_sales_basket(price, margin, volume_share, traffic, conversion_rate):
    """Calcule les métriques de vente pour un panier"""
    selling_price = price + (price * margin/100)
    nb_orders = traffic * (conversion_rate/100) * (volume_share/100)
    revenue = nb_orders * selling_price
    return selling_price, nb_orders, revenue

def calculate_shopify_fees(revenue, nb_orders):
    """Calcule les frais Shopify"""
    return (revenue * 0.029) + (nb_orders * 0.30)

def main():
    st.title("Calculateur E-commerce")
    
    # Sidebar pour les paramètres globaux
    st.sidebar.header("Paramètres globaux")
    traffic = st.sidebar.number_input("Trafic mensuel", min_value=0, value=1000)
    conversion_rate = st.sidebar.number_input("Taux de conversion (%)", min_value=0.0, max_value=100.0, value=2.0)
    tax_rate = st.sidebar.number_input("Taux d'impôt (%)", min_value=0.0, max_value=100.0, value=20.0)

    # Configuration des paniers
    st.header("1. Configuration des paniers")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Panier 1")
        basket1_name = st.text_input("Nom du panier 1", "Panier Standard")
        basket1_price = st.number_input("Prix d'achat Panier 1 (EUR)", min_value=0.0, value=50.0)
        basket1_margin = st.number_input("Marge Panier 1 (%)", min_value=0.0, value=60.0)
        basket1_volume = st.number_input("Part volume Panier 1 (%)", min_value=0.0, max_value=100.0, value=50.0)
        basket1_shipping = st.number_input("Frais annexes Panier 1 (EUR)", min_value=0.0, value=0.0)

    with col2:
        st.subheader("Panier 2")
        basket2_name = st.text_input("Nom du panier 2", "Panier Premium")
        basket2_price = st.number_input("Prix d'achat Panier 2 (EUR)", min_value=0.0, value=50.0)
        basket2_margin = st.number_input("Marge Panier 2 (%)", min_value=0.0, value=60.0)
        basket2_volume = st.number_input("Part volume Panier 2 (%)", min_value=0.0, max_value=100.0, value=50.0)
        basket2_shipping = st.number_input("Frais annexes Panier 2 (EUR)", min_value=0.0, value=0.0)

    # Charges fixes
    st.header("2. Charges fixes mensuelles")
    
    seo_cost = st.number_input("Consultant SEO (EUR/mois)", min_value=0.0, value=200.0)
    marketing_cost = st.number_input("Marketing (EUR/mois)", min_value=0.0, value=300.0)
    
    # Ajout dynamique de coûts fixes
    if 'additional_costs' not in st.session_state:
        st.session_state.additional_costs = []

    if st.button("Ajouter un coût fixe"):
        st.session_state.additional_costs.append({"name": "", "amount": 0.0})

    additional_fixed_costs = 0
    for i, cost in enumerate(st.session_state.additional_costs):
        col1, col2 = st.columns(2)
        with col1:
            cost["name"] = st.text_input(f"Nom du coût {i+1}", cost["name"])
        with col2:
            cost["amount"] = st.number_input(f"Montant (EUR) {i+1}", min_value=0.0, value=cost["amount"])
        additional_fixed_costs += cost["amount"]

    # Calculs
    if st.button("Calculer les résultats"):
        # Vérification que la somme des parts de volume = 100%
        if abs(basket1_volume + basket2_volume - 100) > 0.01:
            st.error("La somme des parts de volume doit être égale à 100%")
            return

        # Calculs panier 1
        selling_price1, nb_orders1, revenue1 = calculate_sales_basket(
            basket1_price, basket1_margin, basket1_volume, traffic, conversion_rate
        )

        # Calculs panier 2
        selling_price2, nb_orders2, revenue2 = calculate_sales_basket(
            basket2_price, basket2_margin, basket2_volume, traffic, conversion_rate
        )

        total_revenue = revenue1 + revenue2
        total_orders = nb_orders1 + nb_orders2

        # Coûts variables
        purchase_cost = (basket1_price * nb_orders1) + (basket2_price * nb_orders2)
        shipping_cost = (basket1_shipping * nb_orders1) + (basket2_shipping * nb_orders2)
        shopify_fees = calculate_shopify_fees(total_revenue, total_orders)

        # Coûts fixes
        fixed_costs = seo_cost + marketing_cost + additional_fixed_costs

        # Marges
        variable_costs = purchase_cost + shipping_cost + shopify_fees
        gross_margin = total_revenue - variable_costs
        net_margin = gross_margin - fixed_costs
        
        # Impôts et résultat net
        tax = max(0, net_margin * (tax_rate/100))
        net_result = net_margin - tax

        # Ratios
        gross_margin_rate = (gross_margin / total_revenue) * 100 if total_revenue > 0 else 0
        marketing_ratio = (marketing_cost / total_revenue) * 100 if total_revenue > 0 else 0
        break_even = fixed_costs / (gross_margin_rate/100) if gross_margin_rate > 0 else 0

        # Affichage des résultats
        st.header("Résultats mensuels")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Détail par panier")
            st.write(f"CA {basket1_name}: {revenue1:.2f} EUR")
            st.write(f"CA {basket2_name}: {revenue2:.2f} EUR")
            st.write(f"Nombre total de commandes: {total_orders:.0f}")
            
        with col2:
            st.subheader("Métriques financières")
            st.write(f"Chiffre d'affaires total: {total_revenue:.2f} EUR")
            st.write(f"Marge brute: {gross_margin:.2f} EUR")
            st.write(f"Marge nette: {net_margin:.2f} EUR")
            st.write(f"Résultat net: {net_result:.2f} EUR")

        st.subheader("Ratios clés")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Taux de marge brute", f"{gross_margin_rate:.1f}%")
        with col2:
            st.metric("Ratio marketing", f"{marketing_ratio:.1f}%")
        with col3:
            st.metric("Point mort", f"{break_even:.2f} EUR")

        # Détail des coûts
        with st.expander("Voir le détail des coûts"):
            st.write("Coûts variables:")
            st.write(f"- Coût d'achat total: {purchase_cost:.2f} EUR")
            st.write(f"- Frais de livraison total: {shipping_cost:.2f} EUR")
            st.write(f"- Frais Shopify: {shopify_fees:.2f} EUR")
            st.write(f"\nCoûts fixes: {fixed_costs:.2f} EUR")
            st.write(f"Impôts: {tax:.2f} EUR")

if __name__ == "__main__":
    st.set_page_config(page_title="Calculateur E-commerce", layout="wide")
    main()
