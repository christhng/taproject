from jiakbot import JiakBot

# test conversations
# ---------------------------------------------
# test sentences (use case 1)
case1_sentences = [None] * 5
case1_sentences[0] = "Hey"  # bot: "Hello there. What would you like to eat today?"
case1_sentences[1] = "I don't know"  # bot: "Where are you?"
case1_sentences[2] = "Raffles Place"  # bot: "What would you like to have?"
case1_sentences[3] = "I want to have curry"  # bot: There is a Ya Kun near Raffles Place...
# bot: Some people say "It's the best kaya toast".
# bot: is that correct?
case1_sentences[4] = "Yes"  # bot: Great! (clear state and repeat cycle)

# test sentences (use case 2)
case2_sentences = [None] * 6
case2_sentences[0] = "Hey"  # bot: "Hello there. What would you like to eat today?"
case2_sentences[1] = "I don't know"  # bot: "Where are you?"
case2_sentences[2] = "Raffles Place"  # bot: "What would you like to have?"
case2_sentences[3] = "Anything"  # bot: There's chicken rice and sandwiches nearby. What do you want?
case2_sentences[4] = "Chicken Rice"  # bot: There is a Tian Tian Chicken Rice near Raffles Place".
# bot: Some people say "Best chicken rice in Singapore"
# bot: Is that what you want?
case2_sentences[5] = "Yes"  # bot: Great! (clear state and repeat cycle)

# PARAMETERS:
# ---------------------------------------------
bot_mode = 'test' # live
test_sentences = case1_sentences # case2_sentences

# jiakbot code
# ---------------------------------------------
print('Initializing jiak bot ... ')
jiakbot = JiakBot()

if bot_mode == 'live':

    run = True
    while run:
        sentence = input('User: ')

        # if input is not 'exit' loop ...
        if(sentence!='exit'):
            print('Jiakbot says: ',jiakbot.respond(sentence))

        else:
            print('bye bye')
            run=False

elif bot_mode == 'test':
    for i in range(0, len(test_sentences)):
        print('User:', test_sentences[i])
        print('Jiakbot says:', jiakbot.respond(test_sentences[i]))