## Introduction

This is a light-weight server for fair blind signature with privacy-preserving smart constract. You can find the complete project at [blockchain-crypto-lab](https://github.com/blockchain-crypto-lab). All rights reserved by `Anonymous Team`.

## Quick Start

We suggest using docker to deploy.

```
docker pull aowatchsea/blindca
docker run -t -i -p 443:8080 aowatchsea/blindca
start.sh
```

Then open http://localhost:8080 in your browser, just enjoy~!

> Firefox browser is recommended in this project.

---

If you want to use the source codes, please ensure that you have installed the following dependencies:

- [charm](https://github.com/JHUISI/charm)
- [metamask](https://metamask.io/)
- [thrift python version](https://github.com/apache/thrift)
- [truffle](https://github.com/trufflesuite/truffle)

```
git clone https://github.com/liu246542/blindCA
cd /root/blindCA/
npm install
truffle compile
thrift --gen py ./ecc.thrift
thrift --gen js:node ./ecc.thrift
webpack
chmod +x ./start.sh
./start.sh
```
