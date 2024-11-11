import streamlit as st

# Initialisation des valeurs par défaut
st.title("Calculateur de Prévisions Financières E-commerce")

# Section : Données de base des paniers
st.header("1. Configuration des Paniers")
panier1_prix_achat = st.number_input("Prix d'achat Panier 1 (€)", value=50)
panier1_marge = st.number_input("Marge Panier 1 (%)", value=60)
panier1_volume = st.number_input("Part volume Panier 1 (%)", value=50)

panier2_prix_achat = st.number_input("Prix d'achat Panier 2 (€)", value=50)
panier2_marge = st.number_input("Marge Panier 2 (%)", value=60)
panier2_volume = st.number_input("Part volume Panier 2 (%)", value=50)

# Section : Trafic et conversion
st.header("2. Trafic et Conversion")
trafic_mensuel = st.number_input("Trafic mensuel initial (visites)", value=1000)
taux_conversion = st.number_input("Taux de conversion (%)", value=2) / 100

# Section : Charges d'exploitation
st.header("3. Charges d'exploitation")
# Variables
frais_annexes_1 = st.number_input("Frais annexes Panier 1 (€)", value=0)
frais_annexes_2 = st.number_input("Frais annexes Panier 2 (€)", value=0)

# Charges fixes
st.subheader("Charges Fixes")
shopify_commission = 0.029
shopify_fees = 0.30
consultant_seo = st.number_input("Consultant SEO (€)", value=200)
marketing = st.number_input("Marketing (€)", value=300)
taux_impot = st.number_input("Taux d'imposition (%)", value=20) / 100

# Calcul du chiffre d'affaires par panier
nb_commandes = trafic_mensuel * taux_conversion
prix_vente_1 = panier1_prix_achat * (1 + panier1_marge / 100)
prix_vente_2 = panier2_prix_achat * (1 + panier2_marge / 100)
ca_1 = nb_commandes * panier1_volume / 100 * prix_vente_1
ca_2 = nb_commandes * panier2_volume / 100 * prix_vente_2
ca_total = ca_1 + ca_2

# Calcul des coûts variables
couts_variables_1 = frais_annexes_1 * (nb_commandes * panier1_volume / 100)
couts_variables_2 = frais_annexes_2 * (nb_commandes * panier2_volume / 100)
couts_variables_totaux = couts_variables_1 + couts_variables_2

# Calcul des coûts fixes
frais_transactions = ca_total * shopify_commission + nb_commandes * shopify_fees
couts_fixes_totaux = consultant_seo + marketing + frais_transactions

# Calculs finaux
marge_brute = ca_total - (panier1_prix_achat * (nb_commandes * panier1_volume / 100) + panier2_prix_achat * (nb_commandes * panier2_volume / 100)) - couts_variables_totaux
marge_nette = marge_brute - couts_fixes_totaux
impot = marge_nette * taux_impot
resultat_net = marge_nette - impot

# Affichage des résultats
st.header("4. Résultats Financiers")
st.write("Nombre de commandes estimé:", nb_commandes)
st.write("Chiffre d'affaires total (€):", ca_total)
st.write("Marge brute (€):", marge_brute)
st.write("Marge nette avant impôt (€):", marge_nette)
st.write("Impôt (€):", impot)
st.write("Résultat net (€):", resultat_net)
