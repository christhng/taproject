# Proposal

## Background
* Working crowd often don't know where to eat
* Interactively suggest places to eat
* Use NLP techniques to build a chatbot

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
* retriever - information extraction
* trainer/topic_finder - topic modeling 

### Database Diagram
* insert database diagram