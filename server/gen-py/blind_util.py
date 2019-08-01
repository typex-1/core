from charm.toolbox.ecgroup import ECGroup,G,ZR
from charm.toolbox.eccurve import secp256k1, secp192k1, secp160k1


def point2Obj(x, group):
  import binascii
  temp_str = hex(x)[2:]
  dict_ecc = {708: 42,
             711: 48,
             714: 64}
  temp_str = (dict_ecc[group.groupType()] - len(temp_str)) * '0' + temp_str  
  return group.encode(binascii.a2b_hex(temp_str), include_ctr=True)

security_dict = {
  '256' : secp256k1,
  '192' : secp192k1,
  '160' : secp160k1
}

def initHandler(kappa):
  group = ECGroup(kappa)
  g, h = group.random(G), group.random(G)
  x, gamma = group.random(ZR), group.random(ZR)
  y, xi = g ** x, g ** gamma
  z = group.hash((g, h, y), G)

  ret = [g, h,\
         bytes.decode(group.serialize(g)), bytes.decode(group.serialize(h)),\
         x, y, gamma, xi,\
         bytes.decode(group.serialize(y)), bytes.decode(group.serialize(xi)),\
         z, bytes.decode(group.serialize(z))]
  return (str(k) for k in ret)

def issuerHandler(issueparam):
  group = ECGroup(security_dict[issueparam.L])
  g = group.deserialize(str.encode(issueparam.sg))
  h = group.deserialize(str.encode(issueparam.sh))
  # print(issueparam.yt)
  
  #####!!!!!!!!!!!!!!!!!!!!!!!Danger!!!!!!!!!!!!!!#######
  # xt = group.random(ZR)
  # yt = g ** xt
  # print('xt: ----====>>>')
  # print(xt)
  yt = point2Obj(int(issueparam.yt), group)
  #####!!!!!!!!!!!!!!!!!!!!!!!Danger!!!!!!!!!!!!!!#######
  
  gamma = group.init(ZR, int(issueparam.gamma))
  z = group.deserialize(str.encode(issueparam.sz))
  
  zu = z ** (gamma ** -1)
  v, u, d, s1, s2 = (group.random(ZR) for i in range(5))
  t1, t2, t3, t4, t5 = (group.random(ZR) for i in range(5))
  z1 = yt ** v
  z2 = zu /z1
  a = g ** u
  b1 = (g ** s1) * (z1 ** d)
  b2 = (h ** s2) * (z2 ** d)

  ret = [zu, v, u, d, s1, s2, \
         t1, t2, t3, t4, t5, \
         z1, z2, a, b1, b2,\
         bytes.decode(group.serialize(zu)), bytes.decode(group.serialize(z1)), bytes.decode(group.serialize(z2)),\
         bytes.decode(group.serialize(a)), bytes.decode(group.serialize(b1)), bytes.decode(group.serialize(b2))]

  return (str(k)  for k in ret)


def oneHandler(oneParameter):
  
  group = ECGroup(security_dict[oneParameter.L])
  t1 = group.init(ZR, int(oneParameter.t1))
  t2 = group.init(ZR, int(oneParameter.t2))
  t3 = group.init(ZR, int(oneParameter.t3))
  t4 = group.init(ZR, int(oneParameter.t4))
  t5 = group.init(ZR, int(oneParameter.t5))
  gamma = group.init(ZR, int(oneParameter.gamma))
  z1 = group.deserialize(str.encode(oneParameter.sz1))
  z = group.deserialize(str.encode(oneParameter.sz))
  a = group.deserialize(str.encode(oneParameter.sa))
  b1 = group.deserialize(str.encode(oneParameter.sb1))
  b2 = group.deserialize(str.encode(oneParameter.sb2))
  g = group.deserialize(str.encode(oneParameter.sg))
  h = group.deserialize(str.encode(oneParameter.sh))
  y = group.deserialize(str.encode(oneParameter.sy))
  message = oneParameter.M

  d = group.init(ZR, int(oneParameter.d))
  u = group.init(ZR, int(oneParameter.u))
  x = group.init(ZR, int(oneParameter.x))
  s1 = group.init(ZR, int(oneParameter.s1))
  s2 = group.init(ZR, int(oneParameter.s2))

  zeta1 = z1 ** gamma
  zeta2 = z / zeta1
  alpha = a * (g ** t1) * (y ** t2)
  beta1 = (b1 ** gamma) * (g ** t3) * (zeta1 ** t5)
  beta2 = (b2 ** gamma) * (h ** t4) * (zeta2 ** t5)
  epsilon = group.hash((zeta1, alpha, beta1, beta2, message), ZR)
  e = epsilon - t2 - t5

  ####---------------------------------------
  c = e - d
  r = u - c * x
  ####=======================================
  roi = r + t1
  omega = c + t2
  sigma1 = gamma * s1 + t3
  sigma2 = gamma * s2 + t4
  delta = d + t5
  ####----------------------------------------
  xi = group.deserialize(str.encode(oneParameter.sxi))
  v = group.init(ZR, int(oneParameter.v))
  xiv = xi ** v

  ret = [zeta1, zeta2, alpha, beta1, beta2, epsilon, e, c, r, roi, omega, sigma1, sigma2, delta, xiv, bytes.decode(group.serialize(xiv)), bytes.decode(group.serialize(zeta1)), bytes.decode(group.serialize(zeta2))]
  return (str(i) for i in ret)

def twoHandler(twoParameter):
  group = ECGroup(security_dict[twoParameter.L])
  omega = group.init(ZR, int(twoParameter.omega))
  delta = group.init(ZR, int(twoParameter.delta))
  g = group.deserialize(str.encode(twoParameter.sg))
  h = group.deserialize(str.encode(twoParameter.sh))
  y = group.deserialize(str.encode(twoParameter.sy))
  zeta1 = group.deserialize(str.encode(twoParameter.szeta1))
  zeta2 = group.deserialize(str.encode(twoParameter.szeta2))
  roi = group.init(ZR, int(twoParameter.roi))
  sigma1 = group.init(ZR, int(twoParameter.sigma1))
  sigma2 = group.init(ZR, int(twoParameter.sigma2))

  tmp1 = (g ** roi) * (y ** omega)
  tmp2 = (g ** sigma1) * (zeta1 ** delta)
  tmp3 = (h ** sigma2) * (zeta2 ** delta)
  m = twoParameter.m
  return (str(omega + delta), str(group.hash((zeta1, tmp1, tmp2, tmp3, m),ZR)))