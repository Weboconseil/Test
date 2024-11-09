import streamlit as st
import pandas as pd
import locale

# Configuration du format français pour les nombres
try:
    locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_ALL, 'fr_FR')
    except:
        pass

def format_number_fr(number, decimal_places=2, is_currency=True, is_integer=False):
    """
    Formate les nombres au format français
    """
    try:
        if is_integer:
            return locale.format_string("%d", round(number), grouping=True)
        
        if is_currency:
            number_str = locale.format_string(f"%.{decimal_places}f", number, grouping=True)
            return f"{number_str.replace('.', ',')} €"
        else:
            return locale.format_string(f"%.{decimal_places}f", number, grouping=True).replace('.', ',')
    except:
        # Fallback si locale ne fonctionne pas
        if is_integer:
            return f"{round(number):,}".replace(',', ' ')
        
        if is_currency:
            return f"{number:,.{decimal_places}f} €".replace(',', ' ').replace('.', ',')
        else:
            return f"{number:.{decimal_places}f}".replace('.', ',')

def initialize_session_state():
    if 'num_paniers' not in st.session_state:
        st.session_state.num_paniers = 2
    if 'paniers_data' not in st.session_state:
        st.session_state.paniers_data = [{
            'nom': f'Panier {i+1}',
            'prix_achat': 10.0,
            'frais_annexes': 2.0,
            'marge': 60,
            'volume': 50  # Ajout du volume en pourcentage
        } for i in range(2)]

def calculate_financials(inputs, paniers_data):
    # Calcul du nombre total de commandes
    nb_commandes_total = inputs['trafic_mensuel'] * (inputs['taux_conversion'] / 100)
    
    # Calcul du chiffre d'affaires et des charges variables pour chaque panier
    ca_par_panier = {}
    ca_total = 0
    charges_variables_achats = 0
    nb_commandes_par_panier = {}
    
    for panier in paniers_data:
        # Calcul du nombre de commandes pour ce panier
        nb_commandes = nb_commandes_total * (panier['volume'] / 100)
        nb_commandes_par_panier[panier['nom']] = nb_commandes
        
        # Calcul du CA pour ce panier
        ca_panier = nb_commandes * panier['prix_achat'] * (1 + panier['marge'] / 100)
        ca_par_panier[panier['nom']] = ca_panier
        ca_total += ca_panier
        
        # Calcul des charges variables d'achat pour ce panier
        charges_variables_achats += nb_commandes * panier['prix_achat']
    
    # Calcul des frais de livraison
    frais_livraison_total = nb_commandes_total * inputs['frais_livraison']
    
    # Total des charges variables
    charges_variables = charges_variables_achats + frais_livraison_total
    
    # Calcul des charges fixes mensuelles
    charges_fixes = (
        inputs['abonnement_shopify'] +
        inputs['consultant_seo'] +
        (inputs['nom_domaine'] / 12) +
        inputs['marketing']
    )
    
    # Calculs finaux
    marge_brute = ca_total - charges_variables
    resultat_avant_impot = marge_brute - charges_fixes
    impot = resultat_avant_impot * 0.25 if resultat_avant_impot > 0 else 0
    resultat_net = resultat_avant_impot - impot
    
    # Calcul du seuil de rentabilité
    if ca_total > 0:
        seuil_rentabilite = charges_fixes / (1 - (charges_variables / ca_total))
    else:
        seuil_rentabilite = 0
    
    resultats = {
        'Nombre de commandes': round(nb_commandes_total),
        'Chiffre d\'affaires Total': ca_total,
        'Charges Variables Achats': charges_variables_achats,
        'Charges Variables Livraison': frais_livraison_total,
        'Charges Variables Total': charges_variables,
        'Charges Fixes': charges_fixes,
        'Marge Brute': marge_brute,
        'Résultat avant impôt': resultat_avant_impot,
        'Impôt': impot,
        'Résultat Net': resultat_net,
        'Seuil de rentabilité': seuil_rentabilite
    }
    
    # Ajouter le CA et le nombre de commandes par panier aux résultats
    for nom_panier, ca in ca_par_panier.items():
        resultats[f"CA {nom_panier}"] = ca
        resultats[f"Commandes {nom_panier}"] = nb_commandes_par_panier[nom_panier]
        
    return resultats

def display_panier_inputs(index):
    panier = st.session_state.paniers_data[index]
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        nouveau_nom = st.text_input(
            'Nom du panier',
            value=panier['nom'],
            key=f'nom_{index}'
        )
        panier['nom'] = nouveau_nom
        
    with col2:
        panier['prix_achat'] = st.number_input(
            'Prix d\'achat',
            value=panier['prix_achat'],
            key=f'prix_{index}',
            step=1.0
        )
        
    with col3:
        panier['marge'] = st.slider(
            'Marge (%)',
            0, 200, int(panier['marge']),
            key=f'marge_{index}'
        )

    with col4:
        panier['volume'] = st.number_input(
            'Volume (%)',
            min_value=0.0,
            max_value=100.0,
            value=float(panier['volume']) if 'volume' in panier else 100.0 / st.session_state.num_paniers,
            key=f'volume_{index}',
            step=1.0
        )

def main():
    st.title('Calculateur de Rentabilité E-commerce')
    
    # Initialiser l'état de la session
    initialize_session_state()
    
    # Gestion des paniers
    st.header('1. Gestion des paniers')
    
    col_add, col_remove = st.columns([1, 1])
    with col_add:
        if st.button('Ajouter un panier'):
            nouveau_volume = 100.0 / (st.session_state.num_paniers + 1)
            # Ajuster les volumes existants
            for panier in st.session_state.paniers_data:
                panier['volume'] = nouveau_volume
            
            st.session_state.num_paniers += 1
            st.session_state.paniers_data.append({
                'nom': f'Panier {st.session_state.num_paniers}',
                'prix_achat': 10.0,
                'frais_annexes': 2.0,
                'marge': 60,
                'volume': nouveau_volume
            })
    
    with col_remove:
        if st.session_state.num_paniers > 1 and st.button('Supprimer le dernier panier'):
            st.session_state.num_paniers -= 1
            st.session_state.paniers_data.pop()
            # Réajuster les volumes pour les paniers restants
            nouveau_volume = 100.0 / st.session_state.num_paniers
            for panier in st.session_state.paniers_data:
                panier['volume'] = nouveau_volume
    
    # Afficher les inputs pour chaque panier
    for i in range(st.session_state.num_paniers):
        st.subheader(f'Configuration {st.session_state.paniers_data[i]["nom"]}')
        display_panier_inputs(i)
        st.divider()
    
    # Vérifier que la somme des volumes est égale à 100%
    total_volume = sum(panier['volume'] for panier in st.session_state.paniers_data)
    if abs(total_volume - 100) > 0.01:  # Permettre une petite marge d'erreur due aux arrondis
        st.warning(f'⚠️ La somme des volumes doit être égale à 100%. Actuellement : {total_volume:.1f}%')
    
    # Trafic et Conversion
    st.header('2. Trafic et Conversion')
    trafic_mensuel = st.number_input('Trafic mensuel', value=1000)
    taux_conversion = st.slider('Taux de conversion (%)', 0.0, 10.0, 2.0, 0.1)
    
    # Charges d'exploitation
    st.header('3. Charges d\'exploitation')
    
    st.subheader('Charges variables')
    frais_livraison = st.number_input('Frais de livraison par commande', value=6.0, step=1.0)
    
    st.subheader('Charges fixes')
    col1, col2 = st.columns(2)
    
    with col1:
        abonnement_shopify = st.number_input('Abonnement Shopify mensuel', value=32.0, step=1.0)
        consultant_seo = st.number_input('Consultant SEO mensuel', value=200.0, step=1.0)
    
    with col2:
        nom_domaine = st.number_input('Nom de domaine annuel', value=15.0, step=1.0)
        marketing = st.number_input('Budget Marketing mensuel', value=250.0, step=1.0)
    
    # Rassembler les entrées pour le calcul
    inputs = {
        'trafic_mensuel': trafic_mensuel,
        'taux_conversion': taux_conversion,
        'frais_livraison': frais_livraison,
        'abonnement_shopify': abonnement_shopify,
        'consultant_seo': consultant_seo,
        'nom_domaine': nom_domaine,
        'marketing': marketing
    }
    
    # Calculer et afficher les résultats
    if st.button('Calculer les prévisions'):
        resultats = calculate_financials(inputs, st.session_state.paniers_data)
        
        st.header('Résultats des Prévisions Financières')
        
        # Afficher les KPIs principaux
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric("Nombre de commandes", format_number_fr(resultats['Nombre de commandes'], is_currency=False, is_integer=True))
        with col2:
            st.metric("Chiffre d'affaires mensuel", format_number_fr(resultats['Chiffre d\'affaires Total']))
        with col3:
            st.metric("Marge Brute", format_number_fr(resultats['Marge Brute']))
        with col4:
            st.metric("Résultat Net", format_number_fr(resultats['Résultat Net']))
        with col5:
            st.metric("Seuil de rentabilité", format_number_fr(resultats['Seuil de rentabilité']))
        
        # Afficher le détail par panier
        st.subheader('Détail par panier')
        details_paniers = []
        for panier in st.session_state.paniers_data:
            details_paniers.append({
                'Panier': panier['nom'],
                'Volume (%)': f"{panier['volume']:.1f}%",
                'Commandes': format_number_fr(resultats[f"Commandes {panier['nom']}"], is_currency=False, is_integer=True),
                'Chiffre d\'affaires': format_number_fr(resultats[f"CA {panier['nom']}"])
            })
        
        df_details = pd.DataFrame(details_paniers)
        st.table(df_details)
        
        # Afficher le détail des charges
        st.subheader('Détail des charges')
        charges = {
            'Charges Variables Achats': resultats['Charges Variables Achats'],
            'Charges Variables Livraison': resultats['Charges Variables Livraison'],
            'Charges Variables Total': resultats['Charges Variables Total'],
            'Charges Fixes': resultats['Charges Fixes']
        }
        df_charges = pd.DataFrame(list(charges.items()), columns=['Type de charge', 'Montant'])
        df_charges['Montant'] = df_charges['Montant'].apply(lambda x: format_number_fr(x))
        st.table(df_charges)
        
        # Afficher les autres métriques financières
        st.subheader('Autres métriques financières')
        autres_metriques = {
            'Marge Brute': resultats['Marge Brute'],
            'Résultat avant impôt': resultats['Résultat avant impôt'],
            'Impôt': resultats['Impôt'],
            'Résultat Net': resultats['Résultat Net'],
            'Seuil de rentabilité': resultats['Seuil de rentabilité']
        }
        df_autres = pd.DataFrame(list(autres_metriques.items()), columns=['Métrique', 'Valeur'])
        df_autres['Valeur'] = df_autres['Valeur'].apply(lambda x: format_number_fr(x))
        st.table(df_autres)

if __name__ == '__main__':
    main()
