from urllib import request, parse
import json
import time
import random
import streamlit as st
import polars as pl

# vedi te se vuoi inserire gli st.sidebar.markdown()

# funzione per comunicare con la struttura dati API del sito di dnd5eapi.co
def get_json(url):
    time.sleep(0.2)
    #ic(url)
    with request.urlopen(url) as req:
        resp = req.read().decode()
        resp = json.loads(resp)
    return resp


# Questa funzione può fare diverse opzioni di ricerca, gestite tramite variabili booleane
# Data la ricerca web o il file json, si possono ricevere file json, liste o valori
def get_json_list(search:str|list, from_web = True, cond_dict = True, return_list = True, json_key = '', list_key = ''):
    
    if from_web: # per avere il file json dal web
        search_quote = parse.quote(search)
        url = f'https://www.dnd5eapi.co/api/{search_quote}'
        search = get_json(url)
    
    if cond_dict: # per avere valore da un dizionario
        search = search[json_key] # le api spesso hanno liste come valore
    
    if return_list: # per avere elementi da una lista di dizionari
        return [result[list_key] for result in search]
    
    return search

# Funzione che simula il lancio di dadi per iniziare a fare la scheda personaggio
@st.cache_data # codice per far eseguire solo una volta la funzione seguente
def get_punteggi():
    punt = []    
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
        punt.append( rand[0] + rand[1] + rand[2] )
    return punt

# Funzione per abbinare i punteggi alle abilità 
def get_scores():
    punt = get_punteggi()
    # Dopo il lancio dei dadi chiedo all'utente l'abbinamento
    st.write('Questo è l\'ordine dei punteggi')
    for i in range(1, 7):
        st.write(f'{i}.', punt[i-1])

    st.write('''Inserisci il numero di posizione del punteggio in base
             alla caratteristica che preferisci abbinare.
             ''')
    
    n = [0 for _ in range(6)]
    
    # ogni colonna serve per abbinare l'abilità al numero scelto
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    
    with c1:
        n[0] = st.number_input("Charisma", 0, len(punt))
        if n[0] != 0:
            st.write(punt[n[0]-1])
    with c2:
        n[1] = st.number_input("Constitution", 0, len(punt))
        if n[1] != 0:
            st.write(punt[n[1]-1])
    with c3:
        n[2] = st.number_input("Dexterity", 0, len(punt))
        if n[2] != 0:
            st.write(punt[n[2]-1])
    with c4:
        n[3] = st.number_input("Intellingence", 0, len(punt))
        if n[3] != 0:
            st.write(punt[n[3]-1])
    with c5:
        n[4] = st.number_input("Strength", 0, len(punt))
        if n[4] != 0:
            st.write(punt[n[4]-1])
    with c6:
        n[5] = st.number_input("Wisdom", 0, len(punt))
        if n[5] != 0:
            st.write(punt[n[5]-1])
    
    # controllo che lo stesso numero non sia abbinato a più abilità
    for i in range(0, len(n)-1):
        for j in range(i+1, len(n)):
            if n[i] == n[j]:
                st.error('I numeri inseriti devono essere tutti diversi')
                return [0 for _ in range(6)]

    return [punt[n[0]-1], punt[n[1]-1], punt[n[2]-1], punt[n[3]-1], punt[n[4]-1], punt[n[5]-1]]

# Funzione per scelte singole (razza/classe)
def get_choice(search = ''):
    # Lista di possibilità di scelta
    list_search = get_json_list(search, json_key='results', list_key='index')
    
    # label in base al tipo di scelta
    if search == 'races': label = 'razza'
    elif search == 'classes': label = 'classe'
    
    # Scelta dell'utente
    df = pl.DataFrame({search: list_search})
    choose = st.selectbox(label = f'Scegli la {label} del tuo personaggio',
                          options = df)
    
    # Prendo il file json da cui poter usare dopo
    file_j = get_json_list(f'{search}/{choose}', cond_dict=False, return_list=False)
    return file_j

# Modifiche agli scores data la razza
def race_modif_score(race_j, ability_scores:dict):
    # Lista delle ability da moficiare
    bonus_list = race_j['ability_bonuses']    
    
    # ccerco la corrispondenza
    for obj in bonus_list:
        name = obj['ability_score']['index']
        for ability in ability_scores.keys():
            if name == ability:
                
                # Dico all'utente cosa è cambiato
                st.write(f"""
                         +{obj['bonus']} a {ability}
                """)
                
                # Modifica degli scores
                ability_scores[ability] += obj['bonus']
    
    # Aggiornando gli scores cambiano i modificatori
    modificatore:list[int] = [ round((score-10.1)/2) for score in ability_scores.values()]    
    return ability_scores, modificatore

# Linguaggi appresi dal personaggio data la razza
def choose_languages(race_j):
    
    # Lingue conosciute dovuta la razza
    languages = get_json_list(race_j, from_web=False, json_key='languages', list_key='name')
    
    for key in race_j.keys():
        # Alcune razze permettono di scegliere linguaggi aggiuntivi da apprendere
        if 'language_options' == key:
            
            lang_op = race_j['language_options']
            # Massimo linguaggi aggiuntivi da poter apprendere
            max_choose = lang_op['choose']
            # Lista linguaggi tra cui scegliere
            option_list = get_json_list(lang_op['from'], from_web=False, json_key='options', list_key='item')
            option_list = get_json_list(option_list, from_web=False, cond_dict=False, list_key='name')
            
            race_name = race_j['name']
            # L'utente sceglie linguaggi da poter apprendere
            select = st.multiselect(
                label=f'La razza {race_name} ti permette inoltre di imparare {max_choose} fra queste lingue',
                options=option_list,
                max_selections=max_choose,
            )
            
            if len(select) != 0: # condizione sennò da errore con lista vuota
                for sel in select:
                    languages.append(sel)    
            
            st.write('##')
    
    # ritorno linguaggi conosciuti dal personaggio
    return languages

# Modificatori dei tiri salvezza data la classe
def get_tiri_salv(class_j, ability_scores:dict, bonus_comp):
    # Data la classe, cerco lista delle ability che hanno il bonus per i tiri salvezza
    list_caratt = get_json_list(class_j, from_web=False, json_key='saving_throws', list_key='index')
    
    st.write(f'Scegliendo questa classe hai ottenuto un bonus di +{bonus_comp} ai tiri salvezza contro: ')
    tiri_salv = dict()
    
    # confronto lista delle ability per il bonus
    for ability in ability_scores.keys():
        for caratt in list_caratt:
            # aggiunta del bonus di competenza all'abilità corrispondente
            if ability == caratt:
                tiri_salv[ability] = round((ability_scores[ability]-10.1)/2) + bonus_comp
                st.write(f'- {caratt}')
                break
            else:
                tiri_salv[ability] = round((ability_scores[ability]-10.1)/2)

    # Ritorno i modificatori per i tiri salvezza
    return tiri_salv

# ogni skill riceve un modificatore in base alla caratteristica da cui deriva
# Funzione eseguita una sola volta perchè c'è in ciclo una chiamata alla rete
@st.cache_data
def get_ability_base(skills_list):
    ability_base = []
    for skill in skills_list:
        # Ricavo la caratteristica di base da ogni skill
        base = get_json_list(f'skills/{skill}', json_key='ability_score', return_list=False)['index']
        ability_base.append(base)
    
    return ability_base

# Funzione per aggiornare i modificatori della skills_list
def get_skills_modif(ability_scores:dict, ability_base, modificatore):
    skills_modif = []
    
    for base in ability_base: # data l'abilità di base della skill
        for ability in ability_scores.keys():
            if base == ability: # aggiungo il modificatore corrispondente
                modif = round((ability_scores[ability] - 10.1) /2)
                skills_modif.append(modif)
    
    return skills_modif

# Funzione per aggiungere bonus di competenza alle skills scelte dall'utente
def bonus_skills(class_j, skills_list, skills_modif, bonus_comp):
    # passaggio intermedio per ricavare i dati
    intermedio = class_j['proficiency_choices'][0]
    # Massima scelta di skill
    max_choose = intermedio['choose']
    # lista di skill che possono avere il bonus competenza
    list_bonus_skills = get_json_list(intermedio['from'], from_web=False, json_key='options', list_key='item')
    list_bonus_skills = [skill['index'] for skill in list_bonus_skills]
    
    # Sistemazione della lista per avere le parole confrontabili
    df = pl.DataFrame({'skills' : list_bonus_skills})
    df = df.with_columns(
        skills = pl.col('skills').str.split('-') # divido in due colonne dove si trova il trattino
                                   .list.to_struct(fields = ['name', 'skills'])
    ).unnest('skills'
    ).with_columns( # rimangon le due colonne divise
        pl.col('name', 'skills')
    )
    
    # Sistemo le skills che hanno più di due parole
    skills = df['skills']
    for i in range(0, len(skills)-1):
        if skills[i] == 'animal': skills[i] = 'animal-handling'
        elif skills[i] == 'sleight': skills[i] = 'sleight-of-hand'
    
    # scelte dell'utente
    class_name = class_j['name']
    chooses = st.multiselect(label = (f'La classe {class_name} ti permette di migliorare {max_choose} di queste skill di +{bonus_comp}:'),
                             options = skills,
                             max_selections = max_choose)    
    
    # corrispondenza con scelta dell'utente
    for choose in chooses:
        for index in range(len(skills_list)):
            if choose == skills_list[index]: # applico il bonus
                skills_modif[index] += bonus_comp

    return skills_modif


# funzione principale per coordinare l'interazione con l'utente
def main():
    
    st.title('Creazione scheda pg')
    
    st.sidebar.title('Indice')
    st.sidebar.markdown('''
    - [Punteggi caratteristica e livello](#punteggi-caratteristica)
    - [Razza del personaggio](#razza)
    - [Classe del personaggio](#classe)
    - [Risultati](#risultati)
    - [Scarica la scheda personaggio](#scarica-scheda-personaggio)
    ''')
    
    st.write('''In questa pagina potrai creare il tuo personaggio usando il manuale D&D 5e.
            \nQuesti sono i tuoi punteggi caratteristica, ovviamente è risaputo che i tiri dei dadi scelti dal destino vanno sempre accettati.
            Solo chi è un debole di cuore sceglie di ritirare i dati... (e quindi far ripartire il programma).
            ''')
    
    name_pg = st.text_input('Inserisci il nome del tuo personaggio:')
    
    # Scelta scores e livello ----------------------------------
    st.write('#')
    st.subheader('Punteggi caratteristica', divider='blue')
    
    ability = get_json_list('ability-scores', json_key='results', list_key='index')
    scores = get_scores()
    
    # Calcolo i modificatori per le skill
    modificatore:list[int] = [ round((score-10.1)/2) for score in scores]
    
    ability_scores = dict()
    for index in range(0, len(ability)):
        ability_scores[ability[index]] = scores[index]
    
    ability_abbinamento = pl.DataFrame({'Caratteristiche' : ability,
                                        'Punteggi' : scores,
                                        'Modificatori' : modificatore
                                        })
    st.write('###')
    st.write('Questi sono i punteggi da te abbinati con i rispettivi modificatori:')
    st.write(ability_abbinamento, '#')
    
    st.write("Un'altra scelta importante è il livello di partenza del tuo personaggio")
    
    # scelta del livello
    if 'lvl_pg_prec' not in st.session_state:
        st.session_state.lvl_pg_prec = 1
    
    st.session_state.lvl_pg =st.slider(
        label = 'Scegli il livello del tuo personaggio: ',
        min_value=1, max_value=20)
    
    # Scelta della razza -----------------------------
    st.write('#')
    st.subheader('Razza', divider='green')
    st.write('''La scelta della razza ti permette di avere ulteriori modificatori ai tuoi punteggi caratteristica
                e influenzerà abilità e lingua parlata del tuo personaggio
                ### ''')
    
    # Ho il file json della razza
    race_j = get_choice('races')
    
    race_name = race_j['name']
    speed = race_j['speed']
    size = race_j['size']
    
    st.write(f"Hai scelto la classe {race_name}, quindi hai ottenuto un modificatore di :")
    ability_scores, modificatore = race_modif_score(race_j, ability_scores)
    
    iniziativa = modificatore[2] # L'iniziativa si calcola in generale tramite la destrezza
    ca = 10 + modificatore[1] + modificatore[2] # La classe armatura è 10 + costituzione + destrezza
    
    st.write('I punteggi caratteristica aggiornati sono visibili a lato.')
    st.write('###')
    
    languages = choose_languages(race_j)
    
    st.write(f'Selezionando la razza {race_name} il tuo personaggio ora possiede: ')
    
    colsx, coldx = st.columns(2)
    
    with colsx:
        st.write(f'''
                Velocità: {speed}
                    
                Stazza: {size}
                    
                Iniziativa: {iniziativa}
                    
                Classe armatura: {ca}''')
    
    with coldx:
        st.write('Conoscenza linguaggi: ')
        
        if len(languages) != 0:
            for lang in languages:
                st.write('- ', lang)
    
    # Scelta della classe ----------------------------
    
    st.write('#')
    st.subheader('Classe', divider='red')
    st.write('La scelta della classe ti permette di potenziare precise skill da utilizzare durante la campagna.')
    st.write('######')
    # Scelta della classe
    class_j = get_choice('classes')
    class_name = class_j['name']
    class_index = class_j['index']
    
    # bonus competenza dovuto a livello e classe del pg
    bonus_comp = get_json_list(f'classes/{class_index}/levels/{st.session_state.lvl_pg}', return_list=False, json_key='prof_bonus')
    
    # bonus da applicare ai tiri salvezza per le abilità di classe
    tiri_salv = get_tiri_salv(class_j, ability_scores, bonus_comp)
    st.write('###')
    
    # Lista delle skills
    skills_list = get_json_list('skills', json_key='results', list_key='index')
    # Lista dei modificatori associati alle skills date le abilità di base
    ability_base = get_ability_base(skills_list)
    
    # Lista dei modificatori per ogni skills
    skills_modif = get_skills_modif(ability_scores, ability_base, modificatore)
    
    # Modifiche dell'utente ai modif_skills in base alle skills di classe scelti
    skills_modif = bonus_skills(class_j, skills_list, skills_modif, bonus_comp)
    
    # Barra laterale
    ability_print = pl.DataFrame({'Caratteristiche' : ability,
                                    'Punteggi' : ability_scores.values(),
                                    'Modificatori' : modificatore
                                    })
    
    st.sidebar.title('')
    st.sidebar.write( 'I punteggi caratteristica del tuo personaggio:')
    st.sidebar.write(ability_print)
    
    
    '#'
    st.subheader('Risultati', divider='violet')
    st.write('Appena hai finito la compilazione scopri tutte le statistiche del tuo personaggio!!')
    if st.button('Statistiche del personaggio'):
        
        count = st.empty()
        bar = st.progress(0)
        for i in range(100):
            count.text(f'Caricamento {i+1}')
            bar.progress(i + 1)
            time.sleep(0.01)
        
        hit_die = class_j['hit_die']
        def vita():
            st.session_state.vita = hit_die + modificatore[1]
            for _ in range(st.session_state.lvl_pg - 1):
                st.session_state.vita = st.session_state.vita + modificatore[1] + random.randint(1, hit_die)
            return st.session_state.vita
        
        if 'vita' not in st.session_state:
            st.session_state.vita = vita()
        
        
        if st.session_state.lvl_pg != st.session_state.lvl_pg_prec:
            st.session_state.lvl_pg_prec = st.session_state.lvl_pg
            st.session_state.vita = vita()
        
        skills = pl.DataFrame({
            'Abilità': skills_list,
            'Modificatori': skills_modif
        })
        
        print1, print2 = st.columns(2)
        
        with print1:
            st.header(f':rainbow[{name_pg}]')
            '#'
            st.write('Punteggi caratteristica: ')
            st.write(ability_print)
            '####'
            
            st.write(f'''
                    :mortar_board: Bonus competenza: +{bonus_comp}
                    
                    :shield: Classe armatura: {ca}
                    
                    :sparkles: Iniziativa: {iniziativa}
                    
                    :runner: Velocità: {speed}
                    
                    :weight_lifter: Stazza: {size}
                    
                    :heart: Punti ferita totali: {st.session_state.vita}
                    
                    :game_die: Dadi vita: {st.session_state.lvl_pg-1}d{hit_die} + {hit_die}
                    ''')
        
        with print2:
            st.write(f'''
                    :blue[Livello]: {st.session_state.lvl_pg}
                     
                    :green[Razza]: {race_name}
                     
                    :red[Classe]: {class_name}
                    ''')
            '####'
            st.write('Punteggi caratteristica per i tiri salvezza: ')
            for key in tiri_salv.keys():
                st.write(key, ':', tiri_salv[key])
                
            '####'
            st.write('Modificatori delle skills:')
            st.write(skills)
        
        
    st.title('')
    st.subheader('Scarica scheda personaggio', divider='grey')
    st.write('''Questo file ti permette di scaricare una scheda personaggio modificabile in formato PDF.
             In questo modo, una volta scaricata, potrai inserire in modo facile e veloce le statistiche visualizzabili qui sopra.''')
    file = 'scheda-personaggio.pdf'
    with open(file, 'rb') as file:
        st.write('Il file verrà salvato nella cartella Download con il nome scheda-personaggio.pdf')
        file_bytes = file.read()
        st.download_button(
            label = 'Scarica la scheda',
            data = file_bytes,
            file_name = 'scheda-personaggio.pdf',
            mime = 'application/pdf'
        )

# commenti

main()