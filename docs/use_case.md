# Use Cases

* Objective is to complete the flow for case 1 and 2 first
* After that then we complicate things =)

### Case 1

* **User:** Hey
* **Bot:** Hello there. What would you like to eat today?
* **User:** I don't know
* **Bot:** Where are you?
* **User:** Raffles Place 
* **Bot:** What would you like to have?
* **User:** Coffee
* **Bot:** There is a Ya Kun near Raffles Place (Information Retrieval)
* **Bot:** Some people say "It's the best kaya toast around" 
* **Bot:** Is that what you want?
* **User:** Yes
* **Bot:** Great! (clear state and repeat cycle)

### Case 2
* **User:** Hey
* **Bot:** Hello there. What would you like to eat today?
* **User:** I don't know
* **Bot:** Where are you?
* **User:** Raffles Place 
* **Bot:** What would you like to have?
* **User:** Anything
* **Bot:** There's chicken rice and sandwiches nearby. What do you want?
* **User:** Chicken Rice 
* **Bot:** There is a Tian Tian Chicken Rice near Raffles Place
* **Bot:** Some people say "Best chicken rice in Singapore"
* **Bot:** Is that what you want?
* **User:** Yes
* **Bot:** Great!

### Cycle 
Parse - Update State - Retrieve(if needed) - Respond 