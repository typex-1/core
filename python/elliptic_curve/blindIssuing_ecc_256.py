from charm.toolbox.ecgroup import ECGroup,G,ZR
from charm.toolbox.eccurve import secp256k1
from collections import namedtuple

import traceback
import sys

Parameters = namedtuple('Parameters', ['secp', 'group', 'g', 'h'])
IssuerKeypair = namedtuple('IssuerKeypair', ['x', 'y', 'parameters'])
UserKeypair = namedtuple('UserKeypair', ['gamma', 'xi', 'parameters'])
TracerKeypair = namedtuple('TracerKeypair', ['xt', 'yt', 'parameters'])

def initialization(kappa):
    group = ECGroup(kappa)
    g, h = group.random(G), group.random(G)
    parameters = Parameters(kappa, group, g, h)
    return parameters

def tracer_choose_keypair(parameters):
  xt = parameters.group.random(ZR)
  yt = parameters.g ** xt
  # print(xt, yt ,parameters.g)
  print(parameters.g)
  print(xt)
  print(yt)
  # print(parameters.group.order())

  return TracerKeypair(xt, yt, parameters)

def user_choose_keypair(parameters):
  gamma = parameters.group.random(ZR)
  xi = parameters.g ** gamma
  return UserKeypair(gamma, xi, parameters)

def gnerate_common_z(parameters, y):
  return parameters.group.hash((parameters.g, parameters.h, y), G)

### Protocol stuff ###
class Issuer:
    '''Issuer S from the paper'''
    def __init__(self, parameters, tkey):
        x = parameters.group.random(ZR)
        y = parameters.g ** x

        self.IssuerKeypair = IssuerKeypair(x, y, parameters)
        self.tkey = tkey

    def start(self):
      self.z = gnerate_common_z(self.IssuerKeypair.parameters, self.IssuerKeypair.y)

    def protocol_two(self,z_u,xi):
      group = self.IssuerKeypair.parameters.group
      v = group.random(ZR)
      self.xiv = xi ** v
      z1 = self.tkey ** v
      z2 = z_u / z1

      self.u, self.d, self.s1, self.s2  = (group.random(ZR) for i in range(4))

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
        self.t1, self.t2, self.t3, self.t4, self.t5 = (self.parameters.group.random(ZR) for i in range(5))
        self.z = gnerate_common_z(self.parameters, self.y)

    def protocol_one(self):
        z_u = self.z ** (self.UserKeypair.gamma ** -1)
        return (z_u, self.UserKeypair.xi)

    def protocol_three(self, z1, a, b1, b2, m):
        self.zeta1 = z1 ** self.UserKeypair.gamma
        self.zeta2 = self.z / self.zeta1
        

        alpha = (a * (self.parameters.g ** self.t1) * (self.y ** self.t2))
        beta1 = ((b1 ** self.UserKeypair.gamma) * (self.parameters.g ** self.t3) * (self.zeta1 ** self.t5))
        beta2 = ((b2 ** self.UserKeypair.gamma) * (self.parameters.h ** self.t4) * (self.zeta2 ** self.t5))
        epsion = self.parameters.group.hash((self.zeta1, alpha, beta1, beta2, m),ZR)
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

    tmp1 = ((g ** roi) * (y ** pi)) 
    tmp2 = (g ** sigma1 * zeta1 ** delta) 
    tmp3 = (h ** sigma2 * zeta2 ** delta) 

    rhs = parameters.group.hash((zeta1, tmp1, tmp2, tmp3, m),ZR)

    return ((pi+delta) == rhs)        
    
def credential_tracing(xiv, xt, zeta1, parameters):
    cred = (xiv ** xt) 
    return cred == zeta1

def identity_tracing(zeta1, xt, xiv, parameters):
    identity = (zeta1 ** (xt ** -1)) 
    return identity == xiv


if __name__ == '__main__':
  m = b'my msg'

  params = initialization(secp256k1)
  tracerKeypair = tracer_choose_keypair(params)

  tkey = tracerKeypair.yt    
  xt = tracerKeypair.xt

  issuer = Issuer(params, tkey)
  issuer.start()

  user = User(params, issuer.IssuerKeypair.y,tkey)    
  user.start()

  zu, xi = user.protocol_one()
  z1, a, b1, b2 = issuer.protocol_two(zu,xi)
  e = user.protocol_three(z1, a, b1, b2, m)
  r, c, s1, s2, d = issuer.protocol_four(e)
  roi, pi, sigma1, sigma2, delta = user.protocol_five(r, c, s1, s2, d)

  try:
  
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