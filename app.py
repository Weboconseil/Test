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

def initialize_session_state():
    """Initialise les variables de session"""
    if 'baskets' not in st.session_state:
        st.session_state.baskets = [
            {
                "name": "Panier Standard",
                "price": 50.0,
                "margin": 60.0,
                "volume": 50.0,
                "shipping": 0.0
            },
            {
                "name": "Panier Premium",
                "price": 50.0,
                "margin": 60.0,
                "volume": 50.0,
                "shipping": 0.0
            }
        ]
    if 'additional_costs' not in st.session_state:
        st.session_state.additional_costs = []

def add_basket():
    """Ajoute un nouveau panier avec des valeurs par défaut"""
    st.session_state.baskets.append({
        "name": f"Nouveau Panier {len(st.session_state.baskets) + 1}",
        "price": 50.0,
        "margin": 60.0,
        "volume": 0.0,
        "shipping": 0.0
    })

def remove_last_basket():
    """Supprime le dernier panier de la liste"""
    if len(st.session_state.baskets) > 1:  # Garder au moins un panier
        st.session_state.baskets.pop()

def update_basket_value(basket_index, field, value):
    """Met à jour une valeur spécifique d'un panier"""
    st.session_state.baskets[basket_index][field] = value

def main():
    st.title("Calculateur E-commerce")
    initialize_session_state()
    
    # Sidebar pour les paramètres globaux
    st.sidebar.header("Paramètres globaux")
    traffic = st.sidebar.number_input("Trafic mensuel", min_value=0, value=1000, step=1)
    conversion_rate = st.sidebar.number_input("Taux de conversion (%)", 
                                            min_value=0.0, 
                                            max_value=100.0, 
                                            value=2.0, 
                                            step=0.1,
                                            format="%.1f")
    tax_rate = st.sidebar.number_input("Taux d'impôt (%)", 
                                      min_value=0.0, 
                                      max_value=100.0, 
                                      value=20.0, 
                                      step=1.0)

    # Configuration des paniers
    st.header("1. Configuration des paniers")
    
    # Boutons pour ajouter/supprimer des paniers
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Ajouter un panier"):
            add_basket()
    with col2:
        if st.button("Supprimer dernier panier"):
            remove_last_basket()

    # Affichage des paniers en colonnes (2 par ligne)
    total_volume = 0
    for i in range(0, len(st.session_state.baskets), 2):
        col1, col2 = st.columns(2)
        
        # Premier panier de la ligne
        with col1:
            if i < len(st.session_state.baskets):
                st.subheader(f"Panier {i+1}")
                basket = st.session_state.baskets[i]
                basket["name"] = st.text_input(f"Nom du panier {i+1}", basket["name"])
                basket["price"] = st.number_input(
                    f"Prix d'achat (EUR)", 
                    min_value=0.0, 
                    value=basket["price"], 
                    step=1.0,
                    key=f"price_{i}",
                    on_change=update_basket_value,
                    args=(i, "price",)
                )
                basket["margin"] = st.number_input(
                    f"Marge (%)", 
                    min_value=0.0, 
                    value=basket["margin"], 
                    step=1.0,
                    key=f"margin_{i}",
                    on_change=update_basket_value,
                    args=(i, "margin",)
                )
                basket["volume"] = st.number_input(
                    f"Part volume (%)", 
                    min_value=0.0, 
                    max_value=100.0, 
                    value=basket["volume"], 
                    step=1.0,
                    key=f"volume_{i}",
                    on_change=update_basket_value,
                    args=(i, "volume",)
                )
                basket["shipping"] = st.number_input(
                    f"Frais annexes (EUR)", 
                    min_value=0.0, 
                    value=basket["shipping"], 
                    step=1.0,
                    key=f"shipping_{i}",
                    on_change=update_basket_value,
                    args=(i, "shipping",)
                )
                total_volume += basket["volume"]
        
        # Deuxième panier de la ligne
        with col2:
            if i+1 < len(st.session_state.baskets):
                st.subheader(f"Panier {i+2}")
                basket = st.session_state.baskets[i+1]
                basket["name"] = st.text_input(f"Nom du panier {i+2}", basket["name"])
                basket["price"] = st.number_input(
                    f"Prix d'achat (EUR)", 
                    min_value=0.0, 
                    value=basket["price"], 
                    step=1.0,
                    key=f"price_{i+1}",
                    on_change=update_basket_value,
                    args=(i+1, "price",)
                )
                basket["margin"] = st.number_input(
                    f"Marge (%)", 
                    min_value=0.0, 
                    value=basket["margin"], 
                    step=1.0,
                    key=f"margin_{i+1}",
                    on_change=update_basket_value,
                    args=(i+1, "margin",)
                )
                basket["volume"] = st.number_input(
                    f"Part volume (%)", 
                    min_value=0.0, 
                    max_value=100.0, 
                    value=basket["volume"], 
                    step=1.0,
                    key=f"volume_{i+1}",
                    on_change=update_basket_value,
                    args=(i+1, "volume",)
                )
                basket["shipping"] = st.number_input(
                    f"Frais annexes (EUR)", 
                    min_value=0.0, 
                    value=basket["shipping"], 
                    step=1.0,
                    key=f"shipping_{i+1}",
                    on_change=update_basket_value,
                    args=(i+1, "shipping",)
                )
                total_volume += basket["volume"]

    # Vérification du volume total
    if abs(total_volume - 100) > 0.01:
        st.warning(f"⚠️ La somme des parts de volume est de {total_volume}%. Elle devrait être de 100%.")

    # Charges fixes
    st.header("2. Charges fixes mensuelles")
    
    seo_cost = st.number_input("Consultant SEO (EUR/mois)", 
                              min_value=0.0, 
                              value=200.0, 
                              step=1.0)
    marketing_cost = st.number_input("Marketing (EUR/mois)", 
                                   min_value=0.0, 
                                   value=300.0, 
                                   step=1.0)
    
    # Ajout dynamique de coûts fixes
    if st.button("Ajouter un coût fixe"):
        st.session_state.additional_costs.append({"name": "", "amount": 0.0})

    additional_fixed_costs = 0
    for i, cost in enumerate(st.session_state.additional_costs):
        col1, col2 = st.columns(2)
        with col1:
            cost["name"] = st.text_input(f"Nom du coût {i+1}", cost["name"])
        with col2:
            cost["amount"] = st.number_input(f"Montant (EUR) {i+1}", 
                                           min_value=0.0, 
                                           value=cost["amount"], 
                                           step=1.0)
        additional_fixed_costs += cost["amount"]

    # Calculs
    if st.button("Calculer les résultats"):
        # Vérification du volume total
        if abs(total_volume - 100) > 0.01:
            st.error("La somme des parts de volume doit être égale à 100%")
            return

        total_revenue = 0
        total_orders = 0
        purchase_cost = 0
        shipping_cost = 0
        basket_revenues = []

        # Calculs pour chaque panier
        for basket in st.session_state.baskets:
            selling_price, nb_orders, revenue = calculate_sales_basket(
                basket["price"], basket["margin"], basket["volume"], 
                traffic, conversion_rate
            )
            total_revenue += revenue
            total_orders += nb_orders
            purchase_cost += basket["price"] * nb_orders
            shipping_cost += basket["shipping"] * nb_orders
            basket_revenues.append((basket["name"], revenue))

        # Coûts variables
        shopify_fees = calculate_shopify_fees(total_revenue, total_orders)

        # Coûts fixes
        fixed_costs = seo_cost + marketing_cost + additional_fixed_costs

        # Marges
        variable_costs = purchase_cost + shipping_cost + shopify_fees
        gross_margin = total_revenue - variable_costs
        net_margin = gross_margin - fixed_costs
        
        # Impôts et résultat net
        profit_before_tax = net_margin
        tax = max(0, profit_before_tax * (tax_rate/100))
        net_result = profit_before_tax - tax

        # Ratios
        gross_margin_rate = (gross_margin / total_revenue) * 100 if total_revenue > 0 else 0
        marketing_ratio = (marketing_cost / total_revenue) * 100 if total_revenue > 0 else 0
        break_even = fixed_costs / (gross_margin_rate/100) if gross_margin_rate > 0 else 0

        # Affichage des résultats
        st.header("Résultats mensuels")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Détail par panier")
            for basket_name, revenue in basket_revenues:
                st.write(f"CA {basket_name}: {revenue:.2f} EUR")
            st.write(f"Nombre total de commandes: {total_orders:.0f}")
            
        with col2:
            st.subheader("Métriques financières")
            st.write(f"Chiffre d'affaires total: {total_revenue:.2f} EUR")
            st.write(f"Marge brute: {gross_margin:.2f} EUR")
            st.write(f"Marge nette (Résultat avant impôt): {profit_before_tax:.2f} EUR")
            st.write(f"Impôts: {tax:.2f} EUR")
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

if __name__ == "__main__":
    st.set_page_config(page_title="Calculateur E-commerce", layout="wide")
    main()
