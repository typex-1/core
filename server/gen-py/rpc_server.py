import json

from ecc import setup
from blind_util import initHandler, oneHandler, twoHandler, issuerHandler
from charm.toolbox.eccurve import secp256k1, secp192k1, secp160k1

from thrift.protocol import TJSONProtocol
from thrift.server import THttpServer

stus = {}

security_dict = {
  '256' : secp256k1,
  '192' : secp192k1,
  '160' : secp160k1
}

class TestHandler:
  def init(self, initList):
    print(initList)
    params = initHandler(security_dict[initList.L])
    ret = setup.PublicParame(*params)
    return ret

  def issue(self, issueparam):
    handret = issuerHandler(issueparam)
    return setup.RetIssue(*handret)

  def execOne(self, paraOne):
    handret = oneHandler(paraOne)
    return setup.ReturnOne(*handret)

  def execTwo(self, paratwo):
    handret = twoHandler(paratwo)
    return setup.ReturnTwo(*handret)
    
processor = setup.Processor(TestHandler())
pfactory = TJSONProtocol.TJSONProtocolFactory()
server = THttpServer.THttpServer(processor, ("127.0.0.1", 2333), pfactory)
print("Starting thrift server in python...")
server.serve()