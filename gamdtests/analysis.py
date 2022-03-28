
import os


def get_directories(directory):
    directories = []
    files = os.listdir(directory)
    for file in files:
        if os.path.isdir(os.path.join(directory, file)):
            directories.append(os.path.join(directory, file))
    return directories


def determine_group_or_single_directory(directory):
    analysis_test = os.path.join(directory, "analysis")
    if os.path.exists(analysis_test) and os.path.isdir(analysis_test):
        simulation_directories = [directory]
    elif os.path.exists(directory):
        simulation_directories = get_directories(directory)
    else:
        print("{} is not a directory and should be".format(directory))
        sys.exit(-1)

    return simulation_directories
