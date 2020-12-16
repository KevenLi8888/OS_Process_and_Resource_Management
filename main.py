# from process import Process
# from resource import Resource
# from pcb import PCB
# from queue import Queue
from enum import Enum
from collections import deque
from automic_counter import AtomicCounter

class Queue:

    def __init__(self):
        self.deques = [deque([]) for _ in range(3)]

    def get_ready_queue(self):
        ready_queue = Queue()
        return ready_queue

    def add_process(self, process):
        priority = process.get_priority()
        the_deque = self.deques[priority]
        the_deque.append(process)

    def get_process(self):
        for i in range(2, 0, -1):
            the_deque = self.deques[i]
            if the_deque:
                return the_deque[0]
        return None

    def remove_process(self, process):
        priority = process.get_priority()
        deque = self.deques[priority]
        deque.remove(process)
        return

class PCB:
    ready_queue = Queue().get_ready_queue()
    # 整个程序只能实例化一个ready_queue，就是PCB中的ready_queue，其他地方都使用pcb.ready_queue来访问，否则会出大问题

    def __init__(self):
        self.exist_process = {}
        self.current_process = None
        self.PID_generator = AtomicCounter()


    def get_PCB(self):
        pcb = PCB()
        return pcb

    def get_current_process(self):
        return self.current_process

    def set_current_process(self, current_process):
        self.current_process = current_process

    def generate_PID(self):
        return self.PID_generator.increment()

    def add_exist_list(self, process):
        self.exist_process[process.get_process_name()] = process
        return process

    def create_process(self, process_name, priority):
        current_process = pcb.get_current_process()
        process = Process(pcb.generate_PID(), process_name, priority, 'new', {}, current_process, [])
        if current_process:
            current_process.get_children().append(process)
            process.set_parent(current_process)
            pcb.add_exist_list(process)
            self.ready_queue.add_process(process)
        else: # 系统初始化时没有current_process，需要设置
            self.current_process = process
            pcb.add_exist_list(process)
        # 将以下两行代码放到上面的if-else结构中，因为系统初始化时init进程无需放到ready_queue里，
        # 直接通过scheduler调度进入running态。否则会导致ready_queue的deques[0]里有两个init进程。
        # pcb.add_exist_list(process)
        # self.ready_queue.add_process(process)
        process.set_state('ready')
        pcb.scheduler()
        return process

    def exist_name(self, name):
        return name in self.exist_process

    def find_process(self, process_name):
        for entry in self.exist_process.keys():
            if entry == process_name:
                return self.exist_process[entry]
        return None

    def scheduler(self):
        current_process = pcb.get_current_process()
        ready_process = self.ready_queue.get_process()
        if ready_process == None:
            pcb.get_current_process().set_state('running')
            return
        elif current_process == None:
            self.ready_queue.remove_process(ready_process)
            pcb.set_current_process(ready_process)
            ready_process.set_state('running')
        elif (current_process.get_state() == 'blocked') | (current_process.get_state() == 'terminated'):
            self.ready_queue.remove_process(ready_process)
            pcb.set_current_process(ready_process)
            ready_process.set_state('running')
        elif current_process.get_state() == 'running':
            if current_process.get_priority() < ready_process.get_priority():
                self.preempt(ready_process, current_process)
        elif current_process.get_state() == 'ready':
            if current_process.get_priority() <= ready_process.get_priority():
                self.preempt(ready_process, current_process)
            else:
                current_process.set_state('running')
        return

    def preempt(self, ready_process, current_process):
        if self.exist_name(current_process.get_process_name()):
            self.ready_queue.add_process(current_process)
            current_process.set_state('ready')
            self.ready_queue.remove_process(ready_process)
            pcb.set_current_process(ready_process)
            ready_process.set_state('running')
            return

    def timeout(self):
        pcb.get_current_process().set_state('ready')
        self.scheduler()

    def kill_process(self, process):
        name = process.get_process_name()
        self.exist_process.pop(name)

    def print_process_tree(self, process, retract):
        for i in range(retract):
            print('  ')
        print('|-')
        self.print_process_detail(process)
        children = process.get_children()
        for i in range(len(children)):
            child = children[i]
            self.print_process_tree(child, retract+1)

    def print_process_detail(self, process):
        print(process.get_process_name()
              + '(PID:' + process.get_PID()
              + ', 进程状态:' + process.get_state()
              + ', 优先级:' + process.get_priority()
              + ',')
        if not process.get_resource_map():
            print('无资源占用！')
        else:
            string = '('
            for key in process.get_resource_map().keys:
                hold_num = process.get_resource_map()[key]
                string.join(',').join('R').join(key.get_RID()).join(':').join(hold_num)
            string.join(")")
            print(string)

class Process:
    state = Enum('state', ('new', 'ready', 'running', 'blocked', 'terminated'))
    pcb = PCB().get_PCB()
    # ready_queue = Queue().get_ready_queue() # 不能重新实例化ready_queue，应直接用pcb.ready_queue访问
    ready_queue = pcb.ready_queue
    block_resource = []

    def __init__(self, PID, process_name, priority, state, resource_map: dict, parent_process, children_process):
        self.PID = PID
        self.process_name = process_name
        self.priority = priority
        self.state = state
        self.resource_map = resource_map
        self.parent_process = parent_process
        self.children_process = children_process

    def get_PID(self):
        return self.PID

    def get_process_name(self):
        return self.process_name

    def get_priority(self):
        return self.priority

    def get_state(self):
        return self.state

    def set_state(self, state):
        self.state = state

    def set_parent(self, parent_process):
        self.parent_process = parent_process

    def get_children(self):
        return self.children_process

    def get_block_resource(self):
        return self.block_resource

    def get_resource_map(self):
        return self.resource_map

    def set_block_resource(self, block_resource):
        self.block_resource = block_resource

    def destroy_process(self):
        self.kill_sub_tree()
        pcb.scheduler()

    def remove_child(self, parent):
        for child in parent.children_process:
            if child == self:
                parent.children_process.remove(child)

    def kill_sub_tree(self):
        if self.children_process: # 当前进程子树不为空
            child_count = len(self.children_process)
            for i in range(child_count):
                child = self.children_process[0]
                child.kill_sub_tree()

        if self.get_state() == 'terminated':
            pcb.kill_process(self)
        elif self.get_state() == 'ready':
            self.ready_queue.remove_process(self)
            pcb.kill_process(self)
            self.set_state('terminated')
        elif self.get_state() == 'blocked':
            block_resource = self.get_block_resource()
            block_resource.remove_block_process(self)
            pcb.kill_process(self)
            self.set_state('terminated')
        elif self.get_state() == 'running':
            pcb.kill_process(self)
            self.set_state('terminated')

        # self.parent_process.remove_child() # 这样会使该父进程的所有子进程都被删掉而不是只删想要的子进程 # 不应该传入self！self为父进程。应该
        parent = self.parent_process
        self.remove_child(parent)
        self.parent_process = []

        duplicate_resource_map = self.resource_map.copy() # prevent: RuntimeError: dictionary changed size during iteration
        for resource in duplicate_resource_map:
            resource.release_process(self)

        return

class Resource:
    pcb = PCB().get_PCB()
    # ready_queue = Queue().get_ready_queue()
    ready_queue = pcb.ready_queue

    class BlockProcess:
        def __init__(self, process, need):
            self.process = process
            self.need = need

        def get_process(self):
            return self.process

        def get_need(self):
            return self.need

    def __init__(self, RID, max):
        self.RID = RID
        self.max = max
        self.remaining = max
        self.block_deque = deque([])

    def get_RID(self):
        return self.RID

    def add_remaining(self, num):
        self.remaining += num

    def remove_block_process(self, process):
        for blocked_process in self.block_deque:
            if blocked_process.get_process() == process:
                self.block_deque.remove(blocked_process)
                return True
        return False

    def request(self, process, need):
        if need > self.max:
            print('请求资源失败！请求资源大于最大数量！')
            return
        elif (need > self.remaining) & (process.get_process_name() != 'init'):
            self.block_deque.append(self.BlockProcess(process, need))
            process.set_state('blocked')
            process.set_block_resource(self)
            pcb.scheduler()
            return
        elif (need > self.remaining) & (process.get_process_name() == 'init'):
            return
        else:
            self.remaining = self.remaining - need
            resource_map = process.get_resource_map()
            if self in resource_map:
                already_allocated_num = resource_map.get(self)
                resource_map[self] = already_allocated_num + need
            else:
                resource_map[self] = need

    def release_process(self, process):
        num = process.get_resource_map().pop(self)
        if num == 0:
            return
        self.remaining = self.remaining + num
        while self.block_deque:
            block_process = self.block_deque[0]
            need = block_process.get_need()
            if self.remaining >= need:
                ready_process = block_process.get_process()
                self.request(ready_process, need)
                self.block_deque.popleft()
                self.ready_queue.add_process(ready_process)
                ready_process.set_state('ready')
                ready_process.set_block_resource([])
                if ready_process.get_priority() > pcb.get_current_process().get_priority():
                    pcb.preempt(ready_process, pcb.get_current_process())
                # else:
                #     break
            else:
                break

    def release(self, process, num):
        if num == 0:
            return
        self.remaining = self.remaining + num
        while self.block_deque:
            block_process = self.block_deque[0]
            need = block_process.get_need()
            if self.remaining >= need: # 大于等于 不是大于
                ready_process = block_process.get_process()
                self.request(ready_process, need)
                self.block_deque.popleft()
                self.ready_queue.add_process(ready_process)
                ready_process.set_state('ready')
                ready_process.set_block_resource([])
                if ready_process.get_priority() > pcb.get_current_process().get_priority():
                    pcb.preempt(ready_process, pcb.get_current_process())
                # else:
                #     break
            else:
                break
        return

    def print_current_status(self):

        string = 'res-'
        string += str(self.RID)
        string += '{max='
        string += str(self.max)
        string += ',remaining:'
        string += str(self.remaining)
        string += '}'
        print(string)

    def print_block_deque(self):

        string = 'res-'
        string += str(self.RID)
        string += ' block_deque '

        for blocked_process in self.block_deque:
            string += '{'
            string += blocked_process.get_process().get_process_name()
            string += ':'
            string += str(blocked_process.get_need())
            string += '}'

        print(string)

def load_file(filename):
    file = open(filename, 'r')
    commands = file.readlines()
    for line in commands:
        commands[commands.index(line)] = line.strip()
    return commands

def exec_commands(cmds):

    if cmds[0] == 'cr':
        if not len(cmds) == 3:
            print('错误！输入命令格式不合法！')
            return -1
        else:
            process_name = cmds[1]
            try:
                priority = int(cmds[2])
                if priority <= 0 | priority > 2:
                    print('错误！输入参数不合法！')
                    return -1
            except:
                print('错误！输入参数不合法！')
                return -1
            if pcb.exist_name(process_name):
                print('错误！进程名' + process_name + '已经存在，请选择其他的进程名！')
                return -1
            pcb.create_process(process_name, priority)

    elif cmds[0] == 'de':
        if not len(cmds) == 2:
            print('错误！输入命令格式不合法！')
            return -1
        else:
            process_name = cmds[1]
            process = pcb.find_process(process_name)
            if process == None:
                print('错误！没有名为' + process_name + '的进程！')
                return -1
            elif process_name == 'init':
                print('错误！没有权限中止init进程！')
                return -1
            else:
                process.destroy_process()

    elif cmds[0] == 'req':
        if not len(cmds) == 3:
            print('错误！输入命令格式不合法！')
            return -1
        else:
            resource_name = cmds[1]
            try:
                need_num = int(cmds[2])
            except:
                print('错误！输入参数不合法！')
                return -1
            current_process = pcb.get_current_process()
            if resource_name == 'R1':
                R1.request(current_process, need_num)
            elif resource_name == 'R2':
                R2.request(current_process, need_num)
            elif resource_name == 'R3':
                R3.request(current_process, need_num)
            elif resource_name == 'R4':
                R4.request(current_process, need_num)
            else:
                print('错误！输入参数不合法！')
                return -1

    elif cmds[0] == 'rel':
        if not len(cmds) == 3:
            print('错误！输入命令格式不合法！')
            return -1
        else:
            resource_name = cmds[1]
            try:
                rel_num = int(cmds[2])
            except:
                print('错误！输入参数不合法！')
                return -1
            current_process = pcb.get_current_process()
            if resource_name == 'R1':
                R1.release(current_process, rel_num)
            elif resource_name == 'R2':
                R2.release(current_process, rel_num)
            elif resource_name == 'R3':
                R3.release(current_process, rel_num)
            elif resource_name == 'R4':
                R4.release(current_process, rel_num)
            else:
                print('错误！输入参数不合法！')
                return -1

    elif cmds[0] == 'to':
        pcb.timeout()

    elif (cmds[0] == 'list') & (cmds[1] == 'ready'):
        print()
        print('...ready list...')
        queue = pcb.ready_queue
        for priority in range(3):
            print(str(priority) + ':', end=' ')
            for process in queue.deques[priority]:
                process_name = process.get_process_name()
                print(' ' + process_name, end=' ')
            print()
        print('...ready list ends...')
        print()
        return 0

    elif (cmds[0] == 'list') & (cmds[1] == 'block'):
        print()
        print('...block list...')
        R1.print_block_deque()
        R2.print_block_deque()
        R3.print_block_deque()
        R4.print_block_deque()
        print('...block list ends...')
        print()
        return 0

    elif (cmds[0] == 'list') & (cmds[1] == 'res'):
        print()
        print('...resource list...')
        R1.print_current_status()
        R2.print_current_status()
        R3.print_current_status()
        R4.print_current_status()
        print('...resource list ends...')
        print()
        return 0

    else:
        print('错误！请输入合法的命令！')
        return -1

    if not pcb.get_current_process() == None:
        print(pcb.get_current_process().get_process_name(), end=' ')
        return 0

if __name__ == '__main__':
    pcb = PCB()
    R1 = Resource(1, 1)
    R2 = Resource(2, 2)
    R3 = Resource(3, 3)
    R4 = Resource(4, 4)

    pcb.create_process('init', 0)
    print('init' + ' ')

    # print('从文件读取数据...')
    filename = '2.txt'
    commands = load_file(filename)

    for command in commands:
        cmds = command.split(' ')
        exec_commands(cmds)
