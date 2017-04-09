from jiakbot import JiakBot

# test conversations
# ---------------------------------------------
# test sentences (use case 1)
case1_sentences = [None] * 5
case1_sentences[0] = "Hey"  # bot: "Hello there. What would you like to eat today?"
case1_sentences[1] = "I don't know"  # bot: "Where are you?"
case1_sentences[2] = "I want to eat at Raffles Place"  # bot: "What would you like to have?"
case1_sentences[3] = "I want to have burgers"  # bot: There is a Ya Kun near Raffles Place...
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


# test sentences (use case 3)
case3_sentences = [None] * 3
case3_sentences[0] = "hi"  # bot: "greeting + question"
case3_sentences[1] = "i would like to have prata"  # bot: "acknowledge + review + satisfied?"
case3_sentences[2] = "okay, i will try that out. thanks!!"  # bot: "acknowledge + departure greeting"

# test sentences (use case 4)
case4_sentences = [None] * 6
case4_sentences[0] = "morning"  # bot: "greeting + question"
case4_sentences[1] = "wah this cool sia"  # bot: "acknowledge + further probe"
case4_sentences[2] = "oh, paiseh i wanted laksa from malay cuisine"  # bot: "acknowledge + review + satisfied?"
case4_sentences[3] = "err, that one try before liao, another one pls"  # bot: "acknowledge + further probe"
case4_sentences[4] = "different restaurant la adoi..."  # bot: "acknowledge + review + satisfied?"
case4_sentences[5] = "ya thats good, shall try that"  # bot: "acknowledge + departure greeting"

# test sentences (use case 5)
case5_sentences = [None] * 8
case5_sentences[0] = "hello!"  # bot: "greeting + question"
case5_sentences[1] = "hmm, i want to eat chicken rice which is chinese cuisine i guess?"  # bot: "acknowledge + review + satisfied?"
case5_sentences[2] = "do you have another restaurant? i don't like that place"  # bot: "acknowledge + further probe"
case5_sentences[3] = "restaurant"  # bot: "acknowledge + review + satisfied?"
case5_sentences[4] = "actually, i changed my mind, i want eat japanese ramen, got any nice places?"  # bot: "acknowledge + further probe"
case5_sentences[5] = "no"  # bot: "acknowledge + further probe"
case5_sentences[6] = "woops, type wrong. change food, i want japanese ramen la"  # bot: "acknowledge + review + satisfied?"
case5_sentences[7] = "yes"  # bot: "acknowledge + departure greeting"

# test sentences (use case 6)
case6_sentences = [None] * 9
case6_sentences[0] = "yo!!"  # bot: "greeting + question"
case6_sentences[1] = "holy shit, it actually works lol"  # bot: "acknowledge + further probe"
case6_sentences[2] = "hehe let me see... chicken rice lor"  # bot: "acknowledge + further probe"
case6_sentences[3] = "chinese la..."  # bot: "acknowledge + review + satisfied?"
case6_sentences[4] = "cool... got other places?"  # bot: "acknowledge + further probe"
case6_sentences[5] = "change place la... isnt it obvious"  # bot: "acknowledge + further probe"
case6_sentences[6] = "zzz. CHANGE RESTAURANT"  # bot: "acknowledge + review + satisfied?"
case6_sentences[7] = "no."  # bot: "acknowledge + further probe"
case6_sentences[8] = "no."  # bot: "acknowledge + further probe"

# test sentences (use case 7)
case7_sentences = [None] * 4
case7_sentences[0] = "wassup"  # bot: "greeting + question"
case7_sentences[1] = "erm. I would like some malay food"  # bot: "acknowledge + further probe"
case7_sentences[2] = "malay food like rendang?"  # bot: "acknowledge + review + satisfied?"
case7_sentences[3] = "Yeah great!! I shall try that out then"  # bot: "acknowledge + departure greeting"

# test sentences (use case 8)
case8_sentences = [None] * 7
case8_sentences[0] = "hey wassup bro"  # bot: "greeting + question"
case8_sentences[1] = "I AM SUPERMAN, I WANT KRYPTONITE!!"  # bot: "acknowledge + further probe"
case8_sentences[2] = "kidding la.. let me think"  # bot: "acknowledge + further probe"
case8_sentences[3] = "western food, how about steak"  # bot: "acknowledge + review + satisfied?"
case8_sentences[4] = "i think i want wings instead"  # bot: "acknowledge + further probe"
case8_sentences[5] = "... i want change food to wings"  # bot: "acknowledge + review + satisfied?"
case8_sentences[6] = "ok la very satisfied, time to talk to chickens. Bye"  # bot: "acknowledge + departure greeting"

# test sentences (use case 9)
case9_sentences = [None] * 7
case9_sentences[0] = "idiot"  # bot: "acknowledge + further probe"
case9_sentences[1] = "what u want, stop asking me to do stuff"  # bot: "acknowledge + further probe"
case9_sentences[2] = "hi"  # bot: "greeting + question"
case9_sentences[3] = "western food, popiah"  # bot: "acknowledge + review + satisfied?"
case9_sentences[4] = "no, what kind of rubbish recommendation is that?"  # bot: "acknowledge + further probe"
case9_sentences[5] = "nope. You don't get me"  # bot: "acknowledge + further probe"
case9_sentences[6] = "whatever.."  # bot: "acknowledge + further probe"


# PARAMETERS:
# ---------------------------------------------
bot_mode = 'live' # live
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
