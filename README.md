# RapidKioskSimulator

## Dependency Installation

This project uses Python dependencies listed in `requirements.txt`.  
Follow the steps below to install them:

1. **Ensure Python is installed**  
   Make sure you have Python 3.8 or above installed on your system.  
   You can check by running:
   ```bash
   python --version or python3 --version

2. **Create a virtual environment**  
   Recommended to prevent conflicts with other projects:
   python -m venv venv

   Activate it:
   
        Windows:
            venv\Scripts\activate
        
        macOS / Linux:
            source venv/bin/activate

3. **Upgrade pip (Optional)**
   ```bash
   pip install --upgrade pip

4. **Installation verification**
   ```bash
   pip list

## How to run the website
1. **Set up database**
   Ensure that metro.db exists and contains the required tables:
   	•	stations
   	•	fares
   	•	times
   	•	routes
   	•	arrivals

2. **Start the Flask application**
   ```bash
   python app.py

3. **Access the kiosk system**
   Open your browser and access to:
   ```bash
   http://localhost:5001

4. **View real time train updates**
   The kiosk dashboard will automatically update as the simulation runs.
