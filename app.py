# Installation des dépendances nécessaires
!pip install ipywidgets

import ipywidgets as widgets
from IPython.display import display, HTML
import pandas as pd

# Création des widgets pour l'interface
style = {'description_width': '200px'}
layout = widgets.Layout(width='400px')

class EcommerceCalculator:
    def __init__(self):
        self.paniers = []
        self.current_panier_id = 1
        
        # Création de l'interface principale
        self.main_container = widgets.VBox([])
        self.paniers_container = widgets.VBox([])
        self.setup_interface()
        
    def create_float_widget(self, description, value=0.0, step=0.1):
        return widgets.FloatText(
            value=value,
            description=description,
            style=style,
            layout=layout
        )
    
    def create_section(self, title):
        return widgets.HTML(value=f"<h3 style='color: #2c3e50; margin-top: 20px;'>{title}</h3>")
    
    def create_panier_section(self, panier_id):
        # Créer le widget de titre personnalisable
        titre_widget = widgets.Text(
            value=f'Panier {panier_id}',
            description='Nom du panier:',
            style=style,
            layout=layout
        )
        
        panier = widgets.VBox([
            self.create_section(f"Panier {panier_id}"),
            titre_widget,
            self.create_float_widget('Prix achat (EUR):', 0.0),
            self.create_float_widget('Frais annexes (EUR):', 0.0),
            self.create_float_widget('Marge beneficiaire (%):', 60.0),
            widgets.FloatText(
                value=1.0,
                description='Part du volume (%):',
                style=style,
                layout=layout
            )
        ])
        
        # Mettre à jour le titre de la section quand le nom change
        def update_title(change):
            panier.children[0].value = f"<h3 style='color: #2c3e50; margin-top: 20px;'>{change.new}</h3>"
        titre_widget.observe(update_title, names='value')
        
        return panier
    
    def add_panier(self, b):
        new_panier = self.create_panier_section(self.current_panier_id)
        self.paniers.append(new_panier)
        self.current_panier_id += 1
        self.update_paniers_display()
    
    def remove_last_panier(self, b):
        if len(self.paniers) > 1:  # Garder au moins un panier
            self.paniers.pop()
            self.current_panier_id -= 1
            self.update_paniers_display()
    
    def update_paniers_display(self):
        self.paniers_container.children = tuple(self.paniers)
    
    def setup_interface(self):
        # Créer le premier panier
        first_panier = self.create_panier_section(self.current_panier_id)
        self.paniers.append(first_panier)
        self.current_panier_id += 1
        
        # Boutons pour gérer les paniers
        self.add_panier_button = widgets.Button(
            description='Ajouter un panier',
            style=widgets.ButtonStyle(button_color='#2ecc71'),
            layout=widgets.Layout(width='150px')
        )
        self.remove_panier_button = widgets.Button(
            description='Supprimer un panier',
            style=widgets.ButtonStyle(button_color='#e74c3c'),
            layout=widgets.Layout(width='150px')
        )
        
        self.add_panier_button.on_click(self.add_panier)
        self.remove_panier_button.on_click(self.remove_last_panier)
        
        # Section trafic
        self.trafic_section = widgets.VBox([
            self.create_section("Trafic"),
            widgets.IntText(value=0, description='Trafic mensuel:', style=style, layout=layout),
            self.create_float_widget('Taux conversion (%):', 1.0),
        ])
        
        # Section charges variables
        self.charges_variables_section = widgets.VBox([
            self.create_section("Charges Variables"),
            self.create_float_widget('Commission (%):', 2.9),
            self.create_float_widget('Commission fixe/cmd (EUR):', 0.30),
            self.create_float_widget('Frais livraison/cmd (EUR):', 6.0),
        ])
        
        # Section charges fixes
        self.charges_fixes_section = widgets.VBox([
            self.create_section("Charges Fixes Mensuelles"),
            self.create_float_widget('Abonnement Shopify (EUR):', 32.0),
            self.create_float_widget('Consultant SEO (EUR):', 200.0),
            self.create_float_widget('Nom de domaine (EUR/mois):', 1.25),
            self.create_float_widget('Marketing (EUR):', 250.0),
        ])
        
        # Bouton de calcul
        self.calculate_button = widgets.Button(
            description='Calculer la rentabilite',
            style=widgets.ButtonStyle(button_color='#3498db'),
            layout=widgets.Layout(width='200px')
        )
        
        self.output = widgets.Output()
        self.calculate_button.on_click(self.calculate_results)
        
        # Mise à jour de l'interface
        self.update_paniers_display()
        self.main_container.children = (
            widgets.HBox([self.add_panier_button, self.remove_panier_button]),
            self.paniers_container,
            self.trafic_section,
            self.charges_variables_section,
            self.charges_fixes_section,
            self.calculate_button,
            self.output
        )
    
    def calculate_results(self, b):
        with self.output:
            self.output.clear_output()
            
            # Récupération des valeurs de trafic et charges
            trafic = self.trafic_section.children[1].value
            conversion = self.trafic_section.children[2].value / 100
            
            comm_percent = self.charges_variables_section.children[1].value / 100
            comm_fixe = self.charges_variables_section.children[2].value
            frais_livraison = self.charges_variables_section.children[3].value
            
            shopify = self.charges_fixes_section.children[1].value
            seo = self.charges_fixes_section.children[2].value
            domaine = self.charges_fixes_section.children[3].value
            marketing = self.charges_fixes_section.children[4].value
            
            # Calculs pour chaque panier
            nb_commandes = trafic * conversion
            ca_total = 0
            resultats_paniers = []
            
            # Normaliser les parts de volume
            total_parts = sum(panier.children[5].value for panier in self.paniers)
            
            for i, panier in enumerate(self.paniers, 1):
                nom_panier = panier.children[1].value
                prix = panier.children[2].value
                frais = panier.children[3].value
                marge = panier.children[4].value / 100
                part = panier.children[5].value / total_parts
                
                prix_vente = (prix + frais) / (1 - marge)
                ca_panier = nb_commandes * part * prix_vente
                
                resultats_paniers.append({
                    'Panier': nom_panier,
                    'Prix de vente': f"{prix_vente:.2f} EUR",
                    'Part du volume': f"{part*100:.1f}%",
                    'CA': f"{ca_panier:.2f} EUR"
                })
                
                ca_total += ca_panier
            
            charges_variables = (ca_total * comm_percent) + (nb_commandes * comm_fixe) + (nb_commandes * frais_livraison)
            charges_fixes = shopify + seo + domaine + marketing
            
            marge_brute = ca_total - charges_variables
            resultat_avant_impot = marge_brute - charges_fixes
            impot = max(0, resultat_avant_impot * 0.25)
            resultat_net = resultat_avant_impot - impot
            
            # Affichage des résultats par panier
            display(HTML("<h2 style='color: #2c3e50;'>Détail par panier</h2>"))
            df_paniers = pd.DataFrame(resultats_paniers)
            display(df_paniers.style.set_properties(**{
                'background-color': '#f8f9fa',
                'border': '1px solid #dee2e6',
                'padding': '8px'
            }))
            
            # Affichage des résultats globaux
            display(HTML("<h2 style='color: #2c3e50;'>Résultats Mensuels Globaux</h2>"))
            results_df = pd.DataFrame({
                'Metrique': [
                    'Nombre de commandes',
                    'Chiffre affaires total',
                    'Charges variables',
                    'Charges fixes',
                    'Marge brute',
                    'Resultat avant impot',
                    'Impot estime',
                    'Resultat net'
                ],
                'Valeur': [
                    f"{nb_commandes:.0f}",
                    f"{ca_total:.2f} EUR",
                    f"{charges_variables:.2f} EUR",
                    f"{charges_fixes:.2f} EUR",
                    f"{marge_brute:.2f} EUR",
                    f"{resultat_avant_impot:.2f} EUR",
                    f"{impot:.2f} EUR",
                    f"{resultat_net:.2f} EUR"
                ]
            })
            
            styled_df = results_df.style\
                .set_properties(**{'background-color': '#f8f9fa', 'border': '1px solid #dee2e6', 'padding': '8px'})\
                .set_table_styles([
                    {'selector': 'th', 'props': [('background-color', '#e9ecef'), ('font-weight', 'bold')]},
                    {'selector': '', 'props': [('border-collapse', 'collapse')]}
                ])
            
            display(styled_df)

# Création et affichage de l'interface
calculator = EcommerceCalculator()
display(calculator.main_container)
