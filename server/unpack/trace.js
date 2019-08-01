import { default as Web3c } from 'web3c';
import ballot_artifacts from '../build/contracts/AuditTracer.json';
var web3c, account, AuditTracer, contractAddress;

window.credential_tracing = async function() {
  try {
    //let xi = getUrlParameter('xi');
    let xiupsilon = $('#xiupsilon').val();
    let xiupsilon_gx = xiupsilon.substring(1, xiupsilon.indexOf(","));
    let xiupsilon_gy = trimStr(xiupsilon.substring(xiupsilon.indexOf(",") + 1, xiupsilon.length - 1));
    console.log(xiupsilon_gy);

    let credential = AuditTracer.methods.credential_calculating(xiupsilon_gx, xiupsilon_gy);
    await credential.send();
    let credential_zeta1 = await AuditTracer.methods.credential_tracing().call();
    $("#res_zeta_1").val("[" + credential_zeta1[0] + "," + credential_zeta1[1] + "]")
  } catch (err) {
    $("#vote-status-alert").text("Error: " + err);
    console.log(err);
  }
}

window.identity_tracing = async function() {
  try {
    let zeta1 = $('#zeta_1').val();
    let zeta1_gx = zeta1.substring(1, zeta1.indexOf(","))
    let zeta1_gy = zeta1.substring(zeta1.indexOf(",") + 2, zeta1.length - 1)
    console.log(zeta1_gx)
    console.log(zeta1_gy)
    let identity = AuditTracer.methods.identity_calculating(zeta1_gx, zeta1_gy);
    await identity.send();
    let identity_xiupsilon = await AuditTracer.methods.identity_tracing().call();
    $("#credential_xiupsilon").val("[" + identity_xiupsilon[0] + "," + identity_xiupsilon[1] + "]")
  } catch (err) {
    $("#vote-status-alert").text("Error: " + err);
    console.log(err);
  }
}

window.trimStr = function(str){
  return str.replace(/(^\s*)|(\s*$)/g,"");
}

window.onload = ()=>{
  let smddrsss = $('#smadress').text();
  let smdiv = "<div class='alert alert-success' style='width: 98%'>Your tracing smart address is deployed at <a href = 'https://blockexplorer.oasiscloud.io/address/"+smddrsss+"/transactions' target = '_blank'>"+smddrsss+"</a></div>"
    $("#smhtml").html(smdiv);
  Web3c.Promise.then(unlock);
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
    contractAddress = $('#smadress').text();
    runAt(contractAddress);
  });
}

window.runAt = async function(address) {
  console.log("running ballot at ", address);
  AuditTracer = new web3c.oasis.Contract(ballot_artifacts.abi, address, {from: account});
  logsubs(address)
}

window.logsubs = function(address){
  let subscription = web3c.oasis.subscribe('logs', {
   //fromBlock: 1,
   //toBlock: "latest",
     address: address
   //topics: [sha3, topic_1] 
  }, function(error, result){
    if (!error){
      //alert(result.transactionHash)
      if($("#tracelog")){
        var log = "<div class='node'><h3></h3><p> Tracing logs: your tracing activity has been recorded permanently in transaction <input value = '"+result.transactionHash+"'></input> and auditable to every entity. Please check <a href = 'https://blockexplorer.oasiscloud.io/tx/"+result.transactionHash+"/internal_transactions' target='_blank'>here</a> for more detail. <span class='myicon-tick-checked'></span> </p></div>"
        $("#tracelog").append(log)
      }
      console.log(result.transactionHash);
      console.log(result)
    }
  });
}