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
    print(client.containers.list())
    client.containers.run(image="period:latest", command="echo hello world")
    containerId = "ef22199e51c69421943234a98110001fa6ac37a94521367b4621554b3846e0f9"
    container = client.containers.get(containerId)
    #print(container.logs())
    #run = "python /workdir/test.py --suffix_labels1=\"1,0;1,0;0,0;1,0;0,0;0,0\" --suffix_labels2=\"0,0;1,0;0,0;1,0;1,0;1,0\""
    run = "python /workdir/PERIOD/test/mars/test.py --suffix_labels1=\""
    run += args.suffix_labels1
    run += "\" --suffix_labels2=\""
    run += args.suffix_labels2
    run += "\""
    #run = "./workdir/PERIOD/test/mars/thread"
    #run = "ls /workdir/PERIOD/test/mars/"
    #run = "pwd"
    ping = container.exec_run(run)
    print ("ping is ", ping)
    lines = ping.output.decode("utf-8").split("\n")
    print ("lines ", lines)
    #lines = ping.split("\n")
    for line in lines :
        #if line.find("Error")>=0 and line.find("Interleavings")>=0 :
        print(line)
            #nums = line.split(" ")
            #print(nums[3])
            
            
#build = "clang++ -fsanitize=thread -g -o thread{} test_try2_gen.cpp".format(num)
# clang++ -fsanitize=thread -g -o thread0 test_try2_gen.cpp
# docker cp can move file under windows to docker
# docker commit 2a47e53e8d4c  Periods/my_experiment0522:version1