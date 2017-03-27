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
c.execute("SELECT distinct lower(cuisine) FROM Cuisines")
cuisines_dict = c.fetchall()
cuisines_dict = [i[0] for i in cuisines_dict]

# Retrieve food corpus as gazetteer / dictionary
c.execute("SELECT distinct lower(food) FROM foods")
foods_dict = c.fetchall()
foods_dict = [i[0] for i in foods_dict]


# Used test cases - Note: Print tag for troubleshooting
sent = 'I want to eat chicken rice near Raffles Place'
tagged_sent = nltk.pos_tag(nltk.word_tokenize(sent))
print('pos tag: \n', tagged_sent)

sent = 'Where can i get good nasi lemak at toa payoh'
tagged_sent = nltk.pos_tag(nltk.word_tokenize(sent))
print('pos tag: \n', tagged_sent)

sent = 'Looking for tonkatsu or yakitori at bras basah'
tagged_sent = nltk.pos_tag(nltk.word_tokenize(sent))
print('pos tag: \n', tagged_sent)

sent = 'Recommend where to go for nasi biryani'
tagged_sent = nltk.pos_tag(nltk.word_tokenize(sent))
print('pos tag: \n', tagged_sent)

sent = 'Where to get french food along purvis street'
tagged_sent = nltk.pos_tag(nltk.word_tokenize(sent))
print('pos tag: \n', tagged_sent)

sent = 'Any good coffee place at tanjong pagar?'
tagged_sent = nltk.pos_tag(nltk.word_tokenize(sent))
print('pos tag: \n', tagged_sent)

sent = 'Any good chicken satay nearby'
tagged_sent = nltk.pos_tag(nltk.word_tokenize(sent))
print('pos tag: \n', tagged_sent)

sent = 'I want to have fish head curry today'
tagged_sent = nltk.pos_tag(nltk.word_tokenize(sent))
print('pos tag: \n', tagged_sent)


# Use regular expression–based chunker to group pos
grammar = r"""
    FP: 
        {<VB.*><JJ.*|IN|>?<RB>?<NN.*>+}
        {<DT><JJ.*>?<NN.*>+}
        {<CC><JJ.*>?<NN.*>+}
    LP: 
        {<IN|TO><NN.*>+<VB.*|RB>?}
        {<IN|TO><JJ.*>?<NN.*>+?}
"""
cp = nltk.RegexpParser(grammar)
result = cp.parse(tagged_sent)
print(result)
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
        location = [w for (w,t) in leaves if re.search(r"(JJ.*|NN.*|VB.*|RB)", t)]
        location = ' '.join(location)
    location_user.append(location)

# Match user input on cuisines and/or food items against the cuisine corpus
cuisines = [cuisine for cuisine in foods_user if cuisine in cuisines_dict]
foods = [food for food in foods_user if food not in cuisines]
location = location_user

# Udpate state
if len(cuisines) > 0:
    current_state[0] = 1

if len(foods) > 0:
    current_state[1] = 1    
    
if len(location) > 0:
    current_state[2] = 1   

print(cuisines)
print(foods)
print(location)
print(current_state)
