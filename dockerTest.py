import docker
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description = "Input Parameters:")
    parser.add_argument("--suffix_labels1", default = "1,0;1,0;0,0;1,0;0,0;0,0", type = str,
                        help = "a list controling which method to generate in the suffix")
    parser.add_argument("--suffix_labels2", default = "0,0;1,0;0,0;1,0;1,0;1,0", type = str,
                        help = "a list controling which method to generate in the suffix")
    args = parser.parse_args()


    client = docker.from_env()
    #print(client.containers.list())
    # client.containers.run(image="period:latest", command="echo hello world")
    containerId = "47636e5b16"
    container = client.containers.get(containerId)
    #print(container.logs())
    #run = "python /workdir/test.py --suffix_labels1=\"1,0;1,0;0,0;1,0;0,0;0,0\" --suffix_labels2=\"0,0;1,0;0,0;1,0;1,0;1,0\""
    run = "python /workdir/test.py --suffix_labels1=\""
    run += args.suffix_labels1
    run += "\" --suffix_labels2=\""
    run += args.suffix_labels2
    run += "\""
    ping = container.exec_run(run)
    lines = ping.decode("utf-8").split("\n")
    for line in lines :
        if line.find("Error")>=0 and line.find("Interleavings")>=0 :
            #print(line)
            nums = line.split(" ")
            print(nums[3])