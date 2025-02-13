from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import csv

# Configurer Selenium avec Chrome en mode headless
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # Exécuter sans interface graphique
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# URL du site Windguru
url = "https://www.windguru.cz/9355"
driver.get(url)

# Attendre quelques secondes pour que la page se charge
time.sleep(8)


# Fonction pour convertir les nœuds en km/h
def convert_knots_to_kmh(knots):
    return round(knots * 1.852, 2)  # Conversion des nœuds en km/h


# Fonction pour extraire les directions du vent et la vitesse à des moments précis
def get_wind_data():
    wind_directions = []
    wind_speeds = []

    # Indices des valeurs à récupérer
    indices = [13, 16, 19]

    for i in indices:
        try:
            # Récupérer la direction du vent (title dans <span>)
            direction_xpath = f"//*[@id='tabid_1_0_SMER']/td[{i}]/span"
            wind_direction_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, direction_xpath))
            )
            direction_value = wind_direction_element.get_attribute("title").split(" ")[1].strip("°()")

            # Récupérer la vitesse du vent (texte dans <td>)
            speed_xpath = f"//*[@id='tabid_1_0_GUST']/td[{i}]"
            wind_speed_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, speed_xpath))
            )
            speed_value_knots = wind_speed_element.text.strip()

            # Conversion en entier
            wind_directions.append(int(direction_value))
            wind_speeds.append(convert_knots_to_kmh(float(speed_value_knots)))

        except Exception as e:
            print(f"⚠️ Erreur lors de l'extraction des données pour l'index {i} : {e}")
            wind_directions.append(None)
            wind_speeds.append(None)

    print(f"✅ Directions extraites : {wind_directions}")
    print(f"✅ Vitesses extraites (km/h) : {wind_speeds}")

    return wind_directions, wind_speeds


# Ouvrir ou créer un fichier CSV pour enregistrer les données
filename = "wind_data1.csv"

# Heures spécifiques des données
hours_of_interest = ['7:00', '13:00', '19:00']

# Récupérer les données
current_directions, current_speeds = get_wind_data()

if current_directions and current_speeds:
    with open(filename, mode='a', newline='') as file:
        writer = csv.writer(file)
        for i in range(len(current_directions)):
            writer.writerow([time.strftime("%Y-%m-%d"), hours_of_interest[i], current_directions[i], current_speeds[i]])

    print(f"📊 Données enregistrées : Directions = {current_directions}, Vitesses (km/h) = {current_speeds}")

# Fermer Selenium
driver.quit()
