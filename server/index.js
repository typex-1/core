const express = require('express');
const path = require('path');
const cookieParser = require('cookie-parser');
const session = require('express-session');
const bodyParser = require('body-parser');

//--------------------------------------------------------------------------
const thrift = require('thrift');
const eccrpc = require('./gen-nodejs/setup.js');
const ttypes = require('./gen-nodejs/ecc_types.js');
const options = {
  transport: thrift.TBUfferedTransport,
  protocol: thrift.TJSONProtocol,
  headers: {"Connection": "close"},
  https: false
};

let connection = thrift.createHttpConnection('localhost', 2333, options);
let client = thrift.createHttpClient(eccrpc, connection);
connection.on('error', (err)=>{
  console.error(err);
})
//============================================================================

let app = express();
app.use(cookieParser('mysession'));
app.use(session({
  secret: 'mysession',
  resave: true,
  saveUninitialized: true
}));
app.use(express.static(path.join(__dirname, 'static')));
app.use(bodyParser.urlencoded({
  extended: true
}));
app.set('views', path.join(__dirname, 'static/views'))
app.set('view engine', 'ejs');

app.get('/', (req, res)=>{
  res.render('index.ejs')
});

app.get('/index', (req, res)=>{
  res.redirect('/');
});

app.post('/setup', (req, res)=>{
  req.session.L = req.body.L;
  let chunk = new ttypes.InitParame({
    'L': req.body.L
  });
  let ecctype = {
    '192': {
      'a': '0',
      'b': '3',
      'p': '6277101735386680763835789423207666416102355444459739541047',
      'n': '6277101735386680763835789423061264271957123915200845512077'
    },
    '256': {
      'a': '0',
      'b': '7',
      'p': '115792089237316195423570985008687907853269984665640564039457584007908834671663',
      'n': '115792089237316195423570985008687907852837564279074904382605163141518161494337'
    }
  };
  client.init(chunk,(err, ret)=>{
    req.session.pp = ret;
    res.json(JSON.stringify({
      'g': ret.g,
      'h': ret.h,
      'a': ecctype[req.session.L].a,
      'b': ecctype[req.session.L].b,
      'p': ecctype[req.session.L].p,
      'n': ecctype[req.session.L].n
    }));
  });
});

app.post('/sendyt', (req, res)=>{
  req.session.address = req.body.contractAddress;
  req.session.yt = req.body.yt;
  res.send('I am fine, thank you');
});

app.get('/issuing', (req, res)=>{  
  if(!req.session.yt){
    res.redirect('/');
  } else{
    let chunk = new ttypes.IssueParame({
      'L': req.session.L,
      'sg': req.session.pp.sg,
      'sh': req.session.pp.sh,
      'yt': req.session.yt,    
      'gamma': req.session.pp.gamma,
      'sz': req.session.pp.sz
    });

    client.issue(chunk,(err, ret)=>{
      req.session.issres = ret;
      res.render('issuing.ejs', {
        'gamma': req.session.pp.gamma,
        'xi': req.session.pp.xi,
        'z': req.session.pp.z,
        'zu': ret.zu,
        'v': ret.v,
        'u': ret.u,
        's1': ret.s1,
        's2': ret.s2,
        'd': ret.d,
        't1': ret.t1,
        't2': ret.t2,
        't3': ret.t3,
        't4': ret.t4,
        't5': ret.t5,
        'y': req.session.pp.y
      });
    });
  }
  
  
});

app.post('/issuerkey', (req, res)=>{
  // console.log(req.session.pp);
  res.json(JSON.stringify({
    'x': req.session.pp.x,
    'y': req.session.pp.y,
    'z': req.session.pp.z
  }));
});

app.post('/userkey', (req, res)=>{
  res.json(JSON.stringify({
    'gamma' : req.session.pp.gamma,
    'xi' : req.session.pp.xi,
    'z' : req.session.pp.z
  }));
});

app.post('/issuerExecuteTwo', (req, res)=>{
  res.json(JSON.stringify({
    'z1': req.session.issres.z1,
    'z2': req.session.issres.z2,
    'a': req.session.issres.a,
    'b1': req.session.issres.b1,
    'b2': req.session.issres.b2
  }));
});

app.post('/userExecuteThree', (req,res)=>{
  req.session.m = req.body.m;
  let chunk = new ttypes.ProtocolOne({
    't1': req.session.issres.t1,
    't2': req.session.issres.t2,
    't3': req.session.issres.t3,
    't4': req.session.issres.t4,
    't5': req.session.issres.t5,
    'gamma': req.session.pp.gamma,
    'sz1': req.session.issres.sz1,
    'sz': req.session.pp.sz,
    'sa': req.session.issres.sa,
    'sb1': req.session.issres.sb1,
    'sb2': req.session.issres.sb2,
    'sg': req.session.pp.sg,
    'sh': req.session.pp.sh,
    'sy': req.session.pp.sy,
    'M': req.body.m,
    'L': req.session.L,
    'd': req.session.issres.d,
    'u': req.session.issres.u,
    'x': req.session.pp.x,
    's1': req.session.issres.s1,
    's2': req.session.issres.s2,
    'v': req.session.issres.v,
    'sxi': req.session.pp.sxi
  });
  client.execOne(chunk,(err, ret)=>{
    req.session.one = ret;
    res.json(JSON.stringify(ret));    
  });
});

app.post('/issuerExecuteFour', (req, res)=>{
  res.json(JSON.stringify({
    'c': req.session.one.c,
    'r': req.session.one.r
  }));
});

app.post('/userExecuteFive', (req, res)=>{
  res.json(JSON.stringify({
    'roi': req.session.one.roi,
    'omega': req.session.one.omega,
    'sigma1': req.session.one.sigma1,
    'sigma2': req.session.one.sigma2,
    'delta': req.session.one.omega
  }));
});

app.post('/issuerExecuteSix', (req, res)=>{
  res.json(JSON.stringify({
    'username': req.session.m.split('|')[0],
    'xi': req.session.pp.xi,
    'xiv': req.session.one.xiv
  }));
});

app.get('/verifying', (req, res)=>{
  if(!req.session.m){
    res.redirect('/');
  }else{
    information = req.session.m.split('|');
    padding = {
      'y': req.session.pp.y,
      'zeta1': req.session.one.zeta1,
      'roi': req.session.one.roi,
      'omega': req.session.one.omega,
      'sigma1': req.session.one.sigma1,
      'sigma2': req.session.one.sigma2,
      'delta': req.session.one.delta,
      'name': information[0],
      'age': information[1],
      'bir': information[2],
      'nation': information[3],
      'gender': information[4], 
      'address': information[5]
    };
    res.render('verifying.ejs', padding);
  }
});

app.post('/verifyCred', (req, res)=>{
  let chunk = new ttypes.ProtocolTwo({
    'omega': req.session.one.omega,
    'delta': req.session.one.delta,
    'L': req.session.L,
    'sg': req.session.pp.sg,
    'roi': req.session.one.roi,
    'sy': req.session.pp.sy,
    'sigma1': req.session.one.sigma1,
    'sigma2': req.session.one.sigma2,
    'szeta1': req.session.one.szeta1,
    'szeta2': req.session.one.szeta2,
    'sh': req.session.pp.sh,
    'm': req.session.m
  });
  client.execTwo(chunk,(err, ret)=>{
    // console.log(ret);
    res.json(JSON.stringify(ret));
  });
});

app.get('/tracing', (req, res)=>{
  if(!req.session.one){
    res.redirect('/');
  }else{
    res.render('tracing.ejs', {
      'xiv': req.session.one.xiv,
      'zeta1': req.session.one.zeta1,
      'smadress': req.session.address
    });
  }  
});

let server = app.listen(8080, ()=>{
  let host = server.address().address;
  let port = server.address().port;

  console.log("Running at " + host + ": " + port);
})

// JSONRPC.loadRouter(path.join(__dirname, ))