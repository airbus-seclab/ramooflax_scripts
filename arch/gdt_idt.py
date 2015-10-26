#!/usr/bin/env python
#
# Pretty print the GDT/IDT
#
import struct

from ramooflax.core  import VM, CPUFamily, log
from ramooflax.utils import SegmentDescriptor, InterruptDescriptor

##
## Main
##
peer = "172.16.131.128:1337"
vm = VM(CPUFamily.Intel, peer)

log.setup(info=True, fail=True,
          gdb=False, vm=True,
          brk=True,  evt=False)

# Retrieve 32 bits GDT/IDT content
vm.attach()
vm.stop()

gdt_sz = vm.cpu.sr.gdtr_limit + 1
gdt_mm = vm.mem.vread(vm.cpu.sr.gdtr_base, gdt_sz)

idt_sz = vm.cpu.sr.idtr_limit + 1
idt_mm = vm.mem.vread(vm.cpu.sr.idtr_base, idt_sz)

vm.detach()

# Pretty print GDT/IDT content
dts = (("-= GDT =-", SegmentDescriptor,   gdt_mm, gdt_sz),
       ("-= IDT =-", InterruptDescriptor, idt_mm, idt_sz))

for (tag,cls,dt,sz) in dts:
    print tag
    dsc = map(cls,struct.unpack("<%dQ"%(sz/8), dt))
    #print dsc[0]
    print dsc[0].hdr(),
    for i in xrange(len(dsc)):
        print "0x%.4x | 0x%.4x%s" % (i,i<<3,repr(dsc[i])),
    print
