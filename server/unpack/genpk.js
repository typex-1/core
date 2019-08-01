
import {default as Web3c} from 'web3c';
import ballot_artifacts from '../build/contracts/AuditTracer.json';
var web3c, account, AuditTracer, contractAddress;

window.get_public_key = async function () {
  try {
    let calculate_public_key = AuditTracer.methods.calculate_public_key();
    await calculate_public_key.send();
    console.log(calculate_public_key);
  
    let public_key = await AuditTracer.methods.get_public_key().call();
    console.log(public_key);

    $("#myicon3").removeClass();
    $("#myicon3").addClass("myicon-tick-checked");
  
    contractAddress = $("#sm_addrsss").text();
  
    $("#publickey-status").removeClass();
    $("#publickey-status").addClass("alert alert-success");
    $("#publickey-status").show()
  
  
    $("#myicon5").removeClass();
    $("#myicon5").addClass("myicon-tick-checked");
  
    $("#myicon6").removeClass();
    $("#myicon6").addClass("myicon-tick-checked");
    
    $("#yt").val("[" + public_key[0] + "," + public_key[1] + "]")
  
    // $("#issueCred").attr("href","http://127.0.0.1/issuing?pk="+public_key[0]+"&contractAddress="+contractAddress);
    // $("#a_issuing").attr("href","http://127.0.0.1/issuing?pk="+public_key[0]+"&contractAddress="+contractAddress);

    $.post('sendyt', {
      'contractAddress' : contractAddress,
      'yt': public_key[0]
    }, (res)=>{
      console.log(res);
    });

  } catch (err) {
    $("#register-status").text("Error Deploying: " + err);
    $("#register-status").removeClass();
    $("#register-status").addClass("alert alert-danger");
    console.log(err);
  }
}

window.register = async function () {
  try {
    let _a = $('#a1').val();
    let _b = $('#b1').val();
    let _p = $('#p1').val();
    let _n = $('#n1').val();
    let _g = $('#g1').val();
    let _gx = _g.substring(1,_g.indexOf(","));
    let _gy = trimStr(_g.substring(_g.indexOf(",")+1, _g.length-1));

    let parameters = AuditTracer.methods.register_parameter(_a,_b,_p,_n,_gx,_gy);
    await  parameters.send();
    //let privatekey = await AuditTracer.methods.get_private_key().call();
    $("#register-status").removeClass();
    $("#register-status").addClass("alert alert-success");
    $("#register-status").show();

    $("#myicon4").removeClass();
    $("#myicon4").addClass("myicon-tick-checked");
    
  } catch (err) {
    $("#register-status").text("Error Deploying: " + err);
    $("#register-status").removeClass();
    $("#register-status").addClass("alert alert-danger");
    console.log(err);
  }
}

window.load = function(){
  console.log("window.ethereum = ", window.ethereum);
  web3c = new Web3c(window.ethereum);

  web3c.eth.getAccounts().then((a) => {
    if (!a.length) {
      $("#check-status").removeClass();
      $("#check-status").addClass("alert alert-danger");
      $("#check-status").text("Please unlock your wallet, and then reload.");
      $("#check-status").show()
      return;
    }
    account = a[0];
    $("#success-deploy-status").css('display','block');
    $("#success-deploy-status").text(account);

    $("#check-status").removeClass();
    $("#check-status").addClass("alert alert-success");
    $("#check-status").show()
  
    $("#ac_addrsss").text(account);
    $("#ac_addrsss").attr("href","https://blockexplorer.oasiscloud.io/address/"+account);
  
    $("#myicon2").removeClass();
    $("#myicon2").addClass("myicon-tick-checked");
    $("#myicon1").removeClass();
    $("#myicon1").addClass("myicon-tick-checked");
  });
}

window.deploy = async function() {

  let protoBallot = new web3c.oasis.Contract(ballot_artifacts.abi, undefined, {from: account});
  
  try {
    let deployMethod = protoBallot.deploy({
      data: ballot_artifacts.bytecode,
      arguments: []
    });
    AuditTracer = await deployMethod.send();
  } catch(e) {
    $("#compile-status").text("Error Deploying: " + e);
    $("#compile-status").removeClass();
    $("#compile-status").addClass("alert alert-danger");
    return;
  }  
  $("#deploy-status").removeClass();
  $("#deploy-status").addClass("alert alert-success");
  $("#deploy-status").show()
  
  $("#compile-status").removeClass();
  $("#compile-status").addClass("alert alert-success");
  $("#compile-status").show()
  
  $("#myicon3").removeClass();
  $("#myicon3").addClass("myicon-tick-checked");
  
  $("#sm_addrsss").text(AuditTracer.options.address);
  $("#sm_addrsss").attr("href","https://blockexplorer.oasiscloud.io/address/"+AuditTracer.options.address+"/transactions");
  
  $("#sm_code").val(ballot_artifacts.bytecode);
  
  logsubs(AuditTracer.options.address);
}

window.logsubs = function(address){
  let subscription = web3c.oasis.subscribe('logs', {
     address: address
  }, function(error, result){
    console.log(result.transactionHash);
    console.log(result);
    
  });
}

window.unlock = function(){
  if (window.ethereum) {
    window.ethereum.enable().then(load).catch((e) => {
      console.error(e);
      $("#error-deploy-status").css('display','block');
      $("#error-deploy-status").text("Error: " + e);
    });
  } else {
    $("#error-deploy-status").css('display','block');
    $("#error-deploy-status").text("Error: Newer version of metamask needed!");
  }
}

window.trimStr = function(str){
  return str.replace(/(^\s*)|(\s*$)/g,"");
}

let setupHandler = (parameter)=>{
  $.post('setup', {'L': parameter}, (res)=>{
    let jdict = JSON.parse(res);
    $('#a1').val(jdict.a);
    $('#b1').val(jdict.b);
    $('#p1').val(jdict.p);
    $('#n1').val(jdict.n);

    $('#a2').val(jdict.a);
    $('#b2').val(jdict.b);
    $('#p2').val(jdict.p);
    $('#n2').val(jdict.n);

    $('#g1').val(jdict.g);
    $('#h1').val(jdict.h);
    $('#g2').val(jdict.g);
    $('#h2').val(jdict.h);
  });
}

window.onload = ()=>{
  setupHandler(256);
  $('#Secp256k1').on('click', ()=>{
    $('#Secp256k1').attr('class','choosItem checked');
    $('#Secp192k1').removeClass('checked');
    setupHandler(256);
  });
  $('#Secp192k1').on('click', ()=>{
    $('#Secp192k1').attr('class','choosItem checked');
    $('#Secp256k1').removeClass('checked');
    setupHandler(192);
  });

  $('#issuerkey').on('click', ()=>{
    $.post('issuerkey', {}, (res)=>{
      let jdict = JSON.parse(res);
      $('#x').val(jdict.x);  
      $('#y').val(jdict.y);
      $('#z1').val(jdict.z);
    })
  });

  $('#userkey').on('click', ()=>{
    $.post('userkey', {}, (res)=>{
      let jdict = JSON.parse(res);
      $('#gamma').val(jdict.gamma);
      $('#xi').val(jdict.xi);
      $('#z2').val(jdict.z);
    })
  });
  $('#confirm').on('click', ()=>{
    Web3c.Promise.then(unlock);
  });
}