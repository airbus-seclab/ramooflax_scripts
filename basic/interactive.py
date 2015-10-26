#!/usr/bin/env python
#
# Enter interactive 'shell' mode
#
from ramooflax.core import VM, CPUFamily, log

##
## Main
##
peer = "172.16.131.128:1337"
vm = VM(CPUFamily.Intel, peer)

log.setup(all=True)

vm.run(dict(globals(), **locals()))
