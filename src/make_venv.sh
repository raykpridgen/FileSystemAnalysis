FOLDER_PATH="../../venv"

if [ -d "$FOLDER_PATH" ]; then
  source ../../venv/bin/activate
  pip3 install zss
  pip3 install matplotlib
  pip3 install igraph
  pip3 install plotly
else
  python3 -m venv ../../venv
  source ../../venv/bin/activate
  pip3 install zss
  pip3 install matplotlib
  pip3 install igraph
  pip3 install plotly
fi
