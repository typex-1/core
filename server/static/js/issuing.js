window.onload = ()=>{
  $('#issuerExecuteTwo').on('click', ()=>{
    $.post('issuerExecuteTwo', {}, (res)=>{
      let jdict = JSON.parse(res);
      $('#z1').val(jdict.z1);
      $('#z2').val(jdict.z2);
      $('#a').val(jdict.a);
      $('#b1').val(jdict.b1);
      $('#b2').val(jdict.b2);
    });
  });

  $('#userExecuteThree').on('click', ()=>{
    $('#ca-popup-1').css('display', 'block');
  });

  $('.ca-exout').on('click', ()=>{
    $('#ca-popup-1').css('display', 'none');
  });

  $('#submitmsg').on('click', ()=>{
    retList = new Array($('#name1').val(), $('#age1').val(), $('#birthday1').val(), $('#nationality1').val(), $('#gender1').val(), $('#address1').val());
    retStr = retList.join('|');
    $('#m').val(retStr);
    $.post('userExecuteThree', {'m': retStr}, (res)=>{
      let jdict = JSON.parse(res);
      $('#zeta1').val(jdict.zeta1);
      $('#zeta_1').val(jdict.zeta1);
      $('#zeta2').val(jdict.zeta2);
      $('#alpha').val(jdict.alpha);
      $('#beta1').val(jdict.beta1);
      $('#beta2').val(jdict.beta2);
      $('#epsilon').val(jdict.epsilon);
      $('#e').val(jdict.e);
      window.setTimeout(()=>{
        $('#ca-popup-1').css('display', 'none');
      }, 1000);      
    });
  });

  $('#issuerExecuteFour').on('click', ()=>{
    $.post('issuerExecuteFour', {}, (res)=>{
      let jdcit = JSON.parse(res);
      $('#c').val(jdcit.c);
      $('#r').val(jdcit.r);
    })
  });

  $('#userExecuteFive').on('click', ()=>{
    $.post('userExecuteFive', {}, (res)=>{
      let jdict = JSON.parse(res);
      $('#rho').val(jdict.roi);
      $('#omega').val(jdict.omega);
      $('#sigma1').val(jdict.sigma1);
      $('#sigma2').val(jdict.sigma2);
      $('#delta').val(jdict.delta);
    });
  });

  $('#issuerExecuteSix').on('click', ()=>{
    $.post('issuerExecuteSix', {}, (res)=>{
      jdict = JSON.parse(res);
      $('#username').val(jdict.username);
      $('#username1').val(jdict.username);      
      $('#upk').val(jdict.xi);
      $('#identity').val(jdict.xiv);
    });
  });
}