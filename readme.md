## Creating environment
First install conda in your machine if not already present. Then run 

    conda create -n aia2 python=3.10 numpy tk
    
in your terminal to create the conda environment `aia2` with required packages. Do not install any other package in this environment as we will run your code with just these packages. You need to create the conda environment just once. 

Second time onwards, just activate the environment using the command
    
    conda activate aia2

and run the game command.

pip install Flask

## Run and Test

Make sure you are in the app.py directory and your conda environment is active.

python app.py
Open your web browser and go to http://127.0.0.1:5000.
