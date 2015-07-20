import sys

class Test(object):
    __modules_count = 0
    __iters_count = 0

    __current_module_num  = 0
    __current_module_iter = 0
    __current_module_name = ""

    @staticmethod
    def __print_progress():
        progress = float(Test.__current_module_num - 1) / Test.__modules_count + (float(Test.__current_module_iter - 1) / Test.__iters_count) / Test.__modules_count
        progress = str(int(100 * progress))
        while len(progress) < 3 : progress = " " + progress

        progress = u"\r\033[1m[%s%%] Module '\033[31m%s\033[30m' started..." % (progress, Test.__current_module_name)
        while len(progress) < 60 : progress = progress + " "

        sys.stdout.write(progress)
        sys.stdout.flush()


    @staticmethod
    def start_test(modules):
        Test.__modules_count = len(modules)
        print u"\033[1mLoading modules: \033[31m" + "".join(map(lambda file: "\n  * %s" % file, modules)) + "\033[0m"
        print ""

    @staticmethod
    def finish_test():
        if Test.__current_module_num > 0:
            Test.__current_module_iter  += 1
            Test.__print_progress()
            sys.stdout.write(u"\033[1m\033[32m OK\033[0m\n\n")
            sys.stdout.flush()

        print u"\033[1mAll tests passed.\033[0m"

    @staticmethod
    def start_module(name, iterations):
        if Test.__current_module_num > 0:
            Test.__current_module_iter  += 1
            Test.__print_progress()
            sys.stdout.write(u"\033[1m\033[32m OK\033[0m\n")
            sys.stdout.flush()

        Test.__iters_count = iterations
        Test.__current_module_num  += 1
        Test.__current_module_iter  = 0
        Test.__current_module_name  = str(name)

    @staticmethod
    def next_iteration():
        Test.__current_module_iter += 1
        Test.__print_progress()