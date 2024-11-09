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
            'part_volume': 50  # Part de volume initiale égale pour chaque panier
        } for i in range(2)]

def calculate_financials(inputs, paniers_data):
    # Calcul du nombre total de commandes
    nb_commandes_total = inputs['trafic_mensuel'] * (inputs['taux_conversion'] / 100)
    
    # Calcul du chiffre d'affaires pour chaque panier
    ca_par_panier = {}
    nb_commandes_par_panier = {}
    ca_total = 0
    
    for panier in paniers_data:
        # Calcul du nombre de commandes pour ce panier
        nb_commandes = nb_commandes_total * (panier['part_volume'] / 100)
        nb_commandes_par_panier[panier['nom']] = nb_commandes
        
        # Calcul du CA pour ce panier
        ca_panier = nb_commandes * panier['prix_achat'] * (1 + panier['marge'] / 100)
        ca_par_panier[panier['nom']] = ca_panier
        ca_total += ca_panier
    
    # Calcul des charges variables
    commissions = (ca_total * 0.029) + (nb_commandes_total * 0.30)
    frais_livraison = nb_commandes_total * inputs['frais_livraison']
    charges_variables = commissions + frais_livraison
    
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
    seuil_rentabilite = charges_fixes / (1 - (charges_variables / ca_total))
    
    resultats = {
        'Nombre de commandes': round(nb_commandes_total),
        'Chiffre d\'affaires Total': ca_total,
        'Charges Variables': charges_variables,
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

def validate_volume_parts():
    """
    Vérifie que la somme des parts de volume est égale à 100%
    """
    total = sum(panier['part_volume'] for panier in st.session_state.paniers_data)
    return abs(total - 100) < 0.01  # Permettre une petite marge d'erreur pour les arrondis

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
        panier['part_volume'] = st.number_input(
            'Part du volume (%)',
            min_value=0.0,
            max_value=100.0,
            value=float(panier['part_volume']),
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
            st.session_state.num_paniers += 1
            # Ajuster les parts de volume pour maintenir un total de 100%
            nouvelle_part = 100 / st.session_state.num_paniers
            for panier in st.session_state.paniers_data:
                panier['part_volume'] = nouvelle_part
            st.session_state.paniers_data.append({
                'nom': f'Panier {st.session_state.num_paniers}',
                'prix_achat': 10.0,
                'frais_annexes': 2.0,
                'marge': 60,
                'part_volume': nouvelle_part
            })
    
    with col_remove:
        if st.session_state.num_paniers > 1 and st.button('Supprimer le dernier panier'):
            st.session_state.num_paniers -= 1
            st.session_state.paniers_data.pop()
            # Réajuster les parts de volume
            nouvelle_part = 100 / st.session_state.num_paniers
            for panier in st.session_state.paniers_data:
                panier['part_volume'] = nouvelle_part
    
    # Afficher les inputs pour chaque panier
    for i in range(st.session_state.num_paniers):
        st.subheader(f'Configuration {st.session_state.paniers_data[i]["nom"]}')
        display_panier_inputs(i)
        st.divider()
    
    # Vérifier que la somme des parts de volume est égale à 100%
    if not validate_volume_parts():
        st.error('La somme des parts de volume doit être égale à 100%')
        return
    
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
                'Part du volume (%)': f"{panier['part_volume']}%",
                'Nombre de commandes': format_number_fr(resultats[f"Commandes {panier['nom']}"], is_currency=False),
                'Chiffre d\'affaires': format_number_fr(resultats[f"CA {panier['nom']}"])
            })
        
        df_details = pd.DataFrame(details_paniers)
        st.table(df_details)
        
        # Afficher les autres métriques
        st.subheader('Détail des métriques')
        autres_metriques = {k: v for k, v in resultats.items() 
                           if not k.startswith('CA ') and not k.startswith('Commandes ')}
        df_resultats = pd.DataFrame(list(autres_metriques.items()), columns=['Métrique', 'Valeur'])
        df_resultats['Valeur'] = df_resultats.apply(lambda row: 
            format_number_fr(row['Valeur'], is_currency=False, is_integer=True) 
            if row['Métrique'] == 'Nombre de commandes'
            else format_number_fr(row['Valeur']), axis=1)
        st.table(df_resultats)

if __name__ == '__main__':
    main()
