import streamlit as st
import pandas as pd

def calculate_metrics(traffic, conversion_rate, baskets, fixed_costs, shipping_cost):
    # Calcul du nombre de commandes
    orders = traffic * (conversion_rate / 100)
    
    # Validation des pourcentages de volume
    total_volume = sum(basket['volume'] for basket in baskets)
    if total_volume != 100:
        st.warning(f"Attention: La somme des parts de volume est de {total_volume}% au lieu de 100%")
    
    # Calcul du panier moyen pondéré et des coûts
    revenue = 0
    total_purchase_cost = 0
    
    for basket in baskets:
        basket_revenue = orders * basket['price'] * (basket['volume']/100)
        revenue += basket_revenue
        purchase_cost = basket_revenue * (1 - basket['margin']/100)
        total_purchase_cost += purchase_cost
    
    # Coûts variables
    shopify_fees = (revenue * 0.029) + (orders * 0.30)
    shipping_costs = orders * shipping_cost
    
    # Total des coûts fixes
    total_fixed_costs = sum(cost['amount'] for cost in fixed_costs)
    
    # Calcul des marges
    gross_margin = revenue - total_purchase_cost - shipping_costs - shopify_fees
    net_margin = gross_margin - total_fixed_costs
    
    # Ratios
    gross_margin_rate = (gross_margin / revenue) * 100 if revenue > 0 else 0
    break_even = total_fixed_costs / (gross_margin_rate/100) if gross_margin_rate > 0 else 0
    
    return {
        "Commandes": round(orders, 2),
        "Chiffre_affaires": round(revenue, 2),
        "Frais_Shopify": round(shopify_fees, 2),
        "Cout_achat_total": round(total_purchase_cost, 2),
        "Frais_livraison": round(shipping_costs, 2),
        "Couts_fixes": round(total_fixed_costs, 2),
        "Marge_brute": round(gross_margin, 2),
        "Marge_nette": round(net_margin, 2),
        "Taux_marge_brute": round(gross_margin_rate, 2),
        "Point_mort": round(break_even, 2)
    }

def main():
    st.title("Previsions Financieres E-commerce")
    
    # Initialisation des listes dans la session state
    if 'baskets' not in st.session_state:
        st.session_state.baskets = [
            {"name": "Panier 1", "price": 80.0, "margin": 60.0, "volume": 50.0},
            {"name": "Panier 2", "price": 60.0, "margin": 40.0, "volume": 50.0}
        ]
    
    if 'fixed_costs' not in st.session_state:
        st.session_state.fixed_costs = [
            {"name": "Abonnement Shopify", "amount": 32.0},
            {"name": "Consultant SEO", "amount": 200.0},
            {"name": "Nom de domaine", "amount": 1.25},
            {"name": "Publicite", "amount": 300.0}
        ]
    
    with st.sidebar:
        st.header("Hypotheses")
        
        # Trafic et conversion
        st.subheader("Trafic et Conversion")
        traffic = st.number_input("Trafic mensuel", min_value=0, value=1000)
        conversion = st.number_input("Taux de conversion (%)", min_value=0.0, value=2.0)
        shipping = st.number_input("Frais de livraison par commande (EUR)", min_value=0.0, value=6.0)
        
        # Gestion des paniers
        st.subheader("Paniers")
        if st.button("Ajouter un panier"):
            st.session_state.baskets.append({
                "name": f"Panier {len(st.session_state.baskets) + 1}",
                "price": 0.0,
                "margin": 0.0,
                "volume": 0.0
            })
        
        # Affichage et modification des paniers
        for i, basket in enumerate(st.session_state.baskets):
            st.markdown(f"**{basket['name']}**")
            basket['price'] = st.number_input(
                f"Prix {basket['name']} (EUR)",
                min_value=0.0,
                value=float(basket['price']),
                key=f"price_{i}"
            )
            basket['margin'] = st.number_input(
                f"Marge {basket['name']} (%)",
                min_value=0.0,
                value=float(basket['margin']),
                key=f"margin_{i}"
            )
            basket['volume'] = st.number_input(
                f"Part volume {basket['name']} (%)",
                min_value=0.0,
                max_value=100.0,
                value=float(basket['volume']),
                key=f"volume_{i}"
            )
            if st.button(f"Supprimer {basket['name']}", key=f"del_basket_{i}"):
                st.session_state.baskets.pop(i)
                st.experimental_rerun()
                
        # Gestion des coûts fixes
        st.subheader("Couts fixes")
        if st.button("Ajouter un cout fixe"):
            st.session_state.fixed_costs.append({
                "name": "Nouveau cout",
                "amount": 0.0
            })
        
        # Affichage et modification des coûts fixes
        for i, cost in enumerate(st.session_state.fixed_costs):
            col1, col2 = st.columns([2, 1])
            with col1:
                cost['name'] = st.text_input(
                    "Nom",
                    value=cost['name'],
                    key=f"cost_name_{i}"
                )
            with col2:
                cost['amount'] = st.number_input(
                    "EUR",
                    min_value=0.0,
                    value=float(cost['amount']),
                    key=f"cost_amount_{i}"
                )
            if st.button(f"Supprimer", key=f"del_cost_{i}"):
                st.session_state.fixed_costs.pop(i)
                st.experimental_rerun()
    
    # Calcul et affichage des résultats
    metrics = calculate_metrics(
        traffic,
        conversion,
        st.session_state.baskets,
        st.session_state.fixed_costs,
        shipping
    )
    
    # Affichage des résultats en colonnes
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Revenus")
        st.metric("Nombre de commandes", str(metrics["Commandes"]))
        st.metric("Chiffre d'affaires", f"{metrics['Chiffre_affaires']} EUR")
        st.metric("Frais Shopify", f"{metrics['Frais_Shopify']} EUR")
        st.metric("Cout d'achat total", f"{metrics['Cout_achat_total']} EUR")
        st.metric("Frais de livraison", f"{metrics['Frais_livraison']} EUR")
    
    with col2:
        st.subheader("Marges et couts")
        st.metric("Couts fixes", f"{metrics['Couts_fixes']} EUR")
        st.metric("Marge brute", f"{metrics['Marge_brute']} EUR")
        st.metric("Marge nette", f"{metrics['Marge_nette']} EUR")
        st.metric("Taux de marge brute", f"{metrics['Taux_marge_brute']}%")
        st.metric("Point mort", f"{metrics['Point_mort']} EUR")

if __name__ == "__main__":
    main()
