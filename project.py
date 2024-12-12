import urllib.request
import urllib.parse
import json
from icecream import ic
import time
import random
import streamlit as st
import polars as pl


# funzione per comunicare con la struttura dati API del sito di dnd5e
def get_json(url):
    time.sleep(0.5)
    #ic(url)
    with urllib.request.urlopen(url) as req:
        resp = req.read().decode()
        resp = json.loads(resp)
    return resp


# Questa funzione può fare due cose, gestibili tramite variabili booleane
# La prima condizione chiede se si vogliono ricevere i dati dal web
# La seconda per sapere se ritornare il file come json o come lista
# Se si possiede già la lista si può passare dirattamente al seccondo
def get_json_list(search:str|list, from_web = True, cond_dict = True, return_list = True, json_key = '', list_key = ''):
    
    if from_web: # per avere il file json dal web
        search_quote = urllib.parse.quote(search)
        url = f'https://www.dnd5eapi.co/api/{search_quote}'
        search = get_json(url)
    
    if cond_dict: # per avere valore da un dizionario
        search = search[json_key] # le api spesso hanno liste come valore
    
    if return_list: # per avere elementi da una lista di dizionari
        return [result[list_key] for result in search]
    
    return search


@st.cache_data # codice per far eseguire solo una volta la funzione seguente
def get_punteggi():
    caratt = []    
    # sono sei caratteristiche
    for i in range(6):
        # lancio 4 dadi da 6 facce
        rand=[]
        for k in range(4):
            rand.append(random.randint(1,6))
        # scarto il valore minore
        rand.sort()
        rand.pop(0)
        # restituisco la somma
        caratt.append( rand[0] + rand[1] + rand[2] )
    return caratt


def get_races():
    # Scelta della razza
    list_races = get_json_list('races', json_key='results', list_key='index')
    
    races_df = pl.DataFrame({'race': list_races})
    race_choose = st.selectbox(label='Sceglia la razza del tuo personaggio',
                          options=races_df)
    
    # Prendo il file json da cui poter prelevare varie info
    race_j = get_json_list(f'races/{race_choose}', cond_dict=False, return_list=False)
    return race_j


def race_modif_score():
    bonus_list = race_j['ability_bonuses']    
    
    st.write(f"""\n
             Hai scelto la classe {race_j['index']}, di conseguenza hai un modificatore di : 
    """)
    # confronto ability modificabili
    for obj in bonus_list:
        name = obj['ability_score']['index']
        # con le ability selezionate in precendeza
        for i in range(len(ability)):
            if name == ability[i]:
                
                # Dico all'utente cosa è cambiato
                st.write(f"""
                         +{obj['bonus']} a {ability[i]}
                """)
                
                # Modificare dovuto alla razza
                scores[i] = scores[i] + obj['bonus']

        
ability:list[str] = get_json_list('ability-scores', json_key='results', list_key='index')
scores:list[int] = get_punteggi()
# Calcolo i modificatori per le skill
modificatore:list[int] = [ round((score-10.1)/2) for score in scores]

# ----->> funzione per far scegliere all'utente la corrispondenza (ability, score)

ability_scores = pl.DataFrame({'caratteristica' : ability,
                               'punteggi' : scores,
                               'modificatore' : modificatore
                               })
st.write(ability_scores)

# provare con st.number_input


def razzaaaaaaaaaaaaaaaaaaaaaaaaaaa():

    # Ho il file json della razza
    race_j = get_races()
    race_modif_score()

    race_name = race_j['name']
    speed = race_j['speed']
    size = race_j['size']

    languages = get_json_list(race_j, from_web=False, json_key='languages', list_key='name')

    def choose_languages():
        lang_op = race_j['language_options']
        max_choose = lang_op['choose']
        option_list = get_json_list(lang_op['from'], from_web=False, json_key='options', list_key='item')
        option_list = get_json_list(option_list, from_web=False, cond_dict=False, list_key='name')
        
        return st.multiselect(
            label=f'La razza {race_name} ti permette di imparare {max_choose} fra queste lingue',
            options=option_list,
            max_selections=max_choose,
        )

    for key in race_j.keys():
        if key == 'language_options':
            risp_lang = choose_languages()
            #languages.append(choose_languages()[0])
            if len(risp_lang) != 0:
                languages.append(risp_lang[0])


    st.write(f'''
            #
            {race_name, speed, size}
            #
            {languages[0]}
            ######
            {languages[1]}
            ''')


# mi sa che serve anche una lista di dizionari {'skill' : mod}
def get_class():
    # Scelta della classe   
    list_classes = get_json_list('classes', json_key='results', list_key='index')
    
    classes_df = pl.DataFrame({'classes': list_classes})
    class_choose = st.selectbox(label='Scegli la classe del tuo personaggio',
                                options=classes_df)
    
    class_j = get_json_list(f'classes/{class_choose}', cond_dict=False, return_list=False)
    return class_j

    proficiency_choices = race_j['proficiency_choices'][0]
    max_choose = proficiency_choices['choose']
    il_lonfo = get_json_list(race_j['from'], from_web=False, json_key='options', list_key='item')


class_j = get_class()
class_name = class_j['index']

def level_pg():
    list_option = []
    for i in range(1,21):
        list_option.append(i)
    lvl_select = st.selectbox(label = 'Scegli il livello del tuo personaggio: ',
                              options=list_option)
    lvl_select = int(lvl_select)
    
    # Ricavo il bonus competenza
    bonus_comp = get_json_list(f'classes/{class_name}/levels/{lvl_select}', return_list=False, json_key='prof_bonus')
    
    return lvl_select, bonus_comp


lvl_pg, bonus_comp = level_pg()


def tiri_salv():
    # Cerco lista delle abilità con bonus data la classe
    list_caratt = get_json_list(class_j, from_web=False, json_key='saving_throws', list_key='index')
    
    # confronto con la lista di ability
    for caratt in list_caratt:
        for index in range(len(ability)):
            # per poter aggiungere il bonus di competenza all'abilità corrispondente
            if caratt == ability[index]:
                scores[index] += bonus_comp


skills_list = get_json_list('skills', json_key='results', list_key='index')

def get_skills_score():
    # allego il bonus di ogni skill derivante dall'abilità di base
    skills_score = []
    for skill in skills_list:
        # Ricavo l'abilità di base da ogni skill
        ability_base = get_json_list(f'skills/{skill}', json_key='ability_score', return_list=False)['index']
        # Fornisco il valore corrispondente
        for index in range(len(ability)):
            if ability_base == ability[index]:
                skills_score.append(scores[index])
    return skills_score
skills_score = get_skills_score()


def bonus_skills():
    # passaggio intermedio per ricavare i dati
    intermedio = class_j['proficiency_choices'][0]
    # Massima scelta di skill
    max_choose = intermedio['choose']
    # lista di skill che possono avere il bonus competenza
    list_bonus_skills = get_json_list(intermedio['from'], from_web=False, json_key='options', list_key='item')['index']
    
    
    # bisogna sistemare la lista di opzioni
    
    
    #st.write(f'La classe {class_j['name']} ti permette di potenziare {max_choose} di queste skill: ')
    chooses = st.multiselect(options=list_bonus_skills,
                             max_selections=max_choose)    
    
    # confronto per mettere bonus
    for choose in chooses:
        for index in range(len(skills_list)):
            if choose == skills_list[index]:
                skills_score[index] += bonus_comp



# errore 414
# associazione ability
# il problema delle skill
# rappresentazione grafica
