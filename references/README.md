## Useful Links

### Chatbots
* How to Build a Chatbot [link] (https://apps.worldwritable.com/tutorials/chatbot/)
* Ultimate Guide to Leveraging NLP & Machine Learning for your Chatbot [link] (https://chatbotslife.com/ultimate-guide-to-leveraging-nlp-machine-learning-for-you-chatbot-531ff2dd870c#.azlcnkgfm)

### SQLite
* DB Browser for SQLite [link](http://sqlitebrowser.org/)

### Git workflow
* Git Workflow [here] (https://www.atlassian.com/git/tutorials/comparing-workflows/centralized-workflow)
* We are probably following the centralized workflow.

### Markdown (.md) to Microsoft Docx
* [pandoc](http://pandoc.org/installing.html) - [Download Link](http://pandoc.org/installing.html)
* Help command : pandoc --help
* Command to convert md to docx :
    * pandoc proposal.md -f markdown -t docx -o output.docx (Works for OSX and Windows)
	* where -f is from
	* -t is to
	* -o is output file name
* Command to convert md to html slides (reveal.js) :
    * pandoc -s --mathjax -t revealjs sample_deck.md -o sample_deck.html
	* where -s is standalone
	* -t is to
	* sample_deck.md is source file name
	* -o is output file name
* For reveal.js, the folder reveal.js needs to be in the same folder as the html slide deck
