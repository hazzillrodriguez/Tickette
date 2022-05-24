# Tickette

[![Actions Status](https://github.com/hazzillrodriguez/Tickette/workflows/Run%20Tests/badge.svg)](https://github.com/hazzillrodriguez/Tickette/actions)
![Python](https://img.shields.io/badge/python-v3.6+-blue.svg)

Tickette is a support ticketing system that handles customer inquiries. It also provides all of the contexts you need to resolve issues and allows you to categorize, prioritize, and assign customer tickets.

## Installation

These instructions will get you a copy of the project up and running on your local machine.

1. Git clone or download the project files.
```
git clone https://github.com/hazzillrodriguez/Tickette.git
cd Tickette
```

2. Create and activate the virtual environment then install requirements.
```
python -m venv env
source env/Scripts/activate
pip install -r requirements.txt
```

3. Set the environment variables.
```
export FLASK_APP=run
export FLASK_ENV=development
```

4. Start Postgres or SQL Server database and update `SQLALCHEMY_DATABASE_URI` in `config.py`.
```
SQLALCHEMY_DATABASE_URI = 'mysql://admin:admin@localhost/tickette'
```

5. Create the database.
```
flask shell
db.create_all()
```

6. Start the development web server.
```
flask run
```

After that, navigate to `http://localhost:5000/login` in your browser to see the application. Log in using these credentials to access the admin, agent, and client areas.

### User Credentials

Administrator
    
    email: admin@tickette.com
    password: admindemo
Agent
    
    email: agent@tickette.com
    password: agentdemo
Customer
    
    email: customer@tickette.com
    password: customerdemo

### Create a local SMTP server to test the email feature

Start an SMTP server in a new terminal.
```
python -m smtpd -n -c DebuggingServer localhost:1025
```

**Note:** It does not send the email out to the target email server, it just discards the email and prints out the email content on the console. If you want to send an email to your SMTP server like Gmail, update the `MAIL_SERVER` configuration in `config.py`.

## Running the Tests

To run all the tests at once, use the command:
```
python -m pytest -v
```

## License

Distributed under the MIT License. See `LICENSE` for more information.

## Contact

Hazzill Rodriguez — [LinkedIn](https://www.linkedin.com/in/hazzillrodriguez/) — hazzillrodriguez@gmail.com