#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour calculer le rendement d'une chaudière
Plusieurs méthodes de calcul disponibles
"""

import math

class CalculateurRendementChaudiere:
    def __init__(self):
        self.nom_combustible = {
            'gaz_naturel': {'pci': 35.17, 'pcs': 39.11},  # MJ/m³
            'fuel_domestique': {'pci': 42.6, 'pcs': 45.4},  # MJ/kg
            'propane': {'pci': 46.35, 'pcs': 50.35},  # MJ/kg
            'bois': {'pci': 15.0, 'pcs': 18.5},  # MJ/kg (valeurs moyennes)
        }
    
    def rendement_direct(self, energie_utile, energie_consommee):
        """
        Calcul direct du rendement
        rendement = énergie utile / énergie consommée
        """
        if energie_consommee <= 0:
            raise ValueError("L'énergie consommée doit être positive")
        
        rendement = (energie_utile / energie_consommee) * 100
        return rendement
    
    def rendement_par_mesure_directe(self, puissance_utile, consommation_combustible, 
                                   type_combustible='gaz_naturel', utiliser_pci=True):
        """
        Calcul du rendement par mesure directe
        Args:
            puissance_utile: puissance thermique utile (kW)
            consommation_combustible: consommation (m³/h pour gaz, kg/h pour autres)
            type_combustible: type de combustible
            utiliser_pci: utiliser PCI (True) ou PCS (False)
        """
        if type_combustible not in self.nom_combustible:
            raise ValueError(f"Combustible non reconnu: {type_combustible}")
        
        # Sélection du pouvoir calorifique
        pc_key = 'pci' if utiliser_pci else 'pcs'
        pouvoir_calorifique = self.nom_combustible[type_combustible][pc_key]
        
        # Conversion en kW (MJ/h -> kW : diviser par 3.6)
        puissance_consommee = (consommation_combustible * pouvoir_calorifique) / 3.6
        
        rendement = (puissance_utile / puissance_consommee) * 100
        
        return {
            'rendement': rendement,
            'puissance_consommee': puissance_consommee,
            'pouvoir_calorifique_utilise': f"{pc_key.upper()}: {pouvoir_calorifique} MJ/unité"
        }
    
    def rendement_par_pertes(self, temp_fumees, temp_air, co2_percent, 
                           type_combustible='gaz_naturel'):
        """
        Calcul du rendement par la méthode des pertes
        Formule simplifiée de Siegert
        """
        # Coefficients selon le type de combustible
        coefficients = {
            'gaz_naturel': {'A1': 0.66, 'A2': 0.009},
            'fuel_domestique': {'A1': 0.68, 'A2': 0.007},
            'propane': {'A1': 0.63, 'A2': 0.008},
            'bois': {'A1': 0.65, 'A2': 0.010}
        }
        
        if type_combustible not in coefficients:
            raise ValueError(f"Combustible non reconnu: {type_combustible}")
        
        A1 = coefficients[type_combustible]['A1']
        A2 = coefficients[type_combustible]['A2']
        
        # Calcul des pertes par les fumées (formule de Siegert simplifiée)
        delta_t = temp_fumees - temp_air
        
        if co2_percent <= 0:
            raise ValueError("Le taux de CO2 doit être positif")
        
        pertes_fumees = (A1 * delta_t / co2_percent) + (A2 * delta_t)
        
        # Rendement = 100 - pertes
        rendement = 100 - pertes_fumees
        
        return {
            'rendement': rendement,
            'pertes_fumees': pertes_fumees,
            'ecart_temperature': delta_t,
            'coefficients_utilises': f"A1={A1}, A2={A2}"
        }
    
    def analyse_complete(self, **kwargs):
        """
        Analyse complète avec plusieurs méthodes si les données sont disponibles
        """
        resultats = {}
        
        # Méthode directe
        if 'energie_utile' in kwargs and 'energie_consommee' in kwargs:
            resultats['methode_directe'] = self.rendement_direct(
                kwargs['energie_utile'], kwargs['energie_consommee']
            )
        
        # Méthode par mesure directe
        if 'puissance_utile' in kwargs and 'consommation_combustible' in kwargs:
            resultats['mesure_directe'] = self.rendement_par_mesure_directe(
                kwargs['puissance_utile'], 
                kwargs['consommation_combustible'],
                kwargs.get('type_combustible', 'gaz_naturel'),
                kwargs.get('utiliser_pci', True)
            )
        
        # Méthode par pertes
        if all(k in kwargs for k in ['temp_fumees', 'temp_air', 'co2_percent']):
            resultats['methode_pertes'] = self.rendement_par_pertes(
                kwargs['temp_fumees'],
                kwargs['temp_air'], 
                kwargs['co2_percent'],
                kwargs.get('type_combustible', 'gaz_naturel')
            )
        
        return resultats

def main():
    """Fonction principale avec exemples d'utilisation"""
    calc = CalculateurRendementChaudiere()
    
    print("=== CALCULATEUR DE RENDEMENT DE CHAUDIÈRE ===\n")
    
    # Exemple 1: Calcul direct
    print("1. Méthode directe:")
    print("Énergie utile: 80 kWh, Énergie consommée: 100 kWh")
    rendement1 = calc.rendement_direct(80, 100)
    print(f"Rendement: {rendement1:.1f}%\n")
    
    # Exemple 2: Mesure directe avec gaz naturel
    print("2. Mesure directe (chaudière gaz):")
    print("Puissance utile: 20 kW, Consommation: 2.5 m³/h")
    result2 = calc.rendement_par_mesure_directe(20, 2.5, 'gaz_naturel', True)
    print(f"Rendement: {result2['rendement']:.1f}%")
    print(f"Puissance consommée: {result2['puissance_consommee']:.1f} kW")
    print(f"Pouvoir calorifique: {result2['pouvoir_calorifique_utilise']}\n")
    
    # Exemple 3: Méthode par pertes
    print("3. Méthode par pertes (analyse des fumées):")
    print("Temp. fumées: 180°C, Temp. air: 20°C, CO2: 10%")
    result3 = calc.rendement_par_pertes(180, 20, 10, 'gaz_naturel')
    print(f"Rendement: {result3['rendement']:.1f}%")
    print(f"Pertes par fumées: {result3['pertes_fumees']:.1f}%")
    print(f"Écart de température: {result3['ecart_temperature']}°C\n")
    
    # Exemple 4: Analyse complète
    print("4. Analyse complète:")
    resultats_complets = calc.analyse_complete(
        energie_utile=85,
        energie_consommee=100,
        puissance_utile=20,
        consommation_combustible=2.5,
        temp_fumees=180,
        temp_air=20,
        co2_percent=10,
        type_combustible='gaz_naturel'
    )
    
    for methode, resultat in resultats_complets.items():
        print(f"{methode.replace('_', ' ').title()}:")
        if isinstance(resultat, dict):
            print(f"  Rendement: {resultat['rendement']:.1f}%")
        else:
            print(f"  Rendement: {resultat:.1f}%")
    
    print("\n=== COMBUSTIBLES DISPONIBLES ===")
    for combustible, proprietes in calc.nom_combustible.items():
        print(f"{combustible.replace('_', ' ').title()}:")
        print(f"  PCI: {proprietes['pci']} MJ/unité")
        print(f"  PCS: {proprietes['pcs']} MJ/unité")

if __name__ == "__main__":
    main()