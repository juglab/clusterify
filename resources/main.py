import argparse
import json


def main():
    """
    This is the entry point for the script which is executed on the cluster-node via singularity.

    All configuration parameters are provided with the `experiment.json` file.

    __Note:__ Do __not__ rename this file, since it is called via the `slurm.job`.

    Authors: Manan Lalit, Tim-Oliver Buchholz
    """
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("--exp_config")

    args = parser.parse_args()

    with open(args.exp_config) as f:
        config = json.load(f)

    print("I am running in Singularity.")
    print("These are my config parameters:")
    for key in config.keys():
        print("    config[{}] : {}".format(key, config[key]))


if __name__ == "__main__":
    main()
