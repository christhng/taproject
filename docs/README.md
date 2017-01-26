**for html5 presentations and code documentation**
# Installing Dependencies

* For clean organisation/isolation of Python dependencies between projects, [virtualenv](http://docs.python-guide.org/en/latest/dev/virtualenvs/) is commonly used
* Install virtualenv by running `pip install virtualenv` in your command line
* Clone the project (this will create a folder with the repository name wherever your current directory is) by running the following code in your command line `git clone https://github.com/junquant/taproject.git`
* Change directory: `cd taproject`
* Create a new virtual environment: `virtualenv -p python3 env`
* After it's done you can `activate` the virtualenv by running `source env/bin/activate` - this is assuming you are in the project's root folder (taproject)
* You are now inside the virtual environment! Now, we need to install the dependencies based on `requirements.txt`, which is located in the `config_app` folder
* Run this command to install dependencies `pip install -r config_app/requirements.txt`
* It should install all 3rd-party Python packages required for this project :)
* To view the dependencies, in your virtualenv mode you can type `pip list`
* To exit/deactivate the virtualenv, just type `deactivate`
