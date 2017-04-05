
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

test_sentences = case1_sentences

# jiakbot code
# ---------------------------------------------
print('Initializing jiak bot ... ')


def get_response(user_input):
    response = "I don't understand you"


    return response

for i in range(0, len(test_sentences)):
    print('User   :', test_sentences[i])
    print('Jiakbot:', get_response(test_sentences[i]))
