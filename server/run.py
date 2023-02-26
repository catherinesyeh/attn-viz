from app import app
from dotenv import load_dotenv
import os
load_dotenv()
# from app import socketio

# The port number should be the same as the front end
# try:
# socketio.run(app, host='localhost', port=8500, use_reloader=False, debug=True)

port = int(os.environ.get("PORT", 8500))
app.run(host='0.0.0.0', port=port, use_reloader=False, debug=True)
# except:
#print("Something wrong!")
