//////////// ADK running steps 

pip install google-adk

python -m venv .venv > .venv\Scripts\Activate.ps1 > adk create yacht_agents 

Set your API key

echo 'GOOGLE_API_KEY="YOUR_API_KEY"' > .env

----- Run with command-line interface

adk run yacht_agents

----- Run with web interface

adk web --port 8000

//////////// agent.py running steps

cd yacht_agents 

install requirements.txt 

windows Powershell > .venv\Scripts\Activate.ps1 > python agent.py