# Final Report

## Background
The project was inspired from a common problem working class adults in Singapore's Central Business District (CBD) faced - where and what to eat for lunch. Daily, the working crowd in CBD look forward to their meal times to recharge and perhaps to catch up with fellow colleagues. However, given the numerous food choices and a lack of time to research on where and what to eat, most people have difficulty deciding their meals. Some have resorted to generating random places to eat using Microsoft Excel. This project aims to suggest places to eat through a chatbot, in order to provide an interactive user experience and to enable the user to make a more informed choice. The chatbot will be built using Natural Language Processing (NLP) techniques.

## Motivation
Chatbots, through Natural Language Processing (NLP), is an attractive method of human-computer interaction due to the interactivity as compared to traditional mediums such as a Frequently Asked Questions (FAQ) section on a website. It has been used in a variety of domains such as environment and sustainable development [1], education [2] and other commercial purposes [3]. The fact that chatbots are not widely used in Singapore for food and restaurants recommendations makes it an obvious primary choice for us to develop one which is specific to Singapore. Furthermore, creating relevant and appropriate response leveraging on various NLP techniques is a tough but critical component to a successful chatbot. Hence, we decided to take on the challenge of developing one. There are also several use cases or scenarios which we think will be immediately useful. They are: 

* Tying up with business to provide exposure as well as a source of revenue (e.g. incentives/discounts). 
* Letting users to have a quick and easy access to information about food places in their vicinity.
* Letting users can subscribe to this service to receive information about trending restaurants based on their preferences communicated to the chatbot
* Providing some entertainment (localized humour) when choosing where to eat.
* Providing other information about food location by complementing current data with other data sources such as Google visitor information (e.g. Popular time, live visits, duration).
* Generating revenue through advertisements within App.

## About the Data

## Analytics Tasks 

## Approach

#### Proposed Bot Architecture 

* include architecture diagram

#### Python Classes
**jiakbot**
* main bot class

**Parsing**
* insert content

**State Machine** 
* The State Machine class is meant to keep track of the context of a conversation, in particular:
    * Where the user want to eat or the user's current location
    * What kind of food cuisine the user is looking for
    * What sort of food the user is looking for
* The State Machine relays the state information and/or status to the Responder to either prompt the user for more information and/or provide the user with a list of recommendations retrieved from the business and food database.

**Responder**
* The main Responder class handles all response construction.
* Points the flow in two main directions:
    * Information retrieval from the database
        * Construct an alternative response if a non-food query is detected
    * The Responder class makes use of several other classes to handle greetings, and other non-food related topics that are detected in the conversation

**Retriever**
* The Retriever function is meant to query the database based on the data provided by the Responder and return a relevant set of information for the Responder class to utilize
* The Retriever function conducts 4 main steps:
    * Simple SQL statements used to extract the related data from the database based on data (query) provided by Responder
    * Reference the tokens: Compare using cosine similarity to get most relevant statement 
    * Convert set of statement(s) into dictionary
    * Return dictionary to Responder class

**Trainer/ Topic_finder**
* insert content 

## Results and Findings
* Defining good response?
* Defining accuracy?

## Discusssions


## References
[1] AluxBot - A Chatbot that Encourages the Care for the Environment. (2016). International Journal of Computer Science Issues, 13(6), 120-123.

[2] Yi Fei Wang, & Stephen Petrina. (2013). Using Learning Analytics to Understand the Design of an Intelligent Language Tutor – Chatbot Lucy. International Journal of Advanced Computer Science and Applications, 4(11), 124-131.

[3] Chatbots Raise Questions About the Future of Customer Service. (2016, April 27). PR Newswire, p. PR Newswire, Apr 27, 2016.


