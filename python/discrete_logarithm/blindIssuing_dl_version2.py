
#author:Feng
#version:1.0

from collections import namedtuple
from charm.toolbox.integergroup import IntegerGroupQ
from charm.core.math.integer import int2Bytes, integer
import hashlib
import sys
import traceback

Parameters = namedtuple('Parameters', ['L', 'group', 'g', 'h'])
IssuerKeypair = namedtuple('IssuerKeypair', ['x', 'y', 'parameters'])
UserKeypair = namedtuple('UserKeypair', ['gamma', 'xi', 'parameters'])
TracerKeypair = namedtuple('TracerKeypair', ['xt', 'yt', 'parameters'])

def initialization(kappa):
    group = IntegerGroupQ()
    group.paramgen(kappa)
    g, h = group.randomGen(), group.randomGen()
    parameters = Parameters(kappa, group, g, h)
    return parameters

def tracer_choose_keypair(parameters):
  xt = parameters.group.random()
  yt = parameters.g ** xt
  return TracerKeypair(xt, yt, parameters)

def user_choose_keypair(parameters):
  gamma = parameters.group.random()
  xi = parameters.g ** gamma
  return UserKeypair(gamma, xi, parameters)

def gnerate_common_z(parameters, y):
  hs = hashlib.new('sha256')
  hs.update(int2Bytes(parameters.group.p))
  hs.update(int2Bytes(parameters.group.q))
  hs.update(int2Bytes(parameters.g))
  hs.update(int2Bytes(parameters.h))
  hs.update(int2Bytes(y))
  return (integer(hs.digest()) ** ((parameters.group.p - 1) / parameters.group.q)) % parameters.group.p

### Protocol stuff ###
class Issuer:
    '''Issuer S from the paper'''
    def __init__(self, parameters, tkey):
        x = parameters.group.random()
        y = parameters.g ** x

        self.IssuerKeypair = IssuerKeypair(x, y, parameters)
        self.tkey = tkey

    def start(self):
      self.z = gnerate_common_z(self.IssuerKeypair.parameters, self.IssuerKeypair.y)

    def protocol_two(self,z_u,xi):
      group = self.IssuerKeypair.parameters.group
      v = group.random()
      self.xiv = xi ** v
      z1 = self.tkey ** v
      z2 = z_u / z1

      self.u, self.d, self.s1, self.s2  = (group.random() for i in range(4))

      a = self.IssuerKeypair.parameters.g ** self.u
      b1 = (self.IssuerKeypair.parameters.g ** self.s1) * (z1 ** self.d) 
      b2 = (self.IssuerKeypair.parameters.h ** self.s2) * (z2 ** self.d)

      return (z1, a, b1, b2)

    def protocol_four(self, e):
      c = e -  self.d
      r = self.u - c * self.IssuerKeypair.x
      return (r, c, self.s1, self.s2, self.d)


class User:
    '''User U from the paper'''
    def __init__(self, parameters, pubkey, tkey):

        self.parameters = parameters
        self.y = pubkey
        self.tkey = tkey
        self.UserKeypair = user_choose_keypair(self.parameters)

    def start(self):
        self.t1, self.t2, self.t3, self.t4, self.t5 = (self.parameters.group.random() for i in range(5))
        self.z = gnerate_common_z(self.parameters, self.y)

    def protocol_one(self):
        z_u = self.z ** (1 / self.UserKeypair.gamma)
        return (z_u, self.UserKeypair.xi)

    def protocol_three(self, z1, a, b1, b2, m):
        self.zeta1 = z1 ** self.UserKeypair.gamma
        self.zeta2 = self.z / self.zeta1
        
        alpha = (a * (self.parameters.g ** self.t1) * (self.y ** self.t2)) % self.parameters.group.p
        beta1 = ((b1 ** self.UserKeypair.gamma) * (self.parameters.g ** self.t3) * (self.zeta1 ** self.t5)) % self.parameters.group.p
        beta2 = ((b2 ** self.UserKeypair.gamma) * (self.parameters.h ** self.t4) * (self.zeta2 ** self.t5)) % self.parameters.group.p
        epsion = self.parameters.group.hash(self.zeta1, alpha, beta1, beta2, m)
        e =  epsion - self.t2 - self.t5

        return e

    def protocol_five(self, r, c, s1, s2, d):
        roi = r + self.t1
        pi = c + self.t2
        sigma1 = (self.UserKeypair.gamma * s1) + self.t3
        sigma2 = (self.UserKeypair.gamma * s2) + self.t4
        delta = d + self.t5
        return (roi, pi, sigma1, sigma2, delta)

def verify(roi, pi, sigma1, sigma2, delta, parameters, m, y, zeta1, zeta2, z):
    g = parameters.g
    h = parameters.h

    tmp1 = ((g ** roi) * (y ** pi)) % parameters.group.p
    tmp2 = (g ** sigma1 * zeta1 ** delta) % parameters.group.p   
    tmp3 = (h ** sigma2 * zeta2 ** delta) % parameters.group.p

    rhs = parameters.group.hash(zeta1, tmp1, tmp2, tmp3, m)

    return ((pi+delta) == rhs)        
    
def credential_tracing(xiv, xt, zeta1, parameters):
    cred = (xiv ** xt) % parameters.group.p
    return cred == zeta1

def identity_tracing(zeta1, xt, xiv, parameters):
    identity = (zeta1 ** (1 / xt)) % parameters.group.p
    return identity == xiv

if __name__ == '__main__':
    kappa = 1024
    
    m = b'my msg'
    
    # prepare the params of 'p', 'q', 'g'
    params = initialization(kappa)
    # get the tracer 's public key 
    tracerKeypair = tracer_choose_keypair(params)
    tkey = tracerKeypair.yt    
    xt = tracerKeypair.xt
    
    issuer = Issuer(params,tkey)
    # get the hash 
    issuer.start()
    
    user = User(params, issuer.IssuerKeypair.y,tkey)    
    user.start()

    zu, xi = user.protocol_one()    
    z1, a, b1, b2 = issuer.protocol_two(zu,xi)    
    e = user.protocol_three(z1, a, b1, b2, m)    
    r, c, s1, s2, d = issuer.protocol_four(e)    
    roi, pi, sigma1, sigma2, delta = user.protocol_five(r, c, s1, s2, d)
    
    try:
        # p has proper form
        assert (params.group.p - 1) % params.group.q == 0
        # requirement to use this F
        assert ((params.group.p - 1) % params.group.q**2) != 0
        # g has proper form
        assert (params.g ** params.group.q) % params.group.p == 1
        # z is in g
        assert (user.z ** params.group.q) % params.group.p == 1
        # signature works
        assert verify(roi, pi, sigma1, sigma2, delta, params, m, user.y, user.zeta1,user.zeta2, user.z)
        
        assert credential_tracing(issuer.xiv, xt, user.zeta1, params)
        
        assert identity_tracing(user.zeta1, xt, issuer.xiv, params)

    except AssertionError:
        _, _, tb = sys.exc_info()
        traceback.print_tb(tb) # Fixed format
        tb_info = traceback.extract_tb(tb)
        filename, line, func, text = tb_info[-1]
    
        print('An error occurred on line {} in statement {}'.format(line, text))
        exit(1)