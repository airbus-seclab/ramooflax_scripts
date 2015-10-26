#!/usr/bin/env python
#
# This script auto disassemble code at each
# single step
#
# You are free to use your prefered disasm engine
# the callback provides current code location
# and bytes at that location
#
# This script uses amoco engine (https://github.com/bdcht/amoco)
#
from amoco.arch.x86  import cpu_x86 as am
from ramooflax.core  import VM, CPUFamily, log
from ramooflax.utils import disassemble

def disasm_wrapper(addr, data):
    return am.disassemble(data, address=addr)

def sstep_disasm(vm):
    insns = disassemble(vm, disasm_wrapper, vm.cpu.code_location())
    print insns.split('\n')[0]
    return True

##
## Main
##
peer = "172.16.131.128:1337"
vm = VM(CPUFamily.Intel, peer)

log.setup(info=True, fail=True, gdb=False)

vm.attach()
vm.stop()
vm.cpu.filter_singlestep(sstep_disasm)

log("info", "\n####\n#### type: vm.singlestep()\n####\n")
vm.interact(dict(globals(), **locals()))
vm.detach()
