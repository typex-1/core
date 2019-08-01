window.onload = ()=>{
  $('#verifyCred').on('click', ()=>{
    $.post('verifyCred', {}, (res)=>{
      jdict = JSON.parse(res);
      $('#omegadelta').val(jdict.omdelta);
      $('#hashresult').val(jdict.hashres);
      $("#success-res").css('display', 'block');
    });
  });

  $('#button2').on('click', ()=>{
    $('#ca-popup-2').css('display', 'block');
  });

  $('.ca-exout').on('click', ()=>{
    $('#ca-popup-2').css('display', 'none');
  });
}