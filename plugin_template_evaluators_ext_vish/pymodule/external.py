# -- start license --
# Highly Optimized Object-oriented Many-particle Dynamics -- Blue Edition
# (HOOMD-blue) Open Source Software License Copyright 2009-2014 The Regents of
# the University of Michigan All rights reserved.

# HOOMD-blue may contain modifications ("Contributions") provided, and to which
# copyright is held, by various Contributors who have granted The Regents of the
# University of Michigan the right to modify and/or distribute such Contributions.

# You may redistribute, use, and create derivate works of HOOMD-blue, in source
# and binary forms, provided you abide by the following conditions:

# * Redistributions of source code must retain the above copyright notice, this
# list of conditions, and the following disclaimer both in the code and
# prominently in any materials provided with the distribution.

# * Redistributions in binary form must reproduce the above copyright notice, this
# list of conditions, and the following disclaimer in the documentation and/or
# other materials provided with the distribution.

# * All publications and presentations based on HOOMD-blue, including any reports
# or published results obtained, in whole or in part, with HOOMD-blue, will
# acknowledge its use according to the terms posted at the time of submission on:
# http://codeblue.umich.edu/hoomd-blue/citations.html

# * Any electronic documents citing HOOMD-Blue will link to the HOOMD-Blue website:
# http://codeblue.umich.edu/hoomd-blue/

# * Apart from the above required attributions, neither the name of the copyright
# holder nor the names of HOOMD-blue's contributors may be used to endorse or
# promote products derived from this software without specific prior written
# permission.

# Disclaimer

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDER AND CONTRIBUTORS ``AS IS'' AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, AND/OR ANY
# WARRANTIES THAT THIS SOFTWARE IS FREE OF INFRINGEMENT ARE DISCLAIMED.

# IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT,
# INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
# ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# -- end license --

from hoomd_plugins.evaluators_ext_conf import _evaluators_ext_conf

# Next, since we are extending an pair potential, we need to bring in the base class and some other parts from
# hoomd_script
from hoomd_script import external
from hoomd_script import util
from hoomd_script import globals
import hoomd
import math

## Lennard-Jones %pair %force
#
# Here, you can document your pair potential.The following is an abbreviated copy of the docs from hoomd itself.
# \f{eqnarray*}
# V_{\mathrm{LJ}}(r)  = & 4 \varepsilon \left[ \left( \frac{\sigma}{r} \right)^{12} -
#                   \alpha \left( \frac{\sigma}{r} \right)^{6} \right] & r < r_{\mathrm{cut}} \\
#                     = & 0 & r \ge r_{\mathrm{cut}} \\
# \f}
#
# The following coefficients must be set per unique %pair of particle types. See hoomd_script.pair or
# the \ref page_quick_start for information on how to set coefficients.
# - \f$ \varepsilon \f$ - \c epsilon (in energy units)
# - \f$ \sigma \f$ - \c sigma (in distance units)
# - \f$ \alpha \f$ - \c alpha (unitless)
#   - <i>optional</i>: defaults to 1.0
# - \f$ r_{\mathrm{cut}} \f$ - \c r_cut (in distance units)
#   - <i>optional</i>: defaults to the global r_cut specified in the %pair command
# - \f$ r_{\mathrm{on}} \f$ - \c r_on (in distance units)
#   - <i>optional</i>: defaults to the global r_cut specified in the %pair command
#
# \b Example:
# \code
# lj.pair_coeff.set('A', 'A', epsilon=1.0, sigma=1.0)
# lj.pair_coeff.set('A', 'B', epsilon=2.0, sigma=1.0, alpha=0.5, r_cut=3.0, r_on=2.0);
# lj.pair_coeff.set('B', 'B', epsilon=1.0, sigma=1.0, r_cut=2**(1.0/6.0), r_on=2.0);
# lj.pair_coeff.set(['A', 'B'], ['C', 'D'], epsilon=1.5, sigma=2.0)
# \endcode
#
class confinement(external._external_force):
    ## Specify the Confinement %external %force
    #
    # This method creates the pair force using the c++ classes exported in module.cc. When creating a new pair force,
    # one must update the referenced classes here.
    def __init__(self, name=""):
        util.print_status_line();

        # initialize the base class
        external._external_force.__init__(self, name);

        # create the c++ mirror class
        if not globals.exec_conf.isCUDAEnabled():
            self.cpp_force = _evaluators_ext_conf.PotentialExternalConfinement(globals.system_definition,self.name);
        else:
            self.cpp_force = _evaluators_ext_conf.PotentialExternalConfinementGPU(globals.system_definition,self.name);

        globals.system.addCompute(self.cpp_force, self.force_name);

        # setup the coefficent options
        self.required_coeffs = ['gamma', 'npower'];
        

    ## Process the coefficients
    #
    # The coefficients that the user specifies need not be the same coefficients that get passed as paramters
    # into your Evaluator. This method processes the named coefficients and turns them into the parameter struct
    # for the Evaluator.
    #
    def process_coeff(self, coeff):
	gamma = coeff['gamma'];
	npower = coeff['npower'];
       
        return hoomd.make_scalar2(gamma, npower);
