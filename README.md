# **Clusterify**

This repository enables your projects to be cluster-ready. Provided is a template, the components of which can be edited to work for your project.

1. Clone this repository inside your project space on the cluster. 
2. Copy-paste its contents in your project space.
3. Save the singularity file (`*.simg`) in the `singularity` directory.
4. Fill in the project configuration parameters in `project_config.json`.
5. Populate the `resources/main.py`.
6. Submit job to the cluster through `python3 run_script.py`.
    * Additional parameters, required by your code, can be exposed via the `run_script.py`. Just add your parameters to the [questions](https://github.com/juglab/clusterify/blob/setup/run_script.py#L122) and don't forget to [add them to the `experiment.json` file](https://github.com/juglab/clusterify/blob/setup/run_script.py#L149).
