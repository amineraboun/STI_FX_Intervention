# Miscelaneous tools

## Setup the python environement 

### On windows with conda:
There is a possibility to create and manage environments with ANACONDA windows application (in a visual way)

In the following instruction, change 'myenv' with the name of the environment you would like to set

```
1. Open anaconda prompt

2. Create an environement with conda 
    > conda create --name myenv

3. Activate the environement: Once the envirenment is activated you can access all the packages 
    > conda activate myenv
On the left of the command line you now must see the name of your environment

4. Install dependencies
    > pip install varfxi jupyter ipykernel

5. Create kernel, so you can access it in the jupyter notebook
    > ipython kernel install --name= kernel_name
```

### On Linux with poetry:
If you are in linux, you can leverage on the poetry toml file to install the repo dependencies

```
1. clone the github repo of the course
    > git clone https://github.com/amineraboun/STI_FX_Intervention.git

2. go to the folder where the repo is clone

3. open terminal

4. Install dependencies specified in pyproject.toml
    > poetry install

5. install ipykernel
    > poetry run pip install ipykernel

6. add a kernel 
    > poetry run python -m ipykernel install --user --name=kernel_name
```
