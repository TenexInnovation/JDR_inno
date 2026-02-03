from app.database import add_character, init_database

init_database()

# Zara Vex - Rusée, riche
add_character('BADGE001', '', 'Zara Vex', 8, 6, 4, 9, 5, 7, 2500, 'RAS')

# Marcus Dorn - Fort, Recherché
add_character('BADGE002', '', 'Marcus Dorn', 9, 3, 7, 4, 8, 6, 150, 'recherche')

# Lyra Shade - Agile, En fuite
add_character('BADGE003', '', 'Lyra Shade', 3, 9, 8, 7, 4, 5, -500, 'en_fuite')

print("3 personnages de test ajoutés!")