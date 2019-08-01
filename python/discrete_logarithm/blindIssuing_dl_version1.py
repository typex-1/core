import os
from collections import namedtuple
import hashlib
import sys
import traceback

Parameters = namedtuple('Parameters', ['L', 'N', 'p', 'q', 'g', 'h'])
IssuerKeypair = namedtuple('IssuerKeypair', ['x', 'y', 'parameters'])
UserKeypair = namedtuple('UserKeypair', ['gamma', 'xi', 'parameters'])
TracerKeypair = namedtuple('TracerKeypair', ['xt', 'yt', 'parameters'])

### Math helper functions ###
def rand_int(nbits):
    if nbits % 8 != 0:
        raise ValueError("nbits must be divisible by 8 so it can be broken"
                         " into bytes.")
    return int.from_bytes(os.urandom(nbits//8), byteorder='little')


def rand_less_than(upper_bound, nbits):
    '''This could be smarter.'''
    while True:
        r = rand_int(nbits)
        if r < upper_bound:
            return r


def fermat_test(p, nbits):
    '''Fermat primality test'''
    for _ in range(5):
        a = rand_less_than(p, nbits)
        if not pow(a, p - 1, p) == 1:
            return False
    return True


def miller_rabin_test(p, nbits):
    '''Miller-Rabin primality test'''
    k = 5  # accuracy parameter, this should be turned up in practice
    r = 1
    while (pow(2, r) & p) != pow(2, r):
        r += 1
    d = p // pow(2, r)
    for _ in range(k):
        a = rand_less_than(p - 2, nbits)
        x = pow(a, d, p)
        if x == 1 or x == p - 1:
            continue
        for _ in range(r - 1):
            x = pow(x, 2, p)
            if x == 1:
                return False
            if x == p - 1:
                break
        else:
            return False
    return True

def prime_test(p, nbits):
    return miller_rabin_test(p, nbits)


def rand_prime(nbits):
    is_prime = False
    while not is_prime:
        p = rand_int(nbits)
        is_prime = prime_test(p, nbits)
    return p


### DSA functions ###
def choose_q(N):
    return rand_prime(N)


def choose_p(L, N, q):
    k = L - N
    is_prime = False
    while not is_prime:
        p = (q*rand_int(k)) + 1
        is_prime = prime_test(p, L)
    return p


def choose_g(L, N, p, q):
    h = 2
    while True:
        g = pow(h, (p - 1)//q, p)
        if pow(g, q, p) == 1:
            return g
        h = rand_less_than(p, L)


def choose_parameters(L, N):
    '''Returns DSA parameters p, q, g'''
    q = choose_q(N)
    p = choose_p(L, N, q)
    #p1 = choose_p(L, N, q)
    
    g = choose_g(L, N, p, q)
    #h = choose_g(L, N, p1, q)
    
    print(103)
    print(q)
    print(p)
    print(g)
    
    h = g
    
    return Parameters(L, N, p, q, g, h)

def issuer_choose_keypair(parameters):
    x = rand_less_than(parameters.q, parameters.N)
    y = pow(parameters.g, x, parameters.p)
    return IssuerKeypair(x,y,parameters)

def user_choose_keypair(parameters):
    gamma = rand_less_than(parameters.q, parameters.N)
    xi = pow(parameters.g, gamma, parameters.p)
    return UserKeypair(gamma, xi, parameters)

def tracer_choose_keypair(parameters):
    xt = rand_less_than(parameters.q, parameters.N)
    yt = pow(parameters.g, xt, parameters.p)
    return TracerKeypair(xt,yt,parameters)

def gnerate_common_z(parameters,h,y):
    h_hash = full_domain_hash(int_to_bytes(parameters.p) + int_to_bytes(parameters.q) + int_to_bytes(parameters.g) +
                                int_to_bytes(h) + int_to_bytes(y), parameters.L)
    i = int.from_bytes(h_hash, byteorder='little') % parameters.p
    return pow(i, (parameters.p - 1)//parameters.q, parameters.p)

def int_to_bytes(in_int):
    i = in_int
    byte_length = ((i).bit_length() + 7) // 8
    return i.to_bytes(byte_length, 'little')

### Hashing functions ###
def do_hash(data):
    '''hash helper'''
    h = hashlib.sha256()
    h.update(data)
    return h.digest()

def full_domain_hash(data, target_length):
    tl_bytes = target_length // 8
    digest_size = hashlib.sha256().digest_size
    ncycles = (tl_bytes // digest_size) + 1
    out = bytearray()
    for i in range(ncycles):
        out.extend(do_hash(data + int_to_bytes(i)))
    return bytes(out[:tl_bytes])

def digest(data, parameters):
    '''F hash function from paper'''
    hashed = full_domain_hash(data, parameters.L)
    i = int.from_bytes(hashed, byteorder='little') % parameters.p
    return pow(i, (parameters.p - 1)//parameters.q, parameters.p)

### Protocol stuff ###
class Issuer:
    '''Issuer S from the paper'''
    def __init__(self, parameters,tkey):
        self.parameters = parameters
        self.L, self.N, self.p, self.q, self.g,self.h = tuple(parameters)
        self.IssuerKeypair = issuer_choose_keypair(self.parameters)
        self.tkey = tkey
        #self.IssuerKeypair = IssuerKeypair(x,y,parameters)
        
    def start(self):
        self.z = gnerate_common_z(self.parameters, self.h, self.IssuerKeypair.y)

    def protocol_two(self,zu):
       
        self.upsilon = rand_less_than(self.q, self.N)
        
        self.z1 = pow(self.tkey, self.upsilon,self.p)
        
        self.mu = rand_less_than(self.q, self.N)
        self.s1 = rand_less_than(self.q, self.N)
        self.s2 = rand_less_than(self.q, self.N)
        self.d = rand_less_than(self.q, self.N)
        
        self.a = pow(self.g, self.mu,self.p)
        
        self.b1 = (pow(self.g, self.s1, self.p) *
                  pow(self.z1, self.d, self.p)) % self.p
        
        #zud = pow(zu, self.d,self.p)
        #nz1d = pow(pow(self.z1,(self.q)-1,self.p), self.d, self.p)
        self.z2 = (zu * pow(self.z1,(self.q)-1,self.p)) % self.p
        
        self.b2 = (pow(self.h, self.s2, self.p) *
                   pow(self.z2, self.d, self.p)
                   ) % self.p
                   
        #print((self.z2 * self.z1) % self.p == zu)
        
        return self.z1, self.a, self.b1, self.b2

    def protocol_four(self, e):
        self.c = (e - self.d) % self.q
        self.r = (self.mu - (self.c * self.IssuerKeypair.x)) % self.q
        return self.r, self.c, self.s1, self.s2, self.d


class User:
    '''User U from the paper'''
    def __init__(self, parameters,pubkey,tkey):
        self.parameters = parameters
        self.L, self.N, self.p, self.q, self.g, self.h = tuple(parameters)
        self.UserKeypair = user_choose_keypair(self.parameters)
        self.y = pubkey
        self.tkey = tkey
        
    def start(self):
        ts = [rand_less_than(self.q, self.N) for _ in range(5)]
        self.t1, self.t2, self.t3, self.t4,self.t5 = ts
        
        self.z = gnerate_common_z(self.parameters, self.h, self.y)
        
    def protocol_one(self):
        
        ngama = pow(self.UserKeypair.gamma, self.q - 2, self.q)
        
        zu = pow(self.z, ngama, self.p)
        
        #print((ngama * self.UserKeypair.gamma) % self.q)
        
        return zu,self.UserKeypair.xi

    def protocol_three(self, z1, a, b1, b2, m):
        
        self.zeta1 = pow(z1, self.UserKeypair.gamma, self.p)
        
        #nzeta1 = pow(self.zeta1, self.p - 2,self.p)
        #self.zeta2 = self.zeta1 * nzeta1 % self.p
        
        alpha = (a * pow(self.g, self.t1, self.p) *
                 pow(self.y, self.t2, self.p)) % self.p
          
        beta1 = (pow(b1, self.UserKeypair.gamma, self.p) *
                pow(self.g, self.t3, self.p) *
                pow(self.zeta1, self.t5, self.p)
                ) % self.p
        
        #zt5 = pow(self.z, self.t5,self.p)
        #nzeta1t5 = pow(pow(self.zeta1,((self.q)-1),self.p), self.t5, self.p)
        
        self.zeta2 = (self.z * pow(self.zeta1,(self.q)-1,self.p)) % self.p
        
        self.beta2 = (pow(b2, self.UserKeypair.gamma, self.p) *
                pow(self.h, self.t4, self.p) *
                pow(self.zeta2,self.t5,self.p)
                ) % self.p
        
        #print(self.beta2)
        
#         self.beta2 = (pow(b2, self.UserKeypair.gamma, self.p) *
#                 pow(self.h, self.t4, self.p)
#                 ) % self.p

        e_bytes = bytearray()
        for v in (self.zeta1, alpha, beta1, self.beta2):
            e_bytes.extend(int_to_bytes(v))
       
        e_bytes.extend(m)

        epsilon = int.from_bytes(full_domain_hash(e_bytes, self.N), 'little')
        
        e = (epsilon - self.t2 - self.t5) % self.q
        
        return e

    def protocol_five(self, r, c, s1,s2, d):
        rho = (r + self.t1) % self.q
        omega = (c + self.t2) % self.q
        sigma1 = (s1 * self.UserKeypair.gamma + self.t3) % self.q
        sigma2 = (s2 * self.UserKeypair.gamma + self.t4) % self.q
        delta = (d + self.t5) % self.q
#         delta = (d) % self.q
        return rho, omega, sigma1, sigma2, delta

def verify(rho, omega, delta, sigma1,sigma2, h, m, y, zeta1, zeta2,z,parameters):
    '''Signature verification'''
    lhs = int_to_bytes((omega + delta) % parameters.q)
    
    rhs_one = zeta1
    
    rhs_two = (pow(parameters.g, rho, parameters.p) *
               pow(y, omega, parameters.p)) % parameters.p
               
    rhs_three = (pow(parameters.g, sigma1, parameters.p) *
               pow(zeta1, delta, parameters.p)) % parameters.p
    
    
    #zdelta = pow(z, delta, parameters.p)
    #zeta1delta = pow(pow(zeta1, ((parameters.q)-1) ,parameters.p), delta, parameters.p)  
    
    rhs_four = (pow(h, sigma2, parameters.p) *
                pow(zeta2,delta,parameters.p)
               ) % parameters.p
    
    #print(rhs_four)
#   print(rhs_four % user.beta2)     
    #print((((zdelta * zeta1delta) % parameters.p * zeta1)) % parameters.p  == z)
  
    rhs_hash = full_domain_hash(int_to_bytes(rhs_one) + int_to_bytes(rhs_two) +
                                int_to_bytes(rhs_three) + int_to_bytes(rhs_four) + m, parameters.N)
    
    rhs = int_to_bytes(int.from_bytes(rhs_hash, 'little') % parameters.q)
#     print(299)
#     print(rhs_four)
    
    #print((zeta2 * zeta1) % parameters.p == z )
    
    return (rhs == lhs)

def credential_tracing(xi, upsilon, xt, parameters):
    cred = pow(xi,upsilon * xt, parameters.p)
    #print(cred)
    #print(user.zeta1)
    return cred == user.zeta1

def identity_tracing(zeta1, xt, upsilon ,parameters):
    
    nxt = pow(xt, parameters.q - 2, parameters.q)
    ide = pow(zeta1, nxt, parameters.p)
    print(ide)
    print(pow(user.UserKeypair.xi, upsilon, parameters.p))
    #print(user.zeta1)
    return ide == pow(user.UserKeypair.xi, upsilon, parameters.p)

if __name__ == '__main__':
    L, N = 1024, 160
    
    m = b'my msg'
    
    # prepare the params of 'p', 'q', 'g'
    params = choose_parameters(L, N)
    
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
    
    z1, a, b1, b2 = issuer.protocol_two(zu)
    
    e = user.protocol_three(z1, a, b1, b2, m)
    
    r, c, s1, s2, d = issuer.protocol_four(e)
    
    rho, omega, sigma1, sigma2, delta = user.protocol_five(r, c, s1, s2, d)
    
    #print((((pow(user.h, ((user.UserKeypair.gamma)*s2) + user.t4, user.p))* pow(issuer.z2, (user.UserKeypair.gamma) * d, user.p))) % user.p == 
    #((pow(b2, user.UserKeypair.gamma, user.p)) * pow(user.h, user.t4, user.p)) % user.p
    #)
    #value1 = (pow(b2, user.UserKeypair.gamma, user.p) * pow(user.h, user.t4, user.p)) % user.p
    #value2 = (pow(user.h, sigma2, user.p) * pow(user.zeta2, d, user.p)) % user.p 
    
    #print(value1 == value2)
    
    #credential_tracing(xi, issuer.upsilon, xt, params)
    
#     print( % user.p == ( % user.p)) 
    
#     print((((pow(user.h, ((user.UserKeypair.gamma)*s2) + user.t4, user.p))* pow(issuer.z2, (user.UserKeypair.gamma) * d, user.p))) % user.p)
    
    try:
        # p has proper form
        assert (params.p - 1) % params.q == 0
        # requirement to use this F
        assert ((params.p - 1) % params.q**2) != 0
        # test params are prime
        assert prime_test(params.p, params.L)
        assert prime_test(params.q, params.N)
        # g has proper form
        assert pow(params.g, params.q, params.p) == 1
        # z is in g
        assert pow(user.z, params.q, params.p) == 1
        # signature works
        assert verify(rho, omega, delta, sigma1, sigma2, user.h, m, user.y, user.zeta1,user.zeta2, user.z, params)
        
        assert credential_tracing(xi, issuer.upsilon, xt, params)
        
        assert identity_tracing(user.zeta1, xt, issuer.upsilon ,params)

    except AssertionError:
        _, _, tb = sys.exc_info()
        traceback.print_tb(tb) # Fixed format
        tb_info = traceback.extract_tb(tb)
        filename, line, func, text = tb_info[-1]
    
        print('An error occurred on line {} in statement {}'.format(line, text))
        exit(1)
