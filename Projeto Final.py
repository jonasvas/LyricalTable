import PySimpleGUI as sg
import glob
import os
import nltk
from nltk import *


def get_lyrics(row, table):
    with open('%s - %s.txt' % (table[row][0], table[row][1])) as file:
        for i in range(5):
            file.readline()
        lyrics = file.read()
        lyrics = lyrics[:-1]
    return lyrics

def update_table():
    global table
    table = []
    for files in glob.glob('* - *.txt'):
        with open(files) as file:
            columns = file.readlines()
            columns = [x.strip() for x in columns]
            if files == '%s - %s.txt' % (columns[0], columns[1]) and len(columns) >= 6:
                while len(columns) != 5:
                    del columns[5]
                table.append(columns)
    window.FindElement('_table_').Update(values=table)

def run(table, filtered=False):
    with open('stopWords.txt', 'r', encoding='utf-8-sig') as stopwords_file:
        stopwords = stopwords_file.read()
    stopwords = nltk.word_tokenize(stopwords, language='Portuguese')

    with open('stopWords-en.txt', 'r') as stopwords_en_file:
        stopwords_en = stopwords_en_file.read()
    stopwords_en = nltk.word_tokenize(stopwords_en, language='English')

    tokens_all = []
    for i in range(len(table)):
        tokenizer = RegexpTokenizer(r'\w+')
        tokens = tokenizer.tokenize(get_lyrics(i, table).lower())
        tokens_all.extend(tokens)

    tokens_all = [word for word in tokens_all if word not in stopwords_en]
    tokens_all = [word for word in tokens_all if word not in stopwords]
    tokens_all = sorted(tokens_all)

    if filtered:
        try:
            top_n = FreqDist(tokens_all).most_common(int(window_keywords.FindElement('_filtered_spin_').Get()))
            results_table = []
            for i in range(len(top_n)):
                top_n[i] = list(top_n[i])
                results_table.append(top_n[i])

            layout_results = [[sg.Table(values=results_table, headings=['Word', 'Occurrences'],
                                        background_color='lightgreen',
                                        auto_size_columns=False,
                                        justification='left',
                                        num_rows=20,
                                        alternating_row_color='blue',
                                        key='_table_results_')],
                              [sg.Button('Close')]
                              ]
            window_results = sg.Window('Results', layout_results)
            window_results.Read()
            window_results.Close()
        except ValueError:
            sg.Popup('Invalid value!')
    else:
        try:
            top_n = FreqDist(tokens_all).most_common(int(window.FindElement('_spin_').Get()))
            results_table = []
            for i in range(len(top_n)):
                top_n[i] = list(top_n[i])
                results_table.append(top_n[i])

            layout_results = [[sg.Table(values=results_table, headings=['Word', 'Occurrences'],
                                        background_color='lightgreen',
                                        auto_size_columns=False,
                                        justification='left',
                                        num_rows=20,
                                        alternating_row_color='blue',
                                        key='_table_results_')],
                              [sg.Button('Close')]
                              ]
            window_results = sg.Window('Results', layout_results)
            window_results.Read()
            window_results.Close()
        except ValueError:
            sg.Popup('Invalid value!')

sg.ChangeLookAndFeel('TealMono')

menu = [['File', ['New entry...', 'See all', 'Quit']],
        ['Search', ['Search by...', ['Artist', 'Album', 'Song name', 'Keywords', 'List of keywords']]],
        ]

table = []

if len(glob.glob('* - *.txt')) > 0:
    for files in glob.glob('* - *.txt'):
        with open(files) as file:
            columns = file.readlines()
            columns = [x.strip() for x in columns]
            if files == '%s - %s.txt' % (columns[0], columns[1]) and len(columns) >= 6:
                while len(columns) != 5:
                    del columns[5]
                table.append(columns)

layout = [[sg.Table(values=table, headings=['Artist', 'Song', 'Album', 'Composer', 'Genre'],
                    background_color='lightgreen',
                    auto_size_columns=False,
                    justification='left',
                    num_rows=20,
                    key='_table_')],
          [sg.Menu(menu)],
          [sg.Button('Run'), sg.Spin([i for i in range(1, 100000)], initial_value=20, key='_spin_'),
           sg.Text('Number of words to be displayed          '),
           sg.Button('Delete'),
           sg.Button('Lyrics'),
           sg.Button('Edit'),
           sg.Button('Information')]
          ]

window = sg.Window('Lyrical Table', layout)

while True:
    event, values = window.Read()
    if event == None:
        break
    elif event == 'Quit':
        answer = sg.PopupYesNo('Are you sure you want to quit?', title='Warning')
        if answer == 'Yes':
            break
    elif event == 'See all':
        answer = sg.PopupYesNo("Are you sure? This will make you cycle through all of the songs' information.\n"
                               "If you have a lot of entries (>100), this might take a while.", title='Warning')
        if answer == 'Yes':
            for i in range(len(table)):
                with open('%s - %s.txt' % (table[i][0], table[i][1])) as file_info:
                    artist = file_info.readline()
                    song = file_info.readline()
                    album = file_info.readline()
                    composer = file_info.readline()
                    genre = file_info.readline()
                    lyrics = file_info.read()
                layout_info = [[sg.Text('Artist:', size=(8, 1)), sg.InputText(default_text=artist, disabled=True)],
                               [sg.Text('Song:', size=(8, 1)), sg.InputText(default_text=song, disabled=True)],
                               [sg.Text('Album:', size=(8, 1)), sg.InputText(default_text=album, disabled=True)],
                               [sg.Text('Composer:', size=(8, 1)), sg.InputText(default_text=composer, disabled=True)],
                               [sg.Text('Genre:', size=(8, 1)), sg.InputText(default_text=genre, disabled=True)],
                               [sg.Text('Lyrics:', size=(8, 1))],
                               [sg.Multiline(size=(60, 15), default_text=lyrics, disabled=True)],
                               [sg.Button('Close')]
                               ]
                window_info = sg.Window('Song info', layout_info)
                event, values = window_info.Read()
                window_info.Close()
    elif event == 'New entry...':
        layout_new_entry = [[sg.Text('Artist:', size=(8, 1)), sg.InputText()],
                            [sg.Text('Song:', size=(8, 1)), sg.InputText()],
                            [sg.Text('Album:', size=(8, 1)), sg.InputText()],
                            [sg.Text('Composer:', size=(8, 1)), sg.InputText()],
                            [sg.Text('Genre:', size=(8, 1)), sg.InputText()],
                            [sg.Text('Lyrics:', size=(8, 1))],
                            [sg.Multiline(size=(60, 15))],
                            [sg.Submit(), sg.Cancel()]
                            ]
        window_new_entry = sg.Window('New entry', layout_new_entry)
        while True:
            event, values = window_new_entry.Read()
            if event == 'Cancel' or event == None:
                break
            elif event == 'Submit':
                if os.path.exists('%s - %s.txt' % (values[0], values[1])):
                    sg.Popup('Entry already exists!')
                else:
                    with open('%s - %s.txt' % (values[0], values[1]), 'w') as info:
                        info.write('%s\n%s\n%s\n%s\n%s\n%s' % (values[0], values[1], values[2], values[3], values[4], values[5]))
                        info.flush()
                    update_table()
                    break
        window_new_entry.Close()
    elif event == 'Edit':
        selected_row = values['_table_']
        if len(selected_row) == 1:
            selected_row = selected_row[0]
            layout_new_entry = [[sg.Text('Artist:', size=(8, 1)), sg.InputText(default_text=table[selected_row][0], disabled=True)],
                                [sg.Text('Song:', size=(8, 1)), sg.InputText(default_text=table[selected_row][1], disabled=True)],
                                [sg.Text('Album:', size=(8, 1)), sg.InputText(default_text=table[selected_row][2])],
                                [sg.Text('Composer:', size=(8, 1)), sg.InputText(default_text=table[selected_row][3])],
                                [sg.Text('Genre:', size=(8, 1)), sg.InputText(default_text=table[selected_row][4])],
                                [sg.Text('Lyrics:', size=(8, 1))],
                                [sg.Multiline(size=(60, 15), default_text=get_lyrics(selected_row, table))],
                                [sg.Submit(), sg.Cancel()]
                                ]
            window_new_entry = sg.Window('New entry', layout_new_entry)
            event, values = window_new_entry.Read()
            if event == 'Submit':
                with open('%s - %s.txt' % (values[0], values[1]), 'w') as info:
                    info.write('%s\n%s\n%s\n%s\n%s\n%s' % (values[0], values[1], values[2], values[3], values[4], values[5]))
                    info.flush()
                update_table()
            window_new_entry.Close()
    elif event == 'Keywords':
        layout_keywords_setup = [[sg.Text('Type in keywords separated by a comma and a space.\nFor example: dog, fox')],
                                 [sg.Text('Songs that contain ANY of the words typed will be displayed.')],
                                 [sg.InputText(key='_keyword_input_', size=(50, 1))],
                                 [sg.Submit(), sg.Cancel()]
                                 ]
        window_keywords_setup = sg.Window('Search by keyword', layout_keywords_setup)
        event, values = window_keywords_setup.Read()
        window_keywords_setup.Close()
        if event == 'Submit':
            keyword_input = list(values['_keyword_input_'].lower().split(', '))
            filtered_table = []
            for i in range(len(table)):
                tokenizer = RegexpTokenizer(r'\w+')
                tokens = tokenizer.tokenize(get_lyrics(i, table).lower())
                if set(keyword_input) & (set(tokens)):
                    filtered_table.append([table[i][0], table[i][1], table[i][2], table[i][3], table[i][4]])
            layout_keywords = [
                [sg.Table(values=filtered_table, headings=['Artist', 'Song', 'Album', 'Composer', 'Genre'],
                          background_color='lightgreen',
                          auto_size_columns=False,
                          justification='left',
                          num_rows=10,
                          alternating_row_color='blue',
                          key='_table_')],
                [sg.Button('Run'), sg.Spin([i for i in range(1, 100000)], initial_value=20, key='_filtered_spin_'),
                 sg.Text('Number of words to be displayed                                               '),
                 sg.Button('Information')]
                ]
            window_keywords = sg.Window('Results', layout_keywords)
            while True:
                event, values = window_keywords.Read()
                if event == None:
                    break
                elif event == 'Information':
                    selected_row = values['_table_']
                    if len(selected_row) == 1:
                        selected_row = selected_row[0]
                        with open('%s - %s.txt' % (filtered_table[selected_row][0], filtered_table[selected_row][1])) as file_lyrics:
                            artist = file_lyrics.readline()
                            song = file_lyrics.readline()
                            album = file_lyrics.readline()
                            composer = file_lyrics.readline()
                            genre = file_lyrics.readline()
                            lyrics = file_lyrics.read()
                        layout_song_name = [
                            [sg.Text('Artist:', size=(8, 1)), sg.InputText(default_text=artist, disabled=True)],
                            [sg.Text('Song:', size=(8, 1)), sg.InputText(default_text=song, disabled=True)],
                            [sg.Text('Album:', size=(8, 1)), sg.InputText(default_text=album, disabled=True)],
                            [sg.Text('Composer:', size=(8, 1)), sg.InputText(default_text=composer, disabled=True)],
                            [sg.Text('Genre:', size=(8, 1)), sg.InputText(default_text=genre, disabled=True)],
                            [sg.Text('Lyrics:', size=(8, 1))],
                            [sg.Multiline(size=(60, 15), default_text=lyrics, disabled=True)],
                            [sg.Button('Close')]
                        ]
                        window_song_name = sg.Window('Song info', layout_song_name)
                        event, values = window_song_name.Read()
                        window_song_name.Close()
                elif event == 'Run':
                    run(filtered_table, filtered=True)
            window_keywords.Close()
    elif event == 'List of keywords':
        layout_keywords_setup = [[sg.Text('Type in keywords separated by a comma and a space.\nFor example: dog, fox')],
                                 [sg.Text('Only songs that contain ALL the words typed will be displayed.')],
                                 [sg.InputText(key='_keyword_input_', size=(52, 1))],
                                 [sg.Submit(), sg.Cancel()]
                                 ]
        window_keywords_setup = sg.Window('Search by list of keywords', layout_keywords_setup)
        event, values = window_keywords_setup.Read()
        window_keywords_setup.Close()
        if event == 'Submit':
            keyword_input = list(values['_keyword_input_'].lower().split(', '))
            filtered_table = []
            for i in range(len(table)):
                tokenizer = RegexpTokenizer(r'\w+')
                tokens = tokenizer.tokenize(get_lyrics(i, table).lower())
                if set(keyword_input).issubset(set(tokens)):
                    filtered_table.append([table[i][0], table[i][1], table[i][2], table[i][3], table[i][4]])
            layout_keywords = [
                [sg.Table(values=filtered_table, headings=['Artist', 'Song', 'Album', 'Composer', 'Genre'],
                          background_color='lightgreen',
                          auto_size_columns=False,
                          justification='left',
                          num_rows=10,
                          alternating_row_color='blue',
                          key='_table_')],
                [sg.Button('Run'), sg.Spin([i for i in range(1, 100000)], initial_value=20, key='_filtered_spin_'),
                 sg.Text('Number of words to be displayed                                               '),
                 sg.Button('Information')]
                ]
            window_keywords = sg.Window('Results', layout_keywords)
            while True:
                event, values = window_keywords.Read()
                if event == None:
                    break
                elif event == 'Information':
                    selected_row = values['_table_']
                    if len(selected_row) == 1:
                        selected_row = selected_row[0]
                        with open('%s - %s.txt' % (filtered_table[selected_row][0], filtered_table[selected_row][1])) as file_lyrics:
                            artist = file_lyrics.readline()
                            song = file_lyrics.readline()
                            album = file_lyrics.readline()
                            composer = file_lyrics.readline()
                            genre = file_lyrics.readline()
                            lyrics = file_lyrics.read()
                        layout_song_name = [
                            [sg.Text('Artist:', size=(8, 1)), sg.InputText(default_text=artist, disabled=True)],
                            [sg.Text('Song:', size=(8, 1)), sg.InputText(default_text=song, disabled=True)],
                            [sg.Text('Album:', size=(8, 1)), sg.InputText(default_text=album, disabled=True)],
                            [sg.Text('Composer:', size=(8, 1)), sg.InputText(default_text=composer, disabled=True)],
                            [sg.Text('Genre:', size=(8, 1)), sg.InputText(default_text=genre, disabled=True)],
                            [sg.Text('Lyrics:', size=(8, 1))],
                            [sg.Multiline(size=(60, 15), default_text=lyrics, disabled=True)],
                            [sg.Button('Close')]
                        ]
                        window_song_name = sg.Window('Song info', layout_song_name)
                        event, values = window_song_name.Read()
                        window_song_name.Close()
                elif event == 'Run':
                    run(filtered_table, filtered=True)
            window_keywords.Close()
    elif event == 'Song name':
        layout_keywords_setup = [[sg.Text('Type in the song name:')],
                                 [sg.InputText(key='_keyword_input_', size=(20, 1))],
                                 [sg.Submit(), sg.Cancel()]
                                 ]
        window_keywords_setup = sg.Window('Search by song name', layout_keywords_setup)
        event, values = window_keywords_setup.Read()
        window_keywords_setup.Close()
        if event == 'Submit':
            keyword_input = values['_keyword_input_'].lower()
            filtered_table = []
            for i in range(len(table)):
                if keyword_input == table[i][1].lower():
                    filtered_table.append([table[i][0], table[i][1], table[i][2], table[i][3], table[i][4]])
            layout = [[sg.Table(values=filtered_table, headings=['Artist', 'Song', 'Album', 'Composer', 'Genre'],
                                background_color='lightgreen',
                                auto_size_columns=False,
                                justification='left',
                                num_rows=10,
                                alternating_row_color='blue',
                                key='_table_')],
                      [sg.Button('Run'),
                       sg.Spin([i for i in range(1, 100000)], initial_value=20, key='_filtered_spin_'),
                       sg.Text('Number of words to be displayed                                               '),
                       sg.Button('Information')]
                      ]
            window_keywords = sg.Window('Results', layout)
            while True:
                event, values = window_keywords.Read()
                if event == None:
                    break
                elif event == 'Information':
                    selected_row = values['_table_']
                    if len(selected_row) == 1:
                        selected_row = selected_row[0]
                        with open('%s - %s.txt' % (filtered_table[selected_row][0], filtered_table[selected_row][1])) as file_lyrics:
                            artist = file_lyrics.readline()
                            song = file_lyrics.readline()
                            album = file_lyrics.readline()
                            composer = file_lyrics.readline()
                            genre = file_lyrics.readline()
                            lyrics = file_lyrics.read()
                        layout_song_name = [
                            [sg.Text('Artist:', size=(8, 1)), sg.InputText(default_text=artist, disabled=True)],
                            [sg.Text('Song:', size=(8, 1)), sg.InputText(default_text=song, disabled=True)],
                            [sg.Text('Album:', size=(8, 1)), sg.InputText(default_text=album, disabled=True)],
                            [sg.Text('Composer:', size=(8, 1)), sg.InputText(default_text=composer, disabled=True)],
                            [sg.Text('Genre:', size=(8, 1)), sg.InputText(default_text=genre, disabled=True)],
                            [sg.Text('Lyrics:', size=(8, 1))],
                            [sg.Multiline(size=(60, 15), default_text=lyrics, disabled=True)],
                            [sg.Button('Close')]
                            ]
                        window_song_name = sg.Window('Song info', layout_song_name)
                        event, values = window_song_name.Read()
                        window_song_name.Close()
                elif event == 'Run':
                    run(filtered_table, filtered=True)
    elif event == 'Artist':
        layout_keywords_setup = [[sg.Text('Type in the name of the artist:')],
                                 [sg.InputText(key='_keyword_input_', size=(25, 1))],
                                 [sg.Submit(), sg.Cancel()]
                                 ]
        window_keywords_setup = sg.Window('Search by artist', layout_keywords_setup)
        event, values = window_keywords_setup.Read()
        window_keywords_setup.Close()
        if event == 'Submit':
            keyword_input = values['_keyword_input_'].lower()
            filtered_table = []
            for i in range(len(table)):
                if keyword_input == table[i][0].lower():
                    filtered_table.append([table[i][0], table[i][1], table[i][2], table[i][3], table[i][4]])
            layout = [[sg.Table(values=filtered_table, headings=['Artist', 'Song', 'Album', 'Composer', 'Genre'],
                                background_color='lightgreen',
                                auto_size_columns=False,
                                justification='left',
                                num_rows=10,
                                alternating_row_color='blue',
                                key='_table_')],
                      [sg.Button('Run'),
                       sg.Spin([i for i in range(1, 100000)], initial_value=20, key='_filtered_spin_'),
                       sg.Text('Number of words to be displayed                                               '),
                       sg.Button('Information')]
                      ]
            window_keywords = sg.Window('Results', layout)
            while True:
                event, values = window_keywords.Read()
                if event == None:
                    break
                elif event == 'Information':
                    selected_row = values['_table_']
                    if len(selected_row) == 1:
                        selected_row = selected_row[0]
                        with open('%s - %s.txt' % (filtered_table[selected_row][0], filtered_table[selected_row][1])) as file_lyrics:
                            artist = file_lyrics.readline()
                            song = file_lyrics.readline()
                            album = file_lyrics.readline()
                            composer = file_lyrics.readline()
                            genre = file_lyrics.readline()
                            lyrics = file_lyrics.read()
                        layout_song_name = [
                            [sg.Text('Artist:', size=(8, 1)), sg.InputText(default_text=artist, disabled=True)],
                            [sg.Text('Song:', size=(8, 1)), sg.InputText(default_text=song, disabled=True)],
                            [sg.Text('Album:', size=(8, 1)), sg.InputText(default_text=album, disabled=True)],
                            [sg.Text('Composer:', size=(8, 1)), sg.InputText(default_text=composer, disabled=True)],
                            [sg.Text('Genre:', size=(8, 1)), sg.InputText(default_text=genre, disabled=True)],
                            [sg.Text('Lyrics:', size=(8, 1))],
                            [sg.Multiline(size=(60, 15), default_text=lyrics, disabled=True)],
                            [sg.Button('Close')]
                        ]
                        window_song_name = sg.Window('Song info', layout_song_name)
                        event, values = window_song_name.Read()
                        window_song_name.Close()
                elif event == 'Run':
                    run(filtered_table, filtered=True)
    elif event == 'Album':
        layout_keywords_setup = [[sg.Text('Type in the name of the album:')],
                                 [sg.InputText(key='_keyword_input_', size=(25, 1))],
                                 [sg.Submit(), sg.Cancel()]
                                 ]
        window_keywords_setup = sg.Window('Search by album', layout_keywords_setup)
        event, values = window_keywords_setup.Read()
        window_keywords_setup.Close()
        if event == 'Submit':
            keyword_input = values['_keyword_input_'].lower()
            filtered_table = []
            for i in range(len(table)):
                if keyword_input == table[i][2].lower():
                    filtered_table.append([table[i][0], table[i][1], table[i][2], table[i][3], table[i][4]])
            layout = [[sg.Table(values=filtered_table, headings=['Artist', 'Song', 'Album', 'Composer', 'Genre'],
                                background_color='lightgreen',
                                auto_size_columns=False,
                                justification='left',
                                num_rows=10,
                                alternating_row_color='blue',
                                key='_table_')],
                      [sg.Button('Run'),
                       sg.Spin([i for i in range(1, 100000)], initial_value=20, key='_filtered_spin_'),
                       sg.Text('Number of words to be displayed                                               '),
                       sg.Button('Information')]
                      ]
            window_keywords = sg.Window('Results', layout)
            while True:
                event, values = window_keywords.Read()
                if event == None:
                    break
                elif event == 'Information':
                    selected_row = values['_table_']
                    if len(selected_row) == 1:
                        selected_row = selected_row[0]
                        with open('%s - %s.txt' % (filtered_table[selected_row][0], filtered_table[selected_row][1])) as file_lyrics:
                            artist = file_lyrics.readline()
                            song = file_lyrics.readline()
                            album = file_lyrics.readline()
                            composer = file_lyrics.readline()
                            genre = file_lyrics.readline()
                            lyrics = file_lyrics.read()
                        layout_song_name = [
                            [sg.Text('Artist:', size=(8, 1)), sg.InputText(default_text=artist, disabled=True)],
                            [sg.Text('Song:', size=(8, 1)), sg.InputText(default_text=song, disabled=True)],
                            [sg.Text('Album:', size=(8, 1)), sg.InputText(default_text=album, disabled=True)],
                            [sg.Text('Composer:', size=(8, 1)), sg.InputText(default_text=composer, disabled=True)],
                            [sg.Text('Genre:', size=(8, 1)), sg.InputText(default_text=genre, disabled=True)],
                            [sg.Text('Lyrics:', size=(8, 1))],
                            [sg.Multiline(size=(60, 15), default_text=lyrics, disabled=True)],
                            [sg.Button('Close')]
                        ]
                        window_song_name = sg.Window('Song info', layout_song_name)
                        event, values = window_song_name.Read()
                        window_song_name.Close()
                elif event == 'Run':
                    run(filtered_table, filtered=True)
    elif event == 'Delete':
        selected_row = values['_table_']
        if len(selected_row) == 1:
            answer = sg.PopupYesNo('Are you sure you want to delete this entry?', title='Warning')
            if answer == 'Yes':
                selected_row = selected_row[0]
                os.remove('%s - %s.txt' % (table[selected_row][0], table[selected_row][1]))
                del table[selected_row]
                update_table()
    elif event == 'Lyrics':
        selected_row = values['_table_']
        if len(selected_row) == 1:
            selected_row = selected_row[0]
            layout = [[sg.Multiline(size=(50, 35), default_text=get_lyrics(selected_row, table), disabled=True)],
                      [sg.Button('Close')]
                      ]
            window_lyrics = sg.Window('Lyrics', layout)
            event, values = window_lyrics.Read()
            window_lyrics.Close()
    elif event == 'Information':
        selected_row = values['_table_']
        if len(selected_row) == 1:
            selected_row = selected_row[0]
            with open('%s - %s.txt' % (table[selected_row][0], table[selected_row][1])) as file_lyrics:
                artist = file_lyrics.readline()
                song = file_lyrics.readline()
                album = file_lyrics.readline()
                composer = file_lyrics.readline()
                genre = file_lyrics.readline()
                lyrics = file_lyrics.read()
            layout_song_name = [
                [sg.Text('Artist:', size=(8, 1)), sg.InputText(default_text=artist, disabled=True)],
                [sg.Text('Song:', size=(8, 1)), sg.InputText(default_text=song, disabled=True)],
                [sg.Text('Album:', size=(8, 1)), sg.InputText(default_text=album, disabled=True)],
                [sg.Text('Composer:', size=(8, 1)), sg.InputText(default_text=composer, disabled=True)],
                [sg.Text('Genre:', size=(8, 1)), sg.InputText(default_text=genre, disabled=True)],
                [sg.Text('Lyrics:', size=(8, 1))],
                [sg.Multiline(size=(60, 15), default_text=lyrics, disabled=True)],
                [sg.Button('Close')]
            ]
            window_song_name = sg.Window('Song info', layout_song_name)
            event, values = window_song_name.Read()
            window_song_name.Close()
    elif event == 'Run':
        run(table)
window.Close()