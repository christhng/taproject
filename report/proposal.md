# Proposal

## Background
The project was inspired from a common problem working class adults in the Singapore CBD faced - where and what to eat for lunch. This project aims to suggest places to eat through a chatbot, in order to provide an interactive user experience. The chatbot will be built using Natural Language Processing (NLP) techniques.

## Motivation
* lack of localized chatbot
* hard to train chatbot using by creating the responses

## Potential Use Cases
* Tie up with business to suggest business to users
* provide some entertainment when choosing where to eat
* customer service for businesses who signed up

## Analytics Tasks
Here we describe the analytics tasks involved in building the chatbot

#### Named Entity Extraction
* Extracting foods, places and locations from user's comments

#### Document Retrieval
* Use of document retrieval to get the most relevant place to have lunch

#### Topic Analysis
* Reviews are used to train the bot to provide relevant responses.
* Each review is tied to a topic

## Approach
* Get the data (APIs and scraping)
* Prepare the corpus
* Prepare statement / response pairs?
* Use part of speech tags to understand?
* Use state machines to model the states
* Use information retrieval to get responses
* Use generic grammar rules to construct responses

## Data

#### Data Preparation
* web scraping
* nlp processing (vector space)
* training - topic modeling etc

#### Initial Exploration of Scraped Data
* Some description and charts
    * length of reviews
    * number of businesses
    * number of foods
    * number of places
    * number of cuisines

## Proposed Bot Architecture
### Python Classes
* jiakbot - main bot class
* parsing - tokenization
* state machine - entity extraction
* responder - construct responses
    * The main Responder class handles all response construction.
    * Points the flow in two main directions:
        * Information retrieval from the database
        * Construct an alternative response if a non-food query is detected
    * The Responder class makes use of several other classes to handle greetings, and other non-food related topics that are detected in the conversation
* retriever - information extraction
* trainer/topic_finder - topic modeling

### Database Diagram
* insert database diagram
