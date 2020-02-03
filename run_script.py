import glob
import json
import os
from distutils.dir_util import copy_tree as copytree
from os.path import join
from shutil import copy as cp

from PyInquirer import prompt, Validator, ValidationError


def main():
    """
    This script requests some inputs from the user. Then it creates the necessary experiment directories
    and copies all files/dirs from '/projects/your-project-name/resources/` to the experiment directory.
    All provided inputs are written to the `experiment.json` file and a `slurm.job` file is created. Finally
    the computation is started with `sbatch slurm.job`.

    The computations are done in a singularity container.

    Authors: Manan Lalit, Tim-Oliver Buchholz
    """
    with open('project_config.json', 'r') as f:
        project_dict = json.load(f)

    singularity_path = project_dict["singularity_path"]
    resources_path = project_dict["resources_path"]
    base_path_data = project_dict["base_path_data"]
    base_path_exp = project_dict["base_path_exp"]
    project_name = project_dict["project_name"]
    slurm_logs = project_dict["slurm_logs"]
    time = project_dict["time"]
    number_tasks = project_dict["number_tasks"]
    number_nodes = project_dict["number_nodes"]
    number_cpus = project_dict["number_cpus"]
    partition = project_dict["partition"]
    gres = project_dict["gres"]
    exclude = project_dict["exclude"]
    mem = project_dict["mem"]
    export = project_dict["export"]


    def data_path(config):
        """
        Lists all the directories in /projects/your-project-name/data/

        :param config:
        :return:
        """
        l = [x[0] if os.path.isdir(x[0]) else 0 for x in os.walk(base_path_data)]
        if len(l) == 0:
            raise Exception("No training data available in {}".format(base_path_data))
        return l


    class ValExpName(Validator):
        """
        This validator checks if an experiment with the same name already exists.
        """
        def validate(self, document):
            names = glob.glob(join(base_path_exp, '*'))
            names = [n.split('/')[-1] for n in names]

            if document.text in names:
                raise ValidationError(
                    message='An experiment with this name already exists. Please choose another name.',
                    cursor_position=len(document.text)
                )


    def create_slurm_script(singularity_cmd):
        """
        Build the slurm.job script with the parameters from the `project_config.json` file.

        :param singularity_cmd:
        :return:
        """
        script = [
            "#!/bin/bash\n",
            "#SBATCH -J {}\n".format(project_name),
            "#SBATCH -o {}\n".format(join(slurm_logs, "slurm-%A.log")),
            "#SBATCH -t {}\n".format(time),  # max. wall clock time 5s\n",
            "#SBATCH -n {}\n".format(number_tasks),  # number of tasks\n",
            "#SBATCH -N {}\n".format(number_nodes),
            "#SBATCH -c {}\n".format(number_cpus),
            "#SBATCH --partition={}\n".format(partition),
            "#SBATCH --gres={}\n".format(gres),
            "#SBATCH --exclude={}\n".format(exclude),
            "#SBATCH --mem={}\n".format(mem),
            "#SBATCH --export={}\n".format(export),
            "\n",
            "srun -J projectname -o {}/projectname.log {}\n".format(exp_path, singularity_cmd)
        ]

        return script


    def start_experiment(exp_conf, exp_path, data_path):
        os.makedirs(exp_path, exist_ok=True)

        copytree(resources_path, exp_path)
        cp(join(resources_path, 'main.py'), exp_path)
        with open(join(exp_path, 'experiment.json'), 'w') as f:
            json.dump(exp_conf, f, sort_keys=True, indent=4)

        singularity_cmd = 'singularity exec -B {}:/notebooks -B {}:/data {} python3 /notebooks/main.py --exp_config ' \
                          '/notebooks/experiment.json'.format(exp_path, data_path, singularity_path)

        slurm_script = create_slurm_script(singularity_cmd)
        with open(join(exp_path, 'slurm.job'), 'w') as f:
            for l in slurm_script:
                f.write(l)
        os.system('chmod -R 775 ' + exp_path)

        # Submit the cluster-job via slurm-script
        os.system('sbatch {}'.format(join(exp_path, 'slurm.job')))

        # If you want to test locally or in an interactive session you can run
        # the singularity command without submitting a slurm-job.
        # os.system(singularity_cmd)


    questions = [
        {
            'type': 'input',
            'name': 'exp_name',
            'message': 'Experiment name:',
            'validate': ValExpName
        },
        {
            'type': 'list',
            'name': 'data_path',
            'message': 'Data path:',
            'choices': data_path
        }
        # PyInquirer
        # How to add more questions: https://github.com/CITGuru/PyInquirer#quickstart
        # Don't forget to add the new information to the `exp_config`.
    ]


    def create_configs(pyinquirer_answers):
        """
        Parse the information from the PyInquirer questions and write them into the
        experiment config.

        :param pyinquirer_answers:
        :return:
        """
        exp_config = {
            "exp_name": pyinquirer_answers['exp_name']
        }
        return exp_config


    pyinquirer_answers = prompt(questions)
    exp_config = create_configs(pyinquirer_answers)
    exp_path = join(base_path_exp, pyinquirer_answers['exp_name'])
    start_experiment(exp_config, exp_path, pyinquirer_answers['data_path'])


if __name__ == "__main__":
    main()
