# Import relevant libraries
import nltk, sqlite3, re
#from nltk import ne_chunk, pos_tag, word_tokenize

# Initialise state
current_state = [0,0,0] # cuisine,food,location - 0 indicates nothing, 1 indicates populated

# Establish connection to SQL Database
db_path = '../database/jiakbot.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

# Retrieve cuisine corpus as gazetteer / dictionary
c.execute("SELECT cuisine FROM Cuisines")
cuisines_dict = c.fetchall()
cuisines_dict = [i[0] for i in cuisines_dict]
cuisines_dict_lc = [w.lower() for w in cuisines_dict]

# Retrieve food corpus as gazetteer / dictionary
c.execute("SELECT distinct lower(food) FROM foods")
foods_dict = c.fetchall()
foods_dict = [i[0] for i in foods_dict]

# Retrieve location gazetteer / dictionary
location_dict = ['Alexandra', 'Aljunied', 'Geylang', 'Ayer Rajah', 'Balestier', 'Bartley', 'Bishan', 
                  'Marymount', 'Sin Ming', 'Bukit Timah', 'Buona Vista', 'Holland Village', 'one-north', 
                  'Ghim Moh', 'Chinatown', 'Clarke Quay', 'City Hall', 'Kreta Ayer', 'Telok Ayer', 
                  'Kallang', 'Bendemeer', 'Geylang Bahru', 'Kallang Bahru', 'Kallang Basin', 'Kolam Ayer', 
                  'Tanjong Rhu', 'Mountbatten', 'Old Airport', 'Lavender', 'Boon Keng', 'Kent Ridge', 
                  'Kim Seng', 'Little India', 'Farrer Park', 'Jalan Besar', 'MacPherson', 'Marina Bay', 
                  'Esplanade', 'Marina Bay Sands', 'Marina Centre', 'Marina East', 'Marina South', 
                  'Mount Faber', 'Mount Vernon', 'Museum', 'Newton', 'Novena', 'Orchard Road', 
                  'Dhoby Ghaut', 'Emerald Hill', 'Tanglin', 'Outram', 'Pasir Panjang', 'Paya Lebar', 'Eunos', 
                  'Geylang East', 'Potong Pasir', 'Rochor-Kampong Glam', 'Bencoolen', 'Bras Basah', 
                  'Bugis', 'Queenstown', 'Dover', 'Commonwealth', 'Raffles Place', 'River Valley', 
                  'Singapore River', 'Southern Islands', 'Tanjong Pagar', 'Shenton Way', 'Telok Blangah', 
                  'Bukit Chandu', 'Bukit Purmei', 'HarbourFront', 'Keppel', 'Radin Mas', 'Mount Faber', 
                  'Tiong Bahru', 'Bukit Ho Swee', 'Bukit Merah', 'Toa Payoh', 'Bukit Brown', 
                  'Caldecott Hill', 'Thomson', 'Whampoa', 'St. Michael', 'Bedok', 'Bedok Reservoir', 
                  'Chai Chee', 'Kaki Bukit', 'Tanah Merah', 'Changi', 'Changi Bay', 'Changi East', 
                  'Changi Village', 'East Coast', 'Joo Chiat', 'Katong', 'Kembangan', 'Pasir Ris', 
                  'Elias', 'Lorong Halus', 'Loyang', 'Marine Parade', 'Siglap', 'Tampines', 'Simei', 
                  'Ubi', 'Central Catchment Nature Reserve', 'Kranji', 'Lentor', 'Lim Chu Kang', 
                  'Neo Tiew', 'Sungei Gedong', 'Mandai', 'Sembawang', 'Canberra', 'Senoko', 'Simpang', 
                  'Sungei Kadut', 'Woodlands', 'Admiralty', 'Innova', 'Marsiling', 'Woodgrove', 
                  'Yishun', 'Chong Pang', 'Ang Mo Kio', 'Cheng San', 'Chong Boon', 'Kebun Baru', 
                  'Teck Ghee', 'Yio Chu Kang', 'Bidadari', 'Hougang', 'Defu', 'Kovan', 'Lorong Chuan', 
                  'North-Eastern Islands', 'Punggol', 'Punggol Point', 'Punggol New Town', 'Seletar', 
                  'Sengkang', 'Serangoon', 'Serangoon Gardens', 'Serangoon North', 'Boon Lay', 'Tukang', 
                  'Liu Fang', 'Samulun', 'Shipyard', 'Bukit Batok', 'Bukit Gombak', 'Hillview', 'Guilin', 
                  'Bukit Batok West', 'Bukit Batok East', 'Bukit Panjang', 'Choa Chu Kang', 'Yew Tee', 
                  'Clementi', 'Toh Tuck', 'West Coast', 'Pandan', 'Jurong East', 'Toh Guan', 
                  'Teban Gardens', 'Penjuru', 'Yuhua', 'Jurong Regional Centre', 'Jurong Lake', 
                  'Jurong River', 'Jurong Port', 'Jurong West', 'Hong Kah', 'Taman Jurong', 
                  'Boon Lay Place', 'Chin Bee', 'Yunnan', 'Jurong Central', 'Kian Teck', 'Safti', 
                  'Wenya', 'Lim Chu Kang', 'Pioneer', 'Joo Koon', 'Gul Circle', 'Pioneer Sector', 
                  'Tengah', 'Tuas', 'Wrexham', 'Promenade', 'Pioneer', 'Soon Lee', 'Tuas South', 
                  'Murai', 'Sarimbun']

location_dict_lc = [w.lower() for w in location_dict]

# Used test cases - Note: Print tag for troubleshooting
sent = 'I want to eat chicken rice near Raffles Place'
tagged = nltk.pos_tag(nltk.word_tokenize(sent))
print('pos tag: \n', tagged)

sent = 'Where can i get good nasi lemak at toa payoh'
tagged = nltk.pos_tag(nltk.word_tokenize(sent))
print('pos tag: \n', tagged)

sent = 'Looking for tonkatsu or yakitori at bras basah'
tagged = nltk.pos_tag(nltk.word_tokenize(sent))
print('pos tag: \n', tagged)

sent = 'Recommend where to go for nasi biryani'
tagged = nltk.pos_tag(nltk.word_tokenize(sent))
print('pos tag: \n', tagged)

sent = 'Where to get french food at HarbourFront'
tagged = nltk.pos_tag(nltk.word_tokenize(sent))
print('pos tag: \n', tagged)

sent = 'Any good coffee place at tanjong pagar?'
tagged = nltk.pos_tag(nltk.word_tokenize(sent))
print('pos tag: \n', tagged)

sent = 'Any good chicken satay nearby'
tagged = nltk.pos_tag(nltk.word_tokenize(sent))
print('pos tag: \n', tagged)

sent = 'I want to have fish head curry today'
tagged = nltk.pos_tag(nltk.word_tokenize(sent))
print('pos tag: \n', tagged)

sent = 'chicken curry or chicken satay at bras basah'
tagged = nltk.pos_tag(nltk.word_tokenize(sent))
print('pos tag: \n', tagged)

sent = 'raffles place'
tagged = nltk.pos_tag(nltk.word_tokenize(sent))
print('pos tag: \n', tagged)

sent = 'bras basah'
tagged = nltk.pos_tag(nltk.word_tokenize(sent))
print('pos tag: \n', tagged)

sent = 'chilli crab'
tagged = nltk.pos_tag(nltk.word_tokenize(sent))
print('pos tag: \n', tagged)


# Use regular expression–based chunker to group pos
grammar = r"""
    FP: 
        {<VB.*><JJ.*|IN|>?<RB>?<NN.*>+}
        {<DT><JJ.*>?<NN.*>+}
        {<CC><JJ.*>?<NN.*>+}
    LP: 
        {<IN|TO><NN.*>+<VB.*|RB>?}
        {<IN|TO><JJ.*>?<NN.*>+?}
        {<NN.*>+<VBP>?}
"""
cp = nltk.RegexpParser(grammar)
result = cp.parse(tagged)
#print(result)
#result.draw()

# Stopword removal
stopword = ['good', 'nice', 'food', 'cuisine', 'restaurant', 'stall', 'place', 'today', 'morning', 'afternoon']

# Identify cuisines and/or food items from user input
foods_user = []
for subtree in result.subtrees(filter = lambda t: t.label() == 'FP'):
    leaves = subtree.leaves()    
    for leaf in leaves:
        food = [w for (w,t) in leaves if re.search(r"(JJ.*|RB|NN.*)", t) and w not in stopword]
        food = ' '.join(food)
    foods_user.append(food)

# Identify place / location from user input
location_user = []
for subtree in result.subtrees(filter = lambda t: t.label() == 'LP'):
    leaves = subtree.leaves()
    for leaf in leaves:
        place = [w for (w,t) in leaves if re.search(r"(JJ.*|NN.*|VB.*|RB)", t)]
        place = ' '.join(place)
    location_user.append(place)
    print(location_user)

not_location =  [location for location in location_user if location not in location_dict 
                 and location not in location_dict_lc]  

# Additional checks for food items in user input
if len(not_location) > 0:
    tagged1 = nltk.pos_tag(nltk.word_tokenize(', '.join(not_location)))

    fgrammar = r"""
        FP: 
            {<JJ>?<NN>+}
    """
    fcp = nltk.RegexpParser(fgrammar)
    result = fcp.parse(tagged1)
    
    for subtree in result.subtrees(filter = lambda t: t.label() == 'FP'):
        leaves = subtree.leaves()    
        for leaf in leaves:
            food = [w for (w,t) in leaves if re.search(r"(JJ|NN)", t) and w not in stopword]
            food = ' '.join(food)
        foods_user.append(food)

# Match user input on cuisines and/or food items against the cuisine corpus
cuisines = [cuisine for cuisine in foods_user if cuisine in cuisines_dict or cuisine in cuisines_dict_lc]
foods = [food for food in foods_user if food not in cuisines_dict and food not in cuisines_dict_lc ]
location = [location for location in location_user if location in location_dict or location in location_dict_lc]

# Udpate state
if len(cuisines) > 0:
    current_state[0] = 1

if len(foods) > 0:
    current_state[1] = 1    
    
if len(location) > 0:
    current_state[2] = 1   
